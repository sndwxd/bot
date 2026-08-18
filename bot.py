import telebot
from telebot import types
import subprocess
import os
import psutil
import time
import requests

# ===== ТВОИ ДАННЫЕ =====
TOKEN = "8872125997:AAFGiMBGIfKmDVZIV7gNx58FK8H9oSB4mFQ"
ADMIN_ID = 7924628949

bot = telebot.TeleBot(TOKEN)

def is_admin(message):
    return message.from_user.id == ADMIN_ID

# ============================================
# ГЛАВНОЕ МЕНЮ С КНОПКАМИ
# ============================================
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("📊 Система")
    btn2 = types.KeyboardButton("📋 Процессы")
    btn3 = types.KeyboardButton("⚡ Выполнить CMD")
    btn4 = types.KeyboardButton("💀 Убить процесс")
    btn5 = types.KeyboardButton("🌐 Мой IP")
    btn6 = types.KeyboardButton("🏓 Пинг")
    btn7 = types.KeyboardButton("⏹ Выключить ПК")
    btn8 = types.KeyboardButton("🔄 Перезагрузить ПК")
    btn9 = types.KeyboardButton("🔒 Блокировка")
    btn10 = types.KeyboardButton("📸 Скриншот")
    btn11 = types.KeyboardButton("💬 Уведомление")
    btn12 = types.KeyboardButton("❓ Помощь")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10, btn11, btn12)
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    if not is_admin(message): return
    bot.send_message(
        message.chat.id,
        "🎮 **ПУЛЬТ УПРАВЛЕНИЯ ПК**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👋 Привет! Я управляю твоим компьютером.\n"
        "Нажми на кнопку ниже, чтобы начать.\n\n"
        "⚠️ **Важно:** Скриншоты, уведомления, выключение и перезагрузка работают ТОЛЬКО если у тебя запущена локальная версия бота на ПК.",
        parse_mode='Markdown',
        reply_markup=main_menu()
    )

# ============================================
# ОБРАБОТКА КНОПОК
# ============================================

# --- Кнопка "Система" ---
@bot.message_handler(func=lambda message: message.text == "📊 Система")
def info_btn(message):
    if not is_admin(message): return
    
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    cpu_bar = "█" * int(cpu/10) + "░" * (10 - int(cpu/10))
    mem_bar = "█" * int(mem.percent/10) + "░" * (10 - int(mem.percent/10))
    disk_bar = "█" * int(disk.percent/10) + "░" * (10 - int(disk.percent/10))
    
    text = (
        "📊 **СИСТЕМА**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚡ CPU  {cpu}%\n"
        f"`{cpu_bar}`\n\n"
        f"💾 RAM  {mem.percent}%\n"
        f"`{mem_bar}`\n\n"
        f"💿 Disk {disk.percent}%\n"
        f"`{disk_bar}`\n\n"
        f"📦 Процессов: {len(psutil.pids())}"
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=main_menu())

# --- Кнопка "Процессы" ---
@bot.message_handler(func=lambda message: message.text == "📋 Процессы")
def ps_btn(message):
    if not is_admin(message): return
    
    processes = []
    for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except:
            pass
    
    processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
    top = processes[:5]
    
    if not top:
        bot.send_message(message.chat.id, "❌ Не удалось получить список процессов", reply_markup=main_menu())
        return
    
    text = "📊 **ТОП ПРОЦЕССОВ**\n━━━━━━━━━━━━━━━━━━━━━\n"
    for i, p in enumerate(top, 1):
        cpu = p.get('cpu_percent', 0)
        mem = p.get('memory_percent', 0)
        name = p.get('name', 'unknown')[:20]
        text += f"{i}. `{name}`\n   ⚡{cpu:.0f}%  💾{mem:.1f}%\n"
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=main_menu())

# --- Кнопка "Выполнить CMD" ---
@bot.message_handler(func=lambda message: message.text == "⚡ Выполнить CMD")
def cmd_btn(message):
    if not is_admin(message): return
    msg = bot.send_message(
        message.chat.id,
        "📟 Введи команду, которую нужно выполнить.\n"
        "Например: `ipconfig` или `dir`",
        parse_mode='Markdown',
        reply_markup=main_menu()
    )
    bot.register_next_step_handler(msg, execute_cmd)

