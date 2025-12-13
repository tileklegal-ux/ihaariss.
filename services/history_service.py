import json
import logging
from datetime import datetime
from database.db import get_db_connection

logger = logging.getLogger(__name__)


# ========================================
#  Сохранение анализа в историю
# ========================================
def save_analysis_history(user_id: int, input_data: dict, ai_result: str):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO analysis_history (user_id, input_data, ai_output, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            user_id,
            json.dumps(input_data, ensure_ascii=False),
            ai_result,
            datetime.utcnow().isoformat()
        ))

        conn.commit()
        conn.close()

    except Exception as e:
        logger.error(f"Ошибка сохранения истории: {e}")


# ========================================
#  Получение истории
# ========================================
def get_user_history(user_id: int, limit: int = 5):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT input_data, ai_output, created_at
            FROM analysis_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit))

        rows = cur.fetchall()
        conn.close()

        history = []
        for row in rows:
            input_data = json.loads(row["input_data"])
            ai_output = row["ai_output"]
            created_at = row["created_at"]

            history.append({
                "input": input_data,
                "output": ai_output,
                "created_at": created_at
            })

        return history

    except Exception as e:
        logger.error(f"Ошибка получения истории: {e}")
        return []
