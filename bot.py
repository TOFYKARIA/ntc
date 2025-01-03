import asyncio
import os
import json
import requests
from telethon import TelegramClient, events
import time

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

# --- Команда .пинг ---
@client.on(events.NewMessage(pattern=r"\.пинг"))
async def ping(event):
    if event.sender_id == OWNER_ID:
        start_time = time.time()
        msg = await event.respond("📡 Проверка задержки...")
        end_time = time.time()
        delay = round((end_time - start_time) * 1000)  # Задержка в миллисекундах
        await msg.edit(f"📡 Задержка: {delay}ms")
    else:
        msg = await event.respond("❌ У вас нет доступа для использования этой команды.")
        await msg.edit("❌ У вас нет доступа для использования этой команды.")

# --- Команда .помощь ---
@client.on(events.NewMessage(pattern=r"\.помощь"))
async def help_command(event):
    if event.sender_id == OWNER_ID:
        help_message = """
        🤖 Список команд:

        1. `.токен <token>` - Устанавливает токен для логирования.
        2. `.лог все` - Включает логирование всех чатов.
        3. `.лог лс` - Включает логирование личных сообщений.
        4. `.лог @username` - Включает логирование чата по @username.
        5. `.задачи` - Показывает текущие настройки задач (логирование).
        6. `.пинг` - Показывает задержку сервера.
        7. `.логстоп` - Останавливает логирование всех сообщений.
        
        🤖 Примечание:
        - Все команды редактируются автоматически.
        
        📲 Бот разработан и поддерживается пользователем @neetchan.
        """
        msg = await event.respond(help_message)
        await msg.edit(help_message)  # Редактируем сразу
    else:
        msg = await event.respond("❌ У вас нет доступа для использования этой команды.")
        await msg.edit("❌ У вас нет доступа для использования этой команды.")

# --- Команда .логстоп ---
@client.on(events.NewMessage(pattern=r"\.логстоп"))
async def log_stop(event):
    if event.sender_id == OWNER_ID:
        log_modes["all"] = False
        log_modes["ls"] = False
        log_modes["chats"] = {}
        await event.respond("✅ Логирование всех сообщений отключено.")
    else:
        await event.respond("❌ У вас нет доступа для использования этой команды.")

# --- Логирование изменения сообщений ---
@client.on(events.MessageEdited)
async def on_message_edited(event):
    if log_modes["all"] or log_modes["ls"]:
        log_message = f"✏️ Сообщение от <a href='tg://user?id={event.sender_id}'>@{event.sender.username}</a> изменено в чате <a href='https://t.me/c/{event.chat_id}/{event.message.id}'>Чат</a>: {event.text}"
        await send_log_message(log_message)

    if log_modes["chats"].get(event.chat_id, False):
        log_message = f"✏️ Сообщение от <a href='tg://user?id={event.sender_id}'>@{event.sender.username}</a> изменено в чате <a href='https://t.me/c/{event.chat_id}/{event.message.id}'>Чат</a>: {event.text}"
        await send_log_message(log_message)

# --- Логирование удаления сообщений ---
@client.on(events.MessageDeleted)
async def on_message_deleted(event):
    if log_modes["all"] or log_modes["ls"]:
        deleted_message = f"❌ Сообщение удалено от <a href='tg://user?id={event.sender_id}'>@{event.sender.username}</a>."
        await send_log_message(deleted_message)

    for chat_id in log_modes["chats"]:
        if chat_id == event.chat_id or log_modes["all"]:
            deleted_message = f"❌ Сообщение удалено в чате <a href='https://t.me/c/{event.chat_id}/{event.message.id}'>Чат</a> от <a href='tg://user?id={event.sender_id}'>@{event.sender.username}</a>."
            await send_log_message(deleted_message)

# --- Запуск бота ---
async def main():
    print("Бот Shizuku запущен. Приятной работы.")
    await client.start()  # Подключение к Telegram
    await client.run_until_disconnected()  # Ожидание событий

if __name__ == "__main__":
    asyncio.run(main())
