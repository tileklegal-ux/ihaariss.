# handlers/role_actions.py

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from database.db import (
    get_user_role,
    get_user_by_username,
    set_role_by_telegram_id,
    give_premium_days,
)
from services.audit_log import log_event

BTN_ADD_MANAGER = "➕ Добавить менеджера"
BTN_REMOVE_MANAGER = "➖ Удалить менеджера"
BTN_GIVE_PREMIUM = "⭐ Выдать Premium"
BTN_EXIT = "⬅️ Выйти"

# Ключи для FSM состояний
ADD_MANAGER_STATE = "add_manager_state"
REMOVE_MANAGER_STATE = "remove_manager_state"
GIVE_PREMIUM_STATE = "give_premium_state"
EXPECTING_USERNAME = "expecting_username"
EXPECTING_DAYS = "expecting_days"


# -------------------------------------------------
# ADD MANAGER - FSM подход
# -------------------------------------------------
async def add_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)
    if role != "owner":
        await update.message.reply_text("❌ Нет доступа.")
        return

    # Устанавливаем состояние ожидания username
    context.user_data[ADD_MANAGER_STATE] = True
    context.user_data[EXPECTING_USERNAME] = True
    
    await update.message.reply_text(
        "Укажите username пользователя (без @), которого нужно сделать менеджером:"
    )


async def add_manager_username_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка username для добавления менеджера"""
    if not context.user_data.get(ADD_MANAGER_STATE):
        return
    
    text = update.message.text.strip()
    
    # Обработка кнопки Назад
    if text == "⬅️ Назад" or text == "Назад":
        # Сбрасываем состояние
        context.user_data.pop(ADD_MANAGER_STATE, None)
        context.user_data.pop(EXPECTING_USERNAME, None)
        
        # Возвращаемся в панель владельца
        role = get_user_role(update.effective_user.id)
        if role == "owner":
            from handlers.owner import owner_start
            await owner_start(update, context)
        return
    
    username = text
    
    # Убираем @ если пользователь его ввел
    if username.startswith('@'):
        username = username[1:]
    
    user = get_user_by_username(username)
    
    if not user:
        await update.message.reply_text(
            f"❌ Пользователь @{username} не найден.\n"
            "Убедитесь, что пользователь уже начал диалог с ботом.\n\n"
            "Попробуйте снова или нажмите 'Назад'."
        )
        return
    
    # Проверяем, не менеджер ли уже
    if user["role"] == "manager":
        await update.message.reply_text(
            f"❌ Пользователь @{username} уже является менеджером."
        )
        # Сбрасываем состояние
        context.user_data.pop(ADD_MANAGER_STATE, None)
        context.user_data.pop(EXPECTING_USERNAME, None)
        return
    
    # Устанавливаем роль менеджера
    set_role_by_telegram_id(user["telegram_id"], "manager")
    log_event(update.effective_user.id, f"add_manager:{user['telegram_id']}")
    
    # Сбрасываем состояние
    context.user_data.pop(ADD_MANAGER_STATE, None)
    context.user_data.pop(EXPECTING_USERNAME, None)
    
    await update.message.reply_text(
        f"✅ Пользователь @{user['username']} назначен менеджером."
    )


# -------------------------------------------------
# REMOVE MANAGER - FSM подход
# -------------------------------------------------
async def remove_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)
    if role != "owner":
        await update.message.reply_text("❌ Нет доступа.")
        return

    # Устанавливаем состояние ожидания username
    context.user_data[REMOVE_MANAGER_STATE] = True
    context.user_data[EXPECTING_USERNAME] = True
    
    await update.message.reply_text(
        "Укажите username менеджера (без @), которого нужно удалить:"
    )


async def remove_manager_username_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка username для удаления менеджера"""
    if not context.user_data.get(REMOVE_MANAGER_STATE):
        return
    
    text = update.message.text.strip()
    
    # Обработка кнопки Назад
    if text == "⬅️ Назад" or text == "Назад":
        # Сбрасываем состояние
        context.user_data.pop(REMOVE_MANAGER_STATE, None)
        context.user_data.pop(EXPECTING_USERNAME, None)
        
        # Возвращаемся в панель владельца
        role = get_user_role(update.effective_user.id)
        if role == "owner":
            from handlers.owner import owner_start
            await owner_start(update, context)
        return
    
    username = text
    
    # Убираем @ если пользователь его ввел
    if username.startswith('@'):
        username = username[1:]
    
    user = get_user_by_username(username)
    
    if not user:
        await update.message.reply_text(
            f"❌ Пользователь @{username} не найден.\n\n"
            "Попробуйте снова или нажмите 'Назад'."
        )
        return
    
    # Проверяем, является ли менеджером
    if user["role"] != "manager":
        await update.message.reply_text(
            f"❌ Пользователь @{username} не является менеджером."
        )
        # Сбрасываем состояние
        context.user_data.pop(REMOVE_MANAGER_STATE, None)
        context.user_data.pop(EXPECTING_USERNAME, None)
        return
    
    # Возвращаем роль user
    set_role_by_telegram_id(user["telegram_id"], "user")
    log_event(update.effective_user.id, f"remove_manager:{user['telegram_id']}")
    
    # Сбрасываем состояние
    context.user_data.pop(REMOVE_MANAGER_STATE, None)
    context.user_data.pop(EXPECTING_USERNAME, None)
    
    await update.message.reply_text(
        f"✅ Пользователь @{user['username']} больше не менеджер."
    )


