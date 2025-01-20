import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from datetime import datetime, timedelta
import asyncio
import time

# Set up logging to help with debugging
logging.basicConfig(level=logging.INFO)

# Initialize the bot with your API credentials
API_ID = '1623073'  # Replace with your API ID
API_HASH = 'a6f2f0a7b2022f8ca7717d9101c5ff5c'  # Replace with your API HASH
TOKEN = '7311175407:AAFNuG40IGoaOXACRf0a0DfGJpqcqahRtcs'  # Replace with your Bot Token

bot = Client("my_bot11", bot_token=TOKEN, api_id=API_ID, api_hash=API_HASH)

# Group chat ID where the reminder system should work
GROUP_CHAT_ID = -1001289294178  # Replace with the actual group chat ID

# Dictionary to store message counts for each user
group_message_data = {}

# Function to handle incoming messages
@bot.on_message(filters.text & filters.chat(GROUP_CHAT_ID))
async def handle_message(client, message):
    user_id = message.from_user.id  # User ID (for hyperlinking)
    first_name = message.from_user.first_name  # First name of the user
    if user_id not in group_message_data:
        group_message_data[user_id] = {"count": 1, "first_name": first_name}
    else:
        group_message_data[user_id]["count"] += 1

# Function to find the most active user and their data
def get_most_active_user():
    if not group_message_data:
        return None, None, 0
    most_active_user_id = max(group_message_data, key=lambda user_id: group_message_data[user_id]["count"])
    most_active_user_data = group_message_data[most_active_user_id]
    return most_active_user_id, most_active_user_data["first_name"], most_active_user_data["count"]

# Function to calculate the total messages sent in the group
def get_total_messages():
    return sum(user_data["count"] for user_data in group_message_data.values())

# Function to send a reminder to the most active user
async def remind_most_active_user():
    user_id, first_name, message_count = get_most_active_user()
    total_messages = get_total_messages()
    if user_id:
        await bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=(
                f"[{first_name}](tg://user?id={user_id}), you’ve sent {message_count} messages! "
                f"Out of the total {total_messages} messages sent in this group. Go touch grass! 🌱"
            ),
            parse_mode=ParseMode.MARKDOWN  # Use ParseMode.MARKDOWN
        )
    else:
        await bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text="No active users to remind right now."
        )
    # Reset the message data
    global group_message_data
    group_message_data = {}

# Function to start the reminder every 1 minute
async def start_reminder():
    while True:
        await remind_most_active_user()
        await asyncio.sleep(60)  # 1 minute in seconds

# Function to handle bot start and retry if time sync fails
async def start_bot():
    retry_count = 3  # Max retry attempts for time sync issue
    for _ in range(retry_count):
        try:
            await bot.start()
            break  # Successfully started, exit the loop
        except pyrogram.errors.BadMsgNotification:
            logging.error("Time synchronization failed, retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying

# Start reminder when the bot is added to the group
@bot.on_message(filters.new_chat_members & filters.chat(GROUP_CHAT_ID))
async def new_member_handler(client, message):
    await bot.send_message(message.chat.id, "Reminder system started! Most active users will be reminded every minute.")
    asyncio.create_task(start_reminder())

# Start the bot
if __name__ == '__main__':
    asyncio.run(start_bot())  # Start the bot with retry mechanism
