import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft
import sqlite3
from src.utils.paths import get_db_path

def resource_path(relative_path: str) -> str:
    """Resolve path for PyInstaller bundles and normal runs."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.getcwd())
    return os.path.join(base_path, relative_path)

def create_account_list_dialog(page: ft.Page, refresh_callback: callable = None):
    # DEBUG: Verificar que estamos en el lugar correcto
    print("🔴 create_account_list_dialog CALLED")
    
    # DEBUG: Verificar la ruta de la base de datos (writable)
    db_path = get_db_path()
    print(f"🔴 DB Path: {db_path}")
    print(f"🔴 DB exists: {os.path.exists(db_path)}")

    cuenta_field = ft.TextField(
        label="Nombre del plan de cuenta",
        hint_text="Escribe el nombre",
        border_color=ft.Colors.BLUE,
        color=ft.Colors.BLACK
    )
    
    # Función build_menu IDÉNTICA a la que funciona
    def build_menu(label: str, color_disabled=ft.Colors.GREY):
        menu = ft.PopupMenuButton(
            content=ft.Container(
                content=ft.Row([
                    ft.Text(label, color=color_disabled),
                    ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=color_disabled)
                ]),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                bgcolor=ft.Colors.WHITE,
            ),
            items=[],
            disabled=True
        )
        print(f"🔴 Menu creado: {label}, disabled: {menu.disabled}")
        return menu
    
    def agregar_cuenta(e):
        print("🔴 agregar_cuenta llamado")
        try:
            nombre_cuenta = (cuenta_field.value or "").strip()
            if not nombre_cuenta:
                page.snack_bar = ft.SnackBar(content=ft.Text("Ingrese el nombre del plan de  cuenta"), bgcolor=ft.Colors.RED)
                page.snack_bar.open = True
                page.update()
                return

            # Sugerir/obtener codigo_cuenta
            conn = sqlite3.connect(db_path, timeout=5)
            conn.execute("PRAGMA busy_timeout=3000")
            try:
                cur = conn.cursor()

                # Insertar cuenta
                cur.execute(
                    """
                    INSERT INTO plan_cuentas (nombre_plan_cuentas)
                    VALUES (?)
                    """,(nombre_cuenta,)
                )
                conn.commit()
            finally:
                try:
                    conn.close()
                except Exception:
                    pass

            # Feedback y cierre
            dlg.open = False
            page.update()
            if refresh_callback:
                try:
                    refresh_callback()
                except Exception as ex:
                    print(f"🔴 Error al refrescar lista: {ex}")
        except Exception as ex:
            print(f"🔴 ERROR en agregar_cuenta: {ex}")
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error al agregar cuenta: {ex}"), bgcolor=ft.Colors.RED)
            page.snack_bar.open = True
            page.update()

    def cancelar_dialog(e):
        print("🔴 cancelar_dialog llamado")
        dlg.open = False
        page.update()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Crear Plan de cuentas", color=ft.Colors.BLUE, weight=ft.FontWeight.BOLD),
        
        content=ft.Container(
            content=ft.Column([
                ft.Text("Nombre del plan de cuentas:", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                cuenta_field
            ], spacing=15),
            width=420,
            height=140,
            padding=20,
            bgcolor=ft.Colors.WHITE,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar_dialog, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ft.ElevatedButton("Agregar", on_click=agregar_cuenta, style=ft.ButtonStyle(color=ft.Colors.WHITE), bgcolor=ft.Colors.BLUE)
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=ft.Colors.WHITE
    )
    
    print("🔴 Abriendo diálogo...")
    page.overlay.append(dlg)
    dlg.open = True
    page.update()
    print("🔴 Diálogo abierto")