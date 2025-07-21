import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))

# Channel configuration - Add your channel usernames/IDs here
REQUIRED_CHANNELS = [
    -1002625009980, # Main channel
    -1002377251009, # Hot forced
    -1002668202156, # Premium 4k
    -1002712524806  # Backup
]

# IMPORTANT: For private channels, the bot MUST be an administrator in each channel
# to be able to verify user membership and create invite links.
# Please replace the example chat_ids above with your actual channel chat_ids.
# You can get the chat_id by forwarding a message from your channel to @RawDataBot.
# Or, if the bot is already an admin, you can use a command like /get_chat_id in the channel.

# Admin user IDs who can approve private links
ADMIN_IDS = [OWNER_ID]  # Owner is automatically an admin

# Database file for storing user data and pending requests
DATABASE_FILE = 'bot_data.json'

# Messages
WELCOME_MESSAGE = """
🎉 Welcome to the Channel Access Bot!

To use this bot, you must join all our required channels first.
Click the button below to see the channels you need to join.
"""

CHANNELS_MESSAGE = """
📢 Please join all the following channels to access the bot:

{channels_list}

After joining all channels, click "✅ I've Joined All Channels" to verify your membership.
"""

ACCESS_GRANTED_MESSAGE = """
✅ Great! You have joined all required channels.
You now have access to the bot features.

Available commands:
/help - Show this help message
/status - Check your membership status
"""

MEMBERSHIP_REQUIRED_MESSAGE = """
❌ You need to join all required channels first.
Use /start to see the channels you need to join.
"""

