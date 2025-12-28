from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>🚀 Serena Forward Bot</h1>
    <p>✅ Service is running successfully!</p>
    <p><strong>Status:</strong> <span style="color: green;">ONLINE</span></p>
    <p><strong>Bot:</strong> Should be responding to Telegram messages</p>
    '''

@app.route('/health')
def health():
    return {'status': 'ok', 'service': 'running'}

def run_web():
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 Web server listening on port {port}")
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 SERENA FORWARD BOT LAUNCHER")
    print("=" * 50)
    
    # Import and start bot
    print("📦 Loading bot modules...")
    from app.main import start_bot
    
    # Start bot in background thread
    print("🤖 Starting Telegram bot in background...")
    bot_thread = threading.Thread(target=start_bot, daemon=True, name="BotThread")
    bot_thread.start()
    print("✅ Bot thread started")
    print(f"📊 Bot thread status: {'Alive' if bot_thread.is_alive() else 'Dead'}")
    
    # Wait a moment and check again
    import time
    time.sleep(2)
    print(f"📊 Bot thread status after 2s: {'Alive' if bot_thread.is_alive() else 'Dead'}")
    
    # Start web server
    print("🌐 Starting web server...")
    run_web()
