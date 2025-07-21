import logging
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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

class ChannelBotLambda:
    def __init__(self):
        """Initialize the bot for Lambda deployment"""
        self.application = None
        self.setup_application()
    
    def setup_application(self):
        """Set up the Telegram application"""
        try:
            # Create application
            self.application = Application.builder().token(BOT_TOKEN).build()
            
            # Add handlers
            self.setup_handlers()
            
            logger.info("🤖 Telegram Channel Bot initialized for Lambda")
            logger.info(f"Bot token: {BOT_TOKEN[:10]}...")
            logger.info(f"Owner ID: {OWNER_ID}")
            logger.info(f"Required channels: {len(REQUIRED_CHANNELS)}")
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise
    
    def setup_handlers(self):
        """Set up command and callback handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CommandHandler("pending", self.pending_command))
        self.application.add_handler(CommandHandler("get_chat_id", self.get_chat_id_command))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handler for unknown commands
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.unknown_message))
    
    async def start_command(self, update: Update, context):
        """Handle /start command"""
        user = update.effective_user
        user_id = user.id
        
        logger.info(f"User {user_id} ({user.username}) started the bot")
        
        # Save user to database
        db.add_user(user_id, user.username or "Unknown", user.first_name or "Unknown")
        
        welcome_text = f"""
🎬 **Welcome to Insta Viral Videos Bot!**

Hello {user.first_name}! 👋

To access our exclusive content, you need to join all our required channels first.

Click the button below to see the channels you need to join.
        """
        
        keyboard = [
            [InlineKeyboardButton("📺 View Required Channels", callback_data="view_channels")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def view_channels(self, update: Update, context):
        """Show required channels"""
        channels_text = "📺 **Required Channels to Join:**\n\n"
        
        for i, (name, link) in enumerate(REQUIRED_CHANNELS.items(), 1):
            channels_text += f"{i}. [{name}]({link})\n"
        
        channels_text += "\n✅ **After joining all channels, click the button below:**"
        
        keyboard = [
            [InlineKeyboardButton("✅ I've Joined All Channels", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query = update.callback_query
        await query.edit_message_text(channels_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def check_membership(self, update: Update, context):
        """Check if user has joined all required channels"""
        query = update.callback_query
        user_id = query.from_user.id
        
        await query.answer("Checking your membership...")
        
        # Check membership in all channels
        not_joined = []
        
        for channel_name, chat_id in CHAT_IDS.items():
            try:
                member = await context.bot.get_chat_member(chat_id, user_id)
                if member.status in ['left', 'kicked']:
                    not_joined.append(channel_name)
            except TelegramError as e:
                logger.error(f"Error checking membership for {channel_name}: {e}")
                not_joined.append(channel_name)
        
        if not_joined:
            # User hasn't joined all channels
            not_joined_text = "❌ **You haven't joined all required channels yet!**\n\n"
            not_joined_text += "**Please join these channels:**\n"
            
            for channel in not_joined:
                if channel in REQUIRED_CHANNELS:
                    not_joined_text += f"• [{channel}]({REQUIRED_CHANNELS[channel]})\n"
            
            not_joined_text += "\n**After joining, click the button again.**"
            
            keyboard = [
                [InlineKeyboardButton("📺 View Required Channels", callback_data="view_channels")],
                [InlineKeyboardButton("✅ I've Joined All Channels", callback_data="check_membership")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(not_joined_text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            # User has joined all channels
            success_text = """
🎉 **Congratulations!** 

You have successfully joined all required channels! 

Now you can request access to our private content.
            """
            
            keyboard = [
                [InlineKeyboardButton("🔗 Request Private Link", callback_data="request_link")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(success_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def request_link(self, update: Update, context):
        """Handle private link request"""
        query = update.callback_query
        user_id = query.from_user.id
        username = query.from_user.username or "Unknown"
        
        # Add request to database
        db.add_link_request(user_id, username)
        
        await query.answer("Request submitted!")
        
        request_text = """
📝 **Link Request Submitted!**

Your request for a private link has been submitted to the admins.

You will be notified once an admin approves your request.

