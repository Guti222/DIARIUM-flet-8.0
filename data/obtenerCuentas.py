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
        cursor.execute("SELECT id_tipo_cuenta, nombre_tipo_cuenta, numero_cuenta FROM tipo_cuenta")
        return [TipoCuenta(id_tipo_cuenta=row[0], nombre_tipo_cuenta=row[1], numero_cuenta=row[2]) for row in cursor.fetchall()]
    
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
            "SELECT id_tipo_cuenta, nombre_tipo_cuenta, numero_cuenta FROM tipo_cuenta WHERE id_tipo_cuenta = ?", 
            (id_tipo_cuenta,)
        )
        row = cursor.fetchone()
        
        if row:
            return TipoCuenta(id_tipo_cuenta=row[0], nombre_tipo_cuenta=row[1], numero_cuenta=row[2])
        return None

    except Error as e:
        print(f"Database error: {e}")
        return None
    
    finally:
        if conn:
            conn.close()


def obtenerTodosRubroPorTipoCuenta(nombre_bd: str, id_tipo_cuenta: int) -> List[Rubro]:
    conn = None
    try:
        conn = sqlite3.connect(nombre_bd)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_rubro, id_tipo_cuenta, nombre_rubro, numero_cuenta FROM rubro WHERE id_tipo_cuenta = ?", 
            (id_tipo_cuenta,)
        )
        return [Rubro(id_rubro=row[0], id_tipo_cuenta=row[1], nombre_rubro=row[2], numero_cuenta=row[3]) for row in cursor.fetchall()]
    
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
            "SELECT id_generico, id_rubro, nombre_generico, numero_cuenta FROM generico WHERE id_rubro = ?", 
            (id_rubro,)
        )
        return [Generico(id_generico=row[0], id_rubro=row[1], nombre_generico=row[2], numero_cuenta=row[3]) for row in cursor.fetchall()]
    
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
        cursor.execute("SELECT id_tipo_cuenta, nombre_tipo_cuenta, numero_cuenta FROM tipo_cuenta")
        tipos = {row[0]: TipoCuenta(id_tipo_cuenta=row[0], nombre_tipo_cuenta=row[1], numero_cuenta=row[2]) for row in cursor.fetchall()}

        cursor.execute("SELECT id_rubro, id_tipo_cuenta, nombre_rubro, numero_cuenta FROM rubro")
        rubros = {}
        for row in cursor.fetchall():
            id_rubro, id_tipo_cuenta, nombre_rubro, numero_cuenta = row
            rubro = Rubro(id_rubro=id_rubro, id_tipo_cuenta=id_tipo_cuenta, nombre_rubro=nombre_rubro, numero_cuenta=numero_cuenta)
            # enlazar tipo si existe
            rubro.tipo_cuenta = tipos.get(id_tipo_cuenta)
            rubros[id_rubro] = rubro

        cursor.execute("SELECT id_generico, id_rubro, nombre_generico, numero_cuenta FROM generico")
        genericos = {}
        for row in cursor.fetchall():
            id_generico, id_rubro, nombre_generico, numero_cuenta = row
            generico = Generico(id_generico=id_generico, id_rubro=id_rubro, nombre_generico=nombre_generico, numero_cuenta=numero_cuenta)
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
    """Obtiene cuentas contables filtradas por plan de cuenta usando la relación
    tipo_cuenta -> rubro -> generico -> cuenta_contable. """
    conn = None
    try:
        conn = sqlite3.connect(nombre_bd)
        cursor = conn.cursor()

        # Mapas de tipos del plan
        cursor.execute(
            "SELECT id_tipo_cuenta, nombre_tipo_cuenta, numero_cuenta FROM tipo_cuenta WHERE id_plan_cuenta = ?",
            (id_plan_cuenta,)
        )
        tipos = {row[0]: TipoCuenta(id_tipo_cuenta=row[0], nombre_tipo_cuenta=row[1], numero_cuenta=row[2]) for row in cursor.fetchall()}

        if not tipos:
            return []

        # Rubros vinculados a los tipos del plan
        cursor.execute(
            "SELECT id_rubro, id_tipo_cuenta, nombre_rubro, numero_cuenta FROM rubro WHERE id_tipo_cuenta IN (" + ",".join([str(tid) for tid in tipos.keys()]) + ")"
        )
        rubros = {}
        for row in cursor.fetchall():
            r = Rubro(id_rubro=row[0], id_tipo_cuenta=row[1], nombre_rubro=row[2], numero_cuenta=row[3])
            r.tipo_cuenta = tipos.get(row[1])
            rubros[row[0]] = r

        # Genéricos vinculados a esos rubros
        if rubros:
            cursor.execute(
                "SELECT id_generico, id_rubro, nombre_generico, numero_cuenta FROM generico WHERE id_rubro IN (" + ",".join([str(rid) for rid in rubros.keys()]) + ")"
            )
        else:
            cursor.execute("SELECT id_generico, id_rubro, nombre_generico, numero_cuenta FROM generico WHERE 1=0")
        genericos = {}
        for row in cursor.fetchall():
            g = Generico(id_generico=row[0], id_rubro=row[1], nombre_generico=row[2], numero_cuenta=row[3])
            g.rubro = rubros.get(row[1])
            genericos[row[0]] = g

        # Cuentas cuyo genérico pertenece al plan
        if genericos:
            cursor.execute(
                "SELECT id_cuenta_contable, id_generico, nombre_cuenta, descripcion, codigo_cuenta FROM cuenta_contable WHERE id_generico IN (" + ",".join([str(gid) for gid in genericos.keys()]) + ")"
            )
        else:
            cursor.execute("SELECT id_cuenta_contable, id_generico, nombre_cuenta, descripcion, codigo_cuenta FROM cuenta_contable WHERE 1=0")

        cuentas = []
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

