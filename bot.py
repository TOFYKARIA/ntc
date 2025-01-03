import os
import requests
from telethon import TelegramClient, events

# Запрос данных при запуске
API_ID = input("Введите ваш API_ID: ")
API_HASH = input("Введите ваш API_HASH: ")
OWNER_ID = int(input("Введите ваш Telegram ID: "))

SESSION_NAME = "shizuku"
bot_token = None

# Папка для скачивания модулей
MODULES_DIR = "./modules"

# Инициализация клиента
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# ID группы для логов
logs_group_id = None

async def create_logs_group():
    global logs_group_id
    # Попробуем найти существующую группу "Shizuku Logs"
    dialogs = await client.get_dialogs()
    for dialog in dialogs:
        if dialog.name == "Shizuku Logs":
            logs_group_id = dialog.id
            return

    # Если группа не найдена, создаём её
    try:
        new_group = await client(CreateChatRequest(users=[OWNER_ID], title="Shizuku Logs"))
        logs_group_id = new_group.chats[0].id
        print("Группа 'Shizuku Logs' успешно создана!")
    except Exception as e:
        print(f"Ошибка при создании группы: {e}")

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
                await client.send_message(logs_group_id, f"✅ Модуль '{file_name}' был успешно скачан и установлен.")
            else:
                await event.edit(f"❌ Ошибка при скачивании модуля с URL: {url}")
                await client.send_message(logs_group_id, f"⚠️ Ошибка при скачивании модуля с URL: {url}")
        except Exception as e:
            await event.edit(f"❌ Ошибка при скачивании модуля: {e}")
            await client.send_message(logs_group_id, f"⚠️ Ошибка при скачивании модуля: {str(e)}")
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
        """
        await event.edit(help_text)
        await client.send_message(logs_group_id, "📜 Отправлен запрос на помощь.")
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
                await client.send_message(logs_group_id, f"✅ Модуль '{module_name}' был успешно удалён.")
            else:
                await event.edit(f"❌ Модуль '{module_name}' не найден.")
                await client.send_message(logs_group_id, f"⚠️ Модуль '{module_name}' не найден для удаления.")
        except Exception as e:
            await event.edit(f"❌ Ошибка при удалении модуля: {e}")
            await client.send_message(logs_group_id, f"⚠️ Ошибка при удалении модуля '{module_name}': {str(e)}")
    else:
        await event.edit("❌ [Нет доступа]")

# --- Запуск ---
print("Shizuku запущен. Ожидание событий...")
await create_logs_group()  # Создание группы при старте

client.start()
client.run_until_disconnected()
