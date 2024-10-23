import asyncio
import logging
import random
from pyrogram import Client, filters, idle
from datetime import datetime
import pytz
import requests
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import google.generativeai as genai
import asyncio
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/health')
def health():
    return 'OK', 200

def run_server():
    app.run(host='0.0.0.0', port=8000)

if __name__ == "__main__":
    threading.Thread(target=run_server).start()
    # Your existing bot code here


api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Timezone setup
local_tz = pytz.timezone('Asia/Kolkata')

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

# Generative AI model (Gemini)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Helper function for greeting
def get_greeting():
    now = datetime.now(local_tz)  
    if now.hour < 12:
        return "🌅 **Gᴏᴏᴅ Mᴏʀɴɪɴɢ!**"
    elif 12 <= now.hour < 18:
        return "☀️ **Gᴏᴏᴅ Aғᴛᴇʀɴᴏᴏɴ!**"
    else:
        return "🌙 **Gᴏᴏᴅ Eᴠᴇɴɪɴɢ!**"

# Fetch random image URL
def get_random_image_url():
    access_key = "rlgeFrHYOvTAISi2xesrfm2d-OU2NFkpCmeq33Es-fo"
    url = f"https://api.unsplash.com/photos/random?client_id={access_key}&query=hot-girl&orientation=portrait"
    response = requests.get(url)
    if response.status_code == 200:
        image_data = response.json()
        return image_data['urls']['regular']
    else:
        logger.error("Failed to fetch image from Unsplash")
        return "https://example.com/path/to/default/image.jpg"

