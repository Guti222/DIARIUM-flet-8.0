from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from data.models.libro import LibroDiario
import sqlite3
from sqlite3 import Error
from typing import List
from data.models.lineaAsiento import LineaAsiento
from data.models.cuenta import CuentaContable

@dataclass
class Asiento:
    id_asiento: int = 0
    id_libro_diario: int = 0
    fecha_asiento: str = ''
    descripcion_asiento: str = ''
    total_debe: float = 0.0
    total_haber: float = 0.0
    numero_asiento: int = 0
    libro: Optional["LibroDiario"] = None  # Relación directa (forward reference)
    
    def __str__(self):
        return f"Asiento {self.id_asiento} - {self.descripcion_asiento}"
    
    def __post_init__(self):
        pass
    
    def get_lineas(self, db_path: str = "libro_facil.db") -> List[LineaAsiento]:
        """Devuelve la lista de LineaAsiento asociadas a este Asiento.

        Usa la función en `data.obtenerLineaAsiento` para mantener la
        lógica de acceso a datos separada del modelo.
        """
        try:
            from data.obtenerLineaAsiento import obtenerLineasPorAsiento
            return obtenerLineasPorAsiento(db_path, self.id_asiento)
        except Exception as ex:
            print(f"Error obteniendo lineas para asiento {self.id_asiento}: {ex}")
            return []

    @property
    def lineas(self) -> List[LineaAsiento]:
        return self.get_lineas()

    
    