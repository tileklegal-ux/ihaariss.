# -*- coding: utf-8 -*-

import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from services.openai_client import ask_openai
from database.db import is_user_premium
from handlers.user_keyboards import (
    company_stage_keyboard,
    step_keyboard,
    premium_keyboard,
    BTN_BACK
)
from handlers.user_texts import t as T
from handlers.user_helpers import clear_fsm, save_insights

logger = logging.getLogger(__name__)

# =============================
# FSM KEYS
# =============================
COMPANY_STAGE_STATE = "company_stage_state"
STAGE_STEP_KEY = "stage_step"
STAGE_TEASER_KEY = "stage_teaser_mode"
STAGE_ANSWERS_KEY = "stage_answers"

# Этапы развития компании
STAGES = {
    1: "🌱 Посевная стадия",
    2: "🚀 Стартап",
    3: "📈 Рост",
    4: "⚡ Масштабирование",
    5: "🏢 Зрелость",
    6: "🔄 Обновление",
    7: "📊 Консолидация",
    8: "🌍 Экспансия",
    9: "🤝 Синергия",
    10: "👑 Лидерство"
}

async def start_company_stage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запуск анализа этапа компании"""
    clear_fsm(context)
    
    user_id = update.effective_user.id
    premium = is_user_premium(user_id)
    
    # Инициализация состояния
    context.user_data[COMPANY_STAGE_STATE] = True
    context.user_data[STAGE_STEP_KEY] = 1
    context.user_data[STAGE_ANSWERS_KEY] = {}
    
    # Если не премиум - режим тизера (2 вопроса)
    if not premium:
        context.user_data[STAGE_TEASER_KEY] = True
        lang = context.user_data.get("lang", "ru")
        await update.message.reply_text(
            T(lang, "company_stage_intro"),
            reply_markup=step_keyboard()
        )
        await ask_next_stage_question(update, context)
    else:
        # Премиум - полная версия
        context.user_data[STAGE_TEASER_KEY] = False
        lang = context.user_data.get("lang", "ru")
        await update.message.reply_text(
            T(lang, "company_stage_intro"),
            reply_markup=step_keyboard()
        )
        await ask_next_stage_question(update, context)
    
    return COMPANY_STAGE_STATE

async def ask_next_stage_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Задаём следующий вопрос"""
    step = context.user_data.get(STAGE_STEP_KEY, 1)
    is_teaser = context.user_data.get(STAGE_TEASER_KEY, False)
    lang = context.user_data.get("lang", "ru")
    
    if is_teaser:
        # Тизирная версия - только 2 вопроса
        if step == 1:
            await update.message.reply_text(
                T(lang, "company_stage_teaser_q1"),
                reply_markup=step_keyboard()
            )
        elif step == 2:
            await update.message.reply_text(
                T(lang, "company_stage_teaser_q2"),
                reply_markup=step_keyboard()
            )
    else:
        # Полная версия - 10 вопросов
        if step <= 10:
            text_key = f"company_stage_premium_q{step}"
            await update.message.reply_text(
                T(lang, text_key),
                reply_markup=step_keyboard()
            )

async def handle_company_stage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ответов для этапа компании"""
    text = update.message.text.strip()
    step = context.user_data.get(STAGE_STEP_KEY, 1)
    is_teaser = context.user_data.get(STAGE_TEASER_KEY, False)
    lang = context.user_data.get("lang", "ru")
    
    if text == BTN_BACK:
        clear_fsm(context)
        await update.message.reply_text(
            "📊 Бизнес-анализ",
            reply_markup=ReplyKeyboardMarkup(
                [
                    [KeyboardButton("💰 Деньги и прибыль"), KeyboardButton("📈 Рост и продажи")],
                    [KeyboardButton("📈 Этап компании")],
                    [KeyboardButton(BTN_BACK)],
                ],
                resize_keyboard=True,
            )
        )
        return
    
    # Сохраняем ответ
    answers = context.user_data.get(STAGE_ANSWERS_KEY, {})
    answers[f"q{step}"] = text
    context.user_data[STAGE_ANSWERS_KEY] = answers
    
    if is_teaser:
        # Тизирная версия
        if step < 2:
            context.user_data[STAGE_STEP_KEY] = step + 1
            await ask_next_stage_question(update, context)
        else:
            # Показываем тизерный результат и предлагаем премиум
            await show_teaser_result(update, context)
    else:
        # Полная версия
        if step < 10:
            context.user_data[STAGE_STEP_KEY] = step + 1
            await ask_next_stage_question(update, context)
        else:
            # Завершаем полный анализ
            await complete_stage_analysis(update, context)

async def show_teaser_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показываем результат тизера и предлагаем премиум"""
    answers = context.user_data.get(STAGE_ANSWERS_KEY, {})
    lang = context.user_data.get("lang", "ru")
    
    goal = answers.get("q1", "Не указано")
    finance = answers.get("q2", "Не указано")
    
    await update.message.reply_text(
        T(lang, "company_stage_teaser_result", goal=goal, finance=finance),
        reply_markup=company_stage_keyboard(2, False)
    )
    
    # Сохраняем инсайты
    save_insights(
        context,
        last_scenario="Анализ этапа компании (тизер)",
        last_verdict=f"Цель: {goal}, Финансы: {finance}",
        risk_level="Средний"
    )
    
    # Очищаем состояние
    context.user_data.pop(COMPANY_STAGE_STATE, None)
    context.user_data.pop(STAGE_STEP_KEY, None)
    context.user_data.pop(STAGE_TEASER_KEY, None)

