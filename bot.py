import asyncio
import random
import os
from telethon import TelegramClient, events
import requests
import time
import json

# Конфигурационный файл для хранения данных
config_file = "config.json"

# Проверка и загрузка конфигурации (API ID и API Hash)
def load_config():
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            config = json.load(file)
        return config.get('API_ID'), config.get('API_HASH')
    return None, None

# Сохранение конфигурации (API ID и API Hash)
def save_config(api_id, api_hash):
    config = {
        "API_ID": api_id,
        "API_HASH": api_hash
    }
    with open(config_file, 'w') as file:
        json.dump(config, file)

# Запрос API ID и API Hash, если их нет в конфиге
def get_api_credentials():
    api_id, api_hash = load_config()
    if api_id and api_hash:
        return api_id, api_hash
    else:
        print("Введите ваш API ID и API Hash.")
        api_id = input("API ID: ")
        api_hash = input("API Hash: ")
        save_config(api_id, api_hash)  # Сохраняем данные в файл
        return api_id, api_hash

# Получаем API ID и API Hash
API_ID, API_HASH = get_api_credentials()

# Ваш ID в Telegram (например, можно узнать через @userinfobot)
OWNER_ID = 1688880140  # Замените на ваш Telegram ID

# Инициализация клиента
client = TelegramClient('shizuku_bot', API_ID, API_HASH)

# Для хранения токена для логирования
bot_token = None

# Словарь для хранения активных режимов логирования
log_modes = {
    "all": False,
    "ls": False,
    "chats": {}
}

# Для хранения текущей авто-операции
auto_mode = None

# --- Функции для логирования ---
async def send_log_message(message):
    """Отправка сообщения в логирующий бот, если установлен токен, только вам."""
    if bot_token:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": OWNER_ID,  # Сообщения будут отправляться только вам
            "text": message
        }
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"Ошибка при отправке лога: {response.status_code}")

# --- Команда .токен ---
@client.on(events.NewMessage(pattern=r"\.токен (.+)"))
async def set_token(event):
    global bot_token
    if event.sender_id == OWNER_ID:
        bot_token = event.pattern_match.group(1)
        await event.respond(f"✅ Токен для логирования установлен: {bot_token}")
        await send_log_message(f"✅ Токен для логирования установлен.")
    else:
        await event.respond("❌ У вас нет доступа для использования этой команды.")

# --- Команды .лог ---
@client.on(events.NewMessage(pattern=r"\.лог все"))
async def log_all_chats(event):
    if event.sender_id == OWNER_ID:
        log_modes["all"] = True
        await event.respond("✅ Логирование всех чатов включено.")
    else:
        await event.respond("❌ У вас нет доступа для использования этой команды.")

@client.on(events.NewMessage(pattern=r"\.лог лс"))
async def log_ls(event):
    if event.sender_id == OWNER_ID:
        log_modes["ls"] = True
        await event.respond("✅ Логирование всех личных сообщений включено.")
    else:
        await event.respond("❌ У вас нет доступа для использования этой команды.")

@client.on(events.NewMessage(pattern=r"\.лог (@?\w+)"))
async def log_chat(event):
    chat_identifier = event.pattern_match.group(1)
    if event.sender_id == OWNER_ID:
        if chat_identifier.startswith("@"):
            log_modes["chats"][chat_identifier] = True
        else:
            log_modes["chats"][int(chat_identifier)] = True
        await event.respond(f"✅ Логирование чата '{chat_identifier}' включено.")
    else:
        await event.respond("❌ У вас нет доступа для использования этой команды.")

