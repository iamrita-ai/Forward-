from flask import Flask
import threading
import os
from app.main import start_bot

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>🚀 Serena Forward Bot</h1>
    <p>Bot is running successfully!</p>
    <p>Status: <span style="color: green;">ONLINE</span></p>
    '''

@app.route('/health')
def health():
    return {'status': 'ok', 'bot': 'running'}

def run_web():
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting web server on port {port}")
    app.run(host='0.0.0.0', port=port, threaded=True)

if __name__ == '__main__':
    # Start bot in separate thread
    print("Starting Telegram bot...")
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start web server
    print("Starting web server...")
    run_web()
