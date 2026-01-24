import sqlite3
import sys
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

# Ensure project root (parent of src/) is on sys.path so src package resolves
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.utils.paths import get_db_path


def exportar_libro_diario(libro_id: int, output_file: str | Path | None = None) -> Path:
    """Genera un Excel del libro diario indicado por id.

    Devuelve la ruta del archivo generado. Si no hay datos, lanza ValueError.
    """
    bd_path = get_db_path()
    conn = sqlite3.connect(bd_path)
    df = pd.read_sql_query(
        """
        SELECT 
            a.id_libro_diario AS Libro_Diario,
            ld.nombre_empresa,
            ld.contador,
            a.id_asiento AS AsientoID,
            a.fecha AS Fecha,
            cc.codigo_cuenta AS Código,
            cc.descripcion AS Descripción,
            la.debe AS Debe,
            la.haber AS Haber,
            a.descripcion AS Comentario
        FROM linea_asiento la 
        INNER JOIN asiento a ON la.id_asiento=a.id_asiento
        INNER JOIN cuenta_contable cc ON la.id_cuenta_contable = cc.id_cuenta_contable
        INNER JOIN libro_diario ld ON a.id_libro_diario = ld.id_libro_diario
        WHERE a.id_libro_diario = ?
        ORDER BY a.id_asiento, la.id_linea_asiento
        """,
        conn,
        params=(libro_id,),
    )
    conn.close()

    if df.empty:
        raise ValueError("No se encontraron registros para exportar.")

    wb = Workbook()
    ws = wb.active
    ws.title = "Libro Diario"

    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    nombre_empresa = df.iloc[0]["nombre_empresa"]
    contador = df.iloc[0]["contador"]

    ws.insert_rows(1)
    ws.merge_cells("A1:E1")
    cell_title = ws["A1"]
    cell_title.value = f"Libro Diario: Empresa({nombre_empresa}) (Contador: {contador})"
    cell_title.font = Font(bold=True, size=16)
    cell_title.alignment = Alignment(horizontal="center", vertical="center")
    cell_title.fill = PatternFill("solid", fgColor="0C46E6")
    cell_title.border = thin_border

    headers = ["Fecha", "Código", "Descripción", "Debe", "Haber"]
    for col_idx, h in enumerate(headers, start=1):
        cell = ws.cell(row=2, column=col_idx, value=h)
        cell.font = Font(bold=True, size=14)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.fill = PatternFill("solid", fgColor="2F9EE7")
        cell.border = thin_border

    fila = 3
    separador_num = 1

    for id_asiento, grupo in df.groupby("AsientoID", sort=False):
        fecha = grupo.iloc[0]["Fecha"]

        ws.cell(row=fila, column=1, value=fecha)
        ws.cell(row=fila, column=3, value=f"-------({separador_num})-------")
        ws.cell(row=fila, column=1).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=fila, column=3).alignment = Alignment(horizontal="center", vertical="center")
        for col in range(1, 6):
            ws.cell(row=fila, column=col).border = thin_border

        fila += 1
        separador_num += 1

        for _, r in grupo.iterrows():
            ws.cell(row=fila, column=1, value=None)
            ws.cell(row=fila, column=2, value=r["Código"])

            cell_desc = ws.cell(row=fila, column=3, value=r["Descripción"])
            if r["Debe"] and r["Debe"] > 0:
                cell_desc.alignment = Alignment(horizontal="left", vertical="center")
            else:
                cell_desc.alignment = Alignment(horizontal="left", vertical="center", indent=2)

            cell_debe = ws.cell(row=fila, column=4, value=r["Debe"])
            cell_debe.alignment = Alignment(horizontal="center", vertical="center")

            cell_haber = ws.cell(row=fila, column=5, value=r["Haber"])
            cell_haber.alignment = Alignment(horizontal="center", vertical="center")

            for col in range(1, 6):
                ws.cell(row=fila, column=col).border = thin_border

            fila += 1

        comentario = grupo.iloc[0]["Comentario"]
        if comentario and comentario.strip() != "":
            cell_coment = ws.cell(row=fila, column=3, value=comentario)
            cell_coment.font = Font(italic=True)
            cell_coment.alignment = Alignment(horizontal="center", vertical="center")
            for col in range(1, 6):
                ws.cell(row=fila, column=col).border = thin_border
            fila += 1

    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 50
    ws.column_dimensions["D"].width = 20
    ws.column_dimensions["E"].width = 20

    for cell in ws["A"]:
        if cell.row != 1 and cell.value not in (None, ""):
            cell.number_format = "DD/MM/YYYY"
            cell.alignment = Alignment(horizontal="center", vertical="center")

    for cell in ws["B"]:
        if cell.row != 1:
            cell.alignment = Alignment(horizontal="center", vertical="center")

    for col in ["D", "E"]:
        for cell in ws[col]:
            if cell.row != 1:
                cell.number_format = "#,##0.00"
                cell.alignment = Alignment(horizontal="center", vertical="center")

    output_path = Path(output_file) if output_file else Path(f"Libro_Diario_{libro_id}.xlsx")
    wb.save(output_path)
    return output_path


if __name__ == "__main__":
    try:
        libro = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        output = exportar_libro_diario(libro)
        print("Archivo Excel creado y formateado correctamente:", output)
    except ValueError as exc:
        print(exc)