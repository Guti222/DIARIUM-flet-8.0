import flet as ft
from types import SimpleNamespace
import sqlite3
from pathlib import Path
import pandas as pd
import threading
import time

# Intento de importar Tkinter (Solo para el diálogo de archivos)
try:
    import tkinter as tk
    from tkinter import filedialog
except Exception:
    tk = None
    filedialog = None

# Tus importaciones personalizadas
from src.ui.components.backgrounds import create_modern_background
from src.ui.pages.menu_page.title_buttons import title_buttons
from src.ui.pages.menu_page.title_viewfiles import title_viewfiles
from src.ui.pages.menu_page.title_menu import titlemenu
from src.ui.pages.book_journal_page.book_journal_page import book_journal_page, create_journal_book, agregar_libro
from src.utils.paths import get_db_path


def menu_page(page: ft.Page):
    
    # --- 1. COMPONENTE DE CARGA (OVERLAY) ---
    # Esto se mostrará mientras se procesa el Excel para que el usuario sepa que está trabajando
    loading_ring = ft.ProgressRing(width=50, height=50, stroke_width=4)
    loading_overlay = ft.Container(
        content=loading_ring,
        alignment=ft.MainAxisAlignment.CENTER,
        bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.BLACK),
        visible=False, # Oculto por defecto
        expand=True,
    )
    # Lo agregamos al overlay de la página (capa superior)
    page.overlay.append(loading_overlay)


    # --- 2. FUNCIONES DE AYUDA (UI) ---
    def show_snack_bar(message):
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            action="OK",
            duration=3000
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()


    # --- 3. SELECTOR DE ARCHIVOS (TKINTER OPTIMIZADO) ---
    def pick_file_with_tk() -> SimpleNamespace | None:
        if filedialog is None:
            show_snack_bar("Tkinter no está disponible")
            return None
        
        path = None
        try:
            # Crear instancia temporal de Tk oculta
            root = tk.Tk()
            root.withdraw() 
            root.attributes('-topmost', True) # Poner al frente
            
            # Abrir diálogo
            path = filedialog.askopenfilename(
                title="Seleccionar libro contable Excel",
                filetypes=[("Excel", "*.xlsx *.xls")],
                parent=root
            )
            
            # Destruir instancia inmediatamente para liberar memoria
            root.destroy()
        except Exception as ex:
            print(f"Error Tkinter: {ex}")
            show_snack_bar(f"Error al abrir selector: {ex}")
            return None

        if path:
            p = Path(path)
            return SimpleNamespace(name=p.name, path=str(p))
        return None


    # --- 4. LÓGICA PESADA (EJECUTADA EN SEGUNDO PLANO) ---
    def procesar_excel_en_hilo(file_path: str):
        """
        Esta función contiene toda la lógica pesada. 
        Se ejecutará en un hilo aparte para no congelar la UI.
        """
        try:
            print(f"[THREAD] Leyendo Excel: {file_path}")
            df = pd.read_excel(file_path, header=None)
            
            if df.empty or df.shape[1] < 5:
                return {"error": "Formato de Excel no reconocido o vacío"}

            # --- Detección de Cabecera ---
            header_idx = None
            for i in range(min(5, len(df))):
                val = str(df.iloc[i, 0]).strip().lower()
                if val == "fecha":
                    header_idx = i
                    break
            if header_idx is None:
                header_idx = 1
            
            start_row = header_idx + 1

            # --- Metadatos (Empresa, Contador, Fecha) ---
            titulo = str(df.iloc[0, 0] or "")
            empresa = Path(file_path).stem
            contador = ""
            if "empresa(" in titulo.lower():
                try: empresa = titulo.split("Empresa(")[1].split(")")[0]
                except: pass
            if "contador:" in titulo.lower():
                try: contador = titulo.split("Contador:")[1].split(")")[0].strip()
                except: pass

            primera_fecha = None
            for idx in range(start_row, len(df)):
                val = df.iloc[idx, 0]
                if pd.notna(val):
                    try:
                        primera_fecha = pd.to_datetime(val).date()
                        break
                    except: continue

            id_mes = primera_fecha.month if primera_fecha else 0
            ano = primera_fecha.year if primera_fecha else 0
            
            # Sello de tiempo
            try:
                mtime = Path(file_path).stat().st_mtime
                from datetime import datetime
                sello_import = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            except: sello_import = ""

            contador_val = f"{contador or 'N/D'} | importado: {sello_import}"

            # --- Crear Libro en BD ---
            libro = create_journal_book(empresa, contador_val, str(ano or ""), id_mes, plan_id=0, origen="importado", fecha_importacion=sello_import)
            libro_id = agregar_libro(libro, get_db_path(), allow_duplicates=True)
            
            if not isinstance(libro_id, int):
                return {"error": "No se pudo crear el libro en la BD"}

            # --- INSERCIÓN DE ASIENTOS (OPTIMIZADO CON TRANSACCIÓN) ---
            conn = sqlite3.connect(get_db_path())
            cur = conn.cursor()
            
            # Cargar mapa de cuentas
            cur.execute("SELECT id_cuenta_contable, codigo_cuenta FROM cuenta_contable")
            cuenta_map = { (c or '').strip(): i for (i, c) in cur.fetchall() }

            # Iniciar Transacción (CRÍTICO PARA VELOCIDAD)
            cur.execute("BEGIN TRANSACTION")

            try:
                numero_asiento = 1
                asiento_id = None
                total_debe = 0.0
                total_haber = 0.0

                for idx in range(start_row, len(df)):
                    fecha_cell = df.iloc[idx, 0]
                    codigo = df.iloc[idx, 1]
                    descripcion = df.iloc[idx, 2]
                    debe = df.iloc[idx, 3]
                    haber = df.iloc[idx, 4]
                    desc_str = str(descripcion) if pd.notna(descripcion) else ""

                    # Nuevo Asiento
                    if pd.notna(fecha_cell) and "---" in desc_str:
                        f_str = pd.to_datetime(fecha_cell).strftime("%Y-%m-%d")
                        cur.execute(
                            "INSERT INTO asiento (id_libro_diario, fecha, numero_asiento, descripcion) VALUES (?, ?, ?, ?)",
                            (libro_id, f_str, numero_asiento, "")
                        )
                        asiento_id = cur.lastrowid
                        numero_asiento += 1
                        continue
                    
                    # Actualizar descripción asiento
                    if pd.isna(codigo) and pd.isna(debe) and pd.isna(haber) and desc_str and asiento_id:
                        cur.execute("UPDATE asiento SET descripcion = ? WHERE id_asiento = ?", (desc_str, asiento_id))
                        continue

                    # Línea contable
                    if pd.notna(codigo):
                        # Fallback si no hay cabecera
                        if asiento_id is None:
                            hoy = pd.Timestamp("today").strftime("%Y-%m-%d")
                            cur.execute(
                                "INSERT INTO asiento (id_libro_diario, fecha, numero_asiento, descripcion) VALUES (?, ?, ?, ?)",
                                (libro_id, hoy, numero_asiento, "Generado Auto")
                            )
                            asiento_id = cur.lastrowid
                            numero_asiento += 1

                        id_cuenta = cuenta_map.get(str(codigo).strip())
                        if id_cuenta:
                            d_val = float(debe or 0)
                            h_val = float(haber or 0)
                            cur.execute(
                                "INSERT INTO linea_asiento (id_asiento, debe, haber, id_cuenta_contable) VALUES (?, ?, ?, ?)",
                                (asiento_id, d_val, h_val, id_cuenta)
                            )
                            total_debe += d_val
                            total_haber += h_val

                # Actualizar totales
                cur.execute(
                    "UPDATE libro_diario SET total_debe = ?, total_haber = ? WHERE id_libro_diario = ?",
                    (total_debe, total_haber, libro_id)
                )
                
                # Commit final (Guarda todo de golpe)
                conn.commit()
            
            except Exception as e:
                conn.rollback()
                conn.close()
                return {"error": f"Error SQL durante la importación: {e}"}
            
            conn.close()
            return {"success": True, "libro_id": libro_id}

        except Exception as ex:
            return {"error": f"Error general: {ex}"}


    # --- 5. ORQUESTADOR DE IMPORTACIÓN ---
    def iniciar_importacion(file_path: str):
        # 1. Mostrar pantalla de carga
        loading_overlay.visible = True
        page.update()

        # 2. Definir lo que pasa al terminar el hilo
        def on_thread_finish(resultado):
            loading_overlay.visible = False
            
            if "error" in resultado:
                show_snack_bar(resultado["error"])
                page.update()
            else:
                # Éxito: Navegar a la página del libro
                nuevo_id = resultado["libro_id"]
                show_snack_bar("Libro cargado correctamente")
                
                page.clean()
                page.add(book_journal_page(page, libro_id=nuevo_id))
                page.update()

        # 3. Función wrapper para el hilo
        def thread_target():
            res = procesar_excel_en_hilo(file_path)
            # Volver al hilo principal no es automático en todas las versiones,
            # pero en Flet podemos acceder a la variable `resultado` desde fuera si usamos closures,
            # o simplemente ejecutar la actualización visual aquí si el entorno lo permite.
            # Lo más seguro es esto:
            on_thread_finish(res)

        # 4. Iniciar hilo
        t = threading.Thread(target=thread_target, daemon=True)
        t.start()


    # --- 6. EVENTO DEL BOTÓN ---
    def open_file_explorer(_e=None):
        # Seleccionar archivo (Bloquea brevemente UI, pero es rápido)
        selected_file = pick_file_with_tk()
        
        if selected_file:
            print(f"[IMPORT] Archivo seleccionado: {selected_file.name}")
            # Iniciar proceso pesado en hilo
            iniciar_importacion(selected_file.path)
        else:
            print("[IMPORT] Selección cancelada")

    # --- 6.1 BOTÓN DE CRÉDITOS ---
    creators = [
        ("Augusto Gutierrez", "augustogutierrez900@gmail.com"),
        ("Juan Salcedo", "goku999d9@gmail.com"),
        ("Andres Molina","molina30165715@usm.edu.ve")
    ]

    def open_creators_dialog(_e=None):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Creadores y Contacto", color=ft.Colors.BLUE),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Equipo de desarrollo", color=ft.Colors.BLACK),
                        ft.Divider(),
                        *[
                            ft.Row([
                                ft.Text(name, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                                ft.Text(email, color=ft.Colors.GREY_800),
                            ], spacing=12)
                            for name, email in creators
                        ],
                    ],
                    spacing=8,
                ),
                width=420,
                height=300,
                bgcolor=ft.Colors.WHITE,
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: (setattr(dlg, "open", False), page.update()), style=ft.ButtonStyle(color=ft.Colors.BLUE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=ft.Colors.WHITE,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()


    # --- 7. CONSTRUCCIÓN DE LA PÁGINA ---
    
    # Pasar la función al botón
    buttons_content = title_buttons(open_file_explorer, page)
    
    # Contenido visual
    fondo = create_modern_background(page)
    
    contenido = ft.Container(
        expand=True,
        padding=ft.padding.only(top=50, left=50, right=50, bottom=80),
        content=ft.Column(
            [
                # Header
                ft.Container(
                    content=ft.Row(
                        [
                            titlemenu(),
                            ft.Container(expand=True),
                            buttons_content,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        expand=True,
                    ),
                ),
                # Lista de archivos recientes
                title_viewfiles(page),
            ],
            expand=True,
        )
    )

    return ft.Stack(
        controls=[
            fondo,
            contenido,
            ft.Container(
                content=ft.FloatingActionButton(
                    icon=ft.Icons.INFO_OUTLINE,
                    on_click=open_creators_dialog,
                    bgcolor=ft.Colors.BLUE,
                    foreground_color=ft.Colors.WHITE,
                    tooltip="Créditos",
                ),
                alignment=ft.alignment.Alignment(1, 1),
                padding=ft.padding.only(right=24, bottom=24),
            ),
            # Nota: loading_overlay ya está en page.overlay, no hace falta ponerlo aquí
        ],
        expand=True
    )