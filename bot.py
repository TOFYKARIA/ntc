from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# Вставьте свой Telegram Bot токен и API ключ Hugging Face
TELEGRAM_TOKEN = "6389857601:AAG7ZWpdyVhmV-lU_iDcZNFsbuXWXSDxICM"
HUGGING_FACE_API_KEY = "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"
HUGGING_FACE_API_URL = "https://api-inference.huggingface.co/models/gpt2"  # Пример модели GPT2, используемой на Hugging Face

# Приветственное сообщение
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Приветик! Я Шизуку, твоя маленькая помощница! Давай дружить и играть! 🎉 Расскажи мне, что ты хочешь узнать или о чем поболтать! 🌟"
    )

# Обработка сообщений
async def chat_with_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем, что сообщение существует и содержит текст
    if update.message and update.message.text:
        user_message = update.message.text

        # Запрос к Hugging Face с добавлением детского стиля
        headers = {
            "Authorization": f"Bearer {HUGGING_FACE_API_KEY}"
        }
        payload = {
            "inputs": f"Ты маленькая девочка, очень веселая и наивная. Ты говоришь простыми словами, и отвечаешь с радостью и улыбкой. {user_message}"
        }

        try:
            response = requests.post(HUGGING_FACE_API_URL, headers=headers, json=payload)
            response.raise_for_status()  # Проверяем на ошибки
            response_json = response.json()
            
            # Ответ от модели
            reply = response_json[0]["generated_text"]
            
            # Отправка ответа пользователю
            await update.message.reply_text(f"Ой! Я думаю вот что по твоему вопросику: {reply} 😊🎈")
        except Exception as e:
            await update.message.reply_text("Ой-ой! Что-то пошло не так... Может попробуем позже? 😥")
    else:
        # Если нет текста в сообщении
        await update.message.reply_text("Эй! Ты что-то не написал... Давай поболтаем! ✨💖")

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
