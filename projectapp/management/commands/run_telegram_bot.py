from django.core.management.base import BaseCommand
import telebot
from projectapp.models import Task

bot = telebot.TeleBot("6764195321:AAET-gCOzOnGh3zeWQ9WKf2ESSDVe7yRMAA")  # Вставьте свой токен

# Флаг, который будет использоваться для хранения текущего шага пользователя
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я твой todo-бот. Используй /help, чтобы узнать доступные команды.")

@bot.message_handler(commands=['tasks'])
def tasks(message):
    tasks_list = Task.objects.all()
    
    if tasks_list:
        response_message = "\n\n".join([f"Task: {task.title}\nDescription: {task.description}\nStatus: {'Выполнено' if task.completed else 'Не выполнено'}" for task in tasks_list])
    else:
        response_message = "Список задач пуст. Используй /add, чтобы добавить новую задачу."

    bot.send_message(message.chat.id, response_message)

@bot.message_handler(commands=['help'])
def help_command(message):
    help_message = (
        "Доступные команды:\n"
        "/start - Начать взаимодействие с ботом\n"
        "/tasks - Вывести список всех задач\n"
        "/help - Показать это сообщение\n"
        "/add - Добавить новую задачу\n"
        "/delete - Удалить задачу\n"
        "/complete - Отметить задачу как выполненную"
    )
    bot.send_message(message.chat.id, help_message)

@bot.message_handler(commands=['add'])
def add_task(message):
    bot.send_message(message.chat.id, "Введите название и описание задачи через запятую (например, Новая задача, Описание):")
    # Устанавливаем флаг текущего шага в 'add'
    user_data[message.chat.id] = 'add'

@bot.message_handler(func=lambda message: user_data.get(message.chat.id) == 'add')
def process_add(message):
    try:
        title, description = map(str.strip, message.text.split(','))
        task = Task.objects.create(title=title, description=description)
        bot.send_message(message.chat.id, f"Задача '{task.title}' успешно добавлена!")
    except ValueError:
        bot.send_message(message.chat.id, "Некорректный формат. Попробуйте еще раз.")
    
    # Сбрасываем флаги в user_data
    user_data[message.chat.id] = None

@bot.message_handler(commands=['delete'])
def delete_task(message):
    tasks_list = Task.objects.all()
    
    if tasks_list:
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for task in tasks_list:
            button_text = f"{task.title} - {'Выполнено' if task.completed else 'Не выполнено'}"
            keyboard.add(button_text)

        bot.send_message(message.chat.id, "Выберите задачу для удаления:", reply_markup=keyboard)
        # Устанавливаем флаг текущего шага в 'delete'
        user_data[message.chat.id] = 'delete'
    else:
        bot.send_message(message.chat.id, "Список задач пуст. Используй /add, чтобы добавить новую задачу.")

@bot.message_handler(func=lambda message: user_data.get(message.chat.id) == 'delete')
def process_delete(message):
    task_title = message.text.split(" - ")[0]
    try:
        task = Task.objects.get(title=task_title)
        task.delete()
        bot.send_message(message.chat.id, f"Задача '{task.title}' успешно удалена.")
    except Task.DoesNotExist:
        bot.send_message(message.chat.id, f"Задача с названием '{task_title}' не найдена.")
    
    # Сбрасываем флаги в user_data
    user_data[message.chat.id] = None

@bot.message_handler(commands=['complete'])
def complete_task(message):
    tasks_list = Task.objects.all()
    
    if tasks_list:
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for task in tasks_list:
            if not task.completed:
                button_text = f"{task.title} - Не выполнено"
                keyboard.add(button_text)

        if keyboard:
            bot.send_message(message.chat.id, "Выберите задачу для отметки как выполненную:", reply_markup=keyboard)
            # Устанавливаем флаг текущего шага в 'complete'
            user_data[message.chat.id] = 'complete'
        else:
            bot.send_message(message.chat.id, "Все задачи уже выполнены.")
    else:
        bot.send_message(message.chat.id, "Список задач пуст. Используй /add, чтобы добавить новую задачу.")

@bot.message_handler(func=lambda message: user_data.get(message.chat.id) == 'complete')
def process_complete(message):
    task_title = message.text.split(" - ")[0]
    try:
        task = Task.objects.get(title=task_title)
        task.completed = True
        task.save()
        bot.send_message(message.chat.id, f"Задача '{task.title}' отмечена как выполненная.")
    except Task.DoesNotExist:
        bot.send_message(message.chat.id, f"Задача с названием '{task_title}' не найдена.")
    
    # Сбрасываем флаги в user_data
    user_data[message.chat.id] = None

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

class Command(BaseCommand):
    help = 'Telegram bot command'

    def handle(self, *args, **kwargs):
        bot.polling(none_stop=True)
