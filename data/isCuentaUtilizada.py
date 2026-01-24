import sqlite3

def is_cuenta_utilizada(db_path: str, id_cuenta_contable: int) -> bool:
    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=5)
        conn.execute("PRAGMA busy_timeout=3000")
        cursor = conn.cursor()
        
        # Check in transactions table
        cursor.execute("SELECT 1 FROM linea_asiento WHERE id_cuenta_contable = ? LIMIT 1", (id_cuenta_contable,))
        if cursor.fetchone():
            return True
        
        return False
    except sqlite3.Error as e:
        print(f"Error checking cuenta contable usage: {e}")
        return False
    finally:
        if conn:
            try: conn.close()
            except Exception: pass