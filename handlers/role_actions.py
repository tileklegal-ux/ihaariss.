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
            return
        elif context.user_data.get(EXPECTING_DAYS):
            await give_premium_days_handler(update, context)
            return
    
    # ЕСЛИ НЕТ АКТИВНОГО FSM СОСТОЯНИЯ - ВЫХОДИМ И ПЕРЕДАЕМ УПРАВЛЕНИЕ
    # (бот передаст сообщение в следующий хендлер в группе)
    return
