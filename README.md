# Telegram Channel Bot

A Telegram bot that manages channel access by requiring users to join all specified channels before using the bot, with admin-approved private link generation capabilities.

## Features

- **Channel Verification**: Users must join all required channels to access the bot
- **Admin Panel**: Admins can view and manage link requests
- **Private Link Generation**: Bot generates private invite links for approved requests
- **Database Management**: Simple JSON-based database for user and request tracking

## Setup Instructions for PythonAnywhere

### 1. Upload Files

Upload all the files from this project to your PythonAnywhere account:
- `bot.py` - Main bot file
- `config.py` - Configuration settings
- `database.py` - Database handler
- `.env` - Environment variables (create this file)
- `requirements.txt` - Python dependencies

### 2. Create Environment File

Create a `.env` file with your bot token:
```
BOT_TOKEN=7797381180:AAFPikEzAxSfK-3SLe-lEwhRKyj5oldpzb0
```

### 3. Install Dependencies

In the PythonAnywhere console, navigate to your project directory and install dependencies:
```bash
pip3.10 install --user -r requirements.txt
```

### 4. Configure Bot Settings

Edit `config.py` to update:
- `OWNER_ID` - Your Telegram user ID
- `ADMIN_IDS` - List of admin user IDs
- `REQUIRED_CHANNELS` - List of channel IDs that users must join

### 5. Set Up Bot as Admin

Make sure your bot (`@Instaviralmmsbot`) is an administrator in all your private channels with the following permissions:
- Invite Users via Link
- Manage Chat

### 6. Run the Bot

In the PythonAnywhere console:
```bash
python3.10 bot.py
```

### 7. Keep Bot Running (Always On Task)

For the bot to run continuously, you'll need to:
1. Go to your PythonAnywhere dashboard
2. Navigate to the "Tasks" tab
3. Create a new "Always On Task"
4. Set the command to: `python3.10 /home/yourusername/path/to/bot.py`

## Bot Commands

### User Commands
- `/start` - Start the bot and check channel requirements
- `/help` - Show help message
- `/status` - Check your membership status
- `/request_link` - Request a private channel link

### Admin Commands
- `/admin` - Show admin panel
- `/pending` - View pending link requests
- `/get_chat_id` - Get chat ID (use in channels/groups)

## Configuration

The bot is configured with the following channels:
- Main channel: -1002625009980
- Hot forced: -1002377251009
- Premium 4k: -1002668202156
- Backup: -1002712524806

## Database

The bot uses a simple JSON file (`bot_data.json`) to store:
- User information and access status
- Pending link requests
- Approved/rejected requests

## Troubleshooting

1. **Bot not responding**: Check if the bot token is correct and the bot is running
2. **Channel verification failing**: Ensure the bot is an admin in all required channels
3. **Link generation failing**: Verify the bot has "Invite Users via Link" permission
4. **Database errors**: Check file permissions for `bot_data.json`

## Support

If you encounter any issues, check the console logs for error messages and ensure all requirements are met.

