from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from datetime import datetime, timedelta
import random
import json

# Вставьте свой токен
TOKEN = "6389857601:AAG7ZWpdyVhmV-lU_iDcZNFsbuXWXSDxICM"

# Путь к файлу для сохранения данных о пользователях
DATA_FILE = "users_data.json"

# Время мутирования
MUTE_TIME = timedelta(minutes=30)

# Максимальное количество варнов, после которых накладывается мут
MAX_WARNS = 3

# Начисление нямков
MIN_NYAMKI = 2
MAX_NYAMKI = 23

# Функция для загрузки данных из файла
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Функция для сохранения данных в файл
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# Функция для отправки сообщений
def send_message(update, message):
    update.message.reply_text(message)

# Команда /упомянуть — упомянуть пользователя
def mention(update: Update, context: CallbackContext):
    data = load_data()
    user_id = update.message.from_user.id
    
    if len(context.args) < 2:
        send_message(update, "❗ Используйте команду так: /упомянуть @username сообщение")
        return

    target_username = context.args[0].lstrip('@')
    message = " ".join(context.args[1:])
    
    if data.get(user_id, {}).get('nyamki', 0) < 10000:
        send_message(update, "❌ У вас недостаточно нямков для использования этой команды!")
        return
    
    # Уменьшаем нямки
    data[user_id]['nyamki'] -= 10000
    save_data(data)

    # Упоминание пользователя
    send_message(update, f"@{target_username}, вы упомянуты! {message}")

# Команда /кикнуть — кикнуть пользователя
def kick(update: Update, context: CallbackContext):
    data = load_data()
    user_id = update.message.from_user.id

    if len(context.args) < 1:
        send_message(update, "❗ Используйте команду так: /кикнуть @username")
        return

    target_username = context.args[0].lstrip('@')
    
    # Проверка на роль пользователя
    if data.get(user_id, {}).get('role') not in ['старший модератор', 'администратор']:
        send_message(update, "❌ У вас нет прав на кик этого пользователя!")
        return

    # Проверка на наличие достаточного количества нямков для кика
    if data.get(user_id, {}).get('nyamki', 0) < 100000:
        send_message(update, "❌ У вас недостаточно нямков для использования этой команды!")
        return
    
    # Уменьшаем нямки
    data[user_id]['nyamki'] -= 100000
    save_data(data)

    # Кикнем пользователя
    send_message(update, f"Пользователь @{target_username} был исключен из чата, но может вернуться.")

# Команда /мутить — мутить пользователя
def mute(update: Update, context: CallbackContext):
    data = load_data()
    user_id = update.message.from_user.id
    
    if len(context.args) < 1:
        send_message(update, "❗ Используйте команду так: /мутить @username")
        return

    target_username = context.args[0].lstrip('@')
    
    # Проверка на роль пользователя
    if data.get(user_id, {}).get('role') not in ['старший модератор', 'администратор']:
        send_message(update, "❌ У вас нет прав на мут этого пользователя!")
        return

    # Мутим пользователя на 30 минут
    mute_until = datetime.now() + MUTE_TIME
    data[user_id]['muted_until'] = mute_until.strftime('%Y-%m-%d %H:%M:%S')
    save_data(data)

    send_message(update, f"Пользователь @{target_username} был замучен на 30 минут.")

# Команда /повысить — повысить пользователя
def promote(update: Update, context: CallbackContext):
    data = load_data()
    user_id = update.message.from_user.id
    
    if len(context.args) < 1:
        send_message(update, "❗ Используйте команду так: /повысить @username")
        return
    
    target_username = context.args[0].lstrip('@')
    
    # Проверка на роль
    if data.get(user_id, {}).get('role') != 'администратор':
        send_message(update, "❌ У вас нет прав на повышение пользователей!")
        return

    # Повышаем роль пользователя
    data[target_username] = data.get(target_username, {})
    data[target_username]['role'] = 'старший модератор'  # Пример повышения
    save_data(data)

    send_message(update, f"Пользователь @{target_username} был повышен до старшего модератора.")

# Команда /понизить — понизить пользователя
def demote(update: Update, context: CallbackContext):
    data = load_data()
    user_id = update.message.from_user.id
    
    if len(context.args) < 1:
        send_message(update, "❗ Используйте команду так: /понизить @username")
        return
    
    target_username = context.args[0].lstrip('@')
    
    # Проверка на роль
    if data.get(user_id, {}).get('role') != 'администратор':
        send_message(update, "❌ У вас нет прав на понижение пользователей!")
        return

    # Понижаем роль пользователя
    data[target_username] = data.get(target_username, {})
    data[target_username]['role'] = 'младший модератор'  # Пример понижения
    save_data(data)

    send_message(update, f"Пользователь @{target_username} был понижен до младшего модератора.")

# Команда /снять — снять роль
def remove_role(update: Update, context: CallbackContext):
    data = load_data()
    user_id = update.message.from_user.id

    if len(context.args) < 1:
        send_message(update, "❗ Используйте команду так: /снять @username")
        return
    
    target_username = context.args[0].lstrip('@')
    
    # Проверка на роль
    if data.get(user_id, {}).get('role') != 'администратор':
        send_message(update, "❌ У вас нет прав на снятие роли у пользователя!")
        return

    # Убираем роль пользователя
    data[target_username]['role'] = 'пользователь'
    save_data(data)

    send_message(update, f"Роль у пользователя @{target_username} была снята.")

# Основная функция для запуска бота
def main():
    # Создаем экземпляр Updater с вашим токеном
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер, чтобы добавить обработчики команд
    dispatcher = updater.dispatcher

    # Добавляем обработчики команд
    dispatcher.add_handler(CommandHandler("упомянуть", mention))
    dispatcher.add_handler(CommandHandler("кикнуть", kick))
    dispatcher.add_handler(CommandHandler("мутить", mute))
    dispatcher.add_handler(CommandHandler("повысить", promote))
    dispatcher.add_handler(CommandHandler("понизить", demote))
    dispatcher.add_handler(CommandHandler("снять", remove_role))

    # Запуск бота
    updater.start_polling()

    # Ожидаем завершения работы
    updater.idle()

if __name__ == "__main__":
    main()
