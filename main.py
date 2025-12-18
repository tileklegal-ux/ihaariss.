import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import TELEGRAM_TOKEN
from database.db import get_user_role, ensure_user_exists

from handlers.user import cmd_start_user, register_handlers_user
from handlers.owner import owner_start, register_handlers_owner
from handlers.manager import manager_start, register_handlers_manager
# УБРАТЬ проблемный импорт
# from handlers.role_actions import register_role_actions


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Сохраняем/обновляем пользователя в БД
    ensure_user_exists(user_id, username)
    
    role = get_user_role(user_id)

    if role == "owner":
        await owner_start(update, context)
        return

    if role == "manager":
        await manager_start(update, context)
        return

    await cmd_start_user(update, context)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # ЕДИНСТВЕННЫЙ /start ВО ВСЁМ ПРОЕКТЕ
    app.add_handler(CommandHandler("start", start_router), group=0)

    # РОЛЕВЫЕ HANDLERS БЕЗ /start - НОВЫЙ ПОРЯДОК
    # УБРАТЬ: register_role_actions(app)        # group 1 - СНАЧАЛА FSM состояния
    register_handlers_owner(app)      # group 2 - ПОТОМ кнопки владельца  
    register_handlers_manager(app)    # group 3 - ПОТОМ кнопки менеджера
    register_handlers_user(app)       # group 4 - ПОСЛЕДНИЙ обычный пользователь

    app.run_polling()


if __name__ == "__main__":
    main()
