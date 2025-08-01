import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ExtBot

# Bot Token and Group ID
BOT_TOKEN = ""
ALLOWED_GROUP_ID = 

# Optional: track usage per user
user_requests = {}

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def like(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Restrict to specific group only
    if chat_id != ALLOWED_GROUP_ID:
        return

    if len(context.args) != 2:
        await update.message.reply_text("⚠️ Usage: `/like {region} {uid}`", parse_mode="Markdown")
        return

    region, uid = context.args
    wait_msg = await update.message.reply_text("⏳ Please wait...")

    url = f"https://ff.deaddos.online/api/likes?region={region}&uid={uid}&key=Only_flexyy_like_bot"

    session = requests.Session()

    try:
        response = session.get(url)
        response.raise_for_status()
        data = response.json()

        if "response" in data:
            details = data["response"]

            if "PlayerNickname" in details:
                if user_id not in user_requests:
                    user_requests[user_id] = {"count": 0}
                user_requests[user_id]["count"] += 1

                message = (
                    f"✅ **Likes Added Successfully!**\n\n"
                    f"**👤 Player:** `{details['PlayerNickname']}`\n"
                    f"**💬 UID:** `{details['UID']}`\n"
                    f"**📊 Likes Before:** `{details['LikesbeforeCommand']}`\n"
                    f"**👍 Likes Given:** `{details['LikesGivenByAPI']}`\n"
                    f"**📈 Likes After:** `{details['LikesafterCommand']}`\n\n"
                    f"🔑 *Remaining Requests:* `{details.get('KeyRemainingRequests', 'Unknown')}`"
                )
            elif "message" in details:
                message = f"⚠️ `{details['message']}`"
            else:
                message = "⚠️ *Unexpected response format from the API.*"
        elif "message" in data:
            message = f"❌ *Error:* `{data['message']}`"
        else:
            message = "⚠️ *Unexpected response from the API.*"
    except requests.RequestException:
        message = "⚠️ Try again in 24 hours."
    except ValueError:
        message = "⚠️ *Invalid API response.*"

    await context.bot.delete_message(chat_id=chat_id, message_id=wait_msg.message_id)
    await update.message.reply_text(message, parse_mode="Markdown")

if __name__ == "__main__":
    bot_instance = ExtBot(token=BOT_TOKEN)
    app = ApplicationBuilder().bot(bot_instance).build()
    app.add_handler(CommandHandler("like", like))
    app.run_polling()
