import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError
import asyncio

from config import *
from database import db

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ChannelBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup bot command and callback handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CommandHandler("pending", self.pending_command))
        self.application.add_handler(CommandHandler("request_link", self.request_link_command))
        self.application.add_handler(CommandHandler("get_chat_id", self.get_chat_id_command))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Add user to database
        db.add_user(user.id, user.username, user.first_name)
        
        # Check if user already has access
        if db.has_access(user.id):
            await update.message.reply_text(
                "✅ You already have access to the bot!\n\n"
                "Available commands:\n"
                "/help - Show help message\n"
                "/status - Check your status\n"
                "/request_link - Request a private channel link"
            )
            return
        
        # Show welcome message with channels
        keyboard = [[InlineKeyboardButton("📢 View Required Channels", callback_data="show_channels")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(WELCOME_MESSAGE, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not db.has_access(update.effective_user.id):
            await update.message.reply_text(MEMBERSHIP_REQUIRED_MESSAGE)
            return
        
        help_text = """
🤖 Bot Commands:

/start - Start the bot and check channel requirements
/help - Show this help message
/status - Check your membership status
/request_link - Request a private channel link

📢 Channel Requirements:
You must join all required channels to use this bot.
"""
        await update.message.reply_text(help_text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        user_id = update.effective_user.id
        user_data = db.get_user(user_id)
        
        if not user_data:
            await update.message.reply_text("❌ User not found. Please use /start first.")
            return
        
        status_text = f"""
👤 Your Status:
User ID: {user_id}
Access: {"✅ Granted" if user_data["has_access"] else "❌ Denied"}
Joined: {user_data["joined_at"][:10]}
"""
        
        if not user_data["has_access"]:
            status_text += "\n❗ You need to join all required channels first."
            keyboard = [[InlineKeyboardButton("📢 View Required Channels", callback_data="show_channels")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(status_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(status_text)
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command"""
        user_id = update.effective_user.id
        
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("❌ You don't have admin privileges.")
            return
        
        admin_text = """
🔧 Admin Panel:

/pending - View pending link requests
/admin - Show this admin panel
/get_chat_id - Get the chat ID of the current chat (use in channel/group)

To approve/reject requests, use the buttons in /pending command.
"""
        await update.message.reply_text(admin_text)
    
    async def pending_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pending command - show pending link requests"""
        user_id = update.effective_user.id
        
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("❌ You don't have admin privileges.")
            return
        
        pending_requests = db.get_pending_links()
        
        if not pending_requests:
            await update.message.reply_text("✅ No pending link requests.")
            return
        
        for request in pending_requests:
            request_text = f"""
📋 Link Request #{request["id"]}
👤 User: @{request["username"]} (ID: {request["user_id"]})
📝 Type: {request["link_type"]}
💬 Description: {request["description"]}
📅 Requested: {request["requested_at"][:16]}
"""
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve_{request['id']}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject_{request['id']}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(request_text, reply_markup=reply_markup)
    
    async def request_link_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /request_link command"""
        user_id = update.effective_user.id
        
        if not db.has_access(user_id):
            await update.message.reply_text(MEMBERSHIP_REQUIRED_MESSAGE)
            return
        
        # Simple link request (in a real bot, you might want a more sophisticated form)
        request_id = db.add_pending_link(
            user_id=user_id,
            username=update.effective_user.username or "Unknown",
            link_type="Private Channel Access",
            description="User requested private channel access"
        )
        
        await update.message.reply_text(
            f"✅ Your link request has been submitted (Request #{request_id}).\n"
            "An admin will review it shortly."
        )
        
        # Notify admins
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    admin_id,
                    f"🔔 New link request #{request_id} from @{update.effective_user.username}\n"
                    "Use /pending to review."
                )
            except:
                pass
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        if data == "show_channels":
            await self.show_channels(query)
        elif data == "check_membership":
            await self.check_membership(query, context)
        elif data.startswith("approve_"):
            request_id = int(data.split("_")[1])
            await self.approve_request(query, context, request_id)
        elif data.startswith("reject_"):
            request_id = int(data.split("_")[1])
            await self.reject_request(query, context, request_id)
        elif data.startswith("genlink_"):
            await self.generate_invite_link(query, context)
    
    async def show_channels(self, query):
        """Show required channels to user"""
        if not REQUIRED_CHANNELS:
            await query.edit_message_text(
                "⚠️ No channels configured yet. Please contact the bot owner."
            )
            return
        
        channels_list = "\n".join([f"• {channel}" for channel in REQUIRED_CHANNELS])
        message_text = CHANNELS_MESSAGE.format(channels_list=channels_list)
        
        keyboard = [[InlineKeyboardButton("✅ I've Joined All Channels", callback_data="check_membership")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message_text, reply_markup=reply_markup)
    
    async def check_membership(self, query, context):
        """Check if user has joined all required channels"""
        user_id = query.from_user.id
        
        if not REQUIRED_CHANNELS:
            # If no channels configured, grant access
            db.grant_access(user_id)
            await query.edit_message_text(ACCESS_GRANTED_MESSAGE)
            return
        
        # Check membership in each channel
        all_joined = True
        not_joined = []
        
        for channel_id in REQUIRED_CHANNELS:
            try:
                member = await context.bot.get_chat_member(channel_id, user_id)
                if member.status in ["left", "kicked"]:
                    all_joined = False
                    not_joined.append(channel_id)
            except TelegramError as e:
                logger.warning(f"Could not check membership for {channel_id}: {e}")
                # If bot can't check (e.g., not admin in channel, or invalid link),
                # assume user hasn't joined for safety.
                all_joined = False
                not_joined.append(channel_id)
        
        if all_joined:
            db.grant_access(user_id)
            await query.edit_message_text(ACCESS_GRANTED_MESSAGE)
        else:
            not_joined_list = "\n".join([f"• {channel}" for channel in not_joined])
            await query.edit_message_text(
                f"❌ You haven't joined all channels yet.\n\n"
                f"Please join these channels:\n{not_joined_list}\n\n"
                f"Then click the button again to verify."
            )
    
    async def approve_request(self, query, context, request_id):
        """Handle approve button callback - ask admin to select channel for link generation"""
        if query.from_user.id not in ADMIN_IDS:
            await query.answer("❌ Not authorized", show_alert=True)
            return
        
        pending_request = None
        for req in db.get_pending_links():
            if req["id"] == request_id:
                pending_request = req
                break
        
        if not pending_request:
            await query.answer("❌ Request not found or already processed", show_alert=True)
            return
        
        keyboard = []
        for channel_id in REQUIRED_CHANNELS:
            try:
                chat = await context.bot.get_chat(channel_id)
                keyboard.append([InlineKeyboardButton(chat.title, callback_data=f"genlink_{request_id}_{channel_id}")])
            except TelegramError as e:
                logger.warning(f"Could not get chat info for {channel_id}: {e}")
                # If we can't get chat info, we can't create a button for it.
                # You might want to add a fallback or inform the admin.
                pass

        if not keyboard:
            await query.edit_message_text("❌ No valid channels found to generate invite links for. Please ensure the bot is an admin in the channels and the links are correct.")
            return

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"✅ Request #{request_id} approved. Please select the channel to generate the invite link for:",
            reply_markup=reply_markup
        )
    
    async def generate_invite_link(self, query, context):
        """Generate an invite link for a specific channel"""
        if query.from_user.id not in ADMIN_IDS:
            await query.answer("❌ Not authorized", show_alert=True)
            return

        data_parts = query.data.split("_")
        request_id = int(data_parts[1])
        channel_id = int(data_parts[2]) # channel_id should be an integer

        # Find the pending request
        pending_request = None
        for req in db.get_pending_links():
            if req["id"] == request_id:
                pending_request = req
                break

        if not pending_request:
            await query.answer("❌ Request not found or already processed", show_alert=True)
            return

        try:
            # Generate a new invite link
            invite_link_object = await context.bot.create_chat_invite_link(
                chat_id=channel_id,
                member_limit=1,  # Limit to one use per link
                expire_date=None # No expiration
            )
            private_link = invite_link_object.invite_link

            if db.approve_link(request_id, query.from_user.id, private_link):
                await query.edit_message_text(
                    f"✅ Request #{request_id} has been approved.\n"
                    f"Private link for {channel_id}: {private_link}"
                )

                # Notify the user
                try:
                    await context.bot.send_message(
                        pending_request["user_id"],
                        f"✅ Your link request #{request_id} has been approved!\n"
                        f"Here is your private link: {private_link}"
                    )
                except Exception as e:
                    logger.error(f"Could not notify user {pending_request['user_id']}: {e}")
            else:
                await query.answer("❌ Failed to update database", show_alert=True)

        except TelegramError as e:
            await query.edit_message_text(f"❌ Error generating link for {channel_id}: {e}")
            logger.error(f"Error creating invite link for {channel_id}: {e}")

    async def get_chat_id_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /get_chat_id command to get chat ID"""
        if update.effective_chat.type in ["group", "supergroup", "channel"]:
            await update.message.reply_text(f"This chat's ID is: `{update.effective_chat.id}`")
        else:
            await update.message.reply_text("Please use this command in the channel or group you want to get the ID for.")

    async def reject_request(self, query, context, request_id):
        """Reject a link request"""
        if query.from_user.id not in ADMIN_IDS:
            await query.answer("❌ Not authorized", show_alert=True)
            return
        
        if db.reject_link(request_id, query.from_user.id, "Rejected by admin"):
            await query.edit_message_text(f"❌ Request #{request_id} has been rejected.")
            
            # Notify the user
            for req in db.data["pending_links"]:
                if req["id"] == request_id:
                    try:
                        await context.bot.send_message(
                            req["user_id"],
                            f"❌ Your link request #{request_id} has been rejected."
                        )
                    except:
                        pass
                    break
        else:
            await query.answer("❌ Request not found or already processed", show_alert=True)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        if not db.has_access(update.effective_user.id):
            await update.message.reply_text(MEMBERSHIP_REQUIRED_MESSAGE)
            return
        
        # Handle other messages from verified users
        await update.message.reply_text(
            "👋 Hello! Use /help to see available commands."
        )
    
    def run(self):
        """Run the bot"""
        print("🤖 Starting Telegram Channel Bot...")
        print(f"Bot token: {BOT_TOKEN[:10]}...")
        print(f"Owner ID: {OWNER_ID}")
        print(f"Required channels: {len(REQUIRED_CHANNELS)}")
        
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = ChannelBot()
    bot.run()

