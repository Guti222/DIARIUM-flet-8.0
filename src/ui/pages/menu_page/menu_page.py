import flet as ft
import sqlite3
from pathlib import Path
import pandas as pd
import threading
import time

# Tus importaciones personalizadas
from src.ui.components.backgrounds import create_modern_background
from src.ui.pages.menu_page.title_buttons import title_buttons
from src.ui.pages.menu_page.title_viewfiles import title_viewfiles
from src.ui.pages.menu_page.title_menu import titlemenu
from src.ui.pages.book_journal_page.book_journal_page import book_journal_page, create_journal_book, agregar_libro
from src.utils.paths import get_db_path
from data.planCuentasOps import crear_plan_cuenta


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
    import_finish_handler = {"fn": None}
    def show_snack_bar(message):
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            action="OK",
            duration=3000
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

    def _run_on_ui(fn):
        """Ejecuta una función en el hilo de UI cuando sea posible."""
        try:
            call_from_thread = getattr(page, "call_from_thread", None)
            if callable(call_from_thread):
                call_from_thread(fn)
                return
            run_on_main = getattr(page, "run_on_main", None)
            if callable(run_on_main):
                run_on_main(fn)
                return
        except Exception:
            pass
        try:
            fn()
        except Exception:
            pass

    def _pubsub_handler(message):
        try:
            if isinstance(message, dict) and message.get("type") == "import_result":
                handler = import_finish_handler.get("fn")
                if callable(handler):
                    handler(message.get("payload"))
        except Exception:
            pass

    try:
        if hasattr(page, "pubsub"):
            page.pubsub.subscribe(_pubsub_handler)
    except Exception:
        pass


    # --- 3. SELECTOR DE ARCHIVOS (TKINTER) ---
    def _load_tk():
        try:
            import tkinter as _tk
            from tkinter import filedialog as _filedialog
            return _tk, _filedialog
        except Exception:
            return None, None

    def pick_file_with_tk() -> str | None:
        tk, filedialog = _load_tk()
        if filedialog is None or tk is None:
            show_snack_bar("Tkinter no está disponible")
            return None
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            path = filedialog.askopenfilename(
                title="Seleccionar libro contable Excel",
                filetypes=[("Excel", "*.xlsx *.xls")],
                parent=root,
            )
            root.destroy()
            return path or None
        except Exception:
            try:
                root.destroy()
            except Exception:
                pass
            return None


    # --- 4. LÓGICA PESADA (EJECUTADA EN SEGUNDO PLANO) ---
    def _get_plan_id_by_name(db_path: str, plan_name: str) -> int | None:
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute(
                "SELECT id_plan_cuenta FROM plan_cuentas WHERE nombre_plan_cuentas = ?",
                (plan_name.strip(),),
            )
            row = cur.fetchone()
            return int(row[0]) if row else None
        except Exception:
            return None
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _load_plan_sheet(file_path: str) -> pd.DataFrame | None:
        try:
            xl = pd.ExcelFile(file_path)
            if "Plan de Cuentas" in xl.sheet_names:
                return pd.read_excel(xl, sheet_name="Plan de Cuentas")
        except Exception:
            return None
        return None

    def _create_plan_from_sheet(db_path: str, plan_name: str, plan_df: pd.DataFrame) -> tuple[int, dict[str, int]]:
        """Crea un plan de cuentas y retorna (plan_id, cuenta_map_por_codigo)."""
        if not plan_name:
            return 0, {}

        plan_id = _get_plan_id_by_name(db_path, plan_name)
        if plan_id is None:
            plan_id = crear_plan_cuenta(db_path, plan_name) or 0

        if plan_id == 0 or plan_df is None or plan_df.empty:
            return plan_id, {}

        # Normalizar columnas
        cols = {str(c).strip(): c for c in plan_df.columns}
        def col(name: str) -> str | None:
            return cols.get(name)

        tipo_code_col = col("TipoCodigo")
        tipo_name_col = col("TipoNombre")
        rubro_code_col = col("RubroCodigo")
        rubro_name_col = col("RubroNombre")
        gen_code_col = col("GenericoCodigo")
        gen_name_col = col("GenericoNombre")
        cuenta_code_col = col("CuentaCodigo")
        cuenta_name_col = col("CuentaNombre")
        cuenta_desc_col = col("CuentaDescripcion")

        if not tipo_code_col:
            return plan_id, {}

        tipo_map: dict[str, int] = {}
        rubro_map: dict[str, int] = {}
        gen_map: dict[str, int] = {}
        cuenta_map: dict[str, int] = {}

        try:
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA busy_timeout=3000")
            cur = conn.cursor()

            for _, row in plan_df.iterrows():
                tipo_code = str(row.get(tipo_code_col, "") or "").strip()
                tipo_name = str(row.get(tipo_name_col, "") or "").strip()
                rubro_code = str(row.get(rubro_code_col, "") or "").strip()
                rubro_name = str(row.get(rubro_name_col, "") or "").strip()
                gen_code = str(row.get(gen_code_col, "") or "").strip()
                gen_name = str(row.get(gen_name_col, "") or "").strip()
                cuenta_code = str(row.get(cuenta_code_col, "") or "").strip()
                cuenta_name = str(row.get(cuenta_name_col, "") or "").strip()
                cuenta_desc = str(row.get(cuenta_desc_col, "") or "").strip()

                if not tipo_code:
                    continue

                if tipo_code not in tipo_map:
                    cur.execute(
                        "SELECT id_tipo_cuenta FROM tipo_cuenta WHERE numero_cuenta = ? AND id_plan_cuenta = ?",
                        (tipo_code, int(plan_id)),
                    )
                    row_tipo = cur.fetchone()
                    if row_tipo:
                        new_id = int(row_tipo[0])
                    else:
                        cur.execute(
                            "INSERT INTO tipo_cuenta (nombre_tipo_cuenta, numero_cuenta, id_plan_cuenta) VALUES (?, ?, ?)",
                            (tipo_name or tipo_code, tipo_code, int(plan_id)),
                        )
                        new_id = int(cur.lastrowid or 0)
                    tipo_map[tipo_code] = int(new_id or 0)

                tipo_id = tipo_map.get(tipo_code, 0)
                if tipo_id and rubro_code:
                    rubro_key = f"{tipo_id}:{rubro_code}"
                    if rubro_key not in rubro_map:
                        cur.execute(
                            "SELECT id_rubro FROM rubro WHERE numero_cuenta = ? AND id_tipo_cuenta = ?",
                            (rubro_code, tipo_id),
                        )
                        row_r = cur.fetchone()
                        if row_r:
                            new_id = int(row_r[0])
                        else:
                            cur.execute(
                                "INSERT INTO rubro (id_tipo_cuenta, nombre_rubro, numero_cuenta) VALUES (?, ?, ?)",
                                (tipo_id, rubro_name or rubro_code, rubro_code),
                            )
                            new_id = int(cur.lastrowid or 0)
                        rubro_map[rubro_key] = int(new_id or 0)

                rubro_id = rubro_map.get(f"{tipo_id}:{rubro_code}", 0)
                if rubro_id and gen_code:
                    gen_key = f"{rubro_id}:{gen_code}"
                    if gen_key not in gen_map:
                        cur.execute(
                            "SELECT id_generico FROM generico WHERE numero_cuenta = ? AND id_rubro = ?",
                            (gen_code, rubro_id),
                        )
                        row_g = cur.fetchone()
                        if row_g:
                            new_id = int(row_g[0])
                        else:
                            cur.execute(
                                "INSERT INTO generico (id_rubro, nombre_generico, numero_cuenta) VALUES (?, ?, ?)",
                                (rubro_id, gen_name or gen_code, gen_code),
                            )
                            new_id = int(cur.lastrowid or 0)
                        gen_map[gen_key] = int(new_id or 0)

                gen_id = gen_map.get(f"{rubro_id}:{gen_code}", 0)
                if gen_id and cuenta_code:
                    if cuenta_code not in cuenta_map:
                        cur.execute(
                            "SELECT id_cuenta_contable FROM cuenta_contable WHERE id_generico = ? AND codigo_cuenta = ?",
                            (gen_id, cuenta_code),
                        )
                        row_c = cur.fetchone()
                        if row_c:
                            cuenta_map[cuenta_code] = int(row_c[0])
                        else:
                            cur.execute(
                                "INSERT INTO cuenta_contable (id_generico, descripcion, nombre_cuenta, codigo_cuenta) VALUES (?, ?, ?, ?)",
                                (gen_id, cuenta_desc, cuenta_name or cuenta_code, cuenta_code),
                            )
                            cuenta_map[cuenta_code] = int(cur.lastrowid or 0)

            conn.commit()
        except Exception as ex:
            print(f"Error creando plan desde Excel: {ex}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

        return plan_id, cuenta_map

    def procesar_excel_en_hilo(file_path: str, plan_name: str | None = None):
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

            # --- Crear Plan si viene en el Excel ---
            plan_df = _load_plan_sheet(file_path)
            plan_id = 0
            cuenta_map_from_plan: dict[str, int] = {}
            if plan_df is not None:
                plan_name_final = (plan_name or "").strip() or Path(file_path).stem
                plan_id, cuenta_map_from_plan = _create_plan_from_sheet(get_db_path(), plan_name_final, plan_df)

            # --- Crear Libro en BD ---
            libro = create_journal_book(empresa, contador_val, str(ano or ""), id_mes, plan_id=plan_id, origen="importado", fecha_importacion=sello_import)
            libro_id = agregar_libro(libro, get_db_path(), allow_duplicates=True)
            
            if not isinstance(libro_id, int):
                return {"error": "No se pudo crear el libro en la BD"}

            # --- INSERCIÓN DE ASIENTOS (OPTIMIZADO CON TRANSACCIÓN) ---
            conn = sqlite3.connect(get_db_path())
            cur = conn.cursor()
            
            # Cargar mapa de cuentas
            if cuenta_map_from_plan:
                cuenta_map = cuenta_map_from_plan
            else:
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
    def iniciar_importacion(file_path: str, plan_name: str | None = None):
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
        import_finish_handler["fn"] = on_thread_finish

        def thread_target():
            res = procesar_excel_en_hilo(file_path, plan_name=plan_name)
            call_from_thread = getattr(page, "call_from_thread", None)
            if callable(call_from_thread):
                call_from_thread(lambda: on_thread_finish(res))
                return
            if hasattr(page, "pubsub"):
                try:
                    page.pubsub.send_all({"type": "import_result", "payload": res})
                    return
                except Exception:
                    pass
            _run_on_ui(lambda: on_thread_finish(res))

        # 4. Iniciar hilo
        t = threading.Thread(target=thread_target, daemon=True)
        t.start()


    # --- 6. EVENTO DEL BOTÓN ---
    def open_file_explorer(_e=None):
        path = pick_file_with_tk()
        if not path:
            return

        # Si el Excel trae plan de cuentas, solicitar nombre del plan
        plan_df_preview = _load_plan_sheet(path)
        if plan_df_preview is None:
            iniciar_importacion(path)
            return

        name_field = ft.TextField(
            label="Nombre del nuevo plan",
            value=Path(path).stem,
            width=420,
            border_color=ft.Colors.BLUE,
            color=ft.Colors.BLACK,
        )

        def close_dialog(dlg):
            dlg.open = False
            page.update()

        def confirm(_e=None):
            plan_name = (name_field.value or "").strip()
            if not plan_name:
                show_snack_bar("Ingresa un nombre para el plan de cuentas")
                return
            close_dialog(dlg)
            iniciar_importacion(path, plan_name=plan_name)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Plan de cuentas detectado", color=ft.Colors.BLUE),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Este archivo trae un plan de cuentas. Indica el nombre para crearlo:", color=ft.Colors.BLACK),
                    name_field,
                ], spacing=10),
                width=520,
                bgcolor=ft.Colors.WHITE,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: close_dialog(dlg), style=ft.ButtonStyle(color=ft.Colors.RED)),
                ft.ElevatedButton("Crear e importar", on_click=confirm, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=ft.Colors.WHITE,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

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
                right=24,
                bottom=24,
                content=ft.FloatingActionButton(
                    icon=ft.Icons.INFO_OUTLINE,
                    on_click=open_creators_dialog,
                    bgcolor=ft.Colors.BLUE,
                    foreground_color=ft.Colors.WHITE,
                    tooltip="Créditos",
                ),
            ),
        ],
        expand=True
    )