import pandas as pd


def generate_excel(path: str, table: dict, ai: dict):
    """
    Генерирует Excel-файл с двумя листами:
    - Таблица Artbazar
    - AI-анализ
    """

    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        df_table = pd.DataFrame(table.items(), columns=["Поле", "Значение"])
        df_ai = pd.DataFrame(ai.items(), columns=["Показатель", "Значение"])

        df_table.to_excel(writer, sheet_name="Таблица", index=False)
        df_ai.to_excel(writer, sheet_name="AI Анализ", index=False)
