import logging
import requests
import time

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
TOKEN = "8456547235:AAGxaJxcYolbeW6m0akaX4iElm-vRNJzmM4"  # Replace with your actual bot token
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# Cache for admin lists (chat_id -> list of admin user_ids)
admin_cache = {}

def get_updates(offset=None):
    """Get new updates from Telegram API."""
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 100, "offset": offset}

    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        logger.error(f"Error getting updates: {e}")
        return {"ok": False, "result": []}

def delete_message(chat_id, message_id):
    """Delete a message using Telegram API."""
    url = f"{BASE_URL}/deleteMessage"
    data = {"chat_id": chat_id, "message_id": message_id}

    try:
        response = requests.post(url, data=data)
        return response.json().get("ok", False)
    except Exception as e:
        logger.error(f"Error deleting message: {e}")
        return False

def get_chat_administrators(chat_id):
    """Get list of administrators for a chat."""
    if chat_id in admin_cache:
        return admin_cache[chat_id]

    url = f"{BASE_URL}/getChatAdministrators"
    data = {"chat_id": chat_id}

    try:
        response = requests.post(url, data=data)
        if response.json().get("ok"):
            admins = [str(admin["user"]["id"]) for admin in response.json()["result"]]
            admin_cache[chat_id] = admins
            logger.info(f"Cached admin list for chat {chat_id}: {admins}")
            return admins
        else:
            logger.error(f"Error getting chat administrators: {response.json()}")
            return []
    except Exception as e:
        logger.error(f"Exception getting chat administrators: {e}")
        return []

def is_user_admin(chat_id, user_id):
    """Check if a user is an administrator in the chat."""
    # For private chats, there are no admins (only the user themselves)
    if str(chat_id) == str(user_id):
        return True

    admins = get_chat_administrators(chat_id)
    return str(user_id) in admins

def process_update(update):
    """Process a single update and delete restricted content."""
    if "message" not in update:
        return

    message = update["message"]
    user_id = str(message["from"]["id"])
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]

    # Skip if user is admin
    if is_user_admin(chat_id, user_id):
        logger.info(f"Skipping message from admin {user_id} in chat {chat_id}")
        return

    # Check for forwarded content
    if "forward_from" in message or "forward_from_chat" in message or "forward_date" in message:
        if delete_message(chat_id, message_id):
            logger.info(f"Deleted forwarded message from user {user_id}")
        return

    # Check for stories
    if "story" in message:
        if delete_message(chat_id, message_id):
            logger.info(f"Deleted story from user {user_id}")
        return

    # Check for links in text
    if "text" in message and ("http://" in message["text"] or "https://" in message["text"]):
        if delete_message(chat_id, message_id):
            logger.info(f"Deleted message with link from user {user_id}")
        return

    # Check for links in caption
    if "caption" in message and ("http://" in message["caption"] or "https://" in message["caption"]):
        if delete_message(chat_id, message_id):
            logger.info(f"Deleted message with link in caption from user {user_id}")
        return

def main():
    """Main function to run the bot."""
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("Please replace YOUR_BOT_TOKEN_HERE with your actual bot token")
        return

    logger.info("Bot is starting...")
    offset = None

    while True:
        try:
            updates = get_updates(offset)

            if updates.get("ok"):
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    process_update(update)

            time.sleep(1)

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()