async def complete_stage_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершаем полный анализ этапа"""
    answers = context.user_data.get(STAGE_ANSWERS_KEY, {})
    lang = context.user_data.get("lang", "ru")
    
    # Формируем данные для AI-анализа
    analysis_text = "Анализ этапа компании:\n\n"
    for i in range(1, 11):
        analysis_text += f"Вопрос {i}: {answers.get(f'q{i}', 'Нет ответа')}\n"
    
    # Запрос к AI для анализа
    ai_prompt = (
        "Проанализируй этап развития компании на основе ответов.\n"
        "Определи этап из 10 возможных (1-Посевная, 10-Лидерство).\n"
        "Дайте оценку от 1 до 100 баллов.\n"
        "Выдели 3 ключевых наблюдения.\n"
        "Предложи 3 фокуса для развития.\n"
        "Запрещено давать советы и прогнозы.\n"
        "Формат ответа строго:\n"
        "Этап: [номер и название]\n"
        "Баллы: [число]/100\n"
        "Наблюдения:\n1) ...\n2) ...\n3) ...\n\n"
        "Фокусы:\n1) ...\n2) ...\n3) ...\n\n"
        f"Данные:\n{analysis_text}"
    )
    
    try:
        await update.message.chat.send_action("typing")
        ai_response = await ask_openai(ai_prompt)
        
        # Парсим ответ AI
        lines = ai_response.split('\n')
        stage_info = "Не определено"
        score = "0"
        observations = []
        focus_areas = []
        
        current_section = None
        for line in lines:
            if line.startswith("Этап:"):
                stage_info = line.replace("Этап:", "").strip()
            elif line.startswith("Баллы:"):
                score = line.replace("Баллы:", "").strip().split('/')[0]
            elif line.startswith("Наблюдения:"):
                current_section = "observations"
            elif line.startswith("Фокусы:"):
                current_section = "focus"
            elif current_section == "observations" and line.strip():
                if line.strip().startswith("1)") or line.strip().startswith("2)") or line.strip().startswith("3)"):
                    observations.append(line.strip())
            elif current_section == "focus" and line.strip():
                if line.strip().startswith("1)") or line.strip().startswith("2)") or line.strip().startswith("3)"):
                    focus_areas.append(line.strip())
        
        observations_text = "\n".join(observations) if observations else "Нет наблюдений"
        focus_text = "\n".join(focus_areas) if focus_areas else "Нет рекомендаций"
        
        await update.message.reply_text(
            T(lang, "company_stage_complete", 
              stage=stage_info, 
              score=score,
              observations=observations_text,
              focus_areas=focus_text),
            reply_markup=company_stage_keyboard(10, True)
        )
        
        # Сохраняем для экспорта
        context.user_data["export_company_stage"] = {
            "stage": stage_info,
            "score": score,
            "observations": observations,
            "focus_areas": focus_areas,
            "answers": answers
        }
        
        # Сохраняем инсайты
        save_insights(
            context,
            last_scenario="Полный анализ этапа компании",
            last_verdict=f"Этап: {stage_info}, Баллы: {score}/100",
            risk_level="Детальный анализ"
        )
        
    except Exception as e:
        logger.error(f"Error in stage analysis: {e}")
        await update.message.reply_text(
            "⚠️ Не удалось завершить анализ. Попробуйте позже.",
            reply_markup=company_stage_keyboard(10, True)
        )
    
    # Очищаем состояние
    context.user_data.pop(COMPANY_STAGE_STATE, None)
    context.user_data.pop(STAGE_STEP_KEY, None)
    context.user_data.pop(STAGE_TEASER_KEY, None)

async def handle_company_stage_export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик экспорта анализа этапа"""
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "ru")
    
    if not is_user_premium(user_id):
        await update.message.reply_text(
            T(lang, "need_premium_for_export"),
            reply_markup=premium_keyboard()
        )
        return
    
    stage_data = context.user_data.get("export_company_stage")
    if not stage_data:
        await update.message.reply_text(
            T(lang, "no_data_for_export"),
            reply_markup=ReplyKeyboardMarkup(
                [
                    [KeyboardButton("📊 Бизнес-анализ")],
                    [KeyboardButton(BTN_BACK)],
                ],
                resize_keyboard=True,
            )
        )
        return
    
    # Формируем текст для экспорта
    export_text = f"📈 Анализ этапа компании\n\n"
    export_text += f"Этап: {stage_data['stage']}\n"
    export_text += f"Оценка: {stage_data['score']}/100 баллов\n\n"
    export_text += "📋 Ответы на вопросы:\n"
    for i in range(1, 11):
        export_text += f"{i}. {stage_data['answers'].get(f'q{i}', 'Нет ответа')}\n"
    
    export_text += "\n🔍 Ключевые наблюдения:\n"
    for i, obs in enumerate(stage_data['observations'], 1):
        export_text += f"{i}. {obs}\n"
    
    export_text += "\n🎯 Фокусы для развития:\n"
    for i, focus in enumerate(stage_data['focus_areas'], 1):
        export_text += f"{i}. {focus}\n"
    
    export_text += "\n⚠️ Это аналитический ориентир, а не рекомендация.\n"
    export_text += "Решение и ответственность остаются за вами."
    
    # Сохраняем для экспортных модулей
    context.user_data["pdf_title"] = "Анализ этапа компании"
    context.user_data["export_text"] = export_text
    
    await update.message.reply_text(
        T(lang, "export_success"),
        reply_markup=ReplyKeyboardMarkup(
            [
                [KeyboardButton("📄 Скачать PDF"), KeyboardButton("📊 Скачать Excel")],
                [KeyboardButton(BTN_BACK)],
            ],
            resize_keyboard=True,
        )
    )
