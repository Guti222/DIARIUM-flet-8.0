import sqlite3
from typing import List, Dict, Any, Tuple

def obtenerAsientosDeLibro(db_path: str, id_libro_diario: int) -> List[Tuple]:
    """
    Devuelve todas las líneas de asientos de un libro, unidas con su cuenta.
    Cada fila incluye:
      (id_asiento, numero_asiento, fecha, descripcion, codigo_cuenta, nombre_cuenta, debe, haber)
    Ordenadas por fecha e id_asiento.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.id_asiento, a.numero_asiento, a.fecha, a.descripcion,
                   c.codigo_cuenta, c.nombre_cuenta,
                   la.debe, la.haber
            FROM asiento a
            JOIN linea_asiento la ON la.id_asiento = a.id_asiento
            JOIN cuenta_contable c ON c.id_cuenta_contable = la.id_cuenta_contable
            WHERE a.id_libro_diario = ?
            ORDER BY a.fecha ASC, a.id_asiento ASC
            """,
            (id_libro_diario,)
        )
        return cur.fetchall() or []
    except Exception:
        return []
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def obtenerResumenAsientos(db_path: str, id_libro_diario: int) -> List[Dict[str, Any]]:
    """
    Devuelve resumen por asiento: totales debe/haber y conteo de líneas.
    Estructura: {id_asiento, fecha, descripcion, total_debe, total_haber, lineas}
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.id_asiento, a.fecha, a.descripcion,
                   COALESCE(SUM(la.debe),0) AS total_debe,
                   COALESCE(SUM(la.haber),0) AS total_haber,
                   COUNT(la.id_linea_asiento) AS lineas
            FROM asiento a
            LEFT JOIN linea_asiento la ON la.id_asiento = a.id_asiento
            WHERE a.id_libro_diario = ?
            GROUP BY a.id_asiento, a.fecha, a.descripcion
            ORDER BY a.fecha ASC, a.id_asiento ASC
            """,
            (id_libro_diario,)
        )
        rows = cur.fetchall() or []
        return [
            {
                "id_asiento": r[0],
                "fecha": r[1],
                "descripcion": r[2],
                "total_debe": float(r[3] or 0),
                "total_haber": float(r[4] or 0),
                "lineas": int(r[5] or 0),
            }
            for r in rows
        ]
    except Exception:
        return []
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
