import flet as ft
import sys
import os

def resource_path(relative_path: str) -> str:
    """Resolve path for PyInstaller bundles and normal runs."""
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(os.getcwd())
    return os.path.join(base_path, relative_path)
from src.ui.pages.menu_page.menu_page import menu_page
from data.database.estructuraBD import (
    crear_estructura_db,
    poblar_tablas_catalogo,
    poblar_cuentas_contables,
)
from src.utils.paths import get_db_path
import sqlite3
import urllib.parse

def main(page: ft.Page):
    # Ensure assets load both in dev and bundled executable
    assets_dir = resource_path('assets')
    try:
        page.assets_dir = assets_dir
    except Exception:
        pass
    # Configuración básica
    page.title = "Libro facil"
    page.window_width = 1200
    page.window_height = 800
    page.window_resizable = True
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Inicializar / reparar BD si está vacía o incompleta
    db_path = get_db_path()
    def ensure_db_initialized(path: str):
        try:
            # 1) Crear siempre la estructura (idempotente por IF NOT EXISTS)
            crear_estructura_db(path)

            # 2) Verificar conteos para poblar catálogos y plan de cuentas
            conn = sqlite3.connect(path)
            cur = conn.cursor()
            tipo_count = mes_count = rubro_count = generico_count = cuenta_count = 0
            try:
                cur.execute("SELECT COUNT(*) FROM tipo_cuenta"); tipo_count = cur.fetchone()[0]
            except Exception:
                tipo_count = 0
            try:
                cur.execute("SELECT COUNT(*) FROM mes"); mes_count = cur.fetchone()[0]
            except Exception:
                mes_count = 0
            try:
                cur.execute("SELECT COUNT(*) FROM rubro"); rubro_count = cur.fetchone()[0]
            except Exception:
                rubro_count = 0
            try:
                cur.execute("SELECT COUNT(*) FROM generico"); generico_count = cur.fetchone()[0]
            except Exception:
                generico_count = 0
            try:
                cur.execute("SELECT COUNT(*) FROM cuenta_contable"); cuenta_count = cur.fetchone()[0]
            except Exception:
                cuenta_count = 0
            conn.close()

            # 3) Poblar según sea necesario
            if tipo_count == 0 or mes_count == 0 or rubro_count == 0 or generico_count == 0:
                poblar_tablas_catalogo(path)
            if cuenta_count == 0:
                poblar_cuentas_contables(path)

            print(f"[DB] Verificación completa. Path: {path}")
        except Exception as ex:
            print(f"[DB] Error inicializando/poblando: {ex}")

    ensure_db_initialized(db_path)
    
    
    
    # Renderizar menú principal (menu_page crea y registra su propio FilePicker)
    content = menu_page(page)
    if content is not None:
        page.add(content)
    else:
        page.add(ft.Text("Error cargando menú"))
    page.update()

if __name__ == "__main__":
    # Flet 0.80+: usar run() en lugar de app()
    ft.run(main)