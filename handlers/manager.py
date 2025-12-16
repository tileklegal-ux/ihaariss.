# -*- coding: utf-8 -*-
import os
import sqlite3
from datetime import datetime, timedelta

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
)

# 📌 ИСПРАВЛЕНИЕ: Импортируем централизованные функции из database.db
from database.db import get_user_role, get_user_by_username 

# ==================================================
# BUTTONS
# ==================================================

BTN_ACTIVATE_PREMIUM = "🟢 Активировать Premium"

# ==================================================
# FSM
# ==================================================

FSM_WAIT_PREMIUM_INPUT = "wait_premium_input"

# ==================================================
# KEYBOARD
# ==================================================

def manager_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton(BTN_ACTIVATE_PREMIUM)]],
        resize_keyboard=True,
    )

def premium_profile_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("📄 Скачать PDF"), KeyboardButton("📊 Скачать Excel")],
            [KeyboardButton("⬅️ Назад")],
        ],
        resize_keyboard=True,
    )

# ==================================================
# DB helpers
# ==================================================

# 📌 УДАЛЕНО: Убрали дублирующие функции базы данных _db_path и _get_user_by_username
# Теперь они вызываются из database.db

def _db_path() -> str:
    # Используем os.path.join для корректного пути
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "database", "artbazar.db")


def set_premium_by_telegram_id(telegram_id: int, days: int):
    conn = sqlite3.connect(_db_path())
    try:
        cur = conn.cursor()
        now = datetime.utcnow()
        premium_until = (now + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

        cur.execute(
            """
            UPDATE users
            SET is_premium = 1,
                premium_until = ?,
                updated_at = ?
            WHERE telegram_id = ?
            """,
            (premium_until, now.strftime("%Y-%m-%d %H:%M:%S"), telegram_id),
        )
        conn.commit()
    finally:
        conn.close()

# ==================================================
# ACTIONS
# ==================================================

async def on_activate_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Убедимся, что это менеджер
    if get_user_role(update.effective_user.id) != "manager":
        return

    context.user_data[FSM_WAIT_PREMIUM_INPUT] = True

    await update.message.reply_text(
        "🟢 *Активация Premium*\n\n"
        "Отправь одной строкой:\n"
        "`@username дни`\n\n"
        "Пример:\n"
        "`@test_user 7`",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )


async def on_premium_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Убедимся, что это менеджер
    if get_user_role(update.effective_user.id) != "manager":
        return

    # Проверяем, ожидает ли бот ввод Premium
    if not context.user_data.get(FSM_WAIT_PREMIUM_INPUT):
        return

    text = (update.message.text or "").strip()
    parts = text.split()

    # ❌ Неверный формат
    if len(parts) != 2 or not parts[0].startswith("@") or not parts[1].isdigit():
        # 📌 ИСПРАВЛЕНИЕ: Сбрасываем FSM при ошибке формата и возвращаем меню
        context.user_data.pop(FSM_WAIT_PREMIUM_INPUT, None) 
        
        await update.message.reply_text(
            "❌ Неверный формат.\n\n"
            "Используй:\n"
            "`@username дни`\n\n"
            "Пример:\n"
            "`@test_user 7`",
            parse_mode="Markdown",
            reply_markup=manager_keyboard(),
        )
        return

    username = parts[0].replace("@", "").strip()
    days = int(parts[1])

    # 📌 ИСПРАВЛЕНИЕ: Используем регистронезависимую функцию из database.db
    user_data = get_user_by_username(username)

    # ❌ Пользователь не найден
    if not user_data:
        # 📌 ИСПРАВЛЕНИЕ: Сбрасываем FSM при ошибке поиска и возвращаем меню
        context.user_data.pop(FSM_WAIT_PREMIUM_INPUT, None)
        
        await update.message.reply_text(
            "❌ Пользователь не найден в базе.\n\n"
            "Убедись, что пользователь:\n"
            "• уже заходил в бот\n"
            "• имеет @username\n\n"
            "Попроси его написать /start и попробуй снова.",
            reply_markup=manager_keyboard(),
        )
        return

    telegram_id = user_data["telegram_id"] # Берем ID из возвращенного словаря
    set_premium_by_telegram_id(telegram_id, days)

    # ✅ УСПЕХ — только тут чистим FSM
    context.user_data.pop(FSM_WAIT_PREMIUM_INPUT, None)

    # 🔔 Уведомление пользователю
    try:
        await context.bot.send_message(
            chat_id=telegram_id,
            text=(
                "🎉 *Premium активирован!*\n\n"
                f"⏳ Срок: *{days} дней*\n\n"
                "Теперь доступны:\n"
                "• история анализов\n"
                "• экспорт в PDF и Excel\n\n"
                "Я сразу открыл твой личный кабинет 👇"
            ),
            parse_mode="Markdown",
        )

        await context.bot.send_message(
            chat_id=telegram_id,
            text=(
                "👤 *Личный кабинет*\n\n"
                "Статус: ⭐ *Premium активен*\n\n"
                "Здесь собраны твои результаты.\n"
                "Ты можешь скачать отчёты в PDF или Excel."
            ),
            parse_mode="Markdown",
            reply_markup=premium_profile_keyboard(),
        )
    except Exception:
        pass

    # Ответ менеджеру (Остается на клавиатуре менеджера)
    await update.message.reply_text(
        f"✅ Premium активирован\n\n"
        f"👤 @{username}\n"
        f"⏳ Дней: {days}",
        reply_markup=manager_keyboard(),
    )

# ==================================================
# REGISTER
# ==================================================

def register_manager_handlers(app):
    app.add_handler(
        MessageHandler(
            filters.Regex(f"^{BTN_ACTIVATE_PREMIUM}$"),
            on_activate_premium,
        ),
        group=1,
    )

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, on_premium_input),
        group=3,
    )
