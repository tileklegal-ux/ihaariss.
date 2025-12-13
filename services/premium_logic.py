import logging
from datetime import datetime, timedelta, timezone
from database.db import (
    get_user,
    update_premium_until,
    remove_premium_from_db,
)

logger = logging.getLogger(__name__)


# -----------------------------
# HELPER: авто-отключение истёкшего премиума
# -----------------------------
def _disable_if_expired(user_id: int, premium_until) -> bool:
    """
    Проверяет срок премиума.
    Если истёк — отключает его в базе.
    Возвращает True, если премиум ещё действует.
    """
    if premium_until is None:
        return False

    now = datetime.now(timezone.utc)

    if premium_until <= now:
        # срок истёк → снимаем премиум
        try:
            remove_premium_from_db(user_id)
            logger.info(f"Premium отключён (истёк) для user_id={user_id}")
        except Exception as e:
            logger.exception(f"Ошибка автоотключения премиума: {e}")
        return False

    return True


# -----------------------------
# PUBLIC: проверка премиума
# -----------------------------
def is_premium_user(user_id: int) -> bool:
    """
    Возвращает True/False.
    Условие: premium_until > NOW.
    """
    try:
        user = get_user(user_id)
    except Exception as e:
        logger.exception(f"Ошибка получения юзера при проверке премиума: {e}")
        return False

    if not user:
        return False

    premium_until = user.get("premium_until")
    return _disable_if_expired(user_id, premium_until)


# -----------------------------
# PUBLIC: выдать премиум
# -----------------------------
def set_premium(user_id: int, days: int = 30) -> bool:
    """
    Устанавливает премиум пользователю на N дней.
    """
    try:
        now = datetime.now(timezone.utc)
        new_until = now + timedelta(days=days)
        update_premium_until(user_id, new_until)
        logger.info(f"Premium выдан user_id={user_id} на {days} дней")
        return True
    except Exception as e:
        logger.exception(f"Ошибка выдачи премиума: {e}")
        return False


# -----------------------------
# PUBLIC: продлить премиум
# -----------------------------
def extend_premium(user_id: int, days: int) -> bool:
    """
    Продлевает текущий премиум. Если не было — начинается от сегодня.
    """
    try:
        user = get_user(user_id)
        now = datetime.now(timezone.utc)

        if user and user.get("premium_until"):
            current = user["premium_until"]
            if current > now:
                # Просто продлеваем сверху
                new_until = current + timedelta(days=days)
            else:
                # Был премиум, но истёк → начинаем с текущего момента
                new_until = now + timedelta(days=days)
        else:
            # Премиума нет → ставим как новый
            new_until = now + timedelta(days=days)

        update_premium_until(user_id, new_until)
        logger.info(f"Premium продлён user_id={user_id} на {days} дней")
        return True
    except Exception as e:
        logger.exception(f"Ошибка продления премиума: {e}")
        return False


# -----------------------------
# PUBLIC: полностью снять премиум
# -----------------------------
def remove_premium(user_id: int) -> bool:
    """
    Полностью отключает премиум.
    """
    try:
        remove_premium_from_db(user_id)
        logger.info(f"Premium снят для user_id={user_id}")
        return True
    except Exception as e:
        logger.exception(f"Ошибка снятия премиума: {e}")
        return False


# -----------------------------
# OPTIONAL: список тех, у кого скоро истекает (для менеджера)
# -----------------------------
def get_users_with_expiring_premium(days_left: int = 3):
    """
    Вернет список пользователей, у которых премиум истекает в ближайшие X дней.
    Позже подключим в менеджерские команды.
    """
    try:
        from database.db import get_all_premium_users
        now = datetime.now(timezone.utc)
        deadline = now + timedelta(days=days_left)

        users = get_all_premium_users()
        result = []

        for u in users:
            _until = u.get("premium_until")
            if _until and now < _until <= deadline:
                result.append(u)

        return result

    except Exception as e:
        logger.exception(f"Ошибка получения списка истекающих премиумов: {e}")
        return []
