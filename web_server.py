from flask import Flask
import threading
import os
import logging

# Disable Flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>🚀 Serena Forward Bot</h1>
    <p>Bot service is running successfully!</p>
    <p>Status: <span style="color: green;">ONLINE</span></p>
    <p><a href="/health">Health Check</a></p>
    '''

@app.route('/health')
def health():
    return {'status': 'ok', 'service': 'running', 'bot': 'loaded'}

def run_web():
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting web server on port {port}")
    app.run(host='0.0.0.0', port=port, threaded=True)

if __name__ == '__main__':
    print("=== SERENA FORWARD BOT LAUNCHER ===")
    
    # Import and start bot
    try:
        print("Loading bot modules...")
        from app.main import start_bot, app as bot_app
        print("✅ Bot modules loaded successfully")
        print(f"Bot app object: {type(bot_app)}")
    except Exception as e:
        print(f"❌ Error loading bot modules: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    
    # Start bot in separate thread
    print("Starting Telegram bot in background thread...")
    try:
        bot_thread = threading.Thread(target=start_bot, name="BotThread")
        bot_thread.daemon = True
        bot_thread.start()
        print("✅ Bot thread started successfully!")
        print(f"Bot thread is alive: {bot_thread.is_alive()}")
    except Exception as e:
        print(f"❌ Error starting bot thread: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    
    # Give the bot thread a moment to start
    import time
    time.sleep(3)
    print(f"Bot thread status after 3 seconds: {bot_thread.is_alive()}")
    
    # Start web server
    print("Starting web server...")
    run_web()
