from openpyxl import Workbook
from io import BytesIO


def generate_excel_report(headers: list[str], rows: list[list]):
    """
    headers: список заголовков колонок
    rows: список строк (каждая строка — список значений)
    """

    wb = Workbook()
    ws = wb.active

    # Заголовки
    ws.append(headers)

    # Данные
    for row in rows:
        ws.append(row)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return buffer
