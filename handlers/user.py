from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters
from typing import Optional

# ... (все константы и вспомогательные функции как в предыдущем ответе) ...

# =============================
# START
# =============================

async def cmd_start_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    user = update.effective_user
    name = user.first_name or user.username or "друг"
    
    await update.message.reply_text(
        f"Привет, {name} 👋\n\n"
        "Artbazar AI — помощник для предпринимателей.\n"
        "Здесь нет прогнозов и советов.\n"
        "Только спокойный разбор идей и рисков,\n"
        "чтобы решения принимались без лишнего давления.\n\n"
        "⚠️ Важно:\n"
        "Это не прогноз и не гарантия результата.\n"
        "Решение и ответственность остаются за тобой.\n\n"
        "Продолжим?",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_YES), KeyboardButton(BTN_NO)]],
            resize_keyboard=True,
        ),
    )

async def on_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Выбери раздел 👇",
        reply_markup=main_menu_keyboard()
    )

async def on_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Хорошо. Я рядом.",
        reply_markup=main_menu_keyboard()
    )

# =============================
# 📊 БИЗНЕС-АНАЛИЗ (хаб)
# =============================

async def on_business_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    await update.message.reply_text(
        "📊 Бизнес-анализ\n\n"
        "Здесь вы можете посмотреть на бизнес со стороны.\n"
        "Не чтобы найти «правильный ответ»,\n"
        "а чтобы прояснить риски, ограничения\n"
        "и точки неопределённости.",
        reply_markup=business_hub_keyboard(),
    )

# =============================
# 💰 ПРИБЫЛЬ И ДЕНЬГИ (FSM)
# =============================

async def pm_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    context.user_data[PM_STATE_KEY] = PM_STATE_REVENUE
    bridge = insights_bridge_text(context)
    
    await update.message.reply_text(
        bridge + "💰 Прибыль и деньги\n\n"
        "Укажи выручку за выбранный месяц.\n"
        "Сколько денег фактически поступило от клиентов.\n"
        "Без прогнозов и ожиданий — только реальные поступления.\n"
        "Период важен: считаем один конкретный месяц.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(BTN_BACK)]],
            resize_keyboard=True
        ),
    )

async def pm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (полный код функции pm_handler) ...

# =============================
# 🚀 РОСТ И ПРОДАЖИ (FSM)
# =============================

async def growth_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (код функции) ...

async def growth_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (код функции) ...

# =============================
# 📦 АНАЛИТИКА ТОВАРА — FSM v1 (полный)
# =============================

async def ta_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (код функции) ...

async def ta_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (код функции) ...

async def send_ta_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (код функции) ...

# =============================
# 🔎 ПОДБОР НИШИ — FSM v1 (полный)
# =============================

async def ns_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (код функции) ...

async def ns_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (код функции) ...

# =============================
# ❤️ PREMIUM (коротко + цены + кнопка "что получу")
# =============================

async def premium_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (код функции) ...

async def premium_benefits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (код функции) ...

# =============================
# ПРОЧЕЕ
# =============================

async def on_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_fsm(context)
    await update.message.reply_text(
        "👤 Личный кабинет\n\nИстория появится позже.",
        reply_markup=main_menu_keyboard(),
    )

# =============================
# ROUTER
# =============================

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (код функции) ...

# =============================
# REGISTER
# =============================

def register_handlers_user(app):
    # стартовые
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_YES}$"), on_yes))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NO}$"), on_no))
    
    # меню/хабы
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_BIZ}$"), on_business_analysis))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PROFILE}$"), on_profile))  # Теперь on_profile определена выше!
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PREMIUM}$"), premium_start))
    
    # premium benefits
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PREMIUM_BENEFITS}$"), premium_benefits))
    
    # бизнес-хаб сценарии
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_PM}$"), pm_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_GROWTH}$"), growth_start))
    
    # product/niche
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_ANALYSIS}$"), ta_start))
    app.add_handler(MessageHandler(filters.Regex(f"^{BTN_NICHE}$"), ns_start))
    
    # общий роутер текста
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))