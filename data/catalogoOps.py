import sqlite3
from typing import Tuple


def _split_codigo(numero: str):
    partes = (numero or "").split(".")
    if len(partes) != 4:
        return None
    return partes


def actualizar_tipo_cuenta(db_path: str, id_tipo_cuenta: int, nombre: str, numero: str) -> bool:
    """Actualiza nombre y número de un tipo de cuenta y propaga a rubros/genéricos/cuentas."""
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT numero_cuenta FROM tipo_cuenta WHERE id_tipo_cuenta = ?", (id_tipo_cuenta,))
            old_num = (cur.fetchone() or [""])[0]

            cur.execute(
                "UPDATE tipo_cuenta SET nombre_tipo_cuenta = ?, numero_cuenta = ? WHERE id_tipo_cuenta = ?",
                (nombre.strip(), numero.strip(), id_tipo_cuenta),
            )

            old_parts = _split_codigo(old_num)
            new_parts = _split_codigo(numero.strip())
            if old_parts and new_parts:
                old_seg1 = old_parts[0]
                new_seg1 = new_parts[0]

                # Actualizar rubros del tipo
                cur.execute("SELECT id_rubro, numero_cuenta FROM rubro WHERE id_tipo_cuenta = ?", (id_tipo_cuenta,))
                rubros = cur.fetchall()
                for rid, rnum in rubros:
                    rparts = _split_codigo(rnum)
                    if not rparts:
                        continue
                    rparts[0] = new_seg1
                    new_rnum = ".".join(rparts)
                    cur.execute("UPDATE rubro SET numero_cuenta = ? WHERE id_rubro = ?", (new_rnum, rid))

                # Actualizar genéricos y cuentas ligados a esos rubros
                cur.execute(
                    """
                    SELECT g.id_generico, g.numero_cuenta
                    FROM generico g
                    JOIN rubro r ON r.id_rubro = g.id_rubro
                    WHERE r.id_tipo_cuenta = ?
                    """,
                    (id_tipo_cuenta,),
                )
                genericos = cur.fetchall()
                for gid, gnum in genericos:
                    gparts = _split_codigo(gnum)
                    if not gparts:
                        continue
                    gparts[0] = new_seg1
                    new_gnum = ".".join(gparts)
                    cur.execute("UPDATE generico SET numero_cuenta = ? WHERE id_generico = ?", (new_gnum, gid))

                    # Cuentas contables del genérico
                    cur.execute("SELECT id_cuenta_contable, codigo_cuenta FROM cuenta_contable WHERE id_generico = ?", (gid,))
                    cuentas = cur.fetchall()
                    for cid, cnum in cuentas:
                        cparts = _split_codigo(cnum)
                        if not cparts:
                            continue
                        cparts[0] = new_seg1
                        new_cnum = ".".join(cparts)
                        cur.execute("UPDATE cuenta_contable SET codigo_cuenta = ? WHERE id_cuenta_contable = ?", (new_cnum, cid))

            conn.commit()
            return cur.rowcount > 0
    except Exception as ex:
        print(f"Error actualizando tipo_cuenta {id_tipo_cuenta}: {ex}")
        return False


def actualizar_rubro(db_path: str, id_rubro: int, nombre: str, numero: str, id_tipo_cuenta: int | None = None) -> bool:
    """Actualiza nombre, número y (opcional) tipo de un rubro. Propaga a genéricos/cuentas."""
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT numero_cuenta FROM rubro WHERE id_rubro = ?", (id_rubro,))
            old_num = (cur.fetchone() or [""])[0]

            if id_tipo_cuenta is None:
                cur.execute(
                    "UPDATE rubro SET nombre_rubro = ?, numero_cuenta = ? WHERE id_rubro = ?",
                    (nombre.strip(), numero.strip(), id_rubro),
                )
            else:
                cur.execute(
                    "UPDATE rubro SET nombre_rubro = ?, numero_cuenta = ?, id_tipo_cuenta = ? WHERE id_rubro = ?",
                    (nombre.strip(), numero.strip(), int(id_tipo_cuenta), id_rubro),
                )

            old_parts = _split_codigo(old_num)
            new_parts = _split_codigo(numero.strip())
            if old_parts and new_parts:
                new_seg1, new_seg2 = new_parts[0], new_parts[1]

                cur.execute("SELECT id_generico, numero_cuenta FROM generico WHERE id_rubro = ?", (id_rubro,))
                genericos = cur.fetchall()
                for gid, gnum in genericos:
                    gparts = _split_codigo(gnum)
                    if not gparts:
                        continue
                    gparts[0] = new_seg1
                    gparts[1] = new_seg2
                    new_gnum = ".".join(gparts)
                    cur.execute("UPDATE generico SET numero_cuenta = ? WHERE id_generico = ?", (new_gnum, gid))

                    cur.execute("SELECT id_cuenta_contable, codigo_cuenta FROM cuenta_contable WHERE id_generico = ?", (gid,))
                    cuentas = cur.fetchall()
                    for cid, cnum in cuentas:
                        cparts = _split_codigo(cnum)
                        if not cparts:
                            continue
                        cparts[0] = new_seg1
                        cparts[1] = new_seg2
                        new_cnum = ".".join(cparts)
                        cur.execute("UPDATE cuenta_contable SET codigo_cuenta = ? WHERE id_cuenta_contable = ?", (new_cnum, cid))

            conn.commit()
            return cur.rowcount > 0
    except Exception as ex:
        print(f"Error actualizando rubro {id_rubro}: {ex}")
        return False


def actualizar_generico(db_path: str, id_generico: int, nombre: str, numero: str, id_rubro: int | None = None) -> bool:
    """Actualiza nombre, número y (opcional) rubro de un genérico. Propaga a cuentas."""
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT numero_cuenta FROM generico WHERE id_generico = ?", (id_generico,))
            old_num = (cur.fetchone() or [""])[0]

            if id_rubro is None:
                cur.execute(
                    "UPDATE generico SET nombre_generico = ?, numero_cuenta = ? WHERE id_generico = ?",
                    (nombre.strip(), numero.strip(), id_generico),
                )
            else:
                cur.execute(
                    "UPDATE generico SET nombre_generico = ?, numero_cuenta = ?, id_rubro = ? WHERE id_generico = ?",
                    (nombre.strip(), numero.strip(), int(id_rubro), id_generico),
                )

            old_parts = _split_codigo(old_num)
            new_parts = _split_codigo(numero.strip())
            if old_parts and new_parts:
                new_seg1, new_seg2, new_seg3 = new_parts[0], new_parts[1], new_parts[2]
                cur.execute("SELECT id_cuenta_contable, codigo_cuenta FROM cuenta_contable WHERE id_generico = ?", (id_generico,))
                cuentas = cur.fetchall()
                for cid, cnum in cuentas:
                    cparts = _split_codigo(cnum)
                    if not cparts:
                        continue
                    cparts[0] = new_seg1
                    cparts[1] = new_seg2
                    cparts[2] = new_seg3
                    new_cnum = ".".join(cparts)
                    cur.execute("UPDATE cuenta_contable SET codigo_cuenta = ? WHERE id_cuenta_contable = ?", (new_cnum, cid))

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
