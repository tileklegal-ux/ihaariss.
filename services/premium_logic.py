from datetime import datetime
from database.models import get_user, remove_premium


def is_premium(user_id: int) -> bool:
    """
    Проверяет, есть ли у пользователя Premium.
    Если срок истёк — автоматически отключает Premium.
    """

    user = get_user(user_id)
    if not user:
        return False

    premium_until = user[5]  # колонка premium_until

    if not premium_until:
        return False

    try:
        end_date = datetime.fromisoformat(premium_until)
    except:
        return False

    # Сравнение со временем UTC
    now = datetime.utcnow()

    # Если Premium закончился → отключаем
    if end_date <= now:
        remove_premium(user_id)
        return False

    return True