# Start command with welcome image and buttons
@app.on_message(filters.command("start"))
async def start(client, message):
    greeting = get_greeting()
    image_url = get_random_image_url()
    buttons = [
        [InlineKeyboardButton("Aᴅᴅ Mᴇ Iɴ Yᴏᴜʀ Gʀᴏᴜᴘ", url="https://t.me/shizumbot?startgroup=true")],
        [
            InlineKeyboardButton("Oᴡɴᴇʀ", url="https://t.me/Shizutail"),
            InlineKeyboardButton("Cʜᴀᴀɴᴇʟ", url="https://t.me/Shizuslife")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    user_mention = message.from_user.mention
    await message.reply_photo(
        photo=image_url,
        caption=f"{greeting}\n\n**Hᴇʏ {user_mention},\nI'ᴍ Sʜɪᴢᴜ, Yᴏᴜʀ Fʀɪᴇɴᴅʟʏ ʙᴏᴛ!\n\nLᴇᴛ's ʜᴀᴠᴇ sᴏᴍᴇ ғᴜɴ!😍**",
        reply_markup=reply_markup
    )



@app.on_message(filters.new_chat_members)
async def welcome(client, message):
    bot = await client.get_me()  # Await to get the bot's user object
    for new_member in message.new_chat_members:
        if new_member.id == bot.id:  # Check if the new member is the bot itself
            greeting = get_greeting()
            welcome_message = (
                f"{greeting}\n\n🌟 **I'ᴍ Hᴇʀᴇ! Tʜᴀɴᴋs Fᴏʀ Aᴅᴅɪɴɢ Mᴇ Tᴏ {message.chat.title}!**\n"
                f"**Lᴇᴛ's Mᴀᴋᴇ Tʜɪs Gʀᴏᴜᴘ Eᴠᴇɴ Mᴏʀᴇ Fᴜɴ! 😄**"
            )
            await message.reply(welcome_message)
        else:
            # Welcome regular members
            greeting = get_greeting()
            welcome_message = (
                f"{greeting}\n\n🌟 **Wᴇʟᴄᴏᴍᴇ, {new_member.mention}!**"
                f" **Tᴏ {message.chat.title}, \nEɴᴊᴏʏ ʏᴏᴜʀ ᴛɪᴍᴇ ʜᴇʀᴇ😉!**"
            )
            try:
                await message.reply(welcome_message)
            except Exception as e:
                logger.error(f"Error sending welcome message: {e}")

        

# Check if bot is promoted to admin and send message
@app.on_message(filters.new_chat_members)
async def check_bot_promotion(client, message):
    bot = await client.get_me()  # Await to get bot's user object
    for new_member in message.new_chat_members:
        if new_member.id == bot.id:  # Check if the new member is the bot itself
            chat_member = await client.get_chat_member(message.chat.id, new_member.id)
            if chat_member.status == "administrator":  # Check if the bot is an admin
                greeting = get_greeting()
                message_text = f"{greeting}\nI have been promoted to admin! I'm here to help!"
                try:
                    await message.reply(message_text)
                except Exception as e:
                    logger.error(f"Error sending admin promotion message: {e}")




# Handle goodbye when someone leaves
@app.on_message(filters.left_chat_member)
async def goodbye(client, message):
    left_member = message.left_chat_member
    leave_message = f"🚪 {left_member.mention} **Hᴀs ʟᴇғᴛ {message.chat.title}. Wᴇ'ʟʟ ᴍɪss ʏᴏᴜ ʙᴀʙʏ!**"
    goodbye_message = await message.reply(leave_message)
    await asyncio.sleep(30)
    await goodbye_message.delete()

# Dictionary to store chat sessions
chat_sessions = {}

# Ask Gemini AI for a response
@app.on_message(filters.command("ask"))
async def gemini(client, message):
    user_id = message.from_user.id
    prompt = message.text.split(' ', 1)[1] if len(message.text.split()) > 1 else None
    if not prompt:
        await message.reply("Please provide a prompt to ask Gemini.")
        return
    processing_message = await message.reply("Processing your request...")
    try:
        if user_id not in chat_sessions:
            chat_sessions[user_id] = model.start_chat()
        chat_session = chat_sessions[user_id]
        response = chat_session.send_message(prompt)
        await message.reply(f'{response.text}')
    except Exception as e:
        await message.reply(f"An error occurred: {e}")
    finally:
        await processing_message.delete()

# ChatterBot configuration (Hindi bot)


import praw
import random

# Reddit API setup
reddit = praw.Reddit(
    client_id='CZAsoS9c4HwvjCciXLnnxA',     # Replace with your Reddit API client_id
    client_secret='P33tp6x4LSzIvfGTW2OxhIhqZ-l8Mw', # Replace with your Reddit API client_secret
    user_agent='shizu-bot'    # Replace with your Reddit API user_agent
)

# Command to fetch memes from Reddit
@app.on_message(filters.command("meme"))
async def get_random_meme_reddit(client, message):
    try:
        # Choose a popular meme subreddit
        subreddit = reddit.subreddit('memes')
        
        # Fetch hot memes from the subreddit
        memes = list(subreddit.hot(limit=100))
        
        # Filter out any text posts (we want only image posts)
        image_memes = [meme for meme in memes if meme.url.endswith(('jpg', 'jpeg', 'png'))]
        
        if image_memes:
            # Choose a random meme from the list
            random_meme = random.choice(image_memes)
            
            meme_url = random_meme.url
            meme_title = random_meme.title
            
            # Reply with the random meme
            await message.reply_photo(photo=meme_url, caption=f"Here's a meme for you: **{meme_title}**")
        else:
            await message.reply("Sorry, I couldn't fetch memes at the moment.")
    
    except Exception as e:
        await message.reply(f"Error: {e}")






async def create_quote_image(user, original_message):
    # Load user profile picture
    photo_path = None
    async for photo in app.get_chat_photos(user.id):
        # Download the most recent profile photo
        photo_path = await app.download_media(photo.file_id)

    if not photo_path:
        # Default profile picture if no photo found
        print("No profile picture found, using default.")
        photo_path = "default_profile_pic.jpg"  # You need to have this image

    # Open the profile picture
    profile_pic = Image.open(photo_path).convert("RGBA")

    # Create a blank image for the quote
    img_width, img_height = 600, 300  # Increased size for better quality
    background_color = (34, 34, 34)  # Dark background
    image = Image.new("RGBA", (img_width, img_height), background_color)
    draw = ImageDraw.Draw(image)

    # Draw user profile picture (circular) with a border
    profile_pic = profile_pic.resize((80, 80))  # Increased size
    mask = Image.new("L", profile_pic.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, 80, 80), fill=255)  # Circle mask
    profile_pic.putalpha(mask)

    # Draw a border around the profile picture
    border_size = 5
    border_color = (255, 215, 0)  # Gold color for the border
    image.paste(border_color, (10, 10, 90, 90))  # Border rectangle
    image.paste(profile_pic, (10, 10), profile_pic)  # Pasting with transparency

    # Create a background for the text
    text_background = Image.new("RGBA", (img_width - 20, 100), (0, 0, 0, 200))  # Semi-transparent black
    image.paste(text_background, (10, 100))

    # Draw username and message
    font_username = ImageFont.truetype("bold.ttf", 24)  # Increased size for better visibility
    font_message = ImageFont.truetype("text.ttf", 18)  # Increased size for better visibility
    draw.text((100, 110), user.username, fill="white", font=font_username)  # Username
    draw.text((10, 140), original_message, fill="white", font=font_message)  # Message

    # Save the image as WEBP with high quality
    image_path = "quote_image.webp"
    image.save(image_path, "WEBP", quality=95)  # Set quality for WEBP

    return image_path

@app.on_message(filters.reply & filters.command("q"))
async def handle_quote(client, message):
    replied_message = message.reply_to_message
    user = replied_message.from_user

    if user:
        original_message = replied_message.text or "No text"
        image_path = await create_quote_image(user, original_message)

        # Send the image
        await app.send_sticker(message.chat.id, image_path)

        # Clean up image file if necessary
        os.remove(image_path)

reactions = ["👍", "😂", "😊", "🎉", "👏", "❤️"]

@app.on_message(filters.command("start_chat"))
async def start_chat(client, message):
    try:
        members = await app.get_chat_members(message.chat.id)
        # Ensure there are members to choose from
        if not members:
            await message.reply("No members found in the chat.")
            return

        # Select a random member from the chat
        selected_member = random.choice(members).user
        user_mention = selected_member.mention
        prompt = f"Hey {user_mention}, how’s it going today?"

        # Send a message tagging the selected member
        await message.reply(prompt)

        # Store or start a conversation with this member
        user_id = selected_member.id
        if user_id not in chat_sessions:
            chat_sessions[user_id] = model.start_chat()

        # Send a message using AI
        chat_session = chat_sessions[user_id]
        response = chat_session.send_message(prompt)
        await message.reply(response.text)

    except Exception as e:
        logger.error(f"Error in start_chat: {e}")
        await message.reply("An error occurred while trying to start a chat.")
        ""

# React to messages automatically
@app.on_message(filters.text & ~filters.command(['start', 'help']))  # Exclude specific commands
async def auto_react(client, message):
    try:
        user_message = message.text.lower()

        # Respond with predefined reactions
        if "hello" in user_message or "hi" in user_message:
            await message.reply(random.choice(reactions))  # Random reaction emoji
        elif "thanks" in user_message or "thank you" in user_message:
            await message.reply("You're welcome! 😊")

        # Check for creation-related questions
        creation_keywords = [
            "who created you", "who made you", "who are you",
            "kya tumhe kisne banaya", "tumhe kisne banaya", "aapko kisne banaya"
            "kon ho", "Kon ho", "Tum Kon ho", "Who're you"
        ]
        if any(keyword in user_message for keyword in creation_keywords):
            await message.reply("Shizu")
            return
            
        shizu_keywords = [
            "Shizu Kon Hai", "Shizu kon hi", "shizu kon hai",
            "Shizu kon hain", "Shizu kaun hai", "Who's shizu"
            "who is shizu" "Who is Shizu", "Who shizu", "Shizu", "shizu"
        ]
        if any(keyword in user_message for keyword in shizu_keywords):
            await message.reply("She's my creator")
            return   

        user_id = message.from_user.id
        if user_id not in chat_sessions:
            chat_sessions[user_id] = model.start_chat()

        chat_session = chat_sessions[user_id]
        response = chat_session.send_message(user_message)
        await message.reply(response.text)

    except Exception as e:
        logger.error(f"Error in auto_react: {e}")
        await message.reply("An error occurred while processing your message.")


# Store popular meme templates in a list
meme_templates = []

# Fetch the meme templates at the start
def fetch_meme_templates():
    url = "https://api.imgflip.com/get_memes"
    response = requests.get(url)
    data = response.json()
    if data['success']:
        global meme_templates
        meme_templates = data['data']['memes']
    else:
        meme_templates = []

fetch_meme_templates()  # Fetch the meme templates when the bot starts

# Meme Generator Command
@app.on_message(filters.command("memeg"))
async def meme_generator(client, message):
    try:
        # Ensure the message contains the top and bottom text
        if len(message.command) < 2:
            await message.reply("Usage: /meme <top_text> | <bottom_text>")
            return

        # Extract the text without the /meme command
        text = message.text[len("/meme "):].strip()

        # Check if there is a "|" separator for top and bottom text
        if '|' not in text:
            await message.reply("Please use the format: /meme <top_text> | <bottom_text>")
            return

        # Split top and bottom text
        top_text, bottom_text = text.split("|", 1)
        
        # Trim any extra spaces
        top_text = top_text.strip()
        bottom_text = bottom_text.strip()

        # API credentials (Get from imgflip)
        username = 'CUTEX'
        password = 'cutexmods2452'

        # Randomly select a meme template from the fetched list
        if not meme_templates:
            await message.reply("Sorry, I don't have any meme templates available.")
            return
        template = random.choice(meme_templates)
        template_id = template['id']  # Get the ID of the selected template

        # Meme API request
        url = "https://api.imgflip.com/caption_image"
        params = {
            'template_id': template_id,
            'username': username,
            'password': password,
            'text0': top_text,
            'text1': bottom_text
        }

        response = requests.post(url, params=params)
        data = response.json()

        if data['success']:
            meme_url = data['data']['url']
            await message.reply_photo(photo=meme_url)
        else:
            await message.reply("Sorry, I couldn't generate a meme.")
    except Exception as e:
        await message.reply(f"Error: {e}")
        



# Start the bot
async def main():
    try:
        await app.start()
        logger.info("Bot started...")        
        await idle()
    except KeyboardInterrupt:
        await app.stop()
        logger.info("Bot stopped")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
