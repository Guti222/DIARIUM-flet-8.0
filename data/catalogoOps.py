import sqlite3
from typing import Tuple


def actualizar_tipo_cuenta(db_path: str, id_tipo_cuenta: int, nombre: str, numero: str) -> bool:
    """Actualiza nombre y número de un tipo de cuenta."""
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE tipo_cuenta SET nombre_tipo_cuenta = ?, numero_cuenta = ? WHERE id_tipo_cuenta = ?",
                (nombre.strip(), numero.strip(), id_tipo_cuenta),
            )
            conn.commit()
            return cur.rowcount > 0
    except Exception as ex:
        print(f"Error actualizando tipo_cuenta {id_tipo_cuenta}: {ex}")
        return False


def actualizar_rubro(db_path: str, id_rubro: int, nombre: str, numero: str) -> bool:
    """Actualiza nombre y número de un rubro."""
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE rubro SET nombre_rubro = ?, numero_cuenta = ? WHERE id_rubro = ?",
                (nombre.strip(), numero.strip(), id_rubro),
            )
            conn.commit()
            return cur.rowcount > 0
    except Exception as ex:
        print(f"Error actualizando rubro {id_rubro}: {ex}")
        return False


def actualizar_generico(db_path: str, id_generico: int, nombre: str, numero: str) -> bool:
    """Actualiza nombre y número de un genérico."""
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE generico SET nombre_generico = ?, numero_cuenta = ? WHERE id_generico = ?",
                (nombre.strip(), numero.strip(), id_generico),
            )
            conn.commit()
            return cur.rowcount > 0
    except Exception as ex:
        print(f"Error actualizando generico {id_generico}: {ex}")
        return False


def eliminar_tipo_cuenta(db_path: str, id_tipo_cuenta: int) -> Tuple[bool, str]:
    """Elimina un tipo de cuenta si no tiene rubros asociados."""
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM rubro WHERE id_tipo_cuenta = ?", (id_tipo_cuenta,))
            if cur.fetchone()[0] > 0:
                return False, "No se puede eliminar: tiene rubros asociados."
            cur.execute("DELETE FROM tipo_cuenta WHERE id_tipo_cuenta = ?", (id_tipo_cuenta,))
            conn.commit()
            return cur.rowcount > 0, "Tipo de cuenta eliminado" if cur.rowcount > 0 else "No se pudo eliminar"
    except Exception as ex:
        print(f"Error eliminando tipo_cuenta {id_tipo_cuenta}: {ex}")
        return False, "Error al eliminar tipo de cuenta"


def eliminar_rubro(db_path: str, id_rubro: int) -> Tuple[bool, str]:
    """Elimina un rubro si no tiene genéricos asociados."""
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM generico WHERE id_rubro = ?", (id_rubro,))
            if cur.fetchone()[0] > 0:
                return False, "No se puede eliminar: tiene genéricos asociados."
            cur.execute("DELETE FROM rubro WHERE id_rubro = ?", (id_rubro,))
            conn.commit()
            return cur.rowcount > 0, "Rubro eliminado" if cur.rowcount > 0 else "No se pudo eliminar"
    except Exception as ex:
        print(f"Error eliminando rubro {id_rubro}: {ex}")
        return False, "Error al eliminar rubro"


def eliminar_generico(db_path: str, id_generico: int) -> Tuple[bool, str]:
    """Elimina un genérico si no tiene cuentas asociadas."""
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM cuenta_contable WHERE id_generico = ?", (id_generico,))
            if cur.fetchone()[0] > 0:
                return False, "No se puede eliminar: tiene cuentas asociadas."
            cur.execute("DELETE FROM generico WHERE id_generico = ?", (id_generico,))
            conn.commit()
            return cur.rowcount > 0, "Genérico eliminado" if cur.rowcount > 0 else "No se pudo eliminar"
    except Exception as ex:
        print(f"Error eliminando generico {id_generico}: {ex}")
        return False, "Error al eliminar genérico"


# Creación de catálogos
def crear_tipo_cuenta(db_path: str, nombre: str, numero: str, id_plan_cuenta: int = 0) -> Tuple[bool, str, int]:
    """Crea un tipo de cuenta en el plan indicado. Retorna (ok, msg, new_id)."""
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO tipo_cuenta (nombre_tipo_cuenta, numero_cuenta, id_plan_cuenta) VALUES (?, ?, ?)",
                (nombre.strip(), numero.strip(), id_plan_cuenta),
            )
            new_id = cur.lastrowid
            conn.commit()
            return True, "Tipo de cuenta creado", int(new_id)
    except Exception as ex:
        print(f"Error creando tipo_cuenta: {ex}")
        return False, "No se pudo crear el tipo de cuenta", 0


def crear_rubro(db_path: str, id_tipo_cuenta: int, nombre: str, numero: str) -> Tuple[bool, str, int]:
    """Crea un rubro asociado a un tipo de cuenta. Retorna (ok, msg, new_id)."""
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO rubro (id_tipo_cuenta, nombre_rubro, numero_cuenta) VALUES (?, ?, ?)",
                (int(id_tipo_cuenta), nombre.strip(), numero.strip()),
            )
            new_id = cur.lastrowid
            conn.commit()
            return True, "Rubro creado", int(new_id)
    except Exception as ex:
        print(f"Error creando rubro: {ex}")
        return False, "No se pudo crear el rubro", 0


def crear_generico(db_path: str, id_rubro: int, nombre: str, numero: str) -> Tuple[bool, str, int]:
    """Crea un genérico asociado a un rubro. Retorna (ok, msg, new_id)."""
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO generico (id_rubro, nombre_generico, numero_cuenta) VALUES (?, ?, ?)",
                (int(id_rubro), nombre.strip(), numero.strip()),
            )
            new_id = cur.lastrowid
            conn.commit()
            return True, "Genérico creado", int(new_id)
    except Exception as ex:
        print(f"Error creando genérico: {ex}")
        return False, "No se pudo crear el genérico", 0