Thank you for your patience! 🙏
        """
        
        keyboard = [
            [InlineKeyboardButton("🏠 Back to Start", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(request_text, reply_markup=reply_markup, parse_mode='Markdown')
        
        # Notify admins
        await self.notify_admins_new_request(context, user_id, username)
    
    async def notify_admins_new_request(self, context, user_id, username):
        """Notify admins about new link request"""
        notification_text = f"""
🔔 **New Link Request**

User: @{username} (ID: {user_id})
Time: {db.get_current_time()}

Use /pending to review all pending requests.
        """
        
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(admin_id, notification_text, parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Failed to notify admin {admin_id}: {e}")
    
    async def admin_command(self, update: Update, context):
        """Handle /admin command"""
        user_id = update.effective_user.id
        
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("❌ You are not authorized to use this command.")
            return
        
        admin_text = """
🔧 **Admin Panel**

Welcome to the admin panel. Here you can manage link requests and bot settings.
        """
        
        keyboard = [
            [InlineKeyboardButton("📋 View Pending Requests", callback_data="admin_pending")],
            [InlineKeyboardButton("📊 Bot Statistics", callback_data="admin_stats")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(admin_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def pending_command(self, update: Update, context):
        """Handle /pending command"""
        user_id = update.effective_user.id
        
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("❌ You are not authorized to use this command.")
            return
        
        pending_requests = db.get_pending_requests()
        
        if not pending_requests:
            await update.message.reply_text("✅ No pending link requests.")
            return
        
        for request in pending_requests:
            request_id, user_id, username, request_time = request
            
            request_text = f"""
📝 **Link Request #{request_id}**

