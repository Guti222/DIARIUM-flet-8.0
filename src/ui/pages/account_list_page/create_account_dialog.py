import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft
import sqlite3
import re
from src.utils.paths import get_db_path
from data.models.cuenta import Rubro, TipoCuenta, Generico
from data.obtenerCuentas import obtenerTodasTipoCuentas, obtenerTodosRubroPorTipoCuenta, obtenerTodosGenericoPorRubro

def resource_path(relative_path: str) -> str:
    """Resolve path for PyInstaller bundles and normal runs."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.getcwd())
    return os.path.join(base_path, relative_path)

def create_account_dialog(page: ft.Page, refresh_callback: callable = None):
    # DEBUG: Verificar que estamos en el lugar correcto
    print("🔴 create_account_dialog CALLED")
    
    # Estado
    selected_account_type = {"id": None, "nombre": None}
    selected_rubro = {"id": None, "nombre": None}
    selected_generico = {"id": None, "nombre": None}
    
    # DEBUG: Verificar la ruta de la base de datos (writable)
    db_path = get_db_path()
    print(f"🔴 DB Path: {db_path}")
    print(f"🔴 DB exists: {os.path.exists(db_path)}")
    
    # Cargar tipos de cuenta desde BD
    try:
        tipocuentas = obtenerTodasTipoCuentas(db_path)
        print(f"🔴 Tipos de cuenta cargados: {len(tipocuentas)}")
        for tc in tipocuentas:
            print(f"  - {tc.id_tipo_cuenta}: {tc.nombre_tipo_cuenta}")
    except Exception as ex:
        print(f"🔴 ERROR cargando tipos de cuenta: {ex}")
        tipocuentas = []
        page.snack_bar = ft.SnackBar(content=ft.Text(f"No se pudo cargar tipos de cuenta: {ex}"), bgcolor=ft.Colors.RED)
        page.snack_bar.open = True
        page.update()

    cuenta_field = ft.TextField(
        label="Cuenta Contable",
        hint_text="Nombre de la cuenta",
        disabled=True,
        border_color=ft.Colors.BLUE,
        color=ft.Colors.BLACK
    )
    
    descripcion_field = ft.TextField(
        label="Descripción",
        hint_text="Descripción de la cuenta",
        disabled=True,
        border_color=ft.Colors.BLUE,
        color=ft.Colors.BLACK,
        multiline=True,
        min_lines=2,
        max_lines=4
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

    tipo_menu = build_menu("Seleccione tipo de cuenta")
    rubro_menu = build_menu("Seleccione rubro")
    generico_menu = build_menu("Seleccione genérico")

    # DEBUG: Verificar items del menú
    print(f"🔴 Items en tipo_menu: {len(tipo_menu.items) if tipo_menu.items else 0}")

    # Configurar tipos
    tipo_menu.items = [
        ft.PopupMenuItem(
            content=ft.Row([
                ft.Text(t.numero_cuenta, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                ft.Text(t.nombre_tipo_cuenta, color=ft.Colors.BLACK),
            ], spacing=8),
            data={"id": t.id_tipo_cuenta, "nombre": t.nombre_tipo_cuenta, "numero": t.numero_cuenta},
            on_click=lambda e, t=t: select_account_type(e.control.data)
        ) for t in tipocuentas
    ]
    
    tipo_menu.disabled = False
    tipo_menu.content.border = ft.border.all(1, ft.Colors.BLUE)
    for c in tipo_menu.content.content.controls:
        if isinstance(c, (ft.Text, ft.Icon)):
            c.color = ft.Colors.BLACK

    print(f"🔴 Tipo_menu configurado - disabled: {tipo_menu.disabled}, items: {len(tipo_menu.items)}")

    def reset_rubro():
        print("🔴 reset_rubro llamado")
        rubro_menu.items = []
        rubro_menu.disabled = True
        rubro_menu.content.border = ft.border.all(1, ft.Colors.GREY_400)
        rubro_menu.content.content.controls[0].value = "Seleccione rubro"
        rubro_menu.content.content.controls[0].color = ft.Colors.GREY
        selected_rubro.update({"id": None, "nombre": None})
        reset_generico()

    def reset_generico():
        print("🔴 reset_generico llamado")
        generico_menu.items = []
        generico_menu.disabled = True
        generico_menu.content.border = ft.border.all(1, ft.Colors.GREY_400)
        generico_menu.content.content.controls[0].value = "Seleccione genérico"
        generico_menu.content.content.controls[0].color = ft.Colors.GREY
        selected_generico.update({"id": None, "nombre": None})
        reset_cuenta()

    def reset_cuenta():
        print("🔴 reset_cuenta llamado")
        cuenta_field.value = ""
        cuenta_field.disabled = True
        descripcion_field.value = ""
        descripcion_field.disabled = True

    def select_account_type(data):
        print(f"🔴 select_account_type llamado: {data}")
        selected_account_type.update(data)
        tipo_menu.content.content.controls[0].value = f"{data['numero']} - {data['nombre']}"
        tipo_menu.content.border = ft.border.all(1, ft.Colors.BLUE)
        
        reset_rubro()
        try:
            print(f"🔴 Cargando rubros para tipo_cuenta_id: {data['id']}")
            rubros = obtenerTodosRubroPorTipoCuenta(db_path, int(data["id"]))
            print(f"🔴 Rubros cargados: {len(rubros)}")
            
            rubro_menu.items = [
                ft.PopupMenuItem(
                    content=ft.Row([
                        ft.Text(r.numero_cuenta, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                        ft.Text(r.nombre_rubro, color=ft.Colors.BLACK),
                    ], spacing=8),
                    data={"id": r.id_rubro, "nombre": r.nombre_rubro, "numero": r.numero_cuenta},
                    on_click=lambda e, r=r: select_rubro(e.control.data)
                ) for r in rubros
            ]
            rubro_menu.disabled = False
            rubro_menu.content.border = ft.border.all(1, ft.Colors.BLUE)
            rubro_menu.content.content.controls[0].color = ft.Colors.BLACK
            page.update()
            print(f"🔴 Rubro_menu actualizado - disabled: {rubro_menu.disabled}")
        except Exception as ex:
            print(f"🔴 ERROR en select_account_type: {ex}")

    def select_rubro(data):
        print(f"🔴 select_rubro llamado: {data}")
        selected_rubro.update(data)
        rubro_menu.content.content.controls[0].value = f"{data['numero']} - {data['nombre']}"
        rubro_menu.content.border = ft.border.all(1, ft.Colors.BLUE)
        
        reset_generico()
        try:
            print(f"🔴 Cargando genéricos para rubro_id: {data['id']}")
            genericos = obtenerTodosGenericoPorRubro(db_path, int(data["id"]))
            print(f"🔴 Genéricos cargados: {len(genericos)}")
            
            generico_menu.items = [
                ft.PopupMenuItem(
                    content=ft.Row([
                        ft.Text(g.numero_cuenta, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                        ft.Text(g.nombre_generico, color=ft.Colors.BLACK),
                    ], spacing=8),
                    data={"id": g.id_generico, "nombre": g.nombre_generico, "numero": g.numero_cuenta},
                    on_click=lambda e, g=g: select_generico(e.control.data)
                ) for g in genericos
            ]
            generico_menu.disabled = False
            generico_menu.content.border = ft.border.all(1, ft.Colors.BLUE)
            generico_menu.content.content.controls[0].color = ft.Colors.BLACK
            page.update()
            print(f"🔴 Generico_menu actualizado - disabled: {generico_menu.disabled}")
        except Exception as ex:
            print(f"🔴 ERROR en select_rubro: {ex}")

    codigo_sugerido_text = ft.Text("Código sugerido: -", color=ft.Colors.GREY_700)
    codigo_sugerido_val = {"value": None}

    def select_generico(data):
        print(f"🔴 select_generico llamado: {data}")
        selected_generico.update(data)
        generico_menu.content.content.controls[0].value = f"{data['numero']} - {data['nombre']}"
        generico_menu.content.border = ft.border.all(1, ft.Colors.BLUE)
        
        cuenta_field.disabled = False
        descripcion_field.disabled = False
        # Calcular código sugerido: tipo.rubro.genérico.###
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute(
                "SELECT MAX(codigo_cuenta) FROM cuenta_contable WHERE id_generico = ?",
                (int(data["id"]),)
            )
            ultimo = cur.fetchone()[0]
        finally:
            try:
                conn.close()
            except Exception:
                pass
        tipo_id = int(selected_account_type["id"]) if selected_account_type["id"] else 0
        rubro_id = int(selected_rubro["id"]) if selected_rubro["id"] else 0
        gen_id = int(selected_generico["id"]) if selected_generico["id"] else 0
        base = f"{tipo_id}.{rubro_id}.{gen_id}"
        sugerido = None
        if ultimo:
            parts = str(ultimo).split('.')
            if len(parts) == 4:
                try:
                    nxt = int(parts[3]) + 1
                except Exception:
                    nxt = 1
                sugerido = f"{parts[0]}.{parts[1]}.{parts[2]}.{nxt:03d}"
        if not sugerido:
            sugerido = f"{base}.001"
        codigo_sugerido_val["value"] = sugerido
        codigo_sugerido_text.value = f"Código sugerido: {sugerido}"
        page.update()
        print("🔴 Campos de cuenta habilitados")

    def agregar_cuenta(e):
        print("🔴 agregar_cuenta llamado")
        try:
            # Validaciones básicas
            if not selected_account_type["id"] or not selected_rubro["id"] or not selected_generico["id"]:
                page.snack_bar = ft.SnackBar(content=ft.Text("Seleccione tipo, rubro y genérico"), bgcolor=ft.Colors.RED)
                page.snack_bar.open = True
                page.update()
                return
            nombre_cuenta = (cuenta_field.value or "").strip()
            if not nombre_cuenta:
                page.snack_bar = ft.SnackBar(content=ft.Text("Ingrese el nombre de la cuenta"), bgcolor=ft.Colors.RED)
                page.snack_bar.open = True
                page.update()
                return
            descripcion = (descripcion_field.value or "").strip()

            # Usar código sugerido calculado
            codigo = codigo_sugerido_val.get("value")
            conn = sqlite3.connect(db_path, timeout=5)
            conn.execute("PRAGMA busy_timeout=3000")
            try:
                cur = conn.cursor()
                if not codigo:
                    # Fallback mínimo si no hay sugerido
                    tipo_id = int(selected_account_type["id"]) if selected_account_type["id"] else 0
                    rubro_id = int(selected_rubro["id"]) if selected_rubro["id"] else 0
                    gen_id = int(selected_generico["id"]) if selected_generico["id"] else 0
                    codigo = f"{tipo_id}.{rubro_id}.{gen_id}.001"

                # Insertar cuenta
                cur.execute(
                    """
                    INSERT INTO cuenta_contable (id_generico, descripcion, nombre_cuenta, codigo_cuenta)
                    VALUES (?, ?, ?, ?)
                    """,
                    (int(selected_generico["id"]), descripcion, nombre_cuenta, codigo)
                )
                conn.commit()
            finally:
                try:
                    conn.close()
                except Exception:
                    pass

            # Feedback y cierre
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Cuenta agregada: {codigo}"), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
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
        title=ft.Text("Agregar Nueva Cuenta", color=ft.Colors.BLUE, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column([
                ft.Text("Tipo de Cuenta:", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                tipo_menu,
                ft.Text("Rubro:", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                rubro_menu,
                ft.Text("Genérico:", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                generico_menu,
                codigo_sugerido_text,
                ft.Text("Cuenta Contable:", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                cuenta_field,
                ft.Text("Descripción:", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                descripcion_field,
            ], 
            spacing=15,
            scroll= ft.ScrollMode.AUTO
            ),
            width=420,
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