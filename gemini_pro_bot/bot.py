import os
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Application,
)
from gemini_pro_bot.filters import AuthFilter, MessageFilter, PhotoFilter
from dotenv import load_dotenv
from gemini_pro_bot.handlers import (
    start,
    help_command,
    newchat_command,
    handle_message,
    handle_image,
)
from gemini_pro_bot.handlers import google_bot
load_dotenv()


def start_bot() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv("BOT_TOKEN1")).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start, filters=AuthFilter))
    application.add_handler(CommandHandler("Info", help_command, filters=AuthFilter))
    application.add_handler(CommandHandler("NewChat", newchat_command, filters=AuthFilter))
    application.add_handler(CommandHandler("Deletemsg", google_bot))

    # Any text message is sent to LLM to generate a response
    application.add_handler(MessageHandler(MessageFilter, handle_message))

    # Any image is sent to LLM to generate a response
    application.add_handler(MessageHandler(PhotoFilter, handle_image))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

