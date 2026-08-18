import telebot
import subprocess
import os
import psutil
import time
import platform
from datetime import datetime
import requests

# ===== ТВОИ ДАННЫЕ =====
TOKEN = "8872125997:AAFGiMBGIfKmDVZIV7gNx58FK8H9oSB4mFQ"
ADMIN_ID = 7924628949

bot = telebot.TeleBot(TOKEN)

# ===== ПРОВЕРКА СКРИНШОТОВ =====
try:
    import pyautogui
    import io
    from PIL import Image
    SCREENSHOT_AVAILABLE = True
except:
    SCREENSHOT_AVAILABLE = False

def is_admin(message):
    return message.from_user.id == ADMIN_ID

# ============================================
# ГЛАВНОЕ МЕНЮ (/start)
# ============================================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    if not is_admin(message): return
    bot.reply_to(message, 
        "🔥 **ПУЛЬТ УПРАВЛЕНИЯ ПК**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 **Команды:**\n"
        "├ /info — загрузка системы\n"
        "├ /ss — скриншот экрана\n"
        "├ /cmd — выполнить команду\n"
        "├ /ps — топ процессов\n"
        "├ /kill — убить процесс\n"
        "├ /reboot — перезагрузка\n"
        "├ /shutdown — выключение\n"
        "├ /lock — блокировка ПК\n"
        "├ /ip — мой IP\n"
        "├ /ping — задержка\n"
        "└ /notify — уведомление\n\n"
        "💡 **Просто напиши текст** — выполнится как CMD",
        parse_mode='Markdown')

# ============================================
# ИНФО О СИСТЕМЕ (красиво)
# ============================================
@bot.message_handler(commands=['info'])
def info_cmd(message):
    if not is_admin(message): return
    
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    uptime = time.time() - psutil.boot_time()
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    
    # Визуальные индикаторы
    cpu_bar = "█" * int(cpu/10) + "░" * (10 - int(cpu/10))
    mem_bar = "█" * int(mem.percent/10) + "░" * (10 - int(mem.percent/10))
    disk_bar = "█" * int(disk.percent/10) + "░" * (10 - int(disk.percent/10))
    
    text = (
        "📊 **СИСТЕМА**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"💻 {platform.node()}\n"
        f"⏱  {hours}ч {minutes}мин\n\n"
        f"⚡ CPU  {cpu}%\n"
        f"`{cpu_bar}`\n\n"
        f"💾 RAM  {mem.percent}%\n"
        f"`{mem_bar}`\n\n"
        f"💿 Disk {disk.percent}%\n"
        f"`{disk_bar}`\n\n"
        f"📦 Процессов: {len(psutil.pids())}"
    )
    bot.reply_to(message, text, parse_mode='Markdown')

# ============================================
# СКРИНШОТ (сократил команду до /ss)
# ============================================
@bot.message_handler(commands=['ss'])
def screenshot_cmd(message):
    if not is_admin(message): return
    
    if not SCREENSHOT_AVAILABLE:
        bot.reply_to(message, "❌ Скриншоты только на ПК")
        return
    
    try:
        msg = bot.reply_to(message, "📸 Делаю скрин...")
        screenshot = pyautogui.screenshot()
        img_bytes = io.BytesIO()
        screenshot.save(img_bytes, format='JPEG', quality=85)
        img_bytes.seek(0)
        bot.delete_message(message.chat.id, msg.message_id)
        bot.send_photo(message.chat.id, img_bytes, caption="✅ Скриншот")
    except Exception as e:
        bot.reply_to(message, f"❌ {e}")

