import sqlite3
from sqlite3 import Error

from data.models.libro import LibroDiario

def obtenerTodosLibros(nombre_bd: str) -> list[LibroDiario]:
    conn = None
    try:
        conn = sqlite3.connect(nombre_bd)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_libro_diario, id_mes, ano, nombre_empresa, contador, total_debe, total_haber, COALESCE(origen,'creado'), fecha_importacion FROM libro_diario"
        )
        return [LibroDiario(
            id_libro_diario=row[0],
            id_mes=row[1],
            ano=row[2],
            nombre_empresa=row[3],
            contador=row[4],
            total_debe=row[5],
            total_haber=row[6],
            origen=row[7],
            fecha_importacion=row[8]
        ) for row in cursor.fetchall()]
    
    except Error as e:
        print(f"Database error: {e}")
        return []
    
    finally:
        if conn:
            conn.close()
            
def obtenerLibroPorId(nombre_bd: str, id_libro_diario: int) -> LibroDiario | None:
    conn = None
    try:
        conn = sqlite3.connect(nombre_bd)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_libro_diario, id_mes, ano, nombre_empresa, contador, total_debe, total_haber, COALESCE(origen,'creado'), fecha_importacion FROM libro_diario WHERE id_libro_diario = ?", 
            (id_libro_diario,)
        )
        row = cursor.fetchone()
        
        if row:
            return LibroDiario(
                id_libro_diario=row[0],
                id_mes=row[1],
                ano=row[2],
                nombre_empresa=row[3],
                contador=row[4],
                total_debe=row[5],
                total_haber=row[6],
                origen=row[7],
                fecha_importacion=row[8]
            )
        return None

    except Error as e:
        print(f"Database error: {e}")
        return None
    
    finally:
        if conn:
            conn.close()