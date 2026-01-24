import sqlite3
from sqlite3 import Error
from data.models.mes import Mes
from src.utils.paths import get_db_path

def obtenerMeses() -> list[Mes]:
    conn=None
    
    try:
        conn=sqlite3.connect(get_db_path())
        cursor=conn.cursor()
        cursor.execute("SELECT id_mes, nombre_mes FROM mes")
        rows=cursor.fetchall()
        
        meses = [Mes(id_mes=row[0], nombre_mes=row[1]) for row in rows]
        
    except Error as e:
        print(f"Database error: {e}")
        meses = []
        
    finally:
        if conn:
            conn.close()
            
    return meses