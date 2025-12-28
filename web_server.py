from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>🚀 Serena Forward Bot - Diagnostics</h1>
    <p>System Status: Running</p>
    <p>Check Render logs for bot connection status</p>
    '''

def run_web():
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 Web server started on port {port}")
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    print("=== SERENA FORWARD BOT DIAGNOSTICS ===")
    
    # Import and start bot
    print("🔧 Loading bot diagnostics...")
    from app.main import start_bot
    
    # Start bot in background
    print("🤖 Starting bot diagnostics...")
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    print("✅ Bot diagnostics thread started")
    
    # Start web server
    print("🌐 Starting web interface...")
    run_web()
