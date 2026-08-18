import telebot
import subprocess
import os
import psutil
import time
import platform
from datetime import datetime

# ===== ТВОИ ДАННЫЕ =====
TOKEN = "8872125997:AAFGiMBGIfKmDVZIV7gNx58FK8H9oSB4mFQ"
ADMIN_ID = 7924628949

bot = telebot.TeleBot(TOKEN)

# ===== ПРОВЕРКА: ЕСТЬ ЛИ ГРАФИЧЕСКИЙ ЭКРАН =====
try:
    import pyautogui
    import io
    from PIL import Image
    SCREENSHOT_AVAILABLE = True
except:
    SCREENSHOT_AVAILABLE = False
    print("⚠️ Скриншоты недоступны (запущено на сервере)")

def is_admin(message):
    return message.from_user.id == ADMIN_ID

@bot.message_handler(commands=['start'])
def start_cmd(message):
    if not is_admin(message): return
    bot.reply_to(message, 
        "🔥 **Бот для управления ПК**\n\n"
        "/info - система\n"
        "/screenshot - скрин (только на ПК)\n"
        "/cmd {команда} - CMD\n"
        "/ps - процессы\n"
        "/kill {имя} - убить процесс\n"
        "/shutdown - выключить\n"
        "/restart - перезагрузка\n"
        "/lock - блокировка\n"
        "/notify {текст} - уведомление\n"
        "/ip - IP-адрес\n"
        "/ping - пинг", 
        parse_mode='Markdown')

@bot.message_handler(commands=['info'])
def info_cmd(message):
    if not is_admin(message): return
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    bot.reply_to(message, 
        f"🖥 **Система**\nCPU: {cpu}%\nRAM: {mem.percent}%\nДиск: {disk.percent}%", 
        parse_mode='Markdown')

@bot.message_handler(commands=['screenshot'])
def screenshot_cmd(message):
    if not is_admin(message): return
    
    if not SCREENSHOT_AVAILABLE:
        bot.reply_to(message, "❌ Скриншоты недоступны на сервере")
        return
    
    try:
        screenshot = pyautogui.screenshot()
        img_bytes = io.BytesIO()
        screenshot.save(img_bytes, format='JPEG', quality=85)
        img_bytes.seek(0)
        bot.send_photo(message.chat.id, img_bytes, caption="📸 Скриншот")
    except Exception as e:
        bot.reply_to(message, f"❌ {e}")

@bot.message_handler(commands=['cmd'])
def cmd_cmd(message):
    if not is_admin(message): return
    command = message.text.replace('/cmd', '').strip()
    if not command:
        bot.reply_to(message, "❌ /cmd ipconfig")
        return
    try:
        result = subprocess.check_output(command, shell=True, text=True, 
                                        stderr=subprocess.STDOUT, 
                                        encoding='cp866', timeout=30)
        if len(result) > 4000:
            result = result[:4000] + "\n...обрезано"
        bot.reply_to(message, f"```\n{result}\n```", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ {e}")

@bot.message_handler(commands=['ps'])
def ps_cmd(message):
    if not is_admin(message): return
    processes = []
    for proc in psutil.process_iter(['name', 'cpu_percent']):
        try:
            processes.append(proc.info)
        except:
            pass
    processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
    top5 = processes[:5]
    text = "📊 **Топ процессов**\n"
    for i, p in enumerate(top5, 1):
        text += f"{i}. {p['name'][:15]} - CPU: {p['cpu_percent']:.1f}%\n"
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['kill'])
def kill_cmd(message):
    if not is_admin(message): return
    name = message.text.replace('/kill', '').strip()
    if not name:
        bot.reply_to(message, "❌ /kill chrome.exe")
        return
    os.system(f"taskkill /f /im {name}")
    bot.reply_to(message, f"✅ {name} убит")

@bot.message_handler(commands=['shutdown'])
def shutdown_cmd(message):
    if not is_admin(message): return
    bot.reply_to(message, "⏳ Выключение через 15 сек")
    time.sleep(15)
    os.system("shutdown /s /t 0")

@bot.message_handler(commands=['restart'])
def restart_cmd(message):
    if not is_admin(message): return
    bot.reply_to(message, "🔄 Перезагрузка через 10 сек")
    time.sleep(10)
    os.system("shutdown /r /t 0")

@bot.message_handler(commands=['lock'])
def lock_cmd(message):
    if not is_admin(message): return
    os.system("rundll32.exe user32.dll,LockWorkStation")
    bot.reply_to(message, "🔒 Заблокировано")

@bot.message_handler(commands=['notify'])
def notify_cmd(message):
    if not is_admin(message): return
    text = message.text.replace('/notify', '').strip()
    if not text:
        bot.reply_to(message, "❌ /notify Привет")
        return
    os.system(f'msg * "{text}"')
    bot.reply_to(message, f"✅ Уведомление: {text}")

@bot.message_handler(commands=['ip'])
def ip_cmd(message):
    if not is_admin(message): return
    try:
        import socket
        import requests
        local = socket.gethostbyname(socket.gethostname())
        external = requests.get('https://api.ipify.org', timeout=5).text
        bot.reply_to(message, f"🌐 Локальный: {local}\nВнешний: {external}")
    except:
        bot.reply_to(message, "❌ Ошибка IP")

@bot.message_handler(commands=['ping'])
def ping_cmd(message):
    if not is_admin(message): return
    start = time.time()
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(1)
    bot.reply_to(message, f"🏓 {int((time.time()-start)*1000)} мс")

@bot.message_handler(func=lambda message: True)
def text_cmd(message):
    if not is_admin(message): return
    if message.text.startswith('/'): return
    try:
        result = subprocess.check_output(message.text, shell=True, text=True, 
                                        stderr=subprocess.STDOUT, 
                                        encoding='cp866', timeout=30)
        if len(result) > 4000:
            result = result[:4000] + "\n...обрезано"
        bot.reply_to(message, f"```\n{result}\n```", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ {e}")

if __name__ == '__main__':
    print("🤖 Бот запущен")
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(f"Ошибка: {e}, перезапуск через 5 сек...")
            time.sleep(5)