import re
import flet as ft
from data.models.cuenta import CuentaContable
from data.obtenerCuentas import obtenerTodasCuentasContables, obtenerCuentasContablesPorPlanCuenta
from src.ui.pages.account_list_page.account_card import create_item_account

#gutyk
class AccountListView:
    def __init__(self, db_path: str, page: ft.Page):
        self.page = page
        self.db_path = db_path
        self.cuentas: list[CuentaContable] = obtenerTodasCuentasContables(self.db_path)
        self._sort_cuentas_inplace()
        self.account_list = ft.ListView(
            expand=True,
            #spacing=5,
            controls=[],
        )
        self._update_list()

    def set_initial_plan_filter(self, plan_name: str):
        """Aplica filtro inicial por nombre de plan sin llamar update()."""
        try:
            if plan_name:
                self.cuentas = [c for c in self.cuentas if c.nombre_plan_cuenta == plan_name]
            self._update_list()
        except Exception:
            # Filtro opcional; en caso de error, mantener lista completa
            pass
    
    def _update_list(self):
        """Actualiza la lista con todas las cuentas"""
        self.account_list.controls.clear()
        
        for idx, cuenta in enumerate(self.cuentas):
            # Pasar el callback de refresco y el índice de fila para estilos
            item = create_item_account(cuenta, self.page, refresh_callback=self.refresh, row_index=idx)
            self.account_list.controls.append(item)
        # No llamar a update() aquí porque el ListView puede no haber sido
        # agregado todavía a la página (causa AssertionError en Flet).
        # El padre (la página) actualizará la UI cuando corresponda.
        pass
    
    def get_view(self) -> ft.ListView:
        """Retorna el ListView para usar en la página"""
        return self.account_list
    
    def filter_accounts(self, filter_text: str = ""):
        """Filtra las cuentas por texto"""
        self.account_list.controls.clear()
        
        filtered_cuentas = self.cuentas
        if filter_text:
            filter_text = filter_text.lower()
            filtered_cuentas = [
                cuenta for cuenta in self.cuentas
                if (filter_text in cuenta.codigo_cuenta.lower() or 
                    filter_text in cuenta.nombre_cuenta.lower() or
                    filter_text in cuenta.nombre_tipo_cuenta.lower() or
                    filter_text in cuenta.nombre_rubro.lower() or
                    filter_text in cuenta.nombre_generico.lower())
            ]
        
        for cuenta in filtered_cuentas:
            # Cuando filtramos, no tenemos el índice original; usar enumerate
            # para alternar colores según el orden filtrado.
            idx = filtered_cuentas.index(cuenta)
            item = create_item_account(cuenta, self.page, refresh_callback=self.refresh, row_index=idx)
            self.account_list.controls.append(item)
        
        self.account_list.update()

    def filter_by_account_plant(self, plan_cuenta: str):
        """Filtra las cuentas por cual plan de cuenta pertenecen"""
        self.account_list.controls.clear()
        
        filtered_cuentas = [
            cuenta for cuenta in self.cuentas
            if cuenta.nombre_plan_cuenta == plan_cuenta
        ]
        
        for idx, cuenta in enumerate(filtered_cuentas):
            item = create_item_account(cuenta, self.page, refresh_callback=self.refresh, row_index=idx)
            self.account_list.controls.append(item)
        
        self.account_list.update()

    def filter_by_account_plan_id(self, id_plan: int):
        """Filtra recargando desde BD por `id_plan_cuenta` y actualiza la vista."""
        try:
            if id_plan is None:
                # Todos
                self.cuentas = obtenerTodasCuentasContables(self.db_path)
            else:
                self.cuentas = obtenerCuentasContablesPorPlanCuenta(self.db_path, id_plan)
            self._sort_cuentas_inplace()
            self._update_list()
            self.account_list.update()
        except Exception as ex:
            print(f"Error filtrando por plan id {id_plan}: {ex}")

    def refresh(self):
        """Recargar las cuentas desde la base de datos y actualizar la vista."""
        try:
            self.cuentas = obtenerTodasCuentasContables(self.db_path)
            self._sort_cuentas_inplace()
            self._update_list()
        except Exception as ex:
            print(f"Error refrescando lista de cuentas: {ex}")
        finally:
            # Intentar actualizar si el control ya está agregado a la página.
            try:
                self.account_list.update()
            except AssertionError:
                # Control aún no agregado; ignorar.
                pass
            except Exception:
                pass

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

