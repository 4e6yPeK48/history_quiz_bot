import asyncio
import logging

import nest_asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from config import token as bot_token

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# /start — выбор теста
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Тест 1", "Тест 2"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Здравствуй, товарищ. Я — товарищ Сталин.\nВыбирай испытание: «Тест 1 (Февральская и Октябрьская революции 1917 года)» или «Тест 2 (Великая Отечественная война)».",
        reply_markup=markup
    )


# Выбор теста
async def select_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip()

    if choice == "Тест 1":
        from questions_test1 import QUESTIONS
    elif choice == "Тест 2":
        from questions_test2 import QUESTIONS
    else:
        await update.message.reply_text("Пожалуйста, выбери «Тест 1» или «Тест 2».")
        return

    context.user_data["questions"] = QUESTIONS
    context.user_data["current"] = 0
    context.user_data["score"] = 0
    await send_question(update, context)


# Отправка вопроса
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = context.user_data["questions"]
    current = context.user_data["current"]

    if current >= len(questions):
        score = context.user_data["score"]

        if score >= 9:
            message = "Ты — гордость партии! Продолжай в том же духе."
        elif score >= 6:
            message = "Неплохо. Но тебе ещё есть куда расти, товарищ."
        elif score >= 3:
            message = "Слабовато, товарищ. Безграмотность — враг социализма!"
        else:
            message = "Позор, товарищ! Такой результат недостоин советского человека."

        await update.message.reply_text(
            f"Тест завершён, товарищ!\nПравильных ответов: {score} из {len(questions)}\n\n{message}",
            reply_markup=ReplyKeyboardMarkup(
                [["Тест 1", "Тест 2"]],
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
        context.user_data.clear()
        return

    q = questions[current]
    keyboard = [[option] for option in q["options"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(q["question"], reply_markup=markup)


# Обработка ответа
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text.strip()
    questions = context.user_data.get("questions")

    if not questions:
        await update.message.reply_text("Сначала выбери тест с помощью команды /start.")
        return

    q = questions[context.user_data["current"]]

    if answer == q["answer"]:
        context.user_data["score"] += 1
        await update.message.reply_text("✅ Верно!")
    else:
        await update.message.reply_text(f"❌ Неверно. Правильный ответ: {q['answer']}")

    context.user_data["current"] += 1
    await send_question(update, context)


# Точка входа
async def main():
    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^Тест 1|Тест 2$"), select_test))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    app.run_polling()


nest_asyncio.apply()
asyncio.get_event_loop().run_until_complete(main())
