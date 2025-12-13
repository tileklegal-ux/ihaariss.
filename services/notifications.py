from telegram import Bot
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)


async def notify_user(user_id: int, text: str):
    """
    Уведомление пользователю (premium, revoke, системные события)
    """
    try:
        await bot.send_message(chat_id=user_id, text=text)
    except Exception:
        pass


async def notify_manager(manager_id: int, text: str):
    """
    Уведомление менеджеру
    """
    try:
        await bot.send_message(chat_id=manager_id, text=text)
    except Exception:
        pass


async def notify_owner(owner_id: int, text: str):
    """
    Уведомление владельцу
    """
    try:
        await bot.send_message(chat_id=owner_id, text=text)
    except Exception:
        pass