# Alias para mantener compatibilidad con el nombre anterior (typo singular/plural)
def obtenerCuentaContablesPorPlanCuenta(nombre_bd: str, id_plan_cuenta: int) -> List[CuentaContable]:
    return obtenerCuentasContablesPorPlanCuenta(nombre_bd, id_plan_cuenta)

def obtenerCuentasContablesGenerales(nombre_bd: str) -> List[CuentaContable]:
    """
    Obtiene cuentas del plan 'General': tipos con id_plan_cuenta = 0.
    Incluye relaciones (tipo, rubro, genérico) para UI.
    """
    conn = None
    try:
        conn = sqlite3.connect(nombre_bd)
        cursor = conn.cursor()

        # Tipos del plan general (id_plan_cuenta = 0)
        cursor.execute("SELECT id_tipo_cuenta, nombre_tipo_cuenta, numero_cuenta FROM tipo_cuenta WHERE id_plan_cuenta = 0")
        tipos = {row[0]: TipoCuenta(id_tipo_cuenta=row[0], nombre_tipo_cuenta=row[1], numero_cuenta=row[2]) for row in cursor.fetchall()}

        if not tipos:
            return []

        # Rubros asociados
        cursor.execute(
            "SELECT id_rubro, id_tipo_cuenta, nombre_rubro, numero_cuenta FROM rubro WHERE id_tipo_cuenta IN (" + ",".join([str(tid) for tid in tipos.keys()]) + ")"
        )
        rubros = {}
        for row in cursor.fetchall():
            r = Rubro(id_rubro=row[0], id_tipo_cuenta=row[1], nombre_rubro=row[2], numero_cuenta=row[3])
            r.tipo_cuenta = tipos.get(row[1])
            rubros[row[0]] = r

        # Genéricos asociados
        if rubros:
            cursor.execute(
                "SELECT id_generico, id_rubro, nombre_generico, numero_cuenta FROM generico WHERE id_rubro IN (" + ",".join([str(rid) for rid in rubros.keys()]) + ")"
            )
        else:
            cursor.execute("SELECT id_generico, id_rubro, nombre_generico, numero_cuenta FROM generico WHERE 1=0")
        genericos = {}
        for row in cursor.fetchall():
            g = Generico(id_generico=row[0], id_rubro=row[1], nombre_generico=row[2], numero_cuenta=row[3])
            g.rubro = rubros.get(row[1])
            genericos[row[0]] = g

        # Cuentas cuyo genérico pertenece al plan general
        if genericos:
            cursor.execute(
                "SELECT id_cuenta_contable, id_generico, nombre_cuenta, descripcion, codigo_cuenta FROM cuenta_contable WHERE id_generico IN (" + ",".join([str(gid) for gid in genericos.keys()]) + ") ORDER BY codigo_cuenta ASC"
            )
        else:
            cursor.execute("SELECT id_cuenta_contable, id_generico, nombre_cuenta, descripcion, codigo_cuenta FROM cuenta_contable WHERE 1=0")
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
            
            

