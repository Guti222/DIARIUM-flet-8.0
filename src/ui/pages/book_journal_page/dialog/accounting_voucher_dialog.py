import flet as ft
from typing import List, Optional
from datetime import datetime
import sqlite3
import asyncio
import asyncio

from src.utils.paths import get_db_path
from data.obtenerCuentas import (
    obtenerTodasCuentasContables,
    obtenerCuentasContablesPorPlanCuenta,
    obtenerCuentasContablesGenerales,
)
from data.models.cuenta import CuentaContable
from data.models.lineaAsiento import LineaAsiento


class VoucherRow:
    """Objeto de fila del comprobante: agrupa controles y estado."""
    def __init__(self, idx: int, tf_codigo: ft.TextField, tf_debe: ft.TextField, tf_haber: ft.TextField,
                 lbl_nombre: ft.Text, lbl_tipo: ft.Text, container: ft.Container):
        self.idx = idx
        self.code_field = tf_codigo
        self.debe_field = tf_debe
        self.haber_field = tf_haber
        self.nombre_label = lbl_nombre
        self.tipo_label = lbl_tipo
        self.container = container
        self.cuenta: Optional[CuentaContable] = None

    def set_account(self, cuenta: CuentaContable, tipo_color, apply_updates: bool = True):
        self.cuenta = cuenta
        self.code_field.value = cuenta.codigo_cuenta or ''
        self.nombre_label.value = cuenta.nombre_cuenta or ''
        tipo = getattr(cuenta, 'nombre_tipo_cuenta', '') or ''
        self.tipo_label.value = f"({tipo})" if tipo else ''
        self.tipo_label.color = tipo_color
        if apply_updates:
            self.code_field.update()
            self.nombre_label.update(); self.tipo_label.update()

    def get_code(self) -> str:
        return (self.code_field.value or '').strip()

    def get_debe(self) -> float:
        try:
            v = self.debe_field.value or ''
            return float(v.replace(',', '.')) if v else 0.0
        except Exception:
            return 0.0

    def get_haber(self) -> float:
        try:
            v = self.haber_field.value or ''
            return float(v.replace(',', '.')) if v else 0.0
        except Exception:
            return 0.0


