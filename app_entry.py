import flet as ft
import sqlite3
import os
import sys
import tempfile
from data.database.estructuraBD import (
    crear_estructura_db,
    poblar_tablas_catalogo,
    poblar_cuentas_contables,
)
from src.utils.paths import get_db_path


def _configure_tk_env():
    try:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            base = sys._MEIPASS  # type: ignore[attr-defined]
            tcl_dir = os.path.join(base, "tcl")
            tk_dir = os.path.join(base, "tk")
            if os.path.isdir(tcl_dir) and os.path.isdir(tk_dir):
                os.environ.setdefault("TCL_LIBRARY", tcl_dir)
                os.environ.setdefault("TK_LIBRARY", tk_dir)
    except Exception:
        pass


_configure_tk_env()


def main(page: ft.Page):
    from src.ui.pages.menu_page.menu_page import menu_page
    # En lugar de usar resource_path
    page.assets_dir = "assets"
    # Configuración básica
    page.title = "Libro facil"
    page.window_width = 1200
    page.window_height = 800
    page.window_resizable = True
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    # Inicializar / reparar BD si está vacía o incompleta
    db_path = get_db_path()

    # En modo instalador, la BD ya debe existir en AppData.
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        page.snack_bar = ft.SnackBar(
            content=ft.Text("No se encontró la base de datos en AppData. Reinstala o ejecuta el instalador."),
            bgcolor=ft.Colors.RED_600,
            duration=6000,
        )
        page.snack_bar.open = True
        page.update()
    else:
        # Si existe, opcionalmente validar estructura mínima
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("SELECT 1 FROM plan_cuentas LIMIT 1")
            conn.close()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"BD inválida en AppData: {ex}"),
                bgcolor=ft.Colors.RED_600,
                duration=6000,
            )
            page.snack_bar.open = True
            page.update()

    # Renderizar menú principal (menu_page crea y registra su propio FilePicker)
    content = menu_page(page)
    if content is not None:
        page.add(content)
    else:
        page.add(ft.Text("Error cargando menú"))
    page.update()
