import sys
import os
# Agregar el directorio raíz del proyecto al path de Python guty
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from sqlite3 import Error
from typing import List, Optional
from data.models.plan_cuenta import PlanCuenta

def obtenerTodosPlanesCuentas(nombre_bd: str) -> List[PlanCuenta]:
    conn = None
    try:
        conn = sqlite3.connect(nombre_bd)
        cursor = conn.cursor()
        cursor.execute("SELECT id_plan_cuenta, nombre_plan_cuentas FROM plan_cuentas")
        return [PlanCuenta(id_plan_cuenta=row[0], nombre_plan_cuenta=row[1]) for row in cursor.fetchall()]
    
    except Error as e:
        print(f"Database error: {e}")
        return []
    
    finally:
        if conn:
            conn.close()

