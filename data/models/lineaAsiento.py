from dataclasses import dataclass
from typing import Optional
from data.models.cuenta import CuentaContable

@dataclass
class LineaAsiento:
    id_linea_asiento: int = 0
    id_asiento: int = 0
    id_cuenta_contable: int = 0
    debe: float = 0.0
    haber: float = 0.0
    cuenta_contable: Optional[CuentaContable] = None  # Relación directa
    
    def __str__(self):
        return f"Línea {self.id_linea_asiento} - {self.descripcion_linea}"
    
    def __post_init__(self):
        if self.cuenta_contable is None:
            self.cuenta_contable = CuentaContable()
            
    @property
    def descripcion_linea(self) -> str:
        return f"{self.cuenta_contable.codigo_cuenta} - {self.cuenta_contable.nombre_cuenta}"
    
    @property
    def nombre_cuenta(self) -> str:
        return self.cuenta_contable.nombre_cuenta if self.cuenta_contable else ''
    
    @property
    def codigo_cuenta(self) -> str:
        return self.cuenta_contable.codigo_cuenta if self.cuenta_contable else ''