class AccountingVoucherDialog:
    def __init__(self, page: ft.Page, id_libro_diario: int, asiento_id: Optional[int] = None, on_saved: Optional[callable] = None):
        self.page = page
        self.id_libro_diario = id_libro_diario
        self.asiento_id = asiento_id
        self.on_saved = on_saved

        # Data
        self.CUENTAS: List[CuentaContable] = []
        try:
            dbp = get_db_path()
            # Intentar usar el plan de cuentas del libro
            conn = sqlite3.connect(dbp)
            cur = conn.cursor()
            cur.execute("SELECT COALESCE(id_plan_cuenta, 0) FROM libro_diario WHERE id_libro_diario = ?", (self.id_libro_diario,))
            row = cur.fetchone()
            try:
                plan_id = int(row[0] or 0) if row else 0
            except Exception:
                plan_id = 0
            try:
                conn.close()
            except Exception:
                pass
            if plan_id is None:
                # Sin plan: todas las cuentas
                self.CUENTAS = obtenerTodasCuentasContables(dbp)
            elif plan_id == 0:
                # Plan General: intentar id=0; si vacío, incluir NULL como general
                cuentas_plan = obtenerCuentasContablesPorPlanCuenta(dbp, 0) or []
                self.CUENTAS = cuentas_plan if cuentas_plan else obtenerCuentasContablesGenerales(dbp)
            else:
                # Plan específico: NO hacer fallback a todas; si vacío, dejar sin sugerencias
                cuentas_plan = obtenerCuentasContablesPorPlanCuenta(dbp, plan_id) or []
                self.CUENTAS = cuentas_plan
        except Exception:
            try:
                self.CUENTAS = obtenerTodasCuentasContables(get_db_path())
            except Exception:
                self.CUENTAS = []

        # UI refs
        self.dialog: Optional[ft.AlertDialog] = None
        self.area_scroll: Optional[ft.Container] = None
        self.overlay_panel = ft.Container(
            visible=False,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK26),
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            padding=ft.padding.symmetric(vertical=6),
            height=180,
            width=360,
            content=ft.Column([], spacing=0, scroll=ft.ScrollMode.AUTO),
        )
        self.overlay_host = ft.Container(visible=False, content=self.overlay_panel, top=0, left=0)
        self.overlay_host.positioned = True
        self.overlay_backdrop = ft.Container(
            visible=False,
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.01, ft.Colors.BLACK),
            on_click=self._backdrop_click,
            top=0,
            left=0,
            right=0,
            bottom=0,
        )
        self.overlay_backdrop.positioned = True

        # Backdrop global para clic fuera del diálogo (usando page.overlay)
        self.global_backdrop = ft.Container(
            expand=True,
            bgcolor=ft.Colors.TRANSPARENT,
            on_click=self._backdrop_click,
        )

        # Filas como objetos
        self.rows: List[VoucherRow] = []
        self.filas_column: Optional[ft.Column] = None

        self.total_debe_text = ft.Text(value="0.00", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)
        self.total_haber_text = ft.Text(value="0.00", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)
        self.error_text = ft.Text(value="", color=ft.Colors.RED, size=12)

        self.dia_field = ft.TextField(hint_text='Ingrese el día', width=140)
        self.comentario_field = ft.TextField(hint_text='Ingrese comentarios', multiline=True, min_lines=1, max_lines=3)
        self.suspend_updates = False
        self._hide_task: asyncio.Task | None = None
        self.code_focused = False
        self.overlay_hovered = False

        # Style helpers
        self.TIPO_COLORES = {
            "Activo": ft.Colors.GREEN_600,
            "Pasivo": ft.Colors.RED_600,
            "Patrimonio": ft.Colors.BLUE_700,
            "Ingresos": ft.Colors.CYAN_700,
            "Gastos": ft.Colors.ORANGE_700,
            "Resultado": ft.Colors.PURPLE_600,
        }

        # Capturar clic global en la página para cerrar sugerencias si están abiertas
        self._prev_pointer_down = getattr(self.page, "on_pointer_down", None)

        def _page_pointer_down(e):
            try:
                if self.overlay_panel.visible:
                    self.hide_overlay()
            finally:
                if callable(self._prev_pointer_down):
                    try:
                        self._prev_pointer_down(e)
                    except Exception:
                        pass

        self.page.on_pointer_down = _page_pointer_down

    def buscar_cuentas_por_codigo(self, query: str, max_items: int = 50):
        q = (query or "").strip().lower()
        if not q:
            return self.CUENTAS[:max_items]

        # Si el usuario escribe prefijo jerárquico (ej: "2." o "2.1."), filtrar sólo códigos que comienzan con ese prefijo
        def is_hierarchical_prefix(s: str) -> bool:
            return "." in s or s.endswith(".") or s.isdigit()

        hierarchical = is_hierarchical_prefix(q)
        scored = []
        for c in self.CUENTAS:
            codigo = (c.codigo_cuenta or "").lower()
            nombre = (c.nombre_cuenta or "").lower()
            s = 0
            if hierarchical:
                # Coincidencia estricta de prefijo al inicio del código
                if codigo.startswith(q):
                    s = 80 if codigo != q else 100
            else:
                # Búsqueda flexible si no parece prefijo jerárquico
                if codigo == q:
                    s = 100
                elif codigo.startswith(q):
                    s = 70
                elif q in codigo:
                    s = 40
                elif q in nombre:
                    s = 15
            if s > 0:
                scored.append((s, c))

        # Ordenar por score y por código para estabilidad
        scored.sort(key=lambda x: ( -x[0], (x[1].codigo_cuenta or "") ))
        return [c for _, c in scored[:max_items]]

    def show_overlay(self, idx: int, items: List[ft.Control]):
        ROW_H = 64
        HEADER_H = 48
        self.overlay_panel.content = ft.Column(items, spacing=0, scroll=ft.ScrollMode.AUTO)
        self.overlay_panel.on_hover = lambda e: (setattr(self, 'overlay_hovered', e.data == 'true'), self.cancel_hide_overlay() if e.data == 'true' else self.schedule_hide_overlay(0.25))
        self.overlay_panel.on_pointer_enter = lambda e: (setattr(self, 'overlay_hovered', True), self.cancel_hide_overlay())
        self.overlay_panel.on_pointer_leave = lambda e: (setattr(self, 'overlay_hovered', False), self.schedule_hide_overlay(0.25))
        self.overlay_panel.on_wheel = lambda e: (setattr(self, 'overlay_hovered', True), self.cancel_hide_overlay())
        panel_h = self.overlay_panel.height or 180
        filas_totales = len(self.rows)
        fila_top = HEADER_H + idx * ROW_H
        mostrar_arriba = idx >= (filas_totales - 3) and filas_totales >= 3
        if mostrar_arriba:
            self.overlay_host.top = max(HEADER_H, fila_top - panel_h)
        else:
            self.overlay_host.top = fila_top + ROW_H - 100
        self.overlay_host.left = 160
        self.overlay_host.visible = True
        self.overlay_panel.visible = True
        self.overlay_backdrop.visible = True
        try:
            if self.global_backdrop not in self.page.overlay:
                self.page.overlay.append(self.global_backdrop)
        except Exception:
            pass
        if self.area_scroll:
            self.area_scroll.update()

    def hide_overlay(self):
        self.cancel_hide_overlay()
        self.overlay_panel.visible = False
        self.overlay_host.visible = False
        self.overlay_backdrop.visible = False
        try:
            if self.global_backdrop in self.page.overlay:
                self.page.overlay.remove(self.global_backdrop)
        except Exception:
            pass
        try:
            if self.area_scroll:
                self.area_scroll.update()
            if self.page:
                self.page.update()
        except Exception:
            pass
        self._pending_blur = False

    def cancel_hide_overlay(self):
        try:
            if self._hide_task and not self._hide_task.done():
                self._hide_task.cancel()
        except Exception:
            pass
        self._hide_task = None

    def schedule_hide_overlay(self, delay: float = 0.25):
        self.cancel_hide_overlay()
        async def _delayed():
            try:
                await asyncio.sleep(delay)
                if self.overlay_panel.visible and not self.code_focused and not self.overlay_hovered:
                    self.hide_overlay()
            except asyncio.CancelledError:
                return
        try:
            self._hide_task = asyncio.create_task(_delayed())
        except Exception:
            self._hide_task = None

    def _backdrop_click(self, e=None):
        # Click afuera: cerrar sugerencias inmediatamente
        self.hide_overlay()

    def recalc_totals(self):
        total_debe = sum(r.get_debe() for r in self.rows)
        total_haber = sum(r.get_haber() for r in self.rows)
        self.total_debe_text.value = f"{total_debe:.2f}"
        self.total_haber_text.value = f"{total_haber:.2f}"
        if not self.suspend_updates:
            self.total_debe_text.update(); self.total_haber_text.update()

    def _fila(self, i: int, prefill: Optional[LineaAsiento] = None, prefill_code: Optional[str] = None) -> ft.Container:
        CODE_W = 160; DEBE_W = 140; HABER_W = 140; GAP = 8
        tf_codigo = ft.TextField(hint_text='Ingrese codigo', width=CODE_W, autofocus=False)
        tf_nombre_nombre = ft.Text()
        tf_nombre_tipo = ft.Text()

        def actualizar_nombre(nombre: str, tipo: str):
            tf_nombre_nombre.value = nombre or ''
            if tipo:
                tf_nombre_tipo.value = f"({tipo})"
                tf_nombre_tipo.color = self.TIPO_COLORES.get(tipo, ft.Colors.BLUE_600)
            else:
                tf_nombre_tipo.value = ''
                tf_nombre_tipo.color = ft.Colors.GREY_500
            tf_nombre_nombre.update(); tf_nombre_tipo.update()

        def seleccionar_sugerencia(cuenta: CuentaContable):
            # Actualizar campo con la cuenta seleccionada
            tipo = getattr(cuenta, 'nombre_tipo_cuenta', '') or ''
            tipo_color = self.TIPO_COLORES.get(tipo, ft.Colors.BLUE_600) if tipo else ft.Colors.GREY_500
            tf_codigo.value = cuenta.codigo_cuenta or ''
            tf_nombre_nombre.value = cuenta.nombre_cuenta or ''
            tf_nombre_tipo.value = f"({tipo})" if tipo else ''
            tf_nombre_tipo.color = tipo_color
            row_obj.cuenta = cuenta
            # Actualizar visualmente
            tf_codigo.update(); tf_nombre_nombre.update(); tf_nombre_tipo.update()
            # Cerrar sugerencias después de seleccionar
            self.hide_overlay()
            try:
                self.page.update()
            except Exception:
                pass

        def mostrar_sugerencias_codigo():
            texto = tf_codigo.value
            sugs = self.buscar_cuentas_por_codigo(texto)
            if sugs:
                items = []
                for c in sugs:
                    tipo = getattr(c, 'nombre_tipo_cuenta', '') or ''
                    tipo_color = self.TIPO_COLORES.get(tipo, ft.Colors.BLUE_600) if tipo else ft.Colors.GREY_500
                    items.append(
                        ft.ListTile(
                            leading=ft.Text(c.codigo_cuenta or '', color=ft.Colors.GREY_700),
                            title=ft.Text(c.nombre_cuenta or ''),
                            trailing=ft.Text(tipo, color=tipo_color),
                            dense=True,
                            mouse_cursor=ft.MouseCursor.CLICK,
                            on_click=lambda e, cuenta=c: seleccionar_sugerencia(cuenta),
                        )
                    )
                self.show_overlay(i, items)
            else:
                self.hide_overlay()
            codigo_actual = (tf_codigo.value or '').strip()
            encontrada = next((c for c in self.CUENTAS if (c.codigo_cuenta or '').strip() == codigo_actual), None) if codigo_actual else None
            if encontrada:
                tipo_encontrada = getattr(encontrada, 'nombre_tipo_cuenta', '') or ''
                actualizar_nombre(encontrada.nombre_cuenta or '', tipo_encontrada)
            else:
                actualizar_nombre('', '')

        tf_codigo.on_change = lambda e: (self.cancel_hide_overlay(), mostrar_sugerencias_codigo())
        tf_codigo.on_focus = lambda e: (setattr(self, 'code_focused', True), self.cancel_hide_overlay(), mostrar_sugerencias_codigo())
        # Al perder foco, marca flag y programa cierre con retraso
        tf_codigo.on_blur = lambda e: (setattr(self, 'code_focused', False), self.schedule_hide_overlay(0.25))
        # Cerrar sugerencias con Escape
        tf_codigo.on_key_down = lambda e: (self.hide_overlay() if e.key == 'Escape' else None)

        tf_debe = ft.TextField(hint_text='Ingrese el valor', width=DEBE_W)
        tf_haber = ft.TextField(hint_text='Ingrese el valor', width=HABER_W)
        tf_debe.on_change = lambda e: self.recalc_totals()
        tf_haber.on_change = lambda e: self.recalc_totals()

        nombre_container = ft.Container(
            expand=True,
            content=ft.Row([tf_nombre_nombre, tf_nombre_tipo], spacing=6),
            padding=ft.padding.only(left=8, top=8, bottom=8, right=8),
            border=ft.border.all(1, ft.Colors.GREY_300), border_radius=4
        )
        fila_ctrl = ft.Container(
            height=64,
            content=ft.Row([tf_codigo, nombre_container, tf_debe, tf_haber], spacing=GAP),
        )
        row_obj = VoucherRow(i, tf_codigo, tf_debe, tf_haber, tf_nombre_nombre, tf_nombre_tipo, fila_ctrl)
        # Prefill si viene información
        if prefill is not None:
            # Montos
            try:
                row_obj.debe_field.value = f"{float(prefill.debe or 0):.2f}"
                row_obj.haber_field.value = f"{float(prefill.haber or 0):.2f}"
                if not self.suspend_updates:
                    row_obj.debe_field.update(); row_obj.haber_field.update()
            except Exception:
                pass
            # Cuenta y código
            cuenta = None
            if prefill.cuenta_contable:
                cuenta = prefill.cuenta_contable
            elif getattr(prefill, 'id_cuenta_contable', 0):
                cuenta = next((c for c in self.CUENTAS if c.id_cuenta_contable == prefill.id_cuenta_contable), None)
            if cuenta:
                tipo = getattr(cuenta, 'nombre_tipo_cuenta', '') or ''
                tipo_color = self.TIPO_COLORES.get(tipo, ft.Colors.BLUE_600) if tipo else ft.Colors.GREY_500
                row_obj.set_account(cuenta, tipo_color, apply_updates=not self.suspend_updates)
            # Si no hay cuenta pero hay código, setearlo
            if not cuenta and prefill_code:
                row_obj.code_field.value = (prefill_code or '').strip()
                if not self.suspend_updates:
                    row_obj.code_field.update()
        self.rows.append(row_obj)
        return fila_ctrl

    def add_row(self, e=None):
        i = len(self.rows)
        return self._fila(i, None, None)

    def build_content(self) -> ft.Container:
        filas_column = ft.Column(spacing=0)
        self.filas_column = filas_column
        # Crear 4 filas iniciales
        for _ in range(4):
            filas_column.controls.append(self.add_row())
        bottom_spacer = ft.Container(height=0)
        filas_stack = ft.Stack(
            controls=[filas_column, self.overlay_backdrop, self.overlay_host],
            clip_behavior=ft.ClipBehavior.NONE,
            expand=True,
        )
        self.area_scroll = ft.Container(
            expand=True,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            padding=8,
            clip_behavior=ft.ClipBehavior.NONE,
            content=ft.Column(controls=[filas_stack], scroll=ft.ScrollMode.AUTO, expand=True, spacing=0),
        )

        header = ft.Container(
            height=48,
            padding=9,
            content=ft.Row([
                ft.Text('Codigo', weight=ft.FontWeight.BOLD, expand=1),
                ft.Text('Nombre de la cuenta', weight=ft.FontWeight.BOLD, expand=2),
                ft.Text('Debe', weight=ft.FontWeight.BOLD, expand=1),
                ft.Text('Haber', weight=ft.FontWeight.BOLD, expand=1),
            ])
        )

        form_top = ft.Row([
            ft.Container(expand=1, padding=8, content=ft.Column([ft.Text('Día'), self.dia_field], spacing=6)),
            ft.Container(expand=3, padding=8, content=ft.Column([ft.Text('Comentario'), self.comentario_field], spacing=6)),
            ft.Container(padding=8, content=ft.ElevatedButton("Agregar fila", icon=ft.Icons.ADD, on_click=lambda e: filas_column.controls.insert(len(filas_column.controls), self.add_row()) or filas_column.update())),
        ])

        total = ft.Row([
            ft.Container(padding=8, content=ft.Text('Totales', weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, size=16)),
            ft.Container(expand=True),
            ft.Row([
                ft.Text('Debe:', weight=ft.FontWeight.BOLD),
                self.total_debe_text,
                ft.Container(width=24),
                ft.Text('Haber:', weight=ft.FontWeight.BOLD),
                self.total_haber_text,
            ], spacing=8),
        ])

        main_column = ft.Column([
            form_top,
            header,
            self.area_scroll,
            total,
            ft.Container(padding=ft.padding.only(left=8, right=8), content=self.error_text),
        ], expand=True, spacing=8)

        return ft.Container(width=820, height=800, padding=ft.padding.only(top=16, left=16, right=16, bottom=8), bgcolor=ft.Colors.WHITE, content=main_column)

    def validate(self) -> bool:
        used_rows = []
        for r in self.rows:
            code = r.get_code()
            d = r.get_debe()
            h = r.get_haber()
            if code:
                used_rows.append((code, d, h))
        if len(used_rows) < 2:
            self.error_text.value = "Debe ingresar al menos 2 cuentas con código."; self.error_text.update(); return False
        for code, d, h in used_rows:
            if d <= 0 and h <= 0:
                self.error_text.value = f"La cuenta {code} debe tener un valor en Debe o Haber."; self.error_text.update(); return False
        debe = float((self.total_debe_text.value or "0").replace(',', '.'))
        haber = float((self.total_haber_text.value or "0").replace(',', '.'))
        if debe != haber:
            self.error_text.value = "El comprobante no está balanceado. El total del Debe debe ser igual al total del Haber."; self.error_text.update(); return False
        self.error_text.value = ""; self.error_text.update(); return True

    def _collect_rows(self) -> List[LineaAsiento]:
        """Construye objetos LineaAsiento de las filas actuales."""
        rows: List[LineaAsiento] = []
        for r in self.rows:
            code = r.get_code()
            if not code:
                continue
            # Determinar id_cuenta_contable por cuenta seleccionada o por código
            id_cuenta = 0
            if r.cuenta and getattr(r.cuenta, 'id_cuenta_contable', 0):
                id_cuenta = int(r.cuenta.id_cuenta_contable)
            else:
                encontrada = next((c for c in self.CUENTAS if (c.codigo_cuenta or '').strip() == code), None)
                if encontrada:
                    id_cuenta = int(getattr(encontrada, 'id_cuenta_contable', 0) or 0)
            rows.append(
                LineaAsiento(
                    id_linea_asiento=0,
                    id_asiento=self.asiento_id or 0,
                    id_cuenta_contable=id_cuenta,
                    debe=r.get_debe(),
                    haber=r.get_haber(),
                    cuenta_contable=r.cuenta if r.cuenta else None,
                )
            )
        return rows

    def save(self):
        if not self.validate():
            return
        lines = self._collect_rows()
        total_debe = sum(l.debe for l in lines)
        total_haber = sum(l.haber for l in lines)

        # Construir fecha usando año/mes del libro_diario
        raw_day = (self.dia_field.value or '').strip()
        day_int = None
        if raw_day.isdigit():
            day_int = max(1, min(31, int(raw_day)))
        # Obtener año y mes desde libro_diario
        db_path = get_db_path()
        conn_tmp = sqlite3.connect(db_path)
        try:
            cur_tmp = conn_tmp.cursor()
            cur_tmp.execute("SELECT ano, id_mes FROM libro_diario WHERE id_libro_diario = ?", (self.id_libro_diario,))
            row_lib = cur_tmp.fetchone()
            if row_lib:
                ano_lib, mes_id = row_lib
                # Si el día no es válido, usar 1
                if day_int is None:
                    day_int = 1
                # Asegurar mes 1-12
                mes_num = int(mes_id or 1)
                mes_num = 1 if mes_num < 1 else (12 if mes_num > 12 else mes_num)
                fecha_str = f"{int(ano_lib):04d}-{mes_num:02d}-{int(day_int):02d}"
            else:
                # Fallback a hoy si no se encuentra el libro
                today = datetime.now()
                fecha_str = today.strftime("%Y-%m-%d")
        except Exception:
            today = datetime.now()
            fecha_str = today.strftime("%Y-%m-%d")
        finally:
            try:
                conn_tmp.close()
            except Exception:
                pass
        descripcion = (self.comentario_field.value or '').strip() or "(Sin descripción)"

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Mapear códigos a id_cuenta_contable (respaldo)
        cuenta_map = { (c.codigo_cuenta or '').strip(): c.id_cuenta_contable for c in self.CUENTAS }

        try:
            if self.asiento_id:
                # Actualizar asiento + reemplazar líneas
                cur.execute("UPDATE asiento SET fecha = ?, descripcion = ? WHERE id_asiento = ?", (fecha_str, descripcion, self.asiento_id))
                # Obtener totales anteriores
                cur.execute("SELECT COALESCE(SUM(debe),0), COALESCE(SUM(haber),0) FROM linea_asiento WHERE id_asiento = ?", (self.asiento_id,))
                old_debe, old_haber = cur.fetchone() or (0.0, 0.0)
                cur.execute("DELETE FROM linea_asiento WHERE id_asiento = ?", (self.asiento_id,))
                for ln in lines:
                    id_cuenta = ln.id_cuenta_contable or cuenta_map.get((ln.cuenta_contable.codigo_cuenta if ln.cuenta_contable else '').strip(), 0)
                    if not id_cuenta:
                        continue
                    cur.execute(
                        "INSERT INTO linea_asiento (id_asiento, debe, haber, id_cuenta_contable) VALUES (?, ?, ?, ?)",
                        (self.asiento_id, ln.debe, ln.haber, id_cuenta)
                    )
                # Ajuste delta a libro
                delta_debe = total_debe - (old_debe or 0.0)
                delta_haber = total_haber - (old_haber or 0.0)
                cur.execute("UPDATE libro_diario SET total_debe = total_debe + ?, total_haber = total_haber + ? WHERE id_libro_diario = ?", (delta_debe, delta_haber, self.id_libro_diario))
            else:
                # Crear asiento nuevo con numero_asiento secuencial dentro del libro
                cur.execute("SELECT COALESCE(MAX(numero_asiento), 0) FROM asiento WHERE id_libro_diario = ?", (self.id_libro_diario,))
                last_num = cur.fetchone()[0] if cur.fetchone() is None else 0
                # fetchone was consumed above; re-run properly
                cur.execute("SELECT COALESCE(MAX(numero_asiento), 0) FROM asiento WHERE id_libro_diario = ?", (self.id_libro_diario,))
                row_max = cur.fetchone()
                next_num = int((row_max[0] or 0)) + 1 if row_max else 1
                cur.execute("INSERT INTO asiento (id_libro_diario, fecha, numero_asiento, descripcion) VALUES (?, ?, ?, ?)", (self.id_libro_diario, fecha_str, next_num, descripcion))
                new_id = cur.lastrowid
                for ln in lines:
                    id_cuenta = ln.id_cuenta_contable or cuenta_map.get((ln.cuenta_contable.codigo_cuenta if ln.cuenta_contable else '').strip(), 0)
                    if not id_cuenta:
                        continue
                    cur.execute(
                        "INSERT INTO linea_asiento (id_asiento, debe, haber, id_cuenta_contable) VALUES (?, ?, ?, ?)",
                        (new_id, ln.debe, ln.haber, id_cuenta)
                    )
                cur.execute("UPDATE libro_diario SET total_debe = total_debe + ?, total_haber = total_haber + ? WHERE id_libro_diario = ?", (total_debe, total_haber, self.id_libro_diario))
            conn.commit()
        finally:
            conn.close()
        # Trigger refresh callback if provided
        try:
            if callable(self.on_saved):
                self.on_saved()
        except Exception:
            pass
        if self.dialog:
            self.dialog.open = False
            self.page.update()

    def open(self):
        content_ctrl = self.build_content()
        # Si es edición, cargar líneas desde BD (prefill)
        if self.asiento_id:
            try:
                self.suspend_updates = True
                db_path = get_db_path()
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                cur.execute("SELECT fecha, descripcion FROM asiento WHERE id_asiento = ?", (self.asiento_id,))
                row = cur.fetchone()
                if row:
                    fecha, descripcion = row
                    # Intentar extraer día
                    try:
                        day = int(str(fecha).split('-')[-1])
                        self.dia_field.value = str(day)
                    except Exception:
                        pass
                    self.comentario_field.value = descripcion or ''
                # Cargar líneas con join para obtener código y nombre de cuenta
                cur.execute(
                    """
                    SELECT la.id_cuenta_contable, c.codigo_cuenta, c.nombre_cuenta, la.debe, la.haber
                    FROM linea_asiento la
                    LEFT JOIN cuenta_contable c ON c.id_cuenta_contable = la.id_cuenta_contable
                    WHERE la.id_asiento = ?
                    ORDER BY la.id_linea_asiento ASC
                    """,
                    (self.asiento_id,)
                )
                cuenta_por_id = {c.id_cuenta_contable: c for c in self.CUENTAS}
                lines = cur.fetchall() or []
                if not lines:
                    pass
                # Limpiar filas iniciales, recrear con datos
                self.rows.clear()
                filas_column = self.filas_column or content_ctrl.content.controls[2].content.controls[0].controls[0]
                filas_column.controls.clear()
                for idx, (id_cuenta, codigo, nombre, d, h) in enumerate(lines):
                    cuenta = cuenta_por_id.get(id_cuenta) if id_cuenta else (
                        next((c for c in self.CUENTAS if (c.codigo_cuenta or '').strip() == (codigo or '').strip()), None)
                    )
                    prefill = LineaAsiento(
                        id_linea_asiento=0,
                        id_asiento=self.asiento_id or 0,
                        id_cuenta_contable=id_cuenta or (cuenta.id_cuenta_contable if cuenta else 0),
                        debe=float(d or 0),
                        haber=float(h or 0),
                        cuenta_contable=cuenta
                    )
                    fila = self._fila(idx, prefill=prefill, prefill_code=(codigo or '').strip() or None)
                    filas_column.controls.append(fila)
                # Asegurar al menos 4 filas
                while len(filas_column.controls) < 4:
                    filas_column.controls.append(self.add_row())
                self.suspend_updates = False
                filas_column.update()
                self.recalc_totals()
            except Exception:
                self.suspend_updates = False
            finally:
                try:
                    conn.close()
                except Exception:
                    pass

        self.dialog = ft.AlertDialog(
            title=ft.Text('Comprobante contable', color=ft.Colors.BLACK, size=18, weight=ft.FontWeight.BOLD),
            modal=True,
            content=content_ctrl,
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=ft.Colors.WHITE,
        )
        self.dialog.actions = [
            ft.TextButton('Cancelar', on_click=lambda e: self._close()),
            ft.ElevatedButton('Guardar', on_click=lambda e: self.save()),
        ]
        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    def _close(self):
        if self.dialog:
            self.dialog.open = False
            self.page.update()
