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
    Copia todas las cuentas del plan `origen_id` al plan `destino_id`.
    Retorna la cantidad de cuentas copiadas.

    Si el plan origen no tiene cuentas y `origen_id == 0` (General),
    intenta copiar desde cuentas con `id_plan_cuenta IS NULL` como fallback.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        conn.execute("PRAGMA busy_timeout=5000")
        cur = conn.cursor()

        # Verificar cantidad de origen
        cur.execute("SELECT COUNT(*) FROM cuenta_contable WHERE id_plan_cuenta = ?", (origen_id,))
        count_origen = cur.fetchone()[0]

        if count_origen and count_origen > 0:
            cur.execute(
                """
                INSERT INTO cuenta_contable (id_generico, descripcion, nombre_cuenta, codigo_cuenta, id_plan_cuenta)
                SELECT id_generico, descripcion, nombre_cuenta, codigo_cuenta, ?
                FROM cuenta_contable
                WHERE id_plan_cuenta = ?
                """,
                (destino_id, origen_id)
            )
            conn.commit()
            return cur.rowcount or 0
        else:
            # Fallback: copiar desde cuentas sin plan asignado
            cur.execute("SELECT COUNT(*) FROM cuenta_contable WHERE id_plan_cuenta IS NULL")
            count_null = cur.fetchone()[0]
            if origen_id == 0 and count_null and count_null > 0:
                cur.execute(
                    """
                    INSERT INTO cuenta_contable (id_generico, descripcion, nombre_cuenta, codigo_cuenta, id_plan_cuenta)
                    SELECT id_generico, descripcion, nombre_cuenta, codigo_cuenta, ?
                    FROM cuenta_contable
                    WHERE id_plan_cuenta IS NULL
                    """,
                    (destino_id,)
                )
                conn.commit()
                return cur.rowcount or 0
        return 0
    except Error as e:
        print(f"Error copiando cuentas de plan {origen_id} a {destino_id}: {e}")
        return 0
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
