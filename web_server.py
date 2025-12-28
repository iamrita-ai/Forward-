from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>🚀 Serena Forward Bot</h1><p>Service is running!</p>'

@app.route('/health')
def health():
    return {'status': 'ok'}

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    print("=== SERENA FORWARD BOT ===")
    
    # Import and start bot
    from app.main import start_bot
    
    # Start bot in background thread
    print("Starting bot...")
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    print("Bot thread started")
    
    # Start web server
    print("Starting web server...")
    run_web()
