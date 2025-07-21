import json
import logging
import asyncio
from telegram import Update
from bot_lambda import bot_instance

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """
    Main AWS Lambda handler function for Telegram webhook
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Parse the incoming webhook data
        if 'body' not in event:
            logger.error("No body in event")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No body in request'})
            }
        
        body = event['body']
        if isinstance(body, str):
            body = json.loads(body)
        
        logger.info(f"Parsed body: {json.dumps(body)}")
        
        # Create an Update object from the webhook data
        update = Update.de_json(body, bot_instance.application.bot)
        
        if update:
            # Process the update using asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(bot_instance.application.process_update(update))
            finally:
                loop.close()
            
            logger.info("Update processed successfully")
        else:
            logger.warning("No valid update found in request")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'status': 'ok'})
        }
        
    except Exception as e:
        logger.error(f"Error processing update: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }

