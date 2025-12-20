async def start_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    ensure_user_exists(u.id, u.username or "")

    role = get_user_role(u.id)

    if role == "owner":
        await owner_start(update, context)
        return

    if role == "manager":
        await manager_start(update, context)
        return

    # ❗ ТОЛЬКО СТАВИМ ФЛАГ
    context.user_data["onboarding"] = True

    await update.message.reply_text(
        "Привет! Продолжим?",
        reply_markup=ReplyKeyboardMarkup(
            [["Да", "Нет"]],
            resize_keyboard=True
        )
    )
