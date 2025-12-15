# -*- coding: utf-8 -*-

"""
PDF-отчёт для Artbazar AI

Назначение:
- читаемый документ
- удобно отправить партнёру / сохранить
- PDF = витрина + выводы
"""

import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


def build_pdf_report(history: list) -> io.BytesIO:
    """
    history: список словарей из context.user_data["history"]
    Берём последние результаты, делаем компактный отчёт.
    """

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 20 * mm

    def draw_line(text: str):
        nonlocal y
        if y < 20 * mm:
            c.showPage()
            y = height - 20 * mm
        c.drawString(20 * mm, y, text)
        y -= 7 * mm

    # Заголовок
    c.setFont("Helvetica-Bold", 14)
    draw_line("Artbazar AI — отчёт")
    y -= 5 * mm

    c.setFont("Helvetica", 10)
    draw_line(f"Дата формирования: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    y -= 5 * mm

    if not history:
        draw_line("Нет данных для формирования отчёта.")
    else:
        draw_line("Последние результаты:")
        y -= 3 * mm

        for item in history[-5:]:
            draw_line(f"Тип: {item.get('type', '')}")
            draw_line(f"Дата: {item.get('date', '')}")
            draw_line(f"Итог: {item.get('summary', '')}")
            risk = item.get("risk_level")
            if risk:
                draw_line(f"Уровень риска: {risk}")
            y -= 3 * mm

    y -= 5 * mm
    draw_line("Примечание:")
    draw_line("Отчёт носит аналитический характер и не является рекомендацией.")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer
