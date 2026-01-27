import re
import flet as ft
from data.models.cuenta import CuentaContable, Generico, Rubro, TipoCuenta
from data.obtenerCuentas import (
    obtenerCuentasContablesPorPlanCuenta,
    obtenerTodasCuentasContables,
    obtenerTodosGenericoPorRubro,
    obtenerTodosRubroPorTipoCuenta,
    obtenerTodasTipoCuentas,
)
from src.ui.pages.account_list_page.account_card import create_item_account
from src.ui.pages.account_list_page.catalog_cards import (
    create_item_generico,
    create_item_rubro,
    create_item_tipo,
)

#gutyk
class AccountListView:
    def __init__(self, db_path: str, page: ft.Page):
        self.page = page
        self.db_path = db_path
        self.cuentas: list[CuentaContable] = obtenerTodasCuentasContables(self.db_path)
        self.tipos_map: dict[int, TipoCuenta] = {}
        self.rubros_map: dict[int, Rubro] = {}
        self.genericos_map: dict[int, Generico] = {}
        self._tipos_summary: list[dict] = []
        self._rubros_summary: list[dict] = []
        self._genericos_summary: list[dict] = []
        self.view_mode = "cuentas"  # cuentas|tipos|rubros|genericos
        self.last_filter_text: str = ""
        self.page_size: int = 50
        self.visible_count: int = self.page_size
        self._load_catalog_data()
        self._rebuild_summaries()
        self._sort_cuentas_inplace()
        self.account_list = ft.ListView(
            expand=True,
            #spacing=5,
            controls=[],
        )
        self._update_list()

    def _safe_update(self):
        try:
            self.account_list.update()
        except AssertionError:
            # Control no agregado aún; ignorar
            pass
        except Exception:
            pass

    def set_initial_plan_filter(self, plan_name: str):
        """Aplica filtro inicial por nombre de plan sin llamar update()."""
        try:
            if plan_name:
                self.cuentas = [c for c in self.cuentas if c.nombre_plan_cuenta == plan_name]
            self._rebuild_summaries()
            self.visible_count = self.page_size
            self._update_list()
        except Exception:
            # Filtro opcional; en caso de error, mantener lista completa
            pass

    def _load_catalog_data(self):
        """Carga catálogo completo para mostrar elementos sin cuentas (estilo left join)."""
        try:
            tipos = obtenerTodasTipoCuentas(self.db_path)
            self.tipos_map = {t.id_tipo_cuenta: t for t in tipos}
            self.rubros_map = {}
            self.genericos_map = {}
            for t in tipos:
                rubros = obtenerTodosRubroPorTipoCuenta(self.db_path, t.id_tipo_cuenta)
                for r in rubros:
                    r.tipo_cuenta = t
                    self.rubros_map[r.id_rubro] = r
                    genericos = obtenerTodosGenericoPorRubro(self.db_path, r.id_rubro)
                    for g in genericos:
                        g.rubro = r
                        self.genericos_map[g.id_generico] = g
        except Exception as ex:
            print(f"Error cargando catálogo para listas: {ex}")

    def _rebuild_summaries(self):
        """Precalcula resúmenes por tipo/rubro/generico para no recalcular en cada filtro."""
        tipo_entries = {
            tid: {"tipo": t, "rubros": set(), "genericos": set(), "cuentas": 0}
            for tid, t in self.tipos_map.items()
        }
        rubro_entries = {
            rid: {"rubro": r, "genericos": set(), "cuentas": 0}
            for rid, r in self.rubros_map.items()
        }
        generico_entries = {
            gid: {"generico": g, "cuentas": 0}
            for gid, g in self.genericos_map.items()
        }

        for c in self.cuentas:
            tipo_id = c.id_tipo_cuenta
            rubro_id = c.id_rubro
            gen_obj: Generico | None = getattr(c, "generico", None)
            gen_id = getattr(gen_obj, "id_generico", None)

            if tipo_id:
                entry = tipo_entries.setdefault(
                    tipo_id,
                    {
                        "tipo": TipoCuenta(id_tipo_cuenta=tipo_id, nombre_tipo_cuenta=c.nombre_tipo_cuenta, numero_cuenta=getattr(c.generico.rubro.tipo_cuenta, "numero_cuenta", "")),
                        "rubros": set(),
                        "genericos": set(),
                        "cuentas": 0,
                    },
                )
                if rubro_id:
                    entry["rubros"].add(rubro_id)
                if gen_id:
                    entry["genericos"].add(gen_id)
                entry["cuentas"] += 1

            if rubro_id:
                rubro_obj = getattr(gen_obj, "rubro", Rubro()) if gen_obj else Rubro()
                entry = rubro_entries.setdefault(
                    rubro_id,
                    {
                        "rubro": Rubro(
                            id_rubro=rubro_id,
                            id_tipo_cuenta=getattr(rubro_obj.tipo_cuenta, "id_tipo_cuenta", tipo_id or 0),
                            nombre_rubro=c.nombre_rubro,
                            numero_cuenta=getattr(rubro_obj, "numero_cuenta", ""),
                            tipo_cuenta=getattr(rubro_obj, "tipo_cuenta", TipoCuenta()),
                        ),
                        "genericos": set(),
                        "cuentas": 0,
                    },
                )
                if gen_id:
                    entry["genericos"].add(gen_id)
                entry["cuentas"] += 1

            if gen_id:
                rubro_obj = getattr(gen_obj, "rubro", Rubro()) if gen_obj else Rubro()
                entry = generico_entries.setdefault(
                    gen_id,
                    {
                        "generico": Generico(
                            id_generico=gen_id,
                            id_rubro=getattr(gen_obj, "id_rubro", 0),
                            nombre_generico=c.nombre_generico,
                            numero_cuenta=getattr(gen_obj, "numero_cuenta", ""),
                            rubro=rubro_obj,
                        ),
                        "cuentas": 0,
                    },
                )
                entry["cuentas"] += 1

        def numeric_key(val: str):
            nums = re.findall(r"\d+", val or "")
            if nums:
                try:
                    return tuple(int(n) for n in nums)
                except Exception:
                    return (val or "",)
            return (val or "",)

        self._tipos_summary = sorted(tipo_entries.values(), key=lambda x: numeric_key(getattr(x["tipo"], "numero_cuenta", "")))
        self._rubros_summary = sorted(rubro_entries.values(), key=lambda x: numeric_key(getattr(x["rubro"], "numero_cuenta", "")))
        self._genericos_summary = sorted(generico_entries.values(), key=lambda x: numeric_key(getattr(x["generico"], "numero_cuenta", "")))
    
    def _update_list(self):
        """Actualiza la lista con todas las cuentas"""
        self.account_list.controls = self._build_view_items(filter_text=self.last_filter_text)
        # No llamar a update() aquí; el padre actualizará cuando corresponda.
    
    def get_view(self) -> ft.ListView:
        """Retorna el ListView para usar en la página"""
        return self.account_list
    
    def filter_accounts(self, filter_text: str = "", force: bool = False, reset_pagination: bool = True):
        """Filtra según el modo de vista actual con caché de texto para evitar renders innecesarios."""
        filter_text = (filter_text or "").lower()
        if not force and filter_text == self.last_filter_text and reset_pagination:
            return
        self.last_filter_text = filter_text
        if reset_pagination:
            self.visible_count = self.page_size
        items = self._build_view_items(filter_text=filter_text)
        self.account_list.controls = items
        self.account_list.update()

    def filter_by_account_plant(self, plan_cuenta: str):
        """Filtra las cuentas por cual plan de cuenta pertenecen"""
        self.cuentas = [
            cuenta for cuenta in self.cuentas
            if cuenta.nombre_plan_cuenta == plan_cuenta
        ]
        self._rebuild_summaries()
        self.visible_count = self.page_size
        self.last_filter_text = ""
        self._update_list()
        self.account_list.update()

    def filter_by_account_plan_id(self, id_plan: int):
        """Filtra recargando desde BD por `id_plan_cuenta` y actualiza la vista."""
        try:
            if id_plan is None:
                # Todos
                self.cuentas = obtenerTodasCuentasContables(self.db_path)
            else:
                self.cuentas = obtenerCuentasContablesPorPlanCuenta(self.db_path, id_plan)
            self._load_catalog_data()
            self._rebuild_summaries()
            self._sort_cuentas_inplace()
            self.visible_count = self.page_size
            self._update_list()
            self._safe_update()
        except Exception as ex:
            print(f"Error filtrando por plan id {id_plan}: {ex}")

    def refresh(self):
        """Recargar las cuentas desde la base de datos y actualizar la vista."""
        try:
            self.cuentas = obtenerTodasCuentasContables(self.db_path)
            self._load_catalog_data()
            self._rebuild_summaries()
            self._sort_cuentas_inplace()
            self.visible_count = self.page_size
            # Reaplicar el filtro activo si existe
            if self.last_filter_text:
                self.filter_accounts(self.last_filter_text, force=True)
            else:
                self._update_list()
        except Exception as ex:
            print(f"Error refrescando lista de cuentas: {ex}")
        finally:
            self._safe_update()

    def _sort_cuentas_inplace(self):
        """Ordena las cuentas por código de forma numérica ascendente."""
        def key(cuenta: CuentaContable):
            code = cuenta.codigo_cuenta or ""
            nums = re.findall(r"\d+", code)
            if nums:
                try:
                    return tuple(int(n) for n in nums)
                except Exception:
                    pass
            return (code,)

        try:
            self.cuentas = sorted(self.cuentas, key=key)
        except Exception:
            # Si falla la ordenación, mantener el orden actual
            pass

    def set_view_mode(self, mode: str):
        """Cambia el modo de vista (cuentas|tipos|rubros|genericos)."""
        if mode not in {"cuentas", "tipos", "rubros", "genericos"}:
            mode = "cuentas"
        self.view_mode = mode
        self.visible_count = self.page_size
        self.filter_accounts("", force=True)
        self._safe_update()

    def load_more(self):
        """Carga el siguiente bloque de elementos visibles y actualiza la lista."""
        self.visible_count += self.page_size
        # Reaplicar filtro actual
        self.filter_accounts(self.last_filter_text, force=True, reset_pagination=False)

    def _build_view_items(self, filter_text: str | None = None):
        ftxt = (filter_text or "").lower()
        items = []

        def numeric_key(val: str):
            nums = re.findall(r"\d+", val or "")
            if nums:
                try:
                    return tuple(int(n) for n in nums)
                except Exception:
                    return (val or "",)
            return (val or "",)

        if self.view_mode == "cuentas":
            data = self.cuentas
            if ftxt:
                data = [
                    c for c in data
                    if (ftxt in (c.codigo_cuenta or "").lower()
                        or ftxt in (c.nombre_cuenta or "").lower()
                        or ftxt in (c.nombre_tipo_cuenta or "").lower()
                        or ftxt in (c.nombre_rubro or "").lower()
                        or ftxt in (c.nombre_generico or "").lower())
                ]
            slice_data = data[: self.visible_count]
            for idx, cuenta in enumerate(slice_data):
                items.append(create_item_account(cuenta, self.page, refresh_callback=self.refresh, row_index=idx))
            if len(data) > self.visible_count:
                items.append(
                    ft.Container(
                        padding=10,
                        alignment=ft.alignment.Alignment(0, 0),
                        content=ft.ElevatedButton(
                            "Cargar más",
                            icon=ft.Icons.MORE_HORIZ,
                            bgcolor=ft.Colors.BLUE,
                            color=ft.Colors.WHITE,
                            on_click=lambda _e: self.load_more(),
                        ),
                    )
                )
            return items

        if self.view_mode == "tipos":
            for idx, data in enumerate(self._tipos_summary):
                label = f"{data['tipo'].numero_cuenta} - {data['tipo'].nombre_tipo_cuenta}"
                if ftxt and ftxt not in label.lower():
                    continue
                items.append(
                    create_item_tipo(
                        data["tipo"],
                        self.page,
                        refresh_callback=self.refresh,
                        row_index=idx,
                        rubro_count=len(data.get("rubros", set())),
                        generico_count=len(data.get("genericos", set())),
                        cuenta_count=data.get("cuentas", 0),
                    )
                )
            return items

        if self.view_mode == "rubros":
            for idx, data in enumerate(self._rubros_summary):
                label = f"{data['rubro'].numero_cuenta} - {data['rubro'].nombre_rubro}"
                if ftxt and ftxt not in label.lower():
                    continue
                items.append(
                    create_item_rubro(
                        data["rubro"],
                        self.page,
                        refresh_callback=self.refresh,
                        row_index=idx,
                        generico_count=len(data.get("genericos", set())),
                        cuenta_count=data.get("cuentas", 0),
                    )
                )
            return items

        if self.view_mode == "genericos":
            for idx, data in enumerate(self._genericos_summary):
                label = f"{data['generico'].numero_cuenta} - {data['generico'].nombre_generico}"
                if ftxt and ftxt not in label.lower():
                    continue
                items.append(
                    create_item_generico(
                        data["generico"],
                        self.page,
                        refresh_callback=self.refresh,
                        row_index=idx,
                        cuenta_count=data.get("cuentas", 0),
                    )
                )
            return items

        return items

