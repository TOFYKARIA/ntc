import asyncio
import random
import os
from telethon import TelegramClient, events
import requests
import json
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

# Переменная для автопечати
auto_typing = False
auto_typing_message = ""

# Режимы логирования (инициализация с пустыми значениями)
log_modes = {
    "all": False,  # Логирование всех чатов
    "ls": False,   # Логирование личных сообщений
    "chats": {}    # Логирование для конкретных чатов
}

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
        msg = await event.respond(f"✅ Токен для логирования установлен: {bot_token}")
        await send_log_message(f"✅ Токен для логирования установлен.")
        await msg.edit(f"✅ Токен для логирования установлен: {bot_token}")
    else:
        msg = await event.respond("❌ У вас нет доступа для использования этой команды.")
        await msg.edit("❌ У вас нет доступа для использования этой команды.")

# --- Команды .лог ---
@client.on(events.NewMessage(pattern=r"\.лог все"))
async def log_all_chats(event):
    if event.sender_id == OWNER_ID:
        log_modes["all"] = True
        msg = await event.respond("✅ Логирование всех чатов включено.")
        await msg.edit("✅ Логирование всех чатов включено.")
    else:
        msg = await event.respond("❌ У вас нет доступа для использования этой команды.")
        await msg.edit("❌ У вас нет доступа для использования этой команды.")

@client.on(events.NewMessage(pattern=r"\.лог лс"))
async def log_ls(event):
    if event.sender_id == OWNER_ID:
        log_modes["ls"] = True
        msg = await event.respond("✅ Логирование всех личных сообщений включено.")
        await msg.edit("✅ Логирование всех личных сообщений включено.")
    else:
        msg = await event.respond("❌ У вас нет доступа для использования этой команды.")
        await msg.edit("❌ У вас нет доступа для использования этой команды.")

@client.on(events.NewMessage(pattern=r"\.лог (@?\w+)"))
async def log_chat(event):
    chat_identifier = event.pattern_match.group(1)
    if event.sender_id == OWNER_ID:
        if chat_identifier.startswith("@"):
            log_modes["chats"][chat_identifier] = True
        else:
            log_modes["chats"][int(chat_identifier)] = True
        msg = await event.respond(f"✅ Логирование чата '{chat_identifier}' включено.")
        await msg.edit(f"✅ Логирование чата '{chat_identifier}' включено.")
    else:
        msg = await event.respond("❌ У вас нет доступа для использования этой команды.")
        await msg.edit("❌ У вас нет доступа для использования этой команды.")

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
        
        # Статус автотайпа
        tasks_status += f"Автотайп: {'включен' if auto_typing else 'выключен'}\n"

        msg = await event.respond(tasks_status)
        await msg.edit(tasks_status)
    else:
        msg = await event.respond("❌ У вас нет доступа для использования этой команды.")
        await msg.edit("❌ У вас нет доступа для использования этой команды.")

# --- Команда .автотайп ---
@client.on(events.NewMessage(pattern=r"\.автотайп (.+)"))
async def start_auto_typing(event):
    global auto_typing, auto_typing_message
    if event.sender_id == OWNER_ID:
        if auto_typing:
            msg = await event.respond("❌ Автотайп уже включен.")
            await msg.edit("❌ Автотайп уже включен.")
            return
        auto_typing_message = event.pattern_match.group(1)
        auto_typing = True
        msg = await event.respond(f"✅ Автотайп включен. Будет имитироваться набор текста для сообщения: {auto_typing_message}")
        
        # Имитируем набор текста
        async def simulate_typing():
            for i in range(1, len(auto_typing_message) + 1):
                # Имитация набора текста (без отправки сообщения)
                await client.send_typing(OWNER_ID)
                await asyncio.sleep(random.uniform(0.1, 0.5))  # Задержка между символами

        # Запускаем имитацию печати
        await simulate_typing()

        await msg.edit(f"✅ Автотайп включен. Будет имитироваться набор текста для сообщения: {auto_typing_message}")

    else:
        msg = await event.respond("❌ У вас нет доступа для использования этой команды.")
        await msg.edit("❌ У вас нет доступа для использования этой команды.")

# --- Команда .автотайп стоп ---
@client.on(events.NewMessage(pattern=r"\.автотайп стоп"))
async def stop_auto_typing(event):
    global auto_typing
    if event.sender_id == OWNER_ID:
        if not auto_typing:
            msg = await event.respond("❌ Автотайп не был включен.")
            await msg.edit("❌ Автотайп не был включен.")
            return
        auto_typing = False
        msg = await event.respond("✅ Автотайп остановлен.")
        await msg.edit("✅ Автотайп остановлен.")
    else:
        msg = await event.respond("❌ У вас нет доступа для использования этой команды.")
        await msg.edit("❌ У вас нет доступа для использования этой команды.")