# -------------------------------------------------
# GIVE PREMIUM (MANAGER) - FSM подход
# -------------------------------------------------
async def give_premium_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)
    if role not in ("manager", "owner"):
        await update.message.reply_text("❌ Нет доступа.")
        return

    # Устанавливаем состояние ожидания username
    context.user_data[GIVE_PREMIUM_STATE] = True
    context.user_data[EXPECTING_USERNAME] = True
    
    await update.message.reply_text(
        "⭐ **Выдача Premium**\n\n"
        "Укажите username пользователя (без @):"
    )


async def give_premium_username_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка username для выдачи Premium"""
    if not context.user_data.get(GIVE_PREMIUM_STATE):
        return
    
    text = update.message.text.strip()
    
    # Обработка кнопки Назад
    if text == "⬅️ Назад" or text == "Назад":
        # Сбрасываем состояние
        context.user_data.pop(GIVE_PREMIUM_STATE, None)
        context.user_data.pop(EXPECTING_USERNAME, None)
        context.user_data.pop(EXPECTING_DAYS, None)
        context.user_data.pop("temp_username", None)
        context.user_data.pop("temp_user_id", None)
        
        # Возвращаемся в панель менеджера/владельца
        role = get_user_role(update.effective_user.id)
        if role == "manager":
            from handlers.manager import manager_start
            await manager_start(update, context)
        elif role == "owner":
            from handlers.owner import owner_start
            await owner_start(update, context)
        return
    
    username = text
    
    # Убираем @ если пользователь его ввел
    if username.startswith('@'):
        username = username[1:]
    
    user = get_user_by_username(username)
    
    if not user:
        await update.message.reply_text(
            f"❌ Пользователь @{username} не найден.\n"
            "Убедитесь, что пользователь уже начал диалог с ботом.\n\n"
            "Попробуйте снова или нажмите 'Назад'."
        )
        return
    
    # Сохраняем username для следующего шага
    context.user_data["temp_username"] = username
    context.user_data["temp_user_id"] = user["telegram_id"]
    
    # Переходим к ожиданию количества дней
    context.user_data[EXPECTING_USERNAME] = False
    context.user_data[EXPECTING_DAYS] = True
    
    await update.message.reply_text(
        f"Пользователь: @{username}\n\n"
        "Укажите количество дней Premium:"
    )


async def give_premium_days_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка количества дней для Premium"""
    if not context.user_data.get(GIVE_PREMIUM_STATE) or not context.user_data.get(EXPECTING_DAYS):
        return
    
    text = update.message.text.strip()
    
    # Обработка кнопки Назад
    if text == "⬅️ Назад" or text == "Назад":
        # Сбрасываем состояние
        context.user_data.pop(GIVE_PREMIUM_STATE, None)
        context.user_data.pop(EXPECTING_USERNAME, None)
        context.user_data.pop(EXPECTING_DAYS, None)
        context.user_data.pop("temp_username", None)
        context.user_data.pop("temp_user_id", None)
        
        # Возвращаемся в панель менеджера/владельца
        role = get_user_role(update.effective_user.id)
        if role == "manager":
            from handlers.manager import manager_start
            await manager_start(update, context)
        elif role == "owner":
            from handlers.owner import owner_start
            await owner_start(update, context)
        return
    
    try:
        days = int(text)
        if days <= 0:
            await update.message.reply_text("❌ Количество дней должно быть положительным числом.")
            return
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введите число (например: 30).")
        return
    
    username = context.user_data.get("temp_username")
    user_id = context.user_data.get("temp_user_id")
    
    if not username or not user_id:
        # Сбрасываем состояние при ошибке
        context.user_data.pop(GIVE_PREMIUM_STATE, None)
        context.user_data.pop(EXPECTING_DAYS, None)
        context.user_data.pop("temp_username", None)
        context.user_data.pop("temp_user_id", None)
        await update.message.reply_text("❌ Ошибка: данные пользователя не найдены.")
        return
    
    # Выдаем Premium
    give_premium_days(user_id, days)
    log_event(update.effective_user.id, f"premium_granted:{user_id}:{days}")
    
    # Сбрасываем состояние
    context.user_data.pop(GIVE_PREMIUM_STATE, None)
    context.user_data.pop(EXPECTING_DAYS, None)
    context.user_data.pop("temp_username", None)
    context.user_data.pop("temp_user_id", None)
    
    await update.message.reply_text(
        f"✅ Premium для @{username} выдан на {days} дней."
    )


# -------------------------------------------------
# ГЛАВНЫЙ ТЕКСТОВЫЙ РОУТЕР ДЛЯ ВЛАДЕЛЬЦА И МЕНЕДЖЕРА
# -------------------------------------------------
async def role_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Роутер текстовых сообщений для владельца и менеджера - ТОЛЬКО FSM"""
    text = update.message.text or ""
    
    # Роутинг по состоянию FSM
    if context.user_data.get(ADD_MANAGER_STATE):
        await add_manager_username_handler(update, context)
        return
    
    if context.user_data.get(REMOVE_MANAGER_STATE):
        await remove_manager_username_handler(update, context)
        return
    
    if context.user_data.get(GIVE_PREMIUM_STATE):
        if context.user_data.get(EXPECTING_USERNAME):
            await give_premium_username_handler(update, context)
        elif context.user_data.get(EXPECTING_DAYS):
            await give_premium_days_handler(update, context)
        return
    
    # Если нет активного FSM состояния - пропускаем, дальше обработают другие handlers
    return


# -------------------------------------------------
# REGISTRATION
# -------------------------------------------------
def register_role_actions(app):
    # Регистрируем роутер для FSM состояний владельца и менеджера
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            role_text_router
        ),
        group=1  # ПЕРВАЯ группа - FSM
    )
