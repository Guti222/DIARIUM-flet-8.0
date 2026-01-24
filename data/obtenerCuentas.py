import sys
import os
# Agregar el directorio raíz del proyecto al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from sqlite3 import Error
from typing import List, Optional
from data.models.cuenta import CuentaContable, Generico, Rubro, TipoCuenta

def obtenerTodasTipoCuentas(nombre_bd: str) -> List[TipoCuenta]:
    conn = None
    try:
        conn = sqlite3.connect(nombre_bd)
        cursor = conn.cursor()
        cursor.execute("SELECT id_tipo_cuenta, nombre_tipo_cuenta FROM tipo_cuenta")
        return [TipoCuenta(id_tipo_cuenta=row[0], nombre_tipo_cuenta=row[1]) for row in cursor.fetchall()]
    
    except Error as e:
        print(f"Database error: {e}")
        return []
    
    finally:
        if conn:
            conn.close()

def obtenerTipoCuenta(nombre_bd: str, id_tipo_cuenta: int) -> Optional[TipoCuenta]:
    conn = None
    try:
        conn = sqlite3.connect(nombre_bd)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_tipo_cuenta, nombre_tipo_cuenta FROM tipo_cuenta WHERE id_tipo_cuenta = ?", 
            (id_tipo_cuenta,)
        )
        row = cursor.fetchone()
        
        if row:
            return TipoCuenta(id_tipo_cuenta=row[0], nombre_tipo_cuenta=row[1])
        return None

    except Error as e:
        print(f"Database error: {e}")
        return None  # Cambiado de [] a None para coincidir con el tipo de retorno
    
    finally:
        if conn:
            conn.close()

def obtenerTodosRubroPorTipoCuenta(nombre_bd: str, id_tipo_cuenta: int) -> List[Rubro]:
    conn = None
    try:
        conn = sqlite3.connect(nombre_bd)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_rubro, id_tipo_cuenta, nombre_rubro FROM rubro WHERE id_tipo_cuenta = ?", 
            (id_tipo_cuenta,)
        )
        return [Rubro(id_rubro=row[0], id_tipo_cuenta=row[1], nombre_rubro=row[2]) for row in cursor.fetchall()]
    
    except Error as e:
        print(f"Database error: {e}")
        return []
    
    finally:
        if conn:
            conn.close()

def obtenerTodosGenericoPorRubro(nombre_bd: str, id_rubro: int) -> List[Generico]:
    conn = None
    try:
        conn = sqlite3.connect(nombre_bd)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_generico, id_rubro, nombre_generico FROM generico WHERE id_rubro = ?", 
            (id_rubro,)
        )
        return [Generico(id_generico=row[0], id_rubro=row[1], nombre_generico=row[2]) for row in cursor.fetchall()]
    
    except Error as e:
        print(f"Database error: {e}")
        return []
    
    finally:
        if conn:
            conn.close()

# CORRECCIÓN IMPORTANTE: Estabas creando objetos Generico en lugar de CuentaContable
def obtenerTodasCuentasPorGenerico(nombre_bd: str, id_generico: int) -> List[CuentaContable]:
    conn = None
    try:
        conn = sqlite3.connect(nombre_bd)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_cuenta_contable, id_generico, nombre_cuenta, descripcion, codigo_cuenta FROM cuenta_contable WHERE id_generico = ?", 
            (id_generico,)
        )
        # CORREGIDO: Crear CuentaContable en lugar de Generico
        return [CuentaContable(
            id_cuenta_contable=row[0], 
            id_generico=row[1], 
            nombre_cuenta=row[2], 
            descripcion=row[3], 
            codigo_cuenta=row[4]
        ) for row in cursor.fetchall()]
    
    except Error as e:
        print(f"Database error: {e}")
        return []
    
    finally:
        if conn:
            conn.close()
            
def obtenerTodasCuentasContables(nombre_bd: str) -> List[CuentaContable]:
    conn = None
    try:
        conn = sqlite3.connect(nombre_bd)
        cursor = conn.cursor()
        # Para mostrar información jerárquica (tipo/rubro/generico)
        # cargamos primero los mapas de TipoCuenta, Rubro y Generico
        cursor.execute("SELECT id_tipo_cuenta, nombre_tipo_cuenta FROM tipo_cuenta")
        tipos = {row[0]: TipoCuenta(id_tipo_cuenta=row[0], nombre_tipo_cuenta=row[1]) for row in cursor.fetchall()}

        cursor.execute("SELECT id_rubro, id_tipo_cuenta, nombre_rubro FROM rubro")
        rubros = {}
        for row in cursor.fetchall():
            id_rubro, id_tipo_cuenta, nombre_rubro = row
            rubro = Rubro(id_rubro=id_rubro, id_tipo_cuenta=id_tipo_cuenta, nombre_rubro=nombre_rubro)
            # enlazar tipo si existe
            rubro.tipo_cuenta = tipos.get(id_tipo_cuenta)
            rubros[id_rubro] = rubro

        cursor.execute("SELECT id_generico, id_rubro, nombre_generico FROM generico")
        genericos = {}
        for row in cursor.fetchall():
            id_generico, id_rubro, nombre_generico = row
            generico = Generico(id_generico=id_generico, id_rubro=id_rubro, nombre_generico=nombre_generico)
            # enlazar rubro si existe
            generico.rubro = rubros.get(id_rubro)
            genericos[id_generico] = generico

        # Finalmente cargar las cuentas y asignar el genérico (y con ello
        # la cadena de relaciones hasta TipoCuenta).
        cursor.execute("SELECT id_cuenta_contable, id_generico, nombre_cuenta, descripcion, codigo_cuenta FROM cuenta_contable")
        cuentas = []
        for row in cursor.fetchall():
            id_cuenta_contable, id_generico, nombre_cuenta, descripcion, codigo_cuenta = row
            cuenta = CuentaContable(
                id_cuenta_contable=id_cuenta_contable,
                id_generico=id_generico,
                nombre_cuenta=nombre_cuenta,
                descripcion=descripcion,
                codigo_cuenta=codigo_cuenta,
            )
            # enlazar generico si existe
            if id_generico in genericos:
                cuenta.generico = genericos[id_generico]
            cuentas.append(cuenta)

        return cuentas
    
    except Error as e:
        print(f"Database error: {e}")
        return []
    
    finally:
        if conn:
            conn.close()
            
