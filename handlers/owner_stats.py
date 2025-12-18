from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
import time
import sqlite3

# ИСПРАВЛЕННЫЕ ИМПОРТЫ:
from database.db import get_user_role, get_connection  # было: get_db_connection
from audit_log import log_event  # было: from services.audit_log import log_event

BTN_STATS = "📊 Статистика бота"


# -------------------------------------------------
# OWNER STATS (EXTENDED)
# -------------------------------------------------
async def owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = get_user_role(update.effective_user.id)
    if role != "owner":
        await update.message.reply_text("❌ Нет доступа.")
        return

    now = int(time.time())

    # --- users DB ---
    conn = get_connection()  # ИЗМЕНЕНО
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE premium_until > ?", (now,))
    active_premium = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE premium_until <= ? AND premium_until > 0", (now,))
    expired_premium = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE premium_until > 0")
    total_premium = cur.fetchone()[0]

    conn.close()

    # --- audit log DB ---
    audit_conn = sqlite3.connect("audit_log.db")
    audit_cur = audit_conn.cursor()

    audit_cur.execute(
        "SELECT COUNT(*) FROM audit_log WHERE event LIKE 'premium_granted%'"
    )
    premium_granted_total = audit_cur.fetchone()[0]

    audit_cur.execute(
        """
        SELECT user_id, COUNT(*) 
        FROM audit_log 
        WHERE event LIKE 'premium_granted%' 
        GROUP BY user_id
        """
    )
    manager_rows = audit_cur.fetchall()

    audit_conn.close()

    managers_stat = ""
    for manager_id, count in manager_rows:
        managers_stat += f"\n— ID {manager_id}: {count}"

    if not managers_stat:
        managers_stat = "\n— нет данных"

    log_event(update.effective_user.id, "owner_view_extended_stats")

    await update.message.reply_text(
        "📊 *Расширенная статистика Artbazar AI*\n\n"
        f"👥 Всего пользователей: {total_users}\n\n"
        f"⭐ Premium всего: {total_premium}\n"
        f"✅ Активных Premium: {active_premium}\n"
        f"⏳ Истекших Premium: {expired_premium}\n\n"
        f"🧾 Premium активаций (всего): {premium_granted_total}\n\n"
        f"👨‍💼 Активации по менеджерам:{managers_stat}",
        parse_mode="Markdown",
    )


# -------------------------------------------------
# АЛИАС ДЛЯ СОВМЕСТИМОСТИ
# -------------------------------------------------
# ❗ owner.py ожидает show_owner_stats
async def show_owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await owner_stats(update, context)


# -------------------------------------------------
# REGISTRATION
# -------------------------------------------------
def register_owner_stats(app):
    app.add_handler(
        MessageHandler(filters.Regex(f"^{BTN_STATS}$"), owner_stats)
    )
