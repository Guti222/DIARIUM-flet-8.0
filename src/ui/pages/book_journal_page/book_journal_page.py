import flet as ft
import sqlite3
from pathlib import Path
from sqlite3 import Error
import time
from src.ui.pages.book_journal_page.dialog.accounting_voucher_dialog import AccountingVoucherDialog
import urllib.parse
from src.services.exportarLibro import exportar_libro_diario

from data.models.libro import LibroDiario
from src.ui.components.backgrounds import create_modern_background
from data.obtenerAsientos import obtenerAsientosDeLibro
from src.utils.paths import get_db_path

def title_widget():
    return ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.MENU_BOOK, color=ft.Colors.BLUE_800, size=34),
            ft.Text(
                "Libro Diario",
                size=32,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE_800,
            ),
        ], spacing=12, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.padding.only(bottom=8),
    )

def button_add_asiento(page: ft.Page, refresh_callback, libro: LibroDiario):
    def abrir_dialogo(e):
        try:
                AccountingVoucherDialog(page, libro.id_libro_diario, on_saved=refresh_callback).open()
                # Optionally call refresh after close; user can add later
        except Exception as ex:
            err = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text(f"Error abriendo diálogo: {ex}"),
                actions=[ft.TextButton("Cerrar", on_click=lambda ev: (setattr(err, 'open', False), page.update()))],
            )
            page.dialog = err
            err.open = True
            page.update()
    return ft.FloatingActionButton(
        "Añadir Comprobante contable",
        icon=ft.Icons.ADD,
        bgcolor=ft.Colors.BLUE,
        foreground_color=ft.Colors.WHITE,
        on_click=abrir_dialogo
    )

