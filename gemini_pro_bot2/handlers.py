import asyncio
from gemini_pro_bot.llm import model, img_model
from google.generativeai.types.generation_types import (
    StopCandidateException,
    BlockedPromptException,
)
from telegram import Update
from telegram.ext import (
    ContextTypes,
)
from telegram.error import NetworkError, BadRequest
from telegram.constants import ChatAction, ParseMode
from gemini_pro_bot.html_format import format_message
import PIL.Image as load_image
from io import BytesIO
import logging
from telegram.ext import Updater, CommandHandler, ContextTypes
import telegram
from openpyxl import Workbook
import datetime
import os
from telegram import ForceReply
import asyncio
from PIL import Image
from io import BytesIO

def new_chat(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data["chat"] = model.start_chat(history=[
  {
    "role": "user",
    "parts": "what is your name? (اسمك؟)"
  },
  {
    "role": "model",
    "parts": "My name is Trimon-AI chat bot, made by Abdullah Amer a medical student ar new mansoura university . I am an AI Chat bot programmed by Abdullah Amer But my language model gemini-pro from google ."
  },
  {
    "role": "user",
    "parts": "Who is your Devoloper?(مطورك؟)"
  },
  {
    "role": "model",
    "parts": "Abdullah Amer . he is a medical student at Mansoura New University. He excels not only in medicine but also showcases intelligence in programming and artificial intelligence. Abdullah is a key member at ABM Research Foundation , where he serves as the Television President. He actively contributes to the development of various AI-related research and software, demonstrating his expertise in the field one of his project was Bi-emo and Trimon AI-chatbot (me)"
  },

])


bot = telegram.Bot(token='6754993756:AAHa1tCI4Ri4Pm6KqOB7sbo1e1xdwrsd04g')
DEVELOPER_ID = 644813997  # Example ID

logging.basicConfig(
    filename="bot_logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, handlers=[handler])





async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}!\n\nI'm Trimon, a chatbot created by  Abdullah Amer, a medical student at Mansoura New University. I can talk to you like a person, answer your questions, and help you with different things.\n\nTo start a new conversation with me, just type /NewChat .\n\n /Info - Get info about bot fuctions",
          reply_markup=ForceReply(selective=True),
    )
    user_name = user.username or user.first_name
    total_users = get_total_users(update.effective_chat.id)  # Implement your user count method


    # Craft notification message with relevant user details
    notification_text = f"New user joined:\n" \
                        f"- User ID: {user.id}\n" \
                        f"- Name: {user_name}\n" \
                        f"- Total users: {total_users}"


    # Send notification to developer's user ID
    await context.bot.send_message(chat_id=DEVELOPER_ID, text=notification_text)


async def google_bot(update, context):
    if update.message.reply_to_message:  # Check if it's a reply
        # Get message ID from the replied-to message
        message_id = update.message.reply_to_message.message_id

        try:
            await bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
            await context.bot.send_message(chat_id=644813997, text="Message deleted successfully!")
        except telegram.error.BadRequest as e:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Error deleting message: " + str(e))
    else:
        await context.bot.send_message(chat_id=644813997, text="Please reply to the message you want me to delete.")



async def get_total_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Retrieves the total number of users based on your chosen method."""

    # Implement your preferred logic to fetch total users (e.g., database, chat member count, etc.)
    # For the sake of demonstration, let's assume using an in-memory counter:
    if not 'total_users' in context.chat_data:
        context.chat_data['total_users'] = 1
        print("New user! First time tracking chat users.")
    else:
        context.chat_data['total_users'] += 1
        print(f"New user joined! Total users: {context.chat_data['total_users']}")
    return context.chat_data['total_users']

async def help_command(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
Bot main commands:
/start - Start the bot
/Info - Get info about bot fuctions

Conversation commands:
/NewChat - Start a new chat session (model will forget previously generated messages)

Send a prompt to the bot to generate a response.
"""
    await update.message.reply_text(help_text)


async def newchat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start a new chat session."""
    init_msg = await update.message.reply_text(
        text="ceating new Conversation session...",
        reply_to_message_id=update.message.message_id,
    )
    new_chat(context)
    await init_msg.edit_text("New Conversation session created.")


# Define the function that will handle incoming messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles incoming text messages from users.

    Checks if a chat session exists for the user, initializes a new session if not.
    Sends the user's message to the chat session to generate a response.
    Streams the response back to the user, handling any errors.
    """
    user = update.effective_user
    message_id = update.message.message_id # Get the message ID
    timestamp = update.message.date

# Open the file for logging
    with open("user_info_logs.txt", "a") as log_file:
        user_info = f"Message ID: {message_id}\n" \
                    f"Message from user: {user.mention_html()}\n" \
                    f"(ID: {user.id})\n" \
                    f"Time : {timestamp}\n" \
                    f"messege type:Text \n" \
                    f"bot :Trimon \n" \
                    f"\n\n" \

        log_file.write(user_info)  # Write to the file without extra newline

