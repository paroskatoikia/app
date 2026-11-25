from io import BytesIO
from datetime import date, datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import (
    Font,
    Alignment,
    Border,
    Side,
    PatternFill,
)
from openpyxl.utils import get_column_letter


def has_value(value):
    return value is not None and str(value).strip() != ""


def format_date(value):
    if isinstance(value, (date, datetime)):
        return value.strftime("%d/%m/%Y")
    return str(value or "")


def read_excel(uploaded_file):

    extension = Path(uploaded_file.name).suffix.lower()
    content = uploaded_file.read()

    # Modern Excel files
    if extension == ".xlsx":

        workbook = load_workbook(
            BytesIO(content),
            data_only=True,
            read_only=True,
        )

        try:
            return list(
                workbook.active.iter_rows(values_only=True)
            )
        finally:
            workbook.close()

    # Old Excel files
    elif extension == ".xls":

        import xlrd

        workbook = xlrd.open_workbook(
            file_contents=content
        )

        sheet = workbook.sheet_by_index(0)
        rows = []

        for row_index in range(sheet.nrows):

            row = []

            for col_index in range(sheet.ncols):

                cell = sheet.cell(row_index, col_index)
                value = cell.value

                if cell.ctype == xlrd.XL_CELL_DATE:
                    value = xlrd.xldate_as_datetime(
                        value,
                        workbook.datemode,
                    )

                row.append(value)

            rows.append(row)

        return rows

    raise ValueError(
        "Please upload an .xls or .xlsx file."
    )


def create_water_sheet(uploaded_file, empty_columns=7):

    rows = read_excel(uploaded_file)

    if len(rows) < 3 or len(rows[1]) < 3:
        raise ValueError(
            "The Excel file does not contain "
            "a valid measurement table."
        )

    if not 1 <= empty_columns <= 12:
        raise ValueError(
            "Empty columns must be between 1 and 12."
        )

    # Original second row contains the headers
    headers = rows[1]

    municipality_header = headers[1]

    # Create new Excel workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "ΔΕΥΑΠ ΜΕΤΡΗΣΕΙΣ"

    total_columns = 3 + empty_columns

    # Main title
    ws.merge_cells(
        start_row=1,
        start_column=1,
        end_row=1,
        end_column=total_columns,
    )

    ws["A1"] = "ΔΕΥΑΠ ΜΕΤΡΗΣΕΙΣ"

    # New headers
    ws.append([
        "ΗΜΕΡΟΜΗΝΙΑ",
        format_date(municipality_header),
        "ΤΕΛΕΥΤΑΙΑ ΜΕΤΡΗΣΗ",
    ] + [None] * empty_columns)

    # Copy each villa and its latest measurement
    for row in rows[2:]:

        if not row or not has_value(row[0]):
            continue

        villa = row[0]

        municipality = (
            row[1] if len(row) > 1 else None
        )

        latest = None

        # Search backwards for the latest reading
        # Zero is also a valid meter reading.
        for value in reversed(row[2:]):

            if has_value(value):
                latest = value
                break

        ws.append([
            villa,
            municipality,
            latest,
        ] + [None] * empty_columns)

    if ws.max_row < 3:
        raise ValueError("No measurement rows found.")

    # ======================================
    # EXCEL FORMATTING
    # ======================================

    thin = Side(
        style="thin",
        color="000000",
    )

    border = Border(
        left=thin,
        right=thin,
        top=thin,
        bottom=thin,
    )

    ws["A1"].font = Font(
        name="Arial",
        size=18,
        bold=True,
    )

    ws["A1"].alignment = Alignment(
        horizontal="center",
        vertical="center",
    )

    ws.row_dimensions[1].height = 35
    ws.row_dimensions[2].height = 45

    for row in ws.iter_rows(
        min_row=2,
        max_row=ws.max_row,
        min_col=1,
        max_col=total_columns,
    ):

        for cell in row:

            cell.border = border

            cell.font = Font(
                name="Arial",
                size=11,
            )

            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
                wrap_text=True,
            )

    # Header formatting
    for cell in ws[2]:

        cell.font = Font(
            name="Arial",
            size=10,
            bold=True,
        )

        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="E7E6E6",
        )

    # Villa rows
    for row_number in range(3, ws.max_row + 1):

        ws.row_dimensions[row_number].height = 32

        ws.cell(row_number, 1).alignment = Alignment(
            horizontal="left",
            vertical="center",
            wrap_text=True,
        )

        # Highlight latest measurement
        ws.cell(row_number, 3).font = Font(
            name="Arial",
            size=11,
            bold=True,
        )

    # Column widths
    ws.column_dimensions["A"].width = 32
    ws.column_dimensions["B"].width = 16
    ws.column_dimensions["C"].width = 19

    for col in range(4, total_columns + 1):

        ws.column_dimensions[
            get_column_letter(col)
        ].width = 13

    # ======================================
    # PRINT SETTINGS
    # ======================================

    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4

    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0

    ws.sheet_properties.pageSetUpPr.fitToPage = True

    ws.print_options.horizontalCentered = True
    ws.print_title_rows = "1:2"

    ws.print_area = (
        f"A1:{get_column_letter(total_columns)}"
        f"{ws.max_row}"
    )

    ws.page_margins.left = 0.2
    ws.page_margins.right = 0.2
    ws.page_margins.top = 0.3
    ws.page_margins.bottom = 0.3

    ws.freeze_panes = "D3"
    ws.sheet_view.showGridLines = False

    # Return Excel file in memory
    output = BytesIO()

    wb.save(output)

    output.seek(0)

    return output

