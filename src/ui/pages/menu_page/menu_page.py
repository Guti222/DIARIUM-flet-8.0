import flet as ft
from types import SimpleNamespace
import sqlite3
from pathlib import Path

import pandas as pd

# Tkinter para diálogos nativos
try:
    import tkinter as tk
    from tkinter import filedialog
except Exception:
    tk = None
    filedialog = None

from src.ui.components.backgrounds import create_modern_background
from src.ui.pages.menu_page.title_buttons import title_buttons
from src.ui.pages.menu_page.title_viewfiles import title_viewfiles
from src.ui.pages.menu_page.title_menu import titlemenu
from src.ui.pages.book_journal_page.book_journal_page import book_journal_page, create_journal_book, agregar_libro
from src.utils.paths import get_db_path


def menu_page(page: ft.Page):
    # ✅ Función auxiliar para mostrar mensajes
    def show_snack_bar(message):
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            action="OK",
            duration=3000
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()
    
    # (Dialogo eliminado) importación directa tras seleccionar archivo

    # ✅ Función para manejar la selección de archivos (Tkinter como respaldo)
    def pick_file_with_tk() -> SimpleNamespace | None:
        if filedialog is None:
            show_snack_bar("Tkinter no está disponible en este entorno")
            return None
        root = None
        try:
            root = tk.Tk()
            root.withdraw()
            try:
                root.attributes('-topmost', True)
                root.update()
            except Exception:
                pass
            path = filedialog.askopenfilename(
                title="Seleccionar libro contable Excel",
                filetypes=[("Excel", "*.xlsx *.xls")]
            )
            if not path:
                return None
            from pathlib import Path
            p = Path(path)
            return SimpleNamespace(name=p.name, path=str(p))
        except Exception as ex:
            show_snack_bar(f"No se pudo abrir el selector: {ex}")
            return None
        finally:
            try:
                if root is not None:
                    root.destroy()
            except Exception:
                pass

    # ✅ Procesamiento común tras elegir archivo
    def handle_selected_file(selected_file: SimpleNamespace):
        if not selected_file:
            show_snack_bar("No se seleccionó ningún archivo")
            return
        print(f"[IMPORT] Archivo seleccionado: name={selected_file.name} path={selected_file.path}")
        show_snack_bar(f"Archivo seleccionado: {selected_file.name}")
        try:
            print(f"[IMPORT] Iniciar import directo: {selected_file.path}")
            new_id = importar_libro_desde_excel(selected_file.path)
            if not isinstance(new_id, int):
                raise ValueError("No se pudo crear el libro en la base de datos")
            page.clean()
            page.add(book_journal_page(page, libro_id=new_id))
            page.update()
            show_snack_bar("Libro cargado correctamente")
        except Exception as ex:
            show_snack_bar(f"No se pudo cargar el libro: {ex}")

    # ✅ Función para abrir el explorador de archivos (solo Tkinter)
    def open_file_explorer(_e=None):
        selected_file = pick_file_with_tk()
        if selected_file:
            handle_selected_file(selected_file)
        else:
            show_snack_bar("No se pudo abrir el selector de archivos")

    # ✅ Importar Excel exportado y cargarlo a la BD
    def importar_libro_desde_excel(file_path: str) -> int:
        print(f"[IMPORT] Archivo recibido: {file_path}")
        df = pd.read_excel(file_path, header=None)
        print(f"[IMPORT] Shape dataframe: {df.shape}")
        if df.empty or df.shape[1] < 5:
            raise ValueError("Formato de Excel no reconocido")

        # Ubicar fila de encabezados (buscar "Fecha" en la primera columna)
        header_idx = None
        for i in range(min(5, len(df))):
            val = str(df.iloc[i, 0]).strip().lower()
            if val == "fecha":
                header_idx = i
                break
        if header_idx is None:
            header_idx = 1  # fallback: después del título

        print(f"[IMPORT] header_idx={header_idx}")

        start_row = header_idx + 1

        # Extraer empresa/contador del título si existe (fila 0, col 0)
        titulo = str(df.iloc[0, 0] or "")
        empresa = Path(file_path).stem
        contador = ""
        if "empresa(" in titulo.lower():
            try:
                empresa = titulo.split("Empresa(")[1].split(")")[0]
            except Exception:
                pass
        if "contador:" in titulo.lower():
            try:
                contador = titulo.split("Contador:")[1].split(")")[0].strip()
            except Exception:
                pass

        # Detectar primera fecha para año/mes
        primera_fecha = None
        for idx in range(start_row, len(df)):
            val = df.iloc[idx, 0]
            if pd.notna(val):
                try:
                    primera_fecha = pd.to_datetime(val).date()
                    break
                except Exception:
                    continue

        id_mes = primera_fecha.month if primera_fecha else 0
        ano = primera_fecha.year if primera_fecha else 0

        # Sello de importación con fecha de creación del archivo
        try:
            mtime = Path(file_path).stat().st_mtime
            from datetime import datetime
            sello_import = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        except Exception:
            sello_import = ""

        print(f"[IMPORT] empresa={empresa} contador={contador} ano={ano} mes={id_mes} sello={sello_import}")

        # Crear libro
        contador_val = contador or "N/D"
        if sello_import:
            contador_val = f"{contador_val} | importado: {sello_import}"
        libro = create_journal_book(empresa, contador_val, str(ano or ""), id_mes, plan_id=0, origen="importado", fecha_importacion=sello_import or None)
        libro_id = agregar_libro(libro, get_db_path(), allow_duplicates=True)
        print(f"[IMPORT] libro_id creado={libro_id}")
        if not isinstance(libro_id, int):
            raise ValueError("No se pudo registrar el libro")

        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Map de cuentas por código
        cur.execute("SELECT id_cuenta_contable, codigo_cuenta FROM cuenta_contable")
        cuenta_map = { (c or '').strip(): i for (i, c) in cur.fetchall() }
        print(f"[IMPORT] cuentas en map={len(cuenta_map)}")

        numero_asiento = 1
        asiento_id = None
        libro_total_debe = 0.0
        libro_total_haber = 0.0

        def crear_asiento(fecha_val, descripcion=""):
            nonlocal numero_asiento, asiento_id
            fecha_str = pd.to_datetime(fecha_val).strftime("%Y-%m-%d") if pd.notna(fecha_val) else None
            cur.execute(
                "INSERT INTO asiento (id_libro_diario, fecha, numero_asiento, descripcion) VALUES (?, ?, ?, ?)",
                (libro_id, fecha_str, numero_asiento, descripcion or "")
            )
            asiento_id = cur.lastrowid
            numero_asiento += 1
            print(f"[IMPORT] Nuevo asiento id={asiento_id} fecha={fecha_str} desc={descripcion}")

        def actualizar_descripcion(desc: str):
            if asiento_id and desc:
                cur.execute("UPDATE asiento SET descripcion = ? WHERE id_asiento = ?", (desc, asiento_id))

        # Recorrer filas del contenido exportado
        for idx in range(start_row, len(df)):
            fecha_cell = df.iloc[idx, 0]
            codigo = df.iloc[idx, 1]
            descripcion = df.iloc[idx, 2]
            debe = df.iloc[idx, 3]
            haber = df.iloc[idx, 4]

            desc_str = str(descripcion) if pd.notna(descripcion) else ""

            # Cabecera de asiento: tiene fecha y separador --- en la descripción
            if pd.notna(fecha_cell) and "---" in desc_str:
                crear_asiento(fecha_cell, "")
                continue

            # Comentario final del asiento (sin código ni montos)
            if pd.isna(codigo) and pd.isna(debe) and pd.isna(haber) and desc_str:
                actualizar_descripcion(desc_str)
                continue

            # Línea contable
            if pd.notna(codigo):
                if asiento_id is None:
                    # Si no hay cabecera previa, crea una genérica con la primera fecha hallada
                    crear_asiento(primera_fecha or pd.Timestamp("today"))
                codigo_str = str(codigo).strip()
                id_cuenta = cuenta_map.get(codigo_str)
                if not id_cuenta:
                    # Cuenta desconocida: saltar la línea
                    print(f"[IMPORT] Cuenta no encontrada para codigo={codigo_str}, fila={idx}")
                    continue
                monto_debe = float(debe or 0)
                monto_haber = float(haber or 0)
                cur.execute(
                    "INSERT INTO linea_asiento (id_asiento, debe, haber, id_cuenta_contable) VALUES (?, ?, ?, ?)",
                    (asiento_id, monto_debe, monto_haber, id_cuenta)
                )
                print(f"[IMPORT] linea -> asiento={asiento_id} codigo={codigo_str} debe={monto_debe} haber={monto_haber}")
                libro_total_debe += monto_debe
                libro_total_haber += monto_haber

        # Actualizar totales del libro
        cur.execute(
            "UPDATE libro_diario SET total_debe = ?, total_haber = ? WHERE id_libro_diario = ?",
            (libro_total_debe, libro_total_haber, libro_id)
        )

        print(f"[IMPORT] Totales libro -> debe={libro_total_debe} haber={libro_total_haber}")

        conn.commit()
        conn.close()
        return libro_id
    
    # Pasar la función a title_buttons
    buttons_content = title_buttons(open_file_explorer, page)
    
    # Contenido de la página
    fondo = create_modern_background(page)
    
    contenido = ft.Container(
        expand=True,
        padding=ft.padding.only(top=50, left=50, right=50, bottom=80),
        content=ft.Column(
            [
                # Fila superior (header)
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
                title_viewfiles(page),
            ],
            expand=True,
        )
    )

    return ft.Stack(
        controls=[
            fondo,
            contenido
        ],
        expand=True
    )