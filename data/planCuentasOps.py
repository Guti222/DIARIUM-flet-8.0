import sqlite3
from sqlite3 import Error
from typing import Optional


def crear_plan_cuenta(db_path: str, nombre_plan: str) -> Optional[int]:
    """
    Crea un nuevo registro en plan_cuentas y retorna su id.
    Si el nombre ya existe, retorna None.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=5)
        conn.execute("PRAGMA busy_timeout=3000")
        cur = conn.cursor()
        # Evitar duplicados por nombre
        cur.execute("SELECT id_plan_cuenta FROM plan_cuentas WHERE nombre_plan_cuentas = ?", (nombre_plan,))
        row = cur.fetchone()
        if row:
            # Ya existe
            return None
        cur.execute(
            "INSERT INTO plan_cuentas (nombre_plan_cuentas) VALUES (?)",
            (nombre_plan,)
        )
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(f"Error creando plan de cuentas: {e}")
        return None
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def copiar_cuentas_de_plan(db_path: str, origen_id: int, destino_id: int) -> int:
    """
    Copia de planes no implementada con el nuevo esquema (cuentas ligadas por
    tipo->rubro->genérico). Se retorna 0 para evitar errores en tiempo de ejecución.
    """
    print("copiar_cuentas_de_plan: no implementado con el esquema sin id_plan_cuenta en cuenta/rubro/generico")
    return 0