def title_book_journal(empresa: str = "", contador: str = "", anio: str = "", mes: str = ""):
    return ft.Container(
        padding=ft.padding.all(12),
        bgcolor=ft.Colors.BLUE_50,
        border=ft.border.all(1, ft.Colors.BLUE_200),
        border_radius=8,
        content=ft.Column([
            ft.Text(f'Empresa: {empresa}', size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
            ft.Text(f'Contador: {contador}', size=14, color=ft.Colors.BLUE_800),
            ft.Text(f'Periodo: {anio}-{str(mes).zfill(2)}', size=14, color=ft.Colors.BLUE_700),
        ], spacing=4)
    )


def contenido(page: ft.Page, libro: LibroDiario):
    # Callback de refresco: re-render del grid cuando ya está en la página
    def refresh_diario():
        try:
            render_journal_grid(do_update=True)
        except Exception:
            page.update()

    # Envolver el contenido en un contenedor blanco para asegurar contraste
    inner = ft.Container(
        content=ft.Column([
            title_widget(),
            button_add_asiento(page, refresh_callback=refresh_diario, libro=libro),
            title_book_journal(empresa=libro.nombre_empresa, contador=libro.contador, anio=libro.ano, mes=libro.mes),
        ], spacing=12),
        padding=16,
        bgcolor=ft.Colors.WHITE,
        border_radius=14,
        opacity=1.0,
        width=270,
        height=300,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=14, color=ft.Colors.BLUE_200, offset=ft.Offset(0, 4)),
    )
    # Wrap inner content in a fixed-width container so inner layout doesn't reflow
    # if outer container is ever animated (prevents text 'squash' on resize).
    inner_fixed = ft.Container(content=inner, width=270,height=300, padding=0)

    # Outer animated container (follows pattern from animatedContainer demo)
    outer = ft.Container(
        content=inner_fixed,
        width=270,
        height=300,
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, ft.Colors.GREY_300),
        padding=0,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        animate=ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.BLACK26, offset=ft.Offset(0, 2)),
    )

    # Grid container + totals; allows refreshing without route reload
    grid_container = ft.Container(height=650, expand=True, border=ft.border.all(1, ft.Colors.BLUE_200), border_radius=12, bgcolor=ft.Colors.WHITE)
    totals_container = ft.Container(
        height=52,
        padding=ft.padding.symmetric(vertical=10, horizontal=12),
        border=ft.border.only(top=ft.border.BorderSide(1, ft.Colors.BLUE_200)),
        border_radius=12,
        bgcolor=ft.Colors.WHITE,
    )

    def render_journal_grid(do_update: bool = False):
        rows = obtenerAsientosDeLibro(get_db_path(), libro.id_libro_diario)
        header = ft.Container(
            gradient=ft.LinearGradient(begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1), colors=[ft.Colors.BLUE_100, ft.Colors.BLUE_50]),
            border=ft.border.only(bottom=ft.border.BorderSide(2, ft.Colors.BLUE_300)),
            padding=12,
            content=ft.Row([
                ft.Text('Fecha', weight=ft.FontWeight.BOLD, expand=1, color=ft.Colors.BLUE_900),
                ft.Text('Código', weight=ft.FontWeight.BOLD, expand=1, color=ft.Colors.BLUE_900),
                ft.Text('Descripción', weight=ft.FontWeight.BOLD, expand=4, color=ft.Colors.BLUE_900),
                ft.Text('Debe', weight=ft.FontWeight.BOLD, expand=1, color=ft.Colors.BLUE_900),
                ft.Text('Haber', weight=ft.FontWeight.BOLD, expand=1, color=ft.Colors.BLUE_900),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        )

        def on_row_click(asiento_id: int):
            try:
                # Abrir en modo edición y refrescar la grilla al guardar
                AccountingVoucherDialog(page, libro.id_libro_diario, asiento_id=asiento_id, on_saved=refresh_diario).open()
            except Exception as ex:
                err = ft.AlertDialog(title=ft.Text("Error"), content=ft.Text(f"No se pudo abrir edición: {ex}"))
                page.dialog = err
                err.open = True
                page.update()

        # Agrupar por asiento; soporta filas con o sin numero_asiento
        grouped = {}
        for row in rows:
            if len(row) == 8:
                id_asiento, numero_asiento, fecha, descripcion, codigo, nombre, debe, haber = row
            elif len(row) == 7:
                id_asiento, fecha, descripcion, codigo, nombre, debe, haber = row
                numero_asiento = id_asiento  # fallback si no viene el campo
            else:
                # estructura inesperada; saltar fila
                continue
            grouped.setdefault(id_asiento, {
                "numero_asiento": numero_asiento,
                "fecha": fecha,
                "descripcion": descripcion,
                "lines": []
            })
            grouped[id_asiento]["lines"].append((codigo, nombre, debe, haber))

        grid_rows = []
        total_debe = 0.0
        total_haber = 0.0
        row_index = 0
        for aid, data in grouped.items():
            fecha = data["fecha"]
            descripcion = data["descripcion"] or ''
            lines = data["lines"]

            # Asiento header line: ----(numero_asiento)---- fecha; other columns empty
            grid_rows.append(
                ft.Container(
                    padding=10,
                    bgcolor=ft.Colors.BLUE_50,
                    border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.BLUE_100), top=ft.border.BorderSide(1, ft.Colors.BLUE_100)),
                    on_click=lambda e, xid=aid: on_row_click(xid),
                    content=ft.Row([
                        ft.Text(f" {fecha}", expand=1, color=ft.Colors.BLUE_800),
                        ft.Text("", expand=1),
                        ft.Text(f"— Asiento {data['numero_asiento']} —", expand=4, text_align=ft.TextAlign.CENTER, color=ft.Colors.BLUE_700),
                        ft.Text("", expand=1),
                        ft.Text("", expand=1),
                    ], spacing=12)
                )
            )

            # Line items: no date; ensure indentation for Haber and correct description per line
            for idx, (codigo, nombre, debe, haber) in enumerate(lines):
                es_ultima = (idx == len(lines) - 1)
                base_nombre = (nombre or '').strip()
                comentario = descripcion.strip() if isinstance(descripcion, str) else ''
                # Descripción de la línea
                if es_ultima:
                    # Última línea: mostrar solo el nombre de la cuenta (el comentario se agrega en la fila aparte abajo)
                    desc_line = base_nombre or comentario
                else:
                    desc_line = base_nombre
                # Determinar sangría según montos
                try:
                    monto_haber = float(haber or 0)
                except Exception:
                    monto_haber = 0.0
                try:
                    monto_debe = float(debe or 0)
                except Exception:
                    monto_debe = 0.0
                # Acumular totales globales
                total_debe += monto_debe
                total_haber += monto_haber
                indent_desc = ft.Container(
                    content=ft.Text(desc_line, color=ft.Colors.BLACK),
                    padding=ft.padding.only(left=24) if (monto_haber > 0 and monto_debe == 0) else ft.padding.all(0),
                    expand=4,
                )
                # Alternar color de fondo (usar BLUE_50 como tono claro disponible)
                row_bg = ft.Colors.WHITE if (row_index % 2 == 0) else ft.Colors.BLUE_50
                grid_rows.append(
                    ft.Container(
                        padding=8,
                        bgcolor=row_bg,
                        border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.BLUE_50)),
                        on_click=lambda e, xid=aid: on_row_click(xid),
                        content=ft.Row([
                            ft.Text("", expand=1),
                            ft.Text(codigo or '', expand=1, color=ft.Colors.GREY_800),
                            indent_desc,
                            ft.Container(
                                expand=1,
                                alignment=ft.Alignment(1, 0),
                                content=ft.Text(f"{float(debe or 0):.2f}", color=ft.Colors.GREEN_700),
                            ),
                            ft.Container(
                                expand=1,
                                alignment=ft.Alignment(1, 0),
                                content=ft.Text(f"{float(haber or 0):.2f}", color=ft.Colors.RED_700),
                            ),
                        ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    )
                )
                row_index += 1
            # Extra comment-only row appended once after all lines
            comentario_final = descripcion.strip() if isinstance(descripcion, str) else ''
            if comentario_final:
                grid_rows.append(
                    ft.Container(
                        padding=8,
                        bgcolor=ft.Colors.BLUE_50,
                        border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.BLUE_100)),
                        on_click=lambda e, xid=aid: on_row_click(xid),
                        content=ft.Row([
                            ft.Text("", expand=1),
                            ft.Text("", expand=1),
                            ft.Text(comentario_final, expand=4, color=ft.Colors.BLUE_800, style=ft.TextStyle(italic=True)),
                            ft.Text("", expand=1),
                            ft.Text("", expand=1),
                        ], spacing=12)
                    )
                )

        grid_container.content = ft.ListView(
            controls=[header] + grid_rows,
            spacing=0,
            padding=0,
        )
        # Render totales debajo de la grilla
        totals_container.content = ft.Row(
            [
                ft.Text("Totales:", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ft.Container(expand=True),
                ft.Text(f"Debe: {total_debe:.2f}", weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                ft.Text(f"Haber: {total_haber:.2f}", weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        # Solo actualizar si el contenedor ya está adjunto a la página
        if do_update and getattr(grid_container, "_Control__page", None) is not None:
            grid_container.update()
            if getattr(totals_container, "_Control__page", None) is not None:
                totals_container.update()

    # Render inicial sin update; el contenedor aún no está adjunto
    render_journal_grid(do_update=False)

    return ft.Container(
        content=ft.Row([
            outer,
            ft.Container(
                expand=True,
                content=ft.Column([
                    ft.Text("Tabla", size=20, weight=ft.FontWeight.BOLD),
                    grid_container,
                    totals_container,
                ], spacing=10, expand=True),
            ),
        ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.START, expand=True),
        alignment=ft.Alignment(0, -1),
        padding=ft.padding.all(20),
        expand=True
    )

from src.ui.pages.book_journal_page.account_book_card import TAccountBookCard
from data.obtenerCuentas import obtenerTodasCuentasContables
from data.models.lineaAsiento import LineaAsiento

def contenido_mayor(page: ft.Page, libro: LibroDiario):
    # Encabezado
    header = ft.Row([
        ft.Icon(ft.Icons.MENU_BOOK, color=ft.Colors.BLUE_800, size=28),
        ft.Text("Libro Mayor", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
    ], spacing=10, alignment=ft.MainAxisAlignment.START)

    # Consultar todas las cuentas usadas en el libro diario
    db_path = get_db_path()
    import sqlite3
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT DISTINCT c.id_cuenta_contable, c.codigo_cuenta, c.nombre_cuenta
        FROM cuenta_contable c
        JOIN linea_asiento la ON la.id_cuenta_contable = c.id_cuenta_contable
        JOIN asiento a ON a.id_asiento = la.id_asiento
        WHERE a.id_libro_diario = ?
        ORDER BY c.codigo_cuenta ASC
        """,
        (libro.id_libro_diario,)
    )
    cuentas_usadas = cur.fetchall() or []

    cards: list[ft.Control] = []
    for (id_cuenta, codigo, nombre) in cuentas_usadas:
        # Traer todas las líneas de esta cuenta para el libro
        cur.execute(
            """
            SELECT la.id_linea_asiento, la.id_asiento, la.debe, la.haber, la.id_cuenta_contable
            FROM linea_asiento la
            JOIN asiento a ON a.id_asiento = la.id_asiento
            WHERE la.id_cuenta_contable = ? AND a.id_libro_diario = ?
            ORDER BY a.fecha ASC, la.id_linea_asiento ASC
            """,
            (id_cuenta, libro.id_libro_diario)
        )
        rows = cur.fetchall() or []
        lineas: list[LineaAsiento] = [
            LineaAsiento(
                id_linea_asiento=r[0], id_asiento=r[1], debe=float(r[2] or 0), haber=float(r[3] or 0), id_cuenta_contable=r[4]
            ) for r in rows
        ]
        total_debe = sum(l.debe or 0 for l in lineas)
        total_haber = sum(l.haber or 0 for l in lineas)
        card = TAccountBookCard(account_name=nombre or "Cuenta", account_code=codigo or "", debe=total_debe, haber=total_haber, listacuentas=lineas)
        cards.append(ft.Container(content=card.build(), padding=ft.padding.symmetric(vertical=8)))

    try:
        conn.close()
    except Exception:
        pass

    # Fila de tarjetas con scroll horizontal (o mensaje si no hay)
    cards_row = ft.Row(cards, spacing=16, scroll=ft.ScrollMode.ALWAYS) if cards else None

    inner = ft.Container(
        content=ft.Column([
            header,
            ft.Container(
                content=(cards_row if cards_row else ft.Text("No hay cuentas utilizadas en este libro.", color=ft.Colors.GREY_600)),
                expand=True,
            ),
        ], spacing=16, expand=True),
        padding=20,
        border_radius=16,
        bgcolor=ft.Colors.WHITE,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=16, color=ft.Colors.BLUE_200, offset=ft.Offset(0, 4)),
        expand=True,
    )

    return ft.Container(
        content=ft.Column([inner], expand=True),
        alignment=ft.Alignment(0, -1),
        padding=ft.padding.all(20),
        expand=True,
    )
    
def create_journal_book(empresa: str = "", contador: str = "", anio: str = "", mes: str = "", plan_id: int = 0, origen: str = "creado", fecha_importacion: str | None = None) -> LibroDiario:
    # Map month name to id if possible
    month_map = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
        "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
        "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
    }

    id_mes = 0
    if isinstance(mes, int):
        id_mes = mes
    elif isinstance(mes, str) and mes.strip():
        try:
            id_mes = int(mes)
        except ValueError:
            id_mes = month_map.get(mes.strip().lower(), 0)

    try:
        ano_int = int(anio)
    except Exception:
        ano_int = 0

    # Crear y retornar una instancia de LibroDiario con los parámetros dados
    libro = LibroDiario(
        nombre_empresa=empresa,
        contador=contador,
        ano=ano_int,
        id_mes=id_mes,
        id_plan_cuenta=plan_id,
        origen=origen or "creado",
        fecha_importacion=fecha_importacion,
    )

    return libro

def agregar_libro(libro: LibroDiario, path_bd: str, allow_duplicates: bool = False):
    # Inserta el libro en la tabla `libro_diario`.
    # Si allow_duplicates=False (por defecto), evita duplicar por misma empresa/año/mes/plan/contador.
    # Si allow_duplicates=True, siempre crea un nuevo registro.
    attempts = 0
    max_attempts = 5
    wait_seconds = 0.3
    while attempts < max_attempts:
        conn = None
        try:
            conn = sqlite3.connect(path_bd, timeout=5)
            conn.execute("PRAGMA busy_timeout=3000")
            conn.execute("PRAGMA journal_mode=WAL")
            cursor = conn.cursor()

            if not allow_duplicates:
                cursor.execute(
                    "SELECT id_libro_diario FROM libro_diario WHERE id_mes = ? AND ano = ? AND nombre_empresa = ? AND contador = ? AND COALESCE(id_plan_cuenta, 0) = ?",
                    (libro.id_mes, libro.ano, libro.nombre_empresa, libro.contador, int(libro.id_plan_cuenta or 0))
                )
                existing = cursor.fetchone()
                if existing:
                    print(f"El libro ya existe (id={existing[0]}). No se creará otro.")
                    return existing[0]

            cursor.execute(
                "INSERT INTO libro_diario (id_mes, ano, contador, nombre_empresa, total_debe, total_haber, id_plan_cuenta, origen, fecha_importacion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (libro.id_mes, libro.ano, libro.contador, libro.nombre_empresa, 0.0, 0.0, int(libro.id_plan_cuenta or 0), libro.origen or "creado", libro.fecha_importacion)
            )
            conn.commit()
            new_id = cursor.lastrowid
            print(f"Libro agregado exitosamente. id={new_id}")
            return new_id
        except Error as e:
            msg = str(e)
            if "database is locked" in msg.lower():
                attempts += 1
                print(f"BD bloqueada, reintentando ({attempts}/{max_attempts})...")
                time.sleep(wait_seconds)
                continue
            print(f"Error al agregar el libro: {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    print("No se pudo insertar el libro tras varios reintentos.")
    return None
    
    

def book_journal_page(page: ft.Page, empresa: str = "", contador: str = "", anio: str = "", mes: str = "", plan_id: str = "0", libro_id: int | None = None, file_picker: ft.FilePicker | None = None):
    # Ensure page background is white so content is readable over decorative background
    try:
        page.bgcolor = ft.Colors.WHITE
    except Exception:
        pass

    # Parse plan_id to int
    try:
        plan_int = int(plan_id or 0)
    except Exception:
        plan_int = 0
    # Construir libro base con parámetros
    libro_diario = create_journal_book(empresa, contador, anio, mes, plan_id=plan_int)
    # Si viene un ID, cargar datos desde BD y evitar inserción automática
    from src.utils.paths import get_db_path
    if isinstance(libro_id, int):
        try:
            conn = sqlite3.connect(get_db_path())
            cur = conn.cursor()
            cur.execute(
                "SELECT id_libro_diario, id_mes, ano, contador, nombre_empresa, COALESCE(id_plan_cuenta,0) FROM libro_diario WHERE id_libro_diario = ?",
                (libro_id,)
            )
            row = cur.fetchone()
            if row:
                _id, _id_mes, _ano, _contador, _empresa, _plan = row
                libro_diario.id_libro_diario = _id
                libro_diario.id_mes = int(_id_mes or 0)
                libro_diario.ano = int(_ano or 0)
                libro_diario.contador = _contador or ""
                libro_diario.nombre_empresa = _empresa or ""
                libro_diario.id_plan_cuenta = int(_plan or 0)
            else:
                # Si no existe, al menos establecer el id para evitar errores en diálogos
                libro_diario.id_libro_diario = libro_id
        except Exception as ex:
            print(f"Error cargando libro por id={libro_id}: {ex}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

    # --- Export dialog setup ---
    # Fields for filename and target directory
    default_filename = f"Libro_Diario_{libro_diario.id_libro_diario or ''}.xlsx".replace("None", "")
    name_field = ft.TextField(hint_text="Nombre de archivo", value=default_filename, width=600)
    path_field = ft.TextField(hint_text="Ruta destino", width=600)

    def _load_tk():
        try:
            import tkinter as _tk
            from tkinter import filedialog as _filedialog
            return _tk, _filedialog
        except Exception:
            return None, None

    def pick_directory_with_tk() -> str | None:
        tk, filedialog = _load_tk()
        if filedialog is None or tk is None:
            return None
        root = None
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            try:
                root.update()
            except Exception:
                pass
            path = filedialog.askdirectory(title="Seleccionar carpeta destino")
            return path or None
        except Exception:
            return None
        finally:
            try:
                if root is not None:
                    root.destroy()
            except Exception:
                pass

    def do_export(e=None):
        try:
            fname = (name_field.value or "").strip()
            dest = (path_field.value or "").strip()
            if not fname:
                page.snack_bar = ft.SnackBar(content=ft.Text("Ingresa un nombre de archivo."), bgcolor=ft.Colors.RED_600, duration=3000)
                page.snack_bar.open = True
                page.update()
                return
            if not dest:
                page.snack_bar = ft.SnackBar(content=ft.Text("Selecciona una ruta de destino."), bgcolor=ft.Colors.RED_600, duration=3000)
                page.snack_bar.open = True
                page.update()
                return
            if not fname.lower().endswith(".xlsx"):
                fname = f"{fname}.xlsx"
            output_path = Path(dest) / fname
            exportar_libro_diario(libro_diario.id_libro_diario, output_path)
            export_dialog.open = False
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Exportado exitosamente: {output_path.name}"),
                bgcolor=ft.Colors.GREEN_600,
                duration=4000,
            )
            page.snack_bar.open = True
            page.update()
        except Exception as exc:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error al exportar: {exc}"), bgcolor=ft.Colors.RED_600, duration=5000)
            page.snack_bar.open = True
            page.update()

    def open_browse(e):
        dest = pick_directory_with_tk()
        if dest:
            path_field.value = dest
            try:
                if export_dialog not in page.overlay:
                    page.overlay.append(export_dialog)
                export_dialog.open = True
                page.update()
            except Exception:
                pass
        else:
            page.snack_bar = ft.SnackBar(content=ft.Text("Tkinter no está disponible"), bgcolor=ft.Colors.RED_600, duration=4000)
            page.snack_bar.open = True
            page.update()

    def close_export_dialog(_e=None):
        try:
            export_dialog.open = False
            page.update()
        except Exception:
            pass

    export_dialog = ft.AlertDialog(
        title=ft.Text("Exportar a Excel"),
        content=ft.Container(
            width=720,
            content=ft.Column([
                name_field,
                ft.Row([
                    path_field,
                    ft.FilledButton("Examinar…", icon=ft.Icons.FOLDER_OPEN, on_click=open_browse),
                ], alignment=ft.MainAxisAlignment.START, spacing=6),
            ], tight=True, spacing=6),
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=close_export_dialog),
            ft.FilledButton("Exportar", icon=ft.Icons.FILE_DOWNLOAD, on_click=do_export),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=close_export_dialog,
    )

    # Acciones del menú lateral
    def navigate_to_menu(_e=None):
        try:
            from src.ui.pages.menu_page.menu_page import menu_page
            page.clean()
            page.add(menu_page(page))
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"No se pudo abrir el menú: {ex}"), bgcolor=ft.Colors.RED_600, duration=4000)
            page.snack_bar.open = True
            page.update()

    def navigate_to_plan_cuentas(_e=None):
        try:
            from src.ui.pages.account_list_page.account_list_page import account_list_page

            def back_to_journal():
                page.clean()
                page.add(book_journal_page(
                    page,
                    empresa=libro_diario.nombre_empresa,
                    contador=libro_diario.contador,
                    anio=str(libro_diario.ano),
                    mes=str(getattr(libro_diario, "id_mes", "") or getattr(libro_diario, "mes", "")),
                    plan_id=str(getattr(libro_diario, "id_plan_cuenta", "0")),
                    libro_id=libro_diario.id_libro_diario,
                ))
                page.update()

            plan_val = getattr(libro_diario, "id_plan_cuenta", None)
            try:
                plan_val = int(plan_val) if plan_val is not None else None
            except Exception:
                plan_val = None

            page.clean()
            page.add(account_list_page(page, back_action=back_to_journal, plan_id=plan_val))
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Plan de cuentas no disponible: {ex}"), bgcolor=ft.Colors.RED_600, duration=4000)
            page.snack_bar.open = True
            page.update()

    def show_filter_placeholder(_e=None):
        page.snack_bar = ft.SnackBar(content=ft.Text("Filtro en construcción"), duration=2500)
        page.snack_bar.open = True
        page.update()

    # Use the sliding drawer style from menulateral_demo.py but keep our options
    destinations = [
        {"label": "Ver plan de cuentas", "icon": ft.Icons.ACCOUNT_BALANCE_OUTLINED, "selected_icon": ft.Icons.ACCOUNT_BALANCE, "action": navigate_to_plan_cuentas , "selectable": True},
        {"label": "Exportar a Excel", "icon": ft.Icons.FILE_DOWNLOAD, "selected_icon": ft.Icons.FILE_DOWNLOAD, "action": lambda e: open_export_dialog(), "selectable": False},
        {"label": "Salir", "icon": ft.Icons.EXIT_TO_APP_OUTLINED, "selected_icon": ft.Icons.EXIT_TO_APP, "action": navigate_to_menu, "selectable": True},
    ]

    selected_index = [0]

    def make_destination(idx: int, item: dict):
        is_selected = item.get("selectable", True) and (selected_index[0] == idx)
        return ft.Container(
            content=ft.Row([
                ft.Icon(
                    item["selected_icon"] if is_selected else item["icon"],
                    size=20,
                    color=ft.Colors.BLUE_700 if is_selected else ft.Colors.GREY_700
                ),
                ft.Text(
                    item["label"],
                    size=14,
                    color=ft.Colors.BLUE_700 if is_selected else ft.Colors.GREY_800,
                    weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                ),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=12, horizontal=16),
            bgcolor=ft.Colors.BLUE_50 if is_selected else None,
            border_radius=8,
            margin=ft.margin.symmetric(horizontal=8, vertical=2),
            on_click=lambda e, ix=idx: on_menu_click(ix),
        )
        
    def open_export_dialog():
        try:
            if not (name_field.value or "").strip():
                name_field.value = default_filename
            if export_dialog not in page.overlay:
                page.overlay.append(export_dialog)
            export_dialog.open = True
            page.update()
        except Exception:
            pass

    header = ft.Container(
        content=ft.Column([
            ft.Text("LibroFácil", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
            ft.Text("Sistema Contable", size=12, color=ft.Colors.GREY_600),
        ]),
        padding=20,
        width=280,
        bgcolor=ft.Colors.BLUE_50,
    )

    def on_menu_click(idx: int):
        try:
            destinations[idx]["action"](None)
        except Exception:
            pass
        if destinations[idx].get("selectable", True):
            selected_index[0] = idx
        # rebuild drawer content selection state
        drawer_content.controls.clear()
        drawer_content.controls.append(header)
        for i, d in enumerate(destinations):
            drawer_content.controls.append(make_destination(i, d))
        # close drawer after selecting (optional)
        toggle_drawer()

    # Drawer content
    drawer_content = ft.Column()
    drawer_content.controls.append(header)
    for i, d in enumerate(destinations):
        drawer_content.controls.append(make_destination(i, d))

    drawer_width = 280

    drawer = ft.Container(
        content=ft.Container(
            content=drawer_content,
            width=drawer_width,
            padding=0,
        ),
        width=drawer_width,
        bgcolor=ft.Colors.WHITE,
        border=ft.border.only(right=ft.border.BorderSide(1, ft.Colors.GREY_300)),
        # start hidden to the left
        left=-drawer_width,
        top=0,
        bottom=0,
        animate_position=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=20, color=ft.Colors.BLACK26, offset=ft.Offset(2, 0)),
    )

    # Overlay should only capture clicks when drawer is open.
    # Use visible flag to prevent intercepting clicks when closed.
    overlay = ft.Container(
        bgcolor=ft.Colors.BLACK54,
        opacity=0,
        visible=False,
        expand=True,
        animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        on_click=lambda e: toggle_drawer(),
    )

    # Tabs state and builders
    current_tab = {"name": "diario"}
    def build_main_area():
        if current_tab["name"] == "diario":
            return contenido(page, libro=libro_diario)
        else:
            return contenido_mayor(page, libro=libro_diario)

    # Main content and top bar
    main_area = build_main_area()

    def set_tab(tab_name: str):
        current_tab["name"] = tab_name
        page_main.controls[1] = build_main_area()
        page.update()

    # Refresh callback to rebuild the journal page content
    def refresh_diario():
        page_main.controls[1] = build_main_area()
        page.update()

    diario_btn = ft.TextButton(
        "Libro Diario",
        style=ft.ButtonStyle(color=ft.Colors.WHITE),
        on_click=lambda e: set_tab("diario"),
    )
    mayor_btn = ft.TextButton(
        "Libro Mayor",
        style=ft.ButtonStyle(color=ft.Colors.WHITE),
        on_click=lambda e: set_tab("mayor"),
    )

    top_bar = ft.Container(
        bgcolor=ft.Colors.TRANSPARENT,
        padding=ft.padding.symmetric(horizontal=16),
        content=ft.Row([
            ft.IconButton(icon=ft.Icons.MENU, on_click=lambda e: toggle_drawer(), icon_color=ft.Colors.WHITE),
            diario_btn,
            mayor_btn,
            ft.Container(expand=True),
        ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        height=56,
    )

    page_main = ft.Column([top_bar, main_area], expand=True)

    drawer_open = [False]

    def toggle_drawer():
        if drawer_open[0]:
            drawer.left = -drawer_width
            overlay.opacity = 0
            overlay.visible = False
        else:
            drawer.left = 0
            overlay.visible = True
            overlay.opacity = 1
        drawer_open[0] = not drawer_open[0]
        page.update()
    

    # Compose Stack: background, main, overlay, drawer
    return ft.Stack([
        create_modern_background(page),
        page_main,
        overlay,
        drawer,
    ], expand=True)