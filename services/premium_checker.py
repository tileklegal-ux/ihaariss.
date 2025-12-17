from database.db import is_user_premium

def is_premium_user(user_id: int) -> bool:
    return is_user_premium(user_id)
