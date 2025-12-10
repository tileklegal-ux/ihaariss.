from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime


def generate_pdf(path: str, table: dict, ai: dict):
    """
    Генерирует PDF отчёт.
    path — путь сохранения PDF.
    table — словарь Artbazar AI Таблицы.
    ai — словарь AI-анализа.
    """

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    y = height - 40

    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "Artbazar AI — Анализ товара")
    y -= 30

    c.setFont("Helvetica", 12)

    # Таблица
    for key, value in table.items():
        c.drawString(40, y, f"{key}: {value}")
        y -= 18

    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "AI-анализ:")
    y -= 20

    c.setFont("Helvetica", 12)

    for key, value in ai.items():
        c.drawString(40, y, f"{key}: {value}")
        y -= 18
        if y < 60:
            c.showPage()
            y = height - 40

    c.showPage()
    c.save()