# Nota: no ejecutar código en la importación del módulo; las llamadas a
# funciones de acceso a datos deben hacerse desde la lógica de la app.

def obtenerCuentasContablesPorPlanCuenta(nombre_bd: str, id_plan_cuenta: int) -> List[CuentaContable]:
    """Obtiene cuentas contables filtradas por plan de cuenta incluyendo relaciones jerárquicas.

    Carga mapas de TipoCuenta, Rubro y Generico para enlazar cada CuentaContable y permitir
    acceder a propiedades derivadas (ruta_completa, nombre_rubro, etc.).
    """
    conn = None
    try:
        conn = sqlite3.connect(nombre_bd)
        cursor = conn.cursor()

        # Mapas de tipos
        cursor.execute("SELECT id_tipo_cuenta, nombre_tipo_cuenta FROM tipo_cuenta")
        tipos = {row[0]: TipoCuenta(id_tipo_cuenta=row[0], nombre_tipo_cuenta=row[1]) for row in cursor.fetchall()}

        # Mapas de rubros
        cursor.execute("SELECT id_rubro, id_tipo_cuenta, nombre_rubro FROM rubro")
        rubros = {}
        for row in cursor.fetchall():
            r = Rubro(id_rubro=row[0], id_tipo_cuenta=row[1], nombre_rubro=row[2])
            r.tipo_cuenta = tipos.get(row[1])
            rubros[row[0]] = r

        # Mapas de genéricos
        cursor.execute("SELECT id_generico, id_rubro, nombre_generico FROM generico")
        genericos = {}
        for row in cursor.fetchall():
            g = Generico(id_generico=row[0], id_rubro=row[1], nombre_generico=row[2])
            g.rubro = rubros.get(row[1])
            genericos[row[0]] = g

        # Cuentas filtradas por plan
        cursor.execute(
            """
            SELECT id_cuenta_contable, id_generico, nombre_cuenta, descripcion, codigo_cuenta
            FROM cuenta_contable
            WHERE id_plan_cuenta = ?
            """,
            (id_plan_cuenta,)
        )
        cuentas = []
        for row in cursor.fetchall():
            cuenta = CuentaContable(
                id_cuenta_contable=row[0],
                id_generico=row[1],
                nombre_cuenta=row[2],
                descripcion=row[3],
                codigo_cuenta=row[4]
            )
            if row[1] in genericos:
                cuenta.generico = genericos[row[1]]
            cuentas.append(cuenta)
        return cuentas
    except Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

# Alias para mantener compatibilidad con el nombre anterior (typo singular/plural)
def obtenerCuentaContablesPorPlanCuenta(nombre_bd: str, id_plan_cuenta: int) -> List[CuentaContable]:
    return obtenerCuentasContablesPorPlanCuenta(nombre_bd, id_plan_cuenta)

def obtenerCuentasContablesGenerales(nombre_bd: str) -> List[CuentaContable]:
    """
    Obtiene cuentas del plan 'General': id_plan_cuenta = 0 o NULL.
    Incluye relaciones (tipo, rubro, genérico) para UI.
    """
    conn = None
    try:
        conn = sqlite3.connect(nombre_bd)
        cursor = conn.cursor()

        # Mapas de tipos
        cursor.execute("SELECT id_tipo_cuenta, nombre_tipo_cuenta FROM tipo_cuenta")
        tipos = {row[0]: TipoCuenta(id_tipo_cuenta=row[0], nombre_tipo_cuenta=row[1]) for row in cursor.fetchall()}

        # Mapas de rubros
        cursor.execute("SELECT id_rubro, id_tipo_cuenta, nombre_rubro FROM rubro")
        rubros = {}
        for row in cursor.fetchall():
            r = Rubro(id_rubro=row[0], id_tipo_cuenta=row[1], nombre_rubro=row[2])
            r.tipo_cuenta = tipos.get(row[1])
            rubros[row[0]] = r

        # Mapas de genéricos
        cursor.execute("SELECT id_generico, id_rubro, nombre_generico FROM generico")
        genericos = {}
        for row in cursor.fetchall():
            g = Generico(id_generico=row[0], id_rubro=row[1], nombre_generico=row[2])
            g.rubro = rubros.get(row[1])
            genericos[row[0]] = g

        # Cuentas del plan general (id=0) o sin asignación (NULL)
        cursor.execute(
            """
            SELECT id_cuenta_contable, id_generico, nombre_cuenta, descripcion, codigo_cuenta
            FROM cuenta_contable
            WHERE id_plan_cuenta = 0 OR id_plan_cuenta IS NULL
            ORDER BY codigo_cuenta ASC
            """
        )
        cuentas: List[CuentaContable] = []
        for row in cursor.fetchall():
            cuenta = CuentaContable(
                id_cuenta_contable=row[0],
                id_generico=row[1],
                nombre_cuenta=row[2],
                descripcion=row[3],
                codigo_cuenta=row[4],
            )
            if row[1] in genericos:
                cuenta.generico = genericos[row[1]]
            cuentas.append(cuenta)
        return cuentas
    except Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()
            
            

