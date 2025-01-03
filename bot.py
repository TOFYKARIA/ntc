import asyncio
import random
import os
from telethon import TelegramClient, events
import requests
import time

# Ваши данные
API_ID = 'your_api_id'
API_HASH = 'your_api_hash'
OWNER_ID = 123456789  # Ваш Telegram ID

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

        # Авто-операции
        if auto_mode:
            tasks_status += f"Авто-операция включена: {auto_mode['type']} (тип: {auto_mode['description']})"
        else:
            tasks_status += "Авто-операция: отключена"

        await event.respond(tasks_status)
    else:
        await event.respond("❌ У вас нет доступа для использования этой команды.")

# --- Команда .авто [1-5] ---
@client.on(events.NewMessage(pattern=r"\.авто ([1-5])"))
async def set_auto_mode(event):
    global auto_mode
    if event.sender_id == OWNER_ID:
        mode = int(event.pattern_match.group(1))
        
        if auto_mode:  # Если уже включена авто-операция, нельзя включить другую
            await event.respond("❌ Уже включена авто-операция. Отключите ее командой .-авто.")
            return
        
        if mode == 1:
            auto_mode = {"type": "Автопечаталка", "description": "Бесконечно отправляются сообщения"}
            while auto_mode:
                await client.send_message(OWNER_ID, f"Автопечаталка: {random.choice(['Привет!', 'Как дела?', 'Я тут'])}")
                await asyncio.sleep(1)
        elif mode == 2:
            auto_mode = {"type": "Авто запись кружка", "description": "Бесконечно повторяется запись в чате"}
            while auto_mode:
                await client.send_message(OWNER_ID, "Авто запись кружка: повторяю запись...")
                await asyncio.sleep(1)
        elif mode == 3:
            auto_mode = {"type": "Имитация игры", "description": "Бесконечно имитируется действие игры"}
            while auto_mode:
                await client.send_message(OWNER_ID, "Играю в игру...")
                await asyncio.sleep(1)
        elif mode == 4:
            auto_mode = {"type": "Отправка фото", "description": "Бесконечно отправляются фото"}
            while auto_mode:
                await client.send_file(OWNER_ID, 'path_to_photo.jpg')
                await asyncio.sleep(1)
        elif mode == 5:
            auto_mode = {"type": "Отправка документа", "description": "Бесконечно отправляется документ"}
            while auto_mode:
                await client.send_file(OWNER_ID, 'path_to_document.pdf')
                await asyncio.sleep(1)

        await event.respond(f"✅ Авто-операция {auto_mode['type']} включена.")
    else:
        await event.respond("❌ У вас нет доступа для использования этой команды.")

# --- Команда .-авто ---
@client.on(events.NewMessage(pattern=r"\.\-авто"))
async def disable_auto_mode(event):
    global auto_mode
    if event.sender_id == OWNER_ID:
        auto_mode = None
        await event.respond("✅ Авто-операция отключена.")
    else:
        await event.respond("❌ У вас нет доступа для использования этой команды.")

# --- Логирование изменения сообщений ---
@client.on(events.MessageEdited)
async def on_message_edited(event):
    if log_modes["all"] or log_modes["ls"]:
        log_message = f"✏️ Сообщение от {event.sender_id} изменено:\n{event.text}"
        await send_log_message(log_message)

    if log_modes["chats"].get(event.chat_id, False):
        log_message = f"✏️ Сообщение от {event.sender_id} изменено в чате {event.chat_id}:\n{event.text}"
        await send_log_message(log_message)

# --- Логирование удаления сообщений ---
@client.on(events.MessageDeleted)
async def on_message_deleted(event):
    if log_modes["all"] or log_modes["ls"]:
        deleted_message = f"❌ Сообщение удалено от {event.sender_id}."
        await send_log_message(deleted_message)

    for chat_id in log_modes["chats"]:
        if chat_id == event.chat_id or log_modes["all"]:
            deleted_message = f"❌ Сообщение удалено в чате {event.chat_id} от {event.sender_id}."
            await send_log_message(deleted_message)

# --- Команда .пинг ---
@client.on(events.NewMessage(pattern=r"\.пинг"))
async def ping(event):
    if event.sender_id == OWNER_ID:
        start_time = time.time()
        await event.respond("📡 Проверка задержки...")
        end_time = time.time()
        delay = round((end_time - start_time) * 1000)  # Задержка в миллисекундах
        await event.respond(f"📡 Задержка: {delay}ms")
    else:
        await event.respond("❌ У вас нет доступа для использования этой команды.")

# --- Запуск бота ---
async def main():
    print("Бот Shizuku запущен.")
    await client.start()  # Подключение к Telegram
    await client.run_until_disconnected()  # Ожидание событий

if __name__ == "__main__":
    asyncio.run(main())  # Используем asyncio для запуска асинхронной функции
