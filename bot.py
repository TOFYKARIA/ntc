from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai

# Вставьте свой Telegram Bot токен и OpenAI API ключ
TELEGRAM_TOKEN = "6389857601:AAG7ZWpdyVhmV-lU_iDcZNFsbuXWXSDxICM"
OPENAI_API_KEY = "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"

# Настройка OpenAI API
openai.api_key = OPENAI_API_KEY

# Приветственное сообщение
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Приветик! Я Шизуку, твоя маленькая помощница! Давай дружить и болтать обо всём на свете!"
    )

# Обработка сообщений
async def chat_with_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    # Запрос к ChatGPT
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты маленькая девочка по имени Шизуку. Ты веселая, добрая и говоришь с пользователями в женском детском тоне. "},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response['choices'][0]['message']['content']
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("Ой, кажется, что-то пошло не так... Попробуем снова позже!")

# Основная функция запуска бота
def main():
    # Создание приложения Telegram
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_with_gpt))

    # Запуск бота
    print("Бот Шизуку запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
