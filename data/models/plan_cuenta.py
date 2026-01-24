from dataclasses import dataclass
from typing import Optional

@dataclass
class PlanCuenta:
    id_plan_cuenta: int = 0
    nombre_plan_cuenta: str = ''
    
    def __str__(self):
        return self.nombre_plan_cuenta
