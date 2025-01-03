import os
import requests
import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.messages import CreateChatRequest
from telethon.tl.functions.messages import SendMessageRequest

# Запрос данных при запуске
API_ID = input("Введите ваш API_ID: ")
API_HASH = input("Введите ваш API_HASH: ")
OWNER_ID = int(input("Введите ваш Telegram ID: "))

SESSION_NAME = "shizuku"
bot_token = None  # Токен бота, в который будут отправляться логи

# Папка для скачивания модулей
MODULES_DIR = "./modules"

# Инициализация клиента
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Используем существующий чат для логов
async def get_logs_bot(token):
    global bot_token
    bot_token = token

# --- Установка Python файла ---
@client.on(events.NewMessage(pattern=r"/установить (.+)"))
async def install_module(event):
    url = event.pattern_match.group(1).strip()
    if event.sender_id == OWNER_ID:
        try:
            # Создаем папку для модулей, если её нет
            if not os.path.exists(MODULES_DIR):
                os.makedirs(MODULES_DIR)
                
            # Загружаем файл
            response = requests.get(url)
            if response.status_code == 200:
                file_name = url.split("/")[-1]
                file_path = os.path.join(MODULES_DIR, file_name)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                await event.edit(f"✅ Модуль '{file_name}' успешно скачан и установлен.")
                if bot_token:
                    await send_log_message(f"✅ Модуль '{file_name}' был успешно скачан и установлен.")
            else:
                await event.edit(f"❌ Ошибка при скачивании модуля с URL: {url}")
                if bot_token:
                    await send_log_message(f"⚠️ Ошибка при скачивании модуля с URL: {url}")
        except Exception as e:
            await event.edit(f"❌ Ошибка при скачивании модуля: {e}")
            if bot_token:
                await send_log_message(f"⚠️ Ошибка при скачивании модуля: {str(e)}")
    else:
        await event.edit("❌ [Нет доступа]")

# --- Просмотр доступных команд (помощь) ---
@client.on(events.NewMessage(pattern=r"/помощь"))
async def help_command(event):
    if event.sender_id == OWNER_ID:
        help_text = """
        Доступные команды:
        
        /установить [URL] - Скачивает Python файл по указанному URL и сохраняет его в папку модулей.
        /помощь - Показать список доступных команд.
        /-удалить [имя файла] - Удалить указанный модуль (файл).
        /токен [токен] - Установить токен для логирования (логирование будет отправляться в этот бот).
        """
        await event.edit(help_text)
        if bot_token:
            await send_log_message("📜 Отправлен запрос на помощь.")
    else:
        await event.edit("❌ [Нет доступа]")

# --- Удаление модуля ---
@client.on(events.NewMessage(pattern=r"/-удалить (.+)"))
async def remove_module(event):
    module_name = event.pattern_match.group(1).strip()
    if event.sender_id == OWNER_ID:
        try:
            module_path = os.path.join(MODULES_DIR, module_name)
            if os.path.exists(module_path):
                os.remove(module_path)
                await event.edit(f"✅ Модуль '{module_name}' успешно удалён.")
                if bot_token:
                    await send_log_message(f"✅ Модуль '{module_name}' был успешно удалён.")
            else:
                await event.edit(f"❌ Модуль '{module_name}' не найден.")
                if bot_token:
                    await send_log_message(f"⚠️ Модуль '{module_name}' не найден для удаления.")
        except Exception as e:
            await event.edit(f"❌ Ошибка при удалении модуля: {e}")
            if bot_token:
                await send_log_message(f"⚠️ Ошибка при удалении модуля '{module_name}': {str(e)}")
    else:
        await event.edit("❌ [Нет доступа]")

# --- Установка токена для логирования ---
@client.on(events.NewMessage(pattern=r"/токен (.+)"))
async def set_token(event):
    global bot_token
    if event.sender_id == OWNER_ID:
        bot_token = event.pattern_match.group(1).strip()
        await event.edit(f"✅ Токен для логирования установлен: {bot_token}")
        await send_log_message(f"✅ Токен для логирования установлен.")
    else:
        await event.edit("❌ [Нет доступа]")

# --- Отправка логов в бот ---
async def send_log_message(message):
    if bot_token:
        try:
            # Отправляем сообщение в бот с токеном, который был установлен
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": OWNER_ID,
                "text": message
            }
            response = requests.post(url, data=payload)
            if response.status_code != 200:
                print(f"Ошибка при отправке лога: {response.status_code}")
        except Exception as e:
            print(f"Ошибка при отправке лога: {e}")
    else:
        print("Токен для логирования не установлен.")

# --- Главная асинхронная функция ---
async def main():
    print("Shizuku запущен. Ожидание событий...")
    await client.start()  # Подключение к Telegram
    await client.run_until_disconnected()  # Ожидание событий

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())  # Используем asyncio для запуска асинхронной функции
