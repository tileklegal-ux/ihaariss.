# services/pdf_generator.py

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import os


def generate_simple_pdf(
    filename: str,
    title: str,
    content: str,
) -> str:
    """
    Генерирует простой PDF-файл с заголовком и текстом.
    Возвращает путь к файлу.
    """

    # папка для PDF
    output_dir = "generated_files"
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, filename)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # Заголовок
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 60, title)

    # Дата
    c.setFont("Helvetica", 9)
    c.drawString(
        40,
        height - 80,
        f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
    )

    # Основной текст
    c.setFont("Helvetica", 11)

    y = height - 120
    for line in content.split("\n"):
        if y < 40:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - 60

        c.drawString(40, y, line)
        y -= 16

    c.showPage()
    c.save()

    return file_path
