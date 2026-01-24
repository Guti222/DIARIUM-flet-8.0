import sqlite3
from sqlite3 import Error
from typing import List
from data.models.lineaAsiento import LineaAsiento
from data.models.cuenta import CuentaContable


def obtenerLineasPorAsiento(db_path: str, id_asiento: int) -> List[LineaAsiento]:
	"""Obtiene las líneas de asiento para un `id_asiento` dado.

	Devuelve una lista de objetos `LineaAsiento` con la propiedad
	`cuenta_contable` rellenada con los datos básicos (id, id_generico,
	descripcion, nombre_cuenta, codigo_cuenta).
	"""
	lineas: List[LineaAsiento] = []
	conn = None
	try:
		conn = sqlite3.connect(db_path)
		cursor = conn.cursor()
		cursor.execute(
			"SELECT id_linea_asiento, id_asiento, id_cuenta_contable, debe, haber FROM linea_asiento WHERE id_asiento = ?",
			(id_asiento,)
		)
		rows = cursor.fetchall()
		for row in rows:
			id_linea, id_asiento_row, id_cuenta, debe, haber = row

			# Obtener datos básicos de la cuenta vinculada
			cursor.execute(
				"SELECT id_cuenta_contable, id_generico, descripcion, nombre_cuenta, codigo_cuenta FROM cuenta_contable WHERE id_cuenta_contable = ?",
				(id_cuenta,)
			)
			crow = cursor.fetchone()
			if crow:
				cuenta = CuentaContable(
					id_cuenta_contable=crow[0],
					id_generico=crow[1],
					descripcion=crow[2],
					nombre_cuenta=crow[3],
					codigo_cuenta=crow[4]
				)
			else:
				cuenta = CuentaContable()

			linea = LineaAsiento(
				id_linea_asiento=id_linea,
				id_asiento=id_asiento_row,
				id_cuenta_contable=id_cuenta,
				debe=debe,
				haber=haber,
				cuenta_contable=cuenta,
			)
			lineas.append(linea)

	except Error as e:
		print(f"Database error obtaining lineas for asiento {id_asiento}: {e}")
	finally:
		if conn:
			conn.close()

	return lineas

def obtenerAsientosPorCuenta(db_path: str, id_cuenta_contable: int) -> List[LineaAsiento]:
    """Obtiene las líneas de asiento asociadas a una cuenta contable específica.

    Devuelve una lista de objetos `LineaAsiento` que pertenecen a la cuenta
    contable indicada por `id_cuenta_contable`.
    """
    lineas: List[LineaAsiento] = []
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_linea_asiento, id_asiento, id_cuenta_contable, debe, haber FROM linea_asiento WHERE id_cuenta_contable = ?",
            (id_cuenta_contable,)
        )
        rows = cursor.fetchall()
        for row in rows:
            id_linea, id_asiento_row, id_cuenta, debe, haber = row

            # Obtener datos básicos de la cuenta vinculada
            cursor.execute(
                "SELECT id_cuenta_contable, id_generico, descripcion, nombre_cuenta, codigo_cuenta FROM cuenta_contable WHERE id_cuenta_contable = ?",
                (id_cuenta,)
            )
            crow = cursor.fetchone()
            if crow:
                cuenta = CuentaContable(
                    id_cuenta_contable=crow[0],
                    id_generico=crow[1],
                    descripcion=crow[2],
                    nombre_cuenta=crow[3],
                    codigo_cuenta=crow[4]
                )
            else:
                cuenta = CuentaContable()

            linea = LineaAsiento(
                id_linea_asiento=id_linea,
                id_asiento=id_asiento_row,
                id_cuenta_contable=id_cuenta,
                debe=debe,
                haber=haber,
                cuenta_contable=cuenta,
            )
            lineas.append(linea)

    except Error as e:
        print(f"Database error obtaining lineas for cuenta {id_cuenta_contable}: {e}")
    finally:
        if conn:
            conn.close()

    return lineas