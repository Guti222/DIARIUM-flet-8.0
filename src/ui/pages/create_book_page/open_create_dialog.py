import flet as ft

from data.models.mes import Mes
from data.obtenerMeses import obtenerMeses
from data.obternet_plan_cuentas import obtenerTodosPlanesCuentas
from data.models.plan_cuenta import PlanCuenta
from src.utils.paths import get_db_path
from src.ui.pages.book_journal_page.book_journal_page import create_journal_book, agregar_libro, book_journal_page


def open_create_dialog(page: ft.Page):
    """Muestra un AlertDialog para crear un nuevo libro contable.

    El dialog construye sus campos localmente y gestiona abrir/cerrar
    usando las APIs de `page`.
    """

    # Campos del formulario
    empresa_field = ft.TextField(
        label="Nombre de la empresa",
        hint_text="Ej: Mi Empresa S.A.",
        width=400,
        focused_bgcolor=ft.Colors.BLUE,
        color=ft.Colors.BLACK,
    )

    contador_field = ft.TextField(
        label="Nombre del contador",
        hint_text="Ej: Juan Pérez",
        width=400,
        focused_bgcolor=ft.Colors.BLUE,
        color=ft.Colors.BLACK,
    )

    anio_field = ft.TextField(
        label="Año fiscal",
        hint_text="2024",
        width=150,
        input_filter=ft.NumbersOnlyInputFilter(),
        focused_bgcolor=ft.Colors.BLUE,
        color=ft.Colors.BLACK,
    )
    
    meses: list[Mes] = obtenerMeses()
    
    mes_field = ft.Dropdown(
            width=150,
            hint_text="Mes",
            options=[
                ft.dropdown.Option(mes.nombre_mes) for mes in meses
            ],
            fill_color=ft.Colors.WHITE,
            color=ft.Colors.BLACK,
            bgcolor=ft.Colors.WHITE
        )

    # Plan de cuentas: cargar desde BD, default "General" (id=0)
    planes: list[PlanCuenta] = obtenerTodosPlanesCuentas(get_db_path())
    plan_options = [ft.dropdown.Option(str(p.id_plan_cuenta), p.nombre_plan_cuenta) for p in planes]
    # Asegurar que siempre haya opción General (id=0)
    if not any(str(p.id_plan_cuenta) == "0" for p in planes):
        plan_options.insert(0, ft.dropdown.Option("0", "General"))

    plan_field = ft.Dropdown(
        width=300,
        label="Plan de Cuentas",
        options=[ft.dropdown.Option("", "Selecciona plan...")] + plan_options,
        value="0",
        fill_color=ft.Colors.WHITE,
        color=ft.Colors.BLACK,
        bgcolor=ft.Colors.WHITE
    )

    def crear_libro(e):
        empresa = empresa_field.value
        contador = contador_field.value
        anio = anio_field.value

        if empresa and contador and anio:
            print(f"Creando libro para: {empresa}")
            print(f"Contador: {contador}")
            print(f"Año: {anio}")
            # Cerrar el diálogo
            dlg.open = False
            page.update()

            # Crear registro de libro y navegar por ID
            try:
                plan_int = 0
                try:
                    plan_int = int(plan_field.value or 0)
                except Exception:
                    plan_int = 0
                # Mapear mes a id
                mes_val = mes_field.value or ''
                meses_map = {
                    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
                    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
                    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
                }
                try:
                    id_mes = int(mes_val)
                except Exception:
                    id_mes = meses_map.get(str(mes_val).strip().lower(), 0)

                libro = create_journal_book(empresa, contador, anio, id_mes, plan_id=plan_int, origen="creado")
                new_id = agregar_libro(libro, get_db_path())
                if isinstance(new_id, int):
                    # Navegación sin router: limpiar y renderizar la vista del libro
                    try:
                        page.clean()
                        page.add(book_journal_page(page, libro_id=new_id))
                        page.update()
                    except Exception as nav_ex:
                        print(f"Error navegando al libro creado: {nav_ex}")
                        page.snack_bar = ft.SnackBar(content=ft.Text("❌ No se pudo abrir el libro creado"))
                        page.snack_bar.open = True
                        page.update()
                else:
                    page.snack_bar = ft.SnackBar(content=ft.Text("❌ No se pudo crear el libro"))
                    page.snack_bar.open = True
                    page.update()
            except Exception as ex:
                print(f"Error creando/navegando a book-journal: {ex}")
                page.snack_bar = ft.SnackBar(content=ft.Text("❌ Error creando el libro"))
                page.snack_bar.open = True
                page.update()
        else:
            page.snack_bar = ft.SnackBar(content=ft.Text("❌ Completa todos los campos"))
            page.snack_bar.open = True
            page.update()

    def cancelar(e):
        dlg.open = False
        page.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Crear Nuevo Libro Contable", color=ft.Colors.BLUE),
        bgcolor=ft.Colors.WHITE,
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text("Información del Libro", size=16, weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE),
                    ft.Container(height=10),
                    empresa_field,
                    ft.Container(height=10),
                    contador_field,
                    ft.Container(height=10),
                    ft.Row(
                        [
                            anio_field,
                            ft.Container(width=20),
                            mes_field,
                        ]
                    ),
                    ft.Container(height=10),
                    plan_field,
                ],
                tight=True,
            ),
            width=450,
            bgcolor=ft.Colors.WHITE,
            padding=ft.padding.all(20),
            border_radius=10,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ft.ElevatedButton("Crear Libro", on_click=crear_libro, style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),bgcolor=ft.Colors.BLUE),
        ],
    )

    # Abrir el dialog usando la API recomendada
    page.overlay.append(dlg)
    dlg.open = True
    page.update()
    
    