# --- Команда .задачи ---
@client.on(events.NewMessage(pattern=r"\.задачи"))
async def show_tasks(event):
    if event.sender_id == OWNER_ID:
        tasks_status = "📜 Статус задач:\n"

        # Логирование всех чатов
        tasks_status += f"Логирование всех чатов: {'включено' if log_modes['all'] else 'выключено'}\n"
        
        # Логирование личных сообщений
        tasks_status += f"Логирование личных сообщений: {'включено' if log_modes['ls'] else 'выключено'}\n"
        
        # Логирование чатов по ID или @username
        if log_modes["chats"]:
            tasks_status += "Логирование чатов по ID или @username:\n"
            for chat, enabled in log_modes["chats"].items():
                tasks_status += f"  - {chat}: {'включено' if enabled else 'выключено'}\n"

        await event.respond(tasks_status)
    else:
        await event.respond("❌ У вас нет доступа для использования этой команды.")

# --- Команда .логстоп ---
@client.on(events.NewMessage(pattern=r"\.логстоп"))
async def log_stop(event):
    if event.sender_id == OWNER_ID:
        log_modes["all"] = False
        log_modes["ls"] = False
        log_modes["chats"] = {}
        await event.respond("✅ Логирование остановлено.")
    else:
        await event.respond("❌ У вас нет доступа для использования этой команды.")

# --- Функция для получения случайного изображения с API waifu ---
def get_random_waifu_image():
    url = "https://api.waifu.pics/sfw/waifu"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['url']
    return None

# --- Команда .аниме ---
@client.on(events.NewMessage(pattern=r"\.аниме"))
async def anime_command(event):
    if event.sender_id == OWNER_ID:  # Чтобы только вы могли использовать команду
        image_url = get_random_waifu_image()
        if image_url:
            # Отправляем изображение в чат
            msg = await event.respond(f"Вот случайное изображение для вас!\n{image_url}")
            await msg.delete()  # Удаляем сообщение через несколько секунд
        else:
            msg = await event.respond("❌ Не удалось получить изображение. Попробуйте позже.")
            await msg.delete()  # Удаляем сообщение через несколько секунд
    else:
        msg = await event.respond("❌ У вас нет доступа для использования этой команды.")
        await msg.delete()  # Удаляем сообщение через несколько секунд

# --- Команда .помощь ---
@client.on(events.NewMessage(pattern=r"\.помощь"))
async def help_command(event):
    if event.sender_id == OWNER_ID:
        help_text = """
        📜 Доступные команды:

        .токен <токен> - Установить токен для логирования.
        .лог все - Включить логирование всех чатов.
        .лог лс - Включить логирование личных сообщений.
        .лог [chat_id или @username] - Включить логирование для чата.
        .задачи - Показать текущий статус задач.
        .логстоп - Остановить логирование.
        .аниме - Отправить случайное изображение с API waifu.
        
        🖋️ Разработано @neetchan
        """
        await event.respond(help_text)
    else:
        await event.respond("❌ У вас нет доступа для использования этой команды.")

# --- Функция для обработки изменений и удалений сообщений ---
@client.on(events.MessageEdited)
async def on_message_edited(event):
    if log_modes["all"] or log_modes["ls"]:
        message = f"✏️ Сообщение от <a href='tg://user?id={event.sender_id}'>@{event.sender.username}</a> изменено в чате "
        if event.chat:
            chat_name = f"@{event.chat.username}" if event.chat.username else f"ID: {event.chat.id}"
            message += f"<a href='https://t.me/{chat_name}/{event.message.id}'>{chat_name}</a>: {event.text}"
        await send_log_message(message)

@client.on(events.MessageDeleted)
async def on_message_deleted(event):
    if log_modes["all"] or log_modes["ls"]:
        message = f"❌ Сообщение удалено от <a href='tg://user?id={event.sender_id}'>@{event.sender.username}</a>."
        if event.chat:
            chat_name = f"@{event.chat.username}" if event.chat.username else f"ID: {event.chat.id}"
            message += f" В чате <a href='https://t.me/{chat_name}/{event.message.id}'>{chat_name}</a>."
        await send_log_message(message)

# --- Запуск бота ---
async def main():
    print("Бот Shizuku запущен. Приятной работы.")
    await client.start()  # Подключение к Telegram
    await client.run_until_disconnected()  # Ожидание событий

if __name__ == "__main__":
    asyncio.run(main())  # Используем asyncio для запуска асинхронной функции
