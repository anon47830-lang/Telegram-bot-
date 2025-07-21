# Complete Deployment Guide for PythonAnywhere

This guide will walk you through deploying your Telegram Channel Bot on PythonAnywhere step by step.

## Prerequisites

1. A PythonAnywhere account (free tier is sufficient)
2. Your bot token: `7797381180:AAFPikEzAxSfK-3SLe-lEwhRKyj5oldpzb0`
3. Your Telegram user ID: `7662679752`
4. Your bot must be added as admin to all channels

## Step 1: Upload Files to PythonAnywhere

1. Log into your PythonAnywhere account
2. Go to the "Files" tab
3. Create a new folder called `telegram_bot`
4. Upload these files to the folder:
   - `bot.py`
   - `config.py`
   - `database.py`
   - `requirements.txt`

## Step 2: Create Environment File

1. In the `telegram_bot` folder, create a new file called `.env`
2. Add this content:
```
BOT_TOKEN=7797381180:AAFPikEzAxSfK-3SLe-lEwhRKyj5oldpzb0
```

## Step 3: Install Dependencies

1. Go to the "Consoles" tab in PythonAnywhere
2. Start a new Bash console
3. Navigate to your bot folder:
```bash
cd telegram_bot
```
4. Install the required packages:
```bash
pip3.10 install --user python-telegram-bot python-dotenv
```

## Step 4: Configure Your Channels

Make sure your bot `@Instaviralmmsbot` is added as an administrator to all these channels with these permissions:
- **Invite Users via Link** ✅
- **Manage Chat** ✅

Your channels (already configured):
- Main channel: -1002625009980
- Hot forced: -1002377251009  
- Premium 4k: -1002668202156
- Backup: -1002712524806

## Step 5: Test the Bot

1. In the console, run:
```bash
python3.10 bot.py
```
2. If you see "🤖 Starting Telegram Channel Bot..." and no errors, the bot is working
3. Test by sending `/start` to `@Instaviralmmsbot` on Telegram
4. Press Ctrl+C to stop the test

## Step 6: Set Up Always-On Task

1. Go to the "Tasks" tab in PythonAnywhere
2. Click "Create a new always-on task"
3. Set the command to:
```
python3.10 /home/yourusername/telegram_bot/bot.py
```
(Replace `yourusername` with your actual PythonAnywhere username)
4. Click "Create"

## Step 7: Verify Everything Works

1. Send `/start` to your bot
2. Try the channel verification process
3. As an admin, try `/admin` and `/pending`
4. Test the private link generation

## Troubleshooting

### Bot Not Responding
- Check if the Always-On Task is running
- Verify the bot token is correct
- Check the console logs for errors

### Channel Verification Failing
- Ensure bot is admin in ALL channels
- Verify channel IDs are correct
- Check bot has proper permissions

### Link Generation Not Working
- Bot needs "Invite Users via Link" permission
- Verify bot is admin in the target channel
- Check for error messages in logs

## Important Notes

- The free PythonAnywhere tier allows one Always-On Task
- The bot will automatically restart if it crashes
- Database is stored in `bot_data.json` in the same folder
- Logs can be viewed in the Tasks tab

Your bot is now ready to use! Users will need to join all your channels before they can request private links.

