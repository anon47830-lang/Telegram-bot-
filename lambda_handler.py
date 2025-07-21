import json
import logging
import os
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram.error import TelegramError

from config import *
from database import db

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Import the bot class from our existing bot.py
from bot import ChannelBot

# Initialize the bot instance
channel_bot = ChannelBot()

async def lambda_handler(event, context):
    """
    AWS Lambda handler function for Telegram webhook
    """
    try:
        # Parse the incoming webhook data
        body = json.loads(event.get('body', '{}'))
        
        # Create an Update object from the webhook data
        update = Update.de_json(body, channel_bot.application.bot)
        
        if update:
            # Process the update using the bot's application
            await channel_bot.application.process_update(update)
            
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'ok'})
        }
        
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def handler(event, context):
    """
    Synchronous wrapper for the async lambda_handler
    """
    import asyncio
    
    # Create a new event loop for this invocation
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Run the async handler
        result = loop.run_until_complete(lambda_handler(event, context))
        return result
    finally:
        loop.close()

