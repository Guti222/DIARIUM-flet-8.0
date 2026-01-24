import sqlite3
from sqlite3 import Error

def eliminar_cuenta_contable(db_path: str, id_cuenta_contable: int) -> bool:
    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=5)
        conn.execute("PRAGMA busy_timeout=3000")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cuenta_contable WHERE id_cuenta_contable = ?", (id_cuenta_contable,))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error eliminando cuenta contable: {e}")
        return False
    finally:
        if conn:
            try: conn.close()
            except Exception: pass
