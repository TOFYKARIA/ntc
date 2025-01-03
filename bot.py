from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# Вставьте свой Telegram Bot токен и Hugging Face API ключ
TELEGRAM_TOKEN = "6389857601:AAG7ZWpdyVhmV-lU_iDcZNFsbuXWXSDxICM"
HUGGING_FACE_API_KEY = "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"  # Ваш ключ Hugging Face

# URL Hugging Face для использования модели
HUGGING_FACE_API_URL = "https://api-inference.huggingface.co/models/gpt2"  # Используем GPT-2 модель для примера

# Приветственное сообщение
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Приветик! Я Шизуку, твоя маленькая помощница! Давай дружить и болтать обо всём на свете!"
    )

# Обработка сообщений
async def chat_with_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    # Запрос к Hugging Face
    headers = {
        "Authorization": f"Bearer {HUGGING_FACE_API_KEY}"
    }
    payload = {
        "inputs": user_message
    }

    try:
        response = requests.post(HUGGING_FACE_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Проверяем на ошибки
        response_json = response.json()
        
        # Ответ от модели
        reply = response_json[0]["generated_text"]
        
        # Отправка ответа пользователю
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
