import os
import threading
from flask import Flask
from bot import bot

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    
    def run_bot():
        bot.infinity_polling()
    
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=port)