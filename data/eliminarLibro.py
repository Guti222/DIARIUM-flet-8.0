import sqlite3
from sqlite3 import Error

def eliminar_libro_diario(db_path: str, id_libro_diario: int) -> bool:
    """
    Elimina un libro diario y todas sus dependencias (asientos y líneas de asiento).
    Retorna True si se eliminó el libro, False en caso contrario.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=5)
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=3000")
        cursor = conn.cursor()

        # 1) Eliminar líneas de asientos de los asientos de este libro
        cursor.execute(
            "DELETE FROM linea_asiento WHERE id_asiento IN (SELECT id_asiento FROM asiento WHERE id_libro_diario = ?)",
            (id_libro_diario,)
        )
        # 2) Eliminar asientos del libro
        cursor.execute(
            "DELETE FROM asiento WHERE id_libro_diario = ?",
            (id_libro_diario,)
        )
        # 3) Eliminar el libro
        cursor.execute(
            "DELETE FROM libro_diario WHERE id_libro_diario = ?",
            (id_libro_diario,)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error eliminando libro diario: {e}")
        return False
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
