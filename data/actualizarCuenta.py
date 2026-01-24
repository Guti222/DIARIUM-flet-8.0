import sqlite3
from sqlite3 import Error

def actualizar_cuenta_contable(db_path: str, id_cuenta_contable: int, id_generico: int, descripcion: str, nombre_cuenta: str, codigo_cuenta: str) -> bool:
    """Actualiza una cuenta contable existente.

    Devuelve True si la actualización fue exitosa, False en caso contrario.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=5)
        conn.execute("PRAGMA busy_timeout=3000")
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE cuenta_contable
                   SET id_generico = ?, descripcion = ?, nombre_cuenta = ?, codigo_cuenta = ?
                 WHERE id_cuenta_contable = ?""",
            (id_generico, descripcion, nombre_cuenta, codigo_cuenta, id_cuenta_contable)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error actualizando cuenta contable: {e}")
        return False
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
