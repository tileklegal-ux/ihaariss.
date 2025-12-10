import json
from datetime import datetime
from database.models import get_connection


def save_history(user_id: int, table_data: dict, ai_result: dict):
    """
    Сохраняет анализ в базу, только для PREMIUM.
    Хранит не больше 5 последних записей.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analysis_history (user_id, table_json, ai_json, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        json.dumps(table_data, ensure_ascii=False),
        json.dumps(ai_result, ensure_ascii=False),
        datetime.utcnow().isoformat()
    ))

    # Оставляем только 5 последних записей по пользователю
    cursor.execute("""
        DELETE FROM analysis_history
        WHERE id NOT IN (
            SELECT id FROM analysis_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 5
        )
        AND user_id = ?
    """, (user_id, user_id))

    conn.commit()
    conn.close()


def get_history(user_id: int):
    """
    Возвращает последние 5 анализов пользователя (от новых к старым).
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT table_json, ai_json, created_at
        FROM analysis_history
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 5
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        table_json = json.loads(row[0])
        ai_json = json.loads(row[1])
        created = row[2]

        result.append({
            "table": table_json,
            "ai": ai_json,
            "created_at": created
        })

    return result


def get_last_analysis(user_id: int):
    """
    Возвращает последний (самый новый) анализ пользователя.
    Формат: (table_dict, ai_dict) или None.
    """
    history = get_history(user_id)
    if not history:
        return None

    last = history[0]
    return last["table"], last["ai"]
