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
    <p>Bot is running successfully!</p>
    <p>Status: <span style="color: green;">ONLINE</span></p>
    <p><a href="/health">Health Check</a></p>
    '''

@app.route('/health')
def health():
    return {'status': 'ok', 'bot': 'running', 'timestamp': str(os.time()) if hasattr(os, 'time') else 'unknown'}

def run_web():
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting web server on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, threaded=True)

if __name__ == '__main__':
    # Import and start bot
    print("Importing bot...")
    from app.main import start_bot
    
    # Start bot in separate thread
    print("Starting Telegram bot in background...")
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    print("Bot thread started!")
    
    # Start web server
    print("Starting web server...")
    run_web()
