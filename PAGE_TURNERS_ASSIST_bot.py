import logging
import os
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Get token from environment
TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    print("ERROR: No token found! Set the TOKEN environment variable.")
    exit(1)

def handle_message(update, context):
    try:
        message = update.message
        user = message.from_user
        
        # Skip if no user
        if not user:
            return
            
        # Check if message is forwarded
        if hasattr(message, 'forward_date') and message.forward_date:
            message.delete()
            logging.info(f"Deleted forwarded message from {user.first_name}")
            return
            
        # Check if message contains links
        if message.entities:
            for entity in message.entities:
                if entity.type in ["url", "text_link"]:
                    message.delete()
                    logging.info(f"Deleted message with link from {user.first_name}")
                    return
                    
    except Exception as e:
        logging.error(f"Error: {e}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.all & ~Filters.command, handle_message))
    
    print("Bot is starting and will run 24/7 on Koyeb!")
    print("It will delete forwarded messages and links.")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()