# --- Логирование изменения сообщений ---
@client.on(events.MessageEdited)
async def on_message_edited(event):
    if log_modes["all"] or log_modes["ls"]:
        # Получаем данные пользователя, который изменил сообщение
        user = await client.get_entity(event.sender_id)
        chat = await client.get_entity(event.chat_id)
        
        # Формируем ссылку на пользователя и чат
        user_link = f"<a href='tg://user?id={user.id}'>@{user.username if user.username else user.id}</a>"
        chat_link = f"<a href='https://t.me/c/{str(chat.id)[4:]}/{event.id}'>Чат</a>"

        log_message = f"✏️ Сообщение от {user_link} изменено в чате {chat_link}:\n{event.text}"
        msg = await send_log_message(log_message)
        await msg.edit(f"✏️ Сообщение от {user_link} изменено в чате {chat_link}:\n{event.text}")

    if log_modes["chats"].get(event.chat_id, False):
        user = await client.get_entity(event.sender_id)
        chat = await client.get_entity(event.chat_id)
        
        user_link = f"<a href='tg://user?id={user.id}'>@{user.username if user.username else user.id}</a>"
        chat_link = f"<a href='https://t.me/c/{str(chat.id)[4:]}/{event.id}'>Чат</a>"

        log_message = f"✏️ Сообщение от {user_link} изменено в чате {chat_link}:\n{event.text}"
        msg = await send_log_message(log_message)
        await msg.edit(f"✏️ Сообщение от {user_link} изменено в чате {chat_link}:\n{event.text}")

# --- Логирование удаления сообщений ---
@client.on(events.MessageDeleted)
async def on_message_deleted(event):
    if log_modes["all"] or log_modes["ls"]:
        user = await client.get_entity(event.sender_id)
        chat = await client.get_entity(event.chat_id)
        
        user_link = f"<a href='tg://user?id={user.id}'>@{user.username if user.username else user.id}</a>"
        chat_link = f"<a href='https://t.me/c/{str(chat.id)[4:]}/{event.id}'>Чат</a>"

        deleted_message = f"❌ Сообщение удалено от {user_link} в чате {chat_link}."
        msg = await send_log_message(deleted_message)
        await msg.edit(f"❌ Сообщение удалено от {user_link} в чате {chat_link}.")

    for chat_id in log_modes["chats"]:
        if chat_id == event.chat_id or log_modes["all"]:
            user = await client.get_entity(event.sender_id)
            chat = await client.get_entity(event.chat_id)
            
            user_link = f"<a href='tg://user?id={user.id}'>@{user.username if user.username else user.id}</a>"
            chat_link = f"<a href='https://t.me/c/{str(chat.id)[4:]}/{event.id}'>Чат</a>"

            deleted_message = f"❌ Сообщение удалено в чате {chat_link} от {user_link}."
            msg = await send_log_message(deleted_message)
            await msg.edit(f"❌ Сообщение удалено в чате {chat_link} от {user_link}.")

# --- Команда .пинг ---
@client.on(events.NewMessage(pattern=r"\.пинг"))
async def ping(event):
    if event.sender_id == OWNER_ID:
        start_time = time.time()
        # Отправляем сообщение с текстом
        msg = await event.respond("📡 Пингуем...")
        ping_time = time.time() - start_time
        # Редактируем сообщение с пингом
        await msg.edit(f"📡 Пинг: {ping_time * 1000:.2f} ms")
    else:
        msg = await event.respond("❌ У вас нет доступа для использования этой команды.")
        await msg.edit("❌ У вас нет доступа для использования этой команды.")

# --- Команда .помощь ---
@client.on(events.NewMessage(pattern=r"\.помощь"))
async def help_command(event):
    if event.sender_id == OWNER_ID:
        help_text = """
        Список команд:
        .токен <token> - Установить токен для логирования.
        .лог все - Включить логирование всех чатов.
        .лог лс - Включить логирование личных сообщений.
        .лог <chat> - Включить логирование для конкретного чата.
        .задачи - Показать текущие задачи.
        .автотайп <сообщение> - Включить автотайп (имитация набора текста).
        .автотайп стоп - Остановить автотайп.
        .пинг - Проверить пинг.
        """
        msg = await event.respond(help_text)
        await msg.edit(help_text)
    else:
        msg = await event.respond("❌ У вас нет доступа для использования этой команды.")
        await msg.edit("❌ У вас нет доступа для использования этой команды.")

# --- Запуск бота ---
async def main():
    print("Бот Shizuku запущен.")
    await client.start()  # Подключение к Telegram
    await client.run_until_disconnected()  # Ожидание событий

if __name__ == "__main__":
    asyncio.run(main())  # Используем asyncio для запуска асинхронной функции