# Optional print statement for debugging
    print(user_info)  # Remove for final version if not needed




    if context.chat_data.get("chat") is None:
        new_chat(context)
    text = update.message.text
    init_msg = await update.message.reply_text(
        text="Generating...", reply_to_message_id=update.message.message_id
    )
    await update.message.chat.send_action(ChatAction.TYPING)
    # Generate a response using the text-generation pipeline
    chat = context.chat_data.get("chat")  # Get the chat session for this chat
    response = None
    try:
        response = await chat.send_message_async(
            text, stream=True
        )  # Generate a response
    except StopCandidateException as sce:
        print("Prompt: ", text, " was stopped. User: ", update.message.from_user)
        print(sce)
        await init_msg.edit_text("The model unexpectedly stopped generating.")
        chat.rewind()  # Rewind the chat session to prevent the bot from getting stuck
        return
    except BlockedPromptException as bpe:
        print("Prompt: ", text, " was blocked. User: ", update.message.from_user)
        print(bpe)
        await init_msg.edit_text("Blocked due to safety concerns.")
        if response:
            # Resolve the response to prevent the chat session from getting stuck
            await response.resolve()
        return
    full_plain_message = ""



    # Stream the responses
    async for chunk in response:
        try:
            if chunk.text:
                full_plain_message += chunk.text
                message = format_message(full_plain_message)
                init_msg = await init_msg.edit_text(
                    text=message,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
        except StopCandidateException as sce:
            await init_msg.edit_text("The model unexpectedly stopped generating.")
            chat.rewind()  # Rewind the chat session to prevent the bot from getting stuck
            continue
        except BadRequest:
            await response.resolve()  # Resolve the response to prevent the chat session from getting stuck
            continue
        except NetworkError:
            raise NetworkError(
                "Looks like you're network is down. Please try again later."
            )
        except IndexError:
            await init_msg.reply_text(
                "Some index error occurred. This response is not supported."
            )
            await response.resolve()
            continue
        except Exception as e:
            print(e)
            if chunk.text:
                full_plain_message = chunk.text
                message = format_message(full_plain_message)
                init_msg = await update.message.reply_text(
                    text=message,
                    parse_mode=ParseMode.HTML,
                    reply_to_message_id=init_msg.message_id,
                    disable_web_page_preview=True,
                )
        # Sleep for a bit to prevent the bot from getting rate-limited
        await asyncio.sleep(0.1)


async def handle_image(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming images with captions and generate a response."""
    init_msg = await update.message.reply_text(
        text="Generating...", reply_to_message_id=update.message.message_id
    )
    images = update.message.photo
    user = update.effective_user
    message_id = update.message.message_id # Get the message ID
    timestamp = update.message.date

# Open the file for logging
    with open("user_info_logs.txt", "a") as log_file:
        user_info = f"Message ID: {message_id}\n" \
                    f"Message from user: {user.mention_html()}\n" \
                    f"(ID: {user.id})\n" \
                    f"Time : {timestamp}\n" \
                    f"messege type:media \n" \
                    f"bot :Trimon \n" \
                    f"\n\n" \

        log_file.write(user_info)  # Write to the file without extra newline

# Optional print statement for debugging
    print(user_info)  # Remove for final version if not needed
    unique_images: dict = {}
    for img in images:
        file_id = img.file_id[:-7]
        if file_id not in unique_images:
            unique_images[file_id] = img
        elif img.file_size > unique_images[file_id].file_size:
            unique_images[file_id] = img
    file_list = list(unique_images.values())
    file = await file_list[0].get_file()
    a_img = load_image.open(BytesIO(await file.download_as_bytearray()))
    prompt = None
    if update.message.caption:
        prompt = update.message.caption
    else:
        prompt = "Analyse this image and generate response"
    response = await img_model.generate_content_async([prompt, a_img], stream=True)
    full_plain_message = ""
    async for chunk in response:
        try:
            if chunk.text:
                full_plain_message += chunk.text
                message = format_message(full_plain_message)
                init_msg = await init_msg.edit_text(
                    text=message,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
        except StopCandidateException:
            await init_msg.edit_text("The model unexpectedly stopped generating.")
        except BadRequest:
            await response.resolve()
            continue
        except NetworkError:
            raise NetworkError(
                "Looks like you're network is down. Please try again later."
            )
        except IndexError:
            await init_msg.reply_text(
                "Some index error occurred. This response is not supported."
            )
            await response.resolve()
            continue
        except Exception as e:
            print(e)
            if chunk.text:
                full_plain_message = chunk.text
                message = format_message(full_plain_message)
                init_msg = await update.message.reply_text(
                    text=message,
                    parse_mode=ParseMode.HTML,
                    reply_to_message_id=init_msg.message_id,
                    disable_web_page_preview=True,
                )
        await asyncio.sleep(0.1)