def execute_cmd(message):
    if not is_admin(message): return
    command = message.text.strip()
    
    try:
        result = subprocess.check_output(command, shell=True, text=True, 
                                        stderr=subprocess.STDOUT, 
                                        encoding='cp866', timeout=30)
        if len(result) > 4000:
            result = result[:4000] + "\n...обрезано"
        bot.send_message(
            message.chat.id,
            f"📟 **{command}**\n```\n{result}\n```",
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
    except subprocess.TimeoutExpired:
        bot.send_message(message.chat.id, "⏰ Команда выполнялась слишком долго (больше 30 секунд)", reply_markup=main_menu())
    except Exception:
        bot.send_message(message.chat.id, "❌ Ошибка при выполнении команды. Проверь правильность ввода.", reply_markup=main_menu())

# --- Кнопка "Убить процесс" ---
@bot.message_handler(func=lambda message: message.text == "💀 Убить процесс")
def kill_btn(message):
    if not is_admin(message): return
    msg = bot.send_message(
        message.chat.id,
        "💀 Введи имя процесса для завершения.\n"
        "Например: `chrome.exe` или `notepad.exe`",
        parse_mode='Markdown',
        reply_markup=main_menu()
    )
    bot.register_next_step_handler(msg, execute_kill)

def execute_kill(message):
    if not is_admin(message): return
    name = message.text.strip()
    
    try:
        result = subprocess.run(f"taskkill /f /im {name}", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            bot.send_message(message.chat.id, f"✅ Процесс **{name}** успешно завершён", parse_mode='Markdown', reply_markup=main_menu())
        else:
            bot.send_message(message.chat.id, f"❌ Процесс **{name}** не найден. Возможно, он уже закрыт.", parse_mode='Markdown', reply_markup=main_menu())
    except:
        bot.send_message(message.chat.id, "❌ Ошибка при завершении процесса", reply_markup=main_menu())

# --- Кнопка "Мой IP" ---
@bot.message_handler(func=lambda message: message.text == "🌐 Мой IP")
def ip_btn(message):
    if not is_admin(message): return
    try:
        ip = requests.get('https://api.ipify.org', timeout=5).text
        bot.send_message(message.chat.id, f"🌐 **Твой внешний IP:**\n`{ip}`", parse_mode='Markdown', reply_markup=main_menu())
    except:
        bot.send_message(message.chat.id, "❌ Не удалось получить IP-адрес", reply_markup=main_menu())

# --- Кнопка "Пинг" ---
@bot.message_handler(func=lambda message: message.text == "🏓 Пинг")
def ping_btn(message):
    if not is_admin(message): return
    start = time.time()
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(0.5)
    ping = int((time.time() - start) * 1000)
    
    if ping < 150:
        emoji = "🟢"
    elif ping < 400:
        emoji = "🟡"
    else:
        emoji = "🔴"
    
    bot.send_message(message.chat.id, f"{emoji} **Пинг:** {ping} мс", parse_mode='Markdown', reply_markup=main_menu())

# --- Кнопка "Помощь" ---
@bot.message_handler(func=lambda message: message.text == "❓ Помощь")
def help_btn(message):
    if not is_admin(message): return
    bot.send_message(
        message.chat.id,
        "🎮 **ПУЛЬТ УПРАВЛЕНИЯ ПК**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📌 **Что умеет бот:**\n"
        "├ Показывать загрузку CPU/RAM/Disk\n"
        "├ Показывать топ процессов\n"
        "├ Выполнять любые CMD команды\n"
        "├ Завершать процессы\n"
        "├ Показывать внешний IP\n"
        "└ Проверять задержку (пинг)\n\n"
        "⚠️ **Скриншоты, уведомления и управление питанием**\n"
        "работают ТОЛЬКО с локальной версией бота на ПК.\n\n"
        "📱 **Просто нажимай на кнопки!**",
        parse_mode='Markdown',
        reply_markup=main_menu()
    )

# --- Кнопки с предупреждением (локальные функции) ---
@bot.message_handler(func=lambda message: message.text in ["📸 Скриншот", "💬 Уведомление", "⏹ Выключить ПК", "🔄 Перезагрузить ПК", "🔒 Блокировка"])
def local_only(message):
    if not is_admin(message): return
    
    if message.text == "📸 Скриншот":
        bot.send_message(
            message.chat.id,
            "📸 **Скриншот**\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "❌ На сервере скриншоты не работают.\n\n"
            "✅ **Как сделать скриншот:**\n"
            "1. Скачай локальную версию бота\n"
            "2. Запусти её на своём ПК\n"
            "3. Напиши `/ss` в Telegram\n\n"
            "🔗 Локальная версия:\n"
            "https://github.com/sndwxd/bot",
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
    elif message.text == "💬 Уведомление":
        msg = bot.send_message(
            message.chat.id,
            "💬 Отправь текст уведомления, которое появится на ПК.\n"
            "Например: `Пора сделать перерыв!`",
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
        bot.register_next_step_handler(msg, send_notify)
    elif message.text == "⏹ Выключить ПК":
        bot.send_message(
            message.chat.id,
            "⏹ **Выключение ПК**\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "❌ Эта команда работает ТОЛЬКО с локальной версией бота.\n\n"
            "✅ Запусти локальную версию на ПК и напиши `/shutdown`",
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
    elif message.text == "🔄 Перезагрузить ПК":
        bot.send_message(
            message.chat.id,
            "🔄 **Перезагрузка ПК**\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "❌ Эта команда работает ТОЛЬКО с локальной версией бота.\n\n"
            "✅ Запусти локальную версию на ПК и напиши `/reboot`",
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
    elif message.text == "🔒 Блокировка":
        bot.send_message(
            message.chat.id,
            "🔒 **Блокировка ПК**\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "❌ Эта команда работает ТОЛЬКО с локальной версией бота.\n\n"
            "✅ Запусти локальную версию на ПК и напиши `/lock`",
            parse_mode='Markdown',
            reply_markup=main_menu()
        )

def send_notify(message):
    if not is_admin(message): return
    text = message.text.strip()
    if not text:
        bot.send_message(message.chat.id, "❌ Текст не может быть пустым", reply_markup=main_menu())
        return
    
    bot.send_message(
        message.chat.id,
        f"💬 **Уведомление**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 Текст: `{text}`\n\n"
        "⚠️ Для отправки нужно запустить локальную версию бота на ПК.",
        parse_mode='Markdown',
        reply_markup=main_menu()
    )

# ============================================
# ЗАПУСК
# ============================================
if __name__ == '__main__':
    print("🔥 Бот с кнопками запущен!")
    print(f"👤 ADMIN ID: {ADMIN_ID}")
    
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            time.sleep(5)