User: @{username} (ID: {user_id})
Requested: {request_time}
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve_{request_id}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject_{request_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(request_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def get_chat_id_command(self, update: Update, context):
        """Get chat ID for the current chat"""
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        
        response_text = f"""
🆔 **Chat Information**

Chat ID: `{chat_id}`
Chat Type: {chat_type}
        """
        
        await update.message.reply_text(response_text, parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context):
        """Handle button callbacks"""
        query = update.callback_query
        data = query.data
        
        try:
            if data == "view_channels":
                await self.view_channels(update, context)
            elif data == "check_membership":
                await self.check_membership(update, context)
            elif data == "request_link":
                await self.request_link(update, context)
            elif data == "back_to_start":
                await self.back_to_start(update, context)
            elif data == "admin_pending":
                await self.admin_pending(update, context)
            elif data == "admin_stats":
                await self.admin_stats(update, context)
            elif data.startswith("approve_"):
                request_id = int(data.split("_")[1])
                await self.approve_request(update, context, request_id)
            elif data.startswith("reject_"):
                request_id = int(data.split("_")[1])
                await self.reject_request(update, context, request_id)
            elif data.startswith("genlink_"):
                parts = data.split("_")
                request_id = int(parts[1])
                channel_name = parts[2]
                await self.generate_invite_link(update, context, request_id, channel_name)
        except Exception as e:
            logger.error(f"Error in button callback: {e}")
            await query.answer("An error occurred. Please try again.")
    
    async def back_to_start(self, update: Update, context):
        """Go back to start message"""
        query = update.callback_query
        user = query.from_user
        
        welcome_text = f"""
🎬 **Welcome to Insta Viral Videos Bot!**

Hello {user.first_name}! 👋

To access our exclusive content, you need to join all our required channels first.

Click the button below to see the channels you need to join.
        """
        
        keyboard = [
            [InlineKeyboardButton("📺 View Required Channels", callback_data="view_channels")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def admin_pending(self, update: Update, context):
        """Show pending requests in admin panel"""
        query = update.callback_query
        
        pending_requests = db.get_pending_requests()
        
        if not pending_requests:
            await query.edit_message_text("✅ No pending link requests.")
            return
        
        requests_text = "📋 **Pending Link Requests:**\n\n"
        
        for request in pending_requests[:5]:  # Show first 5 requests
            request_id, user_id, username, request_time = request
            requests_text += f"#{request_id}: @{username} ({request_time})\n"
        
        if len(pending_requests) > 5:
            requests_text += f"\n... and {len(pending_requests) - 5} more requests."
        
        requests_text += "\n\nUse /pending command to review and approve/reject requests."
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="back_to_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(requests_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def admin_stats(self, update: Update, context):
        """Show bot statistics"""
        query = update.callback_query
        
        total_users = db.get_total_users()
        pending_requests = len(db.get_pending_requests())
        
        stats_text = f"""
📊 **Bot Statistics**

👥 Total Users: {total_users}
📝 Pending Requests: {pending_requests}
📺 Required Channels: {len(REQUIRED_CHANNELS)}
        """
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="back_to_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(stats_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def approve_request(self, update: Update, context, request_id):
        """Approve a link request"""
        query = update.callback_query
        
        # Get request details
        request = db.get_request_by_id(request_id)
        if not request:
            await query.answer("Request not found.")
            return
        
        user_id, username = request[1], request[2]
        
        # Show channel selection for link generation
        channels_text = "🔗 **Select Channel for Private Link:**\n\n"
        channels_text += "Choose which channel to generate a private invite link for:"
        
        keyboard = []
        for channel_name in CHAT_IDS.keys():
            keyboard.append([InlineKeyboardButton(
                f"🔗 {channel_name}", 
                callback_data=f"genlink_{request_id}_{channel_name}"
            )])
        
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="admin_pending")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(channels_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def generate_invite_link(self, update: Update, context, request_id, channel_name):
        """Generate invite link for approved request"""
        query = update.callback_query
        
        try:
            # Get request details
            request = db.get_request_by_id(request_id)
            if not request:
                await query.answer("Request not found.")
                return
            
            user_id, username = request[1], request[2]
            
            # Get chat ID for the channel
            chat_id = CHAT_IDS.get(channel_name)
            if not chat_id:
                await query.answer("Channel not found.")
                return
            
            # Generate invite link
            invite_link = await context.bot.create_chat_invite_link(
                chat_id=chat_id,
                member_limit=1,  # Single use link
                name=f"Private link for @{username}"
            )
            
            # Mark request as approved
            db.approve_request(request_id)
            
            # Send link to user
            link_message = f"""
🎉 **Your Private Link Request Approved!**

Here's your exclusive invite link for **{channel_name}**:

{invite_link.invite_link}

⚠️ **Important:**
- This link is for you only
- It can only be used once
- Don't share it with others

Enjoy the exclusive content! 🎬
            """
            
            try:
                await context.bot.send_message(user_id, link_message, parse_mode='Markdown')
                
                # Confirm to admin
                await query.edit_message_text(
                    f"✅ **Request Approved!**\n\n"
                    f"Private link for **{channel_name}** sent to @{username}.",
                    parse_mode='Markdown'
                )
                
            except Exception as e:
                logger.error(f"Failed to send link to user {user_id}: {e}")
                await query.edit_message_text(
                    f"⚠️ **Link Generated but Failed to Send**\n\n"
                    f"Link: {invite_link.invite_link}\n\n"
                    f"Please send this link manually to @{username}.",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Failed to generate invite link: {e}")
            await query.answer("Failed to generate invite link. Please try again.")
    
    async def reject_request(self, update: Update, context, request_id):
        """Reject a link request"""
        query = update.callback_query
        
        # Get request details
        request = db.get_request_by_id(request_id)
        if not request:
            await query.answer("Request not found.")
            return
        
        user_id, username = request[1], request[2]
        
        # Mark request as rejected
        db.reject_request(request_id)
        
        # Notify user
        rejection_message = """
❌ **Link Request Rejected**

Unfortunately, your request for a private link has been rejected by the admins.

You can try requesting again later or contact support if you believe this was an error.
        """
        
        try:
            await context.bot.send_message(user_id, rejection_message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Failed to notify user {user_id} about rejection: {e}")
        
        # Confirm to admin
        await query.edit_message_text(
            f"❌ **Request Rejected**\n\n"
            f"Request from @{username} has been rejected and user notified.",
            parse_mode='Markdown'
        )
    
    async def unknown_message(self, update: Update, context):
        """Handle unknown messages"""
        await update.message.reply_text(
            "🤖 I don't understand that command. Use /start to begin or /admin for admin functions."
        )

# Global instance for Lambda
bot_instance = ChannelBotLambda()