# ============================================
# CMD КОМАНДА
# ============================================
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
        bot.reply_to(message, f"📟 **{command}**\n```\n{result}\n```", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ {e}")

# ============================================
# ТОП ПРОЦЕССОВ (упростил вывод)
# ============================================
@bot.message_handler(commands=['ps'])
def ps_cmd(message):
    if not is_admin(message): return
    
    processes = []
    for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except:
            pass
    
    processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
    top = processes[:5]
    
    text = "📊 **ТОП ПРОЦЕССОВ**\n━━━━━━━━━━━━━━━━━━━━━\n"
    for i, p in enumerate(top, 1):
        cpu = p['cpu_percent']
        mem = p.get('memory_percent', 0)
        name = p['name'][:20]
        text += f"{i}. {name}\n   ⚡{cpu:.0f}%  💾{mem:.1f}%\n"
    
    bot.reply_to(message, text, parse_mode='Markdown')

# ============================================
# УБИТЬ ПРОЦЕСС
# ============================================
@bot.message_handler(commands=['kill'])
def kill_cmd(message):
    if not is_admin(message): return
    name = message.text.replace('/kill', '').strip()
    if not name:
        bot.reply_to(message, "❌ /kill chrome.exe")
        return
    
    try:
        os.system(f"taskkill /f /im {name} >nul 2>&1")
        bot.reply_to(message, f"✅ **{name}** убит")
    except:
        bot.reply_to(message, f"❌ Не найден {name}")

# ============================================
# ПЕРЕЗАГРУЗКА
# ============================================
@bot.message_handler(commands=['reboot'])
def reboot_cmd(message):
    if not is_admin(message): return
    bot.reply_to(message, "🔄 **Перезагрузка через 10 секунд**")
    time.sleep(10)
    os.system("shutdown /r /t 0")

# ============================================
# ВЫКЛЮЧЕНИЕ
# ============================================
@bot.message_handler(commands=['shutdown'])
def shutdown_cmd(message):
    if not is_admin(message): return
    bot.reply_to(message, "⏳ **Выключение через 15 секунд**")
    time.sleep(15)
    os.system("shutdown /s /t 0")

# ============================================
# БЛОКИРОВКА
# ============================================
@bot.message_handler(commands=['lock'])
def lock_cmd(message):
    if not is_admin(message): return
    os.system("rundll32.exe user32.dll,LockWorkStation")
    bot.reply_to(message, "🔒 **ПК заблокирован**")

# ============================================
# IP (только внешний)
# ============================================
@bot.message_handler(commands=['ip'])
def ip_cmd(message):
    if not is_admin(message): return
    try:
        external = requests.get('https://api.ipify.org', timeout=5).text
        bot.reply_to(message, f"🌐 **Мой IP:**\n`{external}`", parse_mode='Markdown')
    except:
        bot.reply_to(message, "❌ Не удалось получить IP")

# ============================================
# УВЕДОМЛЕНИЕ
# ============================================
@bot.message_handler(commands=['notify'])
def notify_cmd(message):
    if not is_admin(message): return
    text = message.text.replace('/notify', '').strip()
    if not text:
        bot.reply_to(message, "❌ /notify Текст")
        return
    
    os.system(f'msg * "{text}"')
    bot.reply_to(message, f"✅ **Уведомление:** {text}")

# ============================================
# ПИНГ
# ============================================
@bot.message_handler(commands=['ping'])
def ping_cmd(message):
    if not is_admin(message): return
    start = time.time()
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(0.5)
    ping = int((time.time() - start) * 1000)
    emoji = "🟢" if ping < 200 else "🟡" if ping < 500 else "🔴"
    bot.reply_to(message, f"{emoji} **Пинг:** {ping} мс", parse_mode='Markdown')

# ============================================
# ЛЮБОЙ ТЕКСТ КАК CMD
# ============================================
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
        bot.reply_to(message, f"📟 **{message.text}**\n```\n{result}\n```", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ {e}")

# ============================================
# ЗАПУСК
# ============================================
if __name__ == '__main__':
    print("🔥 Бот запущен!")
    print(f"👤 ID: {ADMIN_ID}")
    print("📸 Скриншоты:", "✅" if SCREENSHOT_AVAILABLE else "❌")
    
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            time.sleep(5)
