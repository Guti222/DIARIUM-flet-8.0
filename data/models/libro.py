from __future__ import annotations

from dataclasses import dataclass
from typing import List, TYPE_CHECKING
from data.models.mes import Mes
from src.utils.paths import get_db_path

if TYPE_CHECKING:
    from data.models.asiento import Asiento

@dataclass
class LibroDiario:
    id_libro_diario: int = 0
    id_mes: int = 0
    ano: int = 0
    nombre_empresa: str = ""
    contador: str = ""
    total_debe: float = 0.0
    total_haber: float = 0.0
    id_plan_cuenta: int = 0
    origen: str = "creado"
    fecha_importacion: str | None = None
    
    def __str__(self):
        return f"Libro {self.nombre_empresa} - {self.ano}/{self.id_mes}"
    
    def __post_init__(self):
        pass
    
    @property
    def descripcion(self) -> str:
        return f"{self.nombre_empresa} - {self.ano} - Mes ID: {self.id_mes}"
    
    @property
    
    def nombre_mes(self) -> str:
        mes_nombres = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
        return mes_nombres.get(self.id_mes, "Mes Desconocido")
    
    @property
    def mes(self) -> Mes:
        return Mes(id_mes=self.id_mes, nombre_mes=self.nombre_mes)
    
    @property
    def asientos(self) -> List["Asiento"]:
        """Devuelve la lista de Asientos asociados a este LibroDiario.

        Usa la función en `data.obtenerAsientos` para mantener la
        lógica de acceso a datos separada del modelo.
        """
        try:
            from data.obtenerLineaAsiento import obtenerAsientosPorCuenta
            return obtenerAsientosPorCuenta(get_db_path(), self.id_libro_diario)
        except Exception as ex:
            print(f"Error obteniendo asientos para libro {self.id_libro_diario}: {ex}")
            return []
