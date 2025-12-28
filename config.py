import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API Credentials
API_ID = int(os.getenv("API_ID", "YOUR_API_ID"))
API_HASH = os.getenv("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")

# MongoDB URL
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://...")

# Owner IDs
OWNER_IDS = list(map(int, os.getenv("OWNER_IDS", "1598576202,6518065496").split(",")))

# Channels
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "-1003286415377"))
FORCE_SUB_LINK = os.getenv("FORCE_SUB_LINK", "https://t.me/serenaunzipbot")

# Contact Info
CONTACT_LINKS = os.getenv("CONTACT_LINKS", "@technicalserena,@Xioqui_xin")

# Limits
FREE_LIMIT = int(os.getenv("FREE_LIMIT", 100))
PREMIUM_LIMIT = int(os.getenv("PREMIUM_LIMIT", 1000))

# Images
START_PIC = os.getenv("START_PIC", "https://graph.org/file/your_start_image.jpg")
