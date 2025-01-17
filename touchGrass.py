import logging
from pyrogram import Client, filters, enums
from datetime import datetime, timedelta
import threading
# Set up logging to help with debugging
logging.basicConfig(level=logging.INFO)

# Initialize the bot with your API credentials
API_ID = '1623073'  # Replace with your API ID
API_HASH = 'a6f2f0a7b2022f8ca7717d9101c5ff5c'  # Replace with your API HASH
TOKEN = '7311175407:AAHU0eTriwjYtGm4kFQclv1Mm9JhrBkOSgI'  # Replace with your Bot Token
bot = Client("my_bot4", bot_token=TOKEN, api_id=API_ID, api_hash=API_HASH)

# Group chat ID where the reminder system should work
GROUP_CHAT_ID = -1002481107578  # Replace with the actual group chat ID

# Dictionary to store message counts and timestamps for each user
group_message_data = {}

# Time window (in seconds) to consider for the specific period
TIME_WINDOW = 3600  # 5 minutes

# Function to handle incoming messages
@bot.on_message(filters.text)
def handle_message(client, message):
    # Only track messages from the specified group
    if message.chat.id == GROUP_CHAT_ID:
        user_id = message.from_user.id  # User ID (for hyperlinking)
        first_name = message.from_user.first_name  # First name of the user
        timestamp = datetime.now()  # Timestamp of the message

        # If the user is not in the data, add them
        if user_id not in group_message_data:
            group_message_data[user_id] = {"first_name": first_name, "messages": []}

        # Append the message timestamp
        group_message_data[user_id]["messages"].append(timestamp)

        # Remove old messages outside the time window
        group_message_data[user_id]["messages"] = [
            msg_time for msg_time in group_message_data[user_id]["messages"]
            if (datetime.now() - msg_time).total_seconds() <= TIME_WINDOW
        ]

# Function to find the most active user in the specific period
def get_most_active_user():
    if not group_message_data:
        return None, None, 0

    # Calculate the number of messages for each user in the time window
    most_active_user_id = max(
        group_message_data,
        key=lambda user_id: len(group_message_data[user_id]["messages"])
    )
    most_active_user_data = group_message_data[most_active_user_id]
    message_count = len(most_active_user_data["messages"])
    return most_active_user_id, most_active_user_data["first_name"], message_count

# Function to send a reminder to the most active user
def remind_most_active_user():
    user_id, first_name, message_count = get_most_active_user()
    if user_id and message_count > 0:
        bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"[{first_name}](tg://user?id={user_id}), go touch grass! 🌱\nYou’ve sent {message_count} messages in the last {TIME_WINDOW // 60} minutes.",
            parse_mode=enums.ParseMode.MARKDOWN  # Correct parse mode
        )
    else:
        bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text="No active users to remind right now."
        )

# Function to start the reminder every 1 minute
def start_reminder():
    threading.Timer(60, start_reminder).start()  # 1 minute in seconds
    remind_most_active_user()

# Start reminder when the bot is added to the group
@bot.on_message(filters.new_chat_members)
def new_member_handler(client, message):
    if message.chat.id == GROUP_CHAT_ID:
        bot.send_message(message.chat.id, f"Reminder system started! Monitoring activity over the last {TIME_WINDOW // 60} minutes.")
        start_reminder()

# Start the bot
if __name__ == '__main__':
    bot.run()