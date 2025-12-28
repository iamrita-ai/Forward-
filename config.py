import os
from dotenv import load_dotenv

load_dotenv()

print("Loading configuration...")

# Telegram API Credentials
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

print(f"API_ID: {API_ID if API_ID != 0 else 'NOT SET'}")
print(f"API_HASH: {'SET' if API_HASH else 'NOT SET'}")
print(f"BOT_TOKEN: {'SET' if BOT_TOKEN else 'NOT SET'}")

# MongoDB URL
MONGO_URI = os.getenv("MONGO_URI", "")

# Owner IDs
OWNER_IDS = list(map(int, os.getenv("OWNER_IDS", "1598576202,6518065496").split(",")))

# Channels
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "-1003286415377"))
FORCE_SUB_LINK = os.getenv("FORCE_SUB_LINK", "https://t.me/serenaunzipbot")

# Contact Info
CONTACT_LINKS = os.getenv("CONTACT_LINKS", "@technicalserena,@Xioqui_xin").split(",")

# Limits
FREE_LIMIT = int(os.getenv("FREE_LIMIT", 100))
PREMIUM_LIMIT = int(os.getenv("PREMIUM_LIMIT", 1000))

# Images
START_PIC = os.getenv("START_PIC", "https://graph.org/file/your_start_image.jpg")

# Bot Control
BOT_STATUS = os.getenv("BOT_STATUS", "on")  # "on" or "off"

# Progress Settings
PROGRESS_DELAY = int(os.getenv("PROGRESS_DELAY", "7"))  # seconds between updates

print("Configuration loaded successfully!")
