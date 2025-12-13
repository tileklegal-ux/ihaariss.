from telegram import Update
from telegram.ext import ContextTypes
from database.db import (
    get_db_connection,
    get_user_role,
    give_premium_days,
    get_user_by_username,
)


# ---------------------------------------------------------
# OWNER — Статистика проекта
# ---------------------------------------------------------
async def owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db_connection()
    cur = conn.cursor()

    users = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    premium = cur.execute("SELECT COUNT(*) FROM users WHERE premium_days > 0").fetchone()[0]
    managers = cur.execute("SELECT COUNT(*) FROM users WHERE role='manager'").fetchone()[0]
    history = cur.execute("SELECT COUNT(*) FROM analysis_history").fetchone()[0]

    conn.close()

    msg = (
        "📊 *Статистика проекта*\n\n"
        f"👥 Пользователи: {users}\n"
        f"💎 Premium: {premium}\n"
        f"🧑‍💼 Менеджеры: {managers}\n"
        f"📦 Анализов: {history}"
    )

    await update.message.reply_text(msg, parse_mode="Markdown")


# ---------------------------------------------------------
# OWNER — список пользователей
# ---------------------------------------------------------
async def owner_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db_connection()
    cur = conn.cursor()

    rows = cur.execute("SELECT id, username, first_name, role FROM users ORDER BY id DESC LIMIT 20").fetchall()
    conn.close()

    if not rows:
        return await update.message.reply_text("Нет пользователей.")

    msg = "👥 *Последние 20 пользователей:*\n\n"
    for r in rows:
        msg += f"ID: {r['id']} | @{r['username']} | {r['first_name']} | роль: {r['role']}\n"

    await update.message.reply_text(msg, parse_mode="Markdown")


# ---------------------------------------------------------
# OWNER — список менеджеров
# ---------------------------------------------------------
async def owner_managers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db_connection()
    cur = conn.cursor()

    rows = cur.execute("SELECT id, username, first_name FROM users WHERE role='manager'").fetchall()
    conn.close()

    if not rows:
        return await update.message.reply_text("Менеджеров пока нет.")

    msg = "👔 *Менеджеры:*\n\n"
    for r in rows:
        msg += f"ID: {r['id']} | @{r['username']} | {r['first_name']}\n"

    await update.message.reply_text(msg, parse_mode="Markdown")


# ---------------------------------------------------------
# OWNER — настройки (заглушка)
# ---------------------------------------------------------
async def owner_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔧 Раздел настроек в разработке.")


# ---------------------------------------------------------
# MANAGER — одобрить премиум
# ---------------------------------------------------------
async def manager_approve_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not text.startswith("@"):
        return await update.message.reply_text("Введите username в формате: @username")

    username = text.replace("@", "")
    user = get_user_by_username(username)

    if not user:
        return await update.message.reply_text("Пользователь не найден.")

    user_id = user["id"]

    # даём 30 дней премиума
    give_premium_days(user_id, 30)

    await update.message.reply_text(f"Премиум для @{username} активирован на 30 дней.")

    # уведомление пользователю
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="🎉 Ваш аккаунт получил PREMIUM доступ на 30 дней!",
        )
    except:
        pass


# ---------------------------------------------------------
# MANAGER — последние клиенты
# ---------------------------------------------------------
async def manager_clients(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db_connection()
    cur = conn.cursor()

    rows = cur.execute("SELECT id, username, first_name, premium_days FROM users ORDER BY id DESC LIMIT 20").fetchall()
    conn.close()

    if not rows:
        return await update.message.reply_text("Клиентов пока нет.")

    msg = "📝 *Последние клиенты:*\n\n"
    for r in rows:
        msg += f"ID: {r['id']} | @{r['username']} | премиум дней: {r['premium_days']}\n"

    await update.message.reply_text(msg, parse_mode="Markdown")


# ---------------------------------------------------------
# MANAGER — история анализов
# ---------------------------------------------------------
async def manager_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db_connection()
    cur = conn.cursor()

    rows = cur.execute(
        "SELECT user_id, niche, product, created_at FROM analysis_history ORDER BY id DESC LIMIT 20"
    ).fetchall()
    conn.close()

    if not rows:
        return await update.message.reply_text("Анализов пока нет.")

    msg = "📦 *Последние 20 анализов:*\n\n"
    for r in rows:
        msg += (
            f"Пользователь {r['user_id']} | Ниша: {r['niche']} | "
            f"Товар: {r['product']} | Время: {r['created_at']}\n"
        )

    await update.message.reply_text(msg, parse_mode="Markdown")
