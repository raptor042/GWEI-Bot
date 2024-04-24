import os
from dotenv import load_dotenv

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

import logging

from __db__.db import connect_db, get_user, set_user, update_user
from __api__.index import get, transfer

logging.basicConfig(format="%(asctime)s -%(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
load_dotenv()

START, END = range(2)

MONGO_URI = os.getenv("MONGO_URI")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

db = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        user = update.message.from_user
        logger.info(f"{user.username} started a conversation.")

        if update.message.chat.type == "private":
            _user = get_user(db=db, query={"userId" : user.id})
            info = get()
            print(info)

            if not _user:
                context.user_data["username"] = user.username
                context.user_data["user_id"] = user.id

                print(context.args)

                ref = 0

                if len(context.args) > 0:
                    ref = context.args[0]
                    print(ref)

                    update_user(db=db, query={"userId" : int(ref)}, value={"$push" : {"referrals" : user.username}})
                    update_user(db=db, query={"userId" : int(ref)}, value={"$inc" : {"referral_balance" : 50}})

                user_ = set_user(db=db, value={"userId" : user.id, "username" : user.username, "balance" : 0, "address" : "0x0", "twitter": "--", "discord": "--", "referee": ref, "referrals": [], "referral_balance": 0})
                print(user_)

                keyboard = [
                    [InlineKeyboardButton("Continue 🚀", callback_data="continue")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                reply_msg = f"<b>Hello {user.username} 🎉, I am your friendly $GWEI Airdrop Bot 🤖.</b>\n\n<i>🎁 Earn Free 150 GWEI For Completing All Task.</i>\n\n<i>👨‍👨‍👦 Earn 50 GWEI For Every Each Referral.</i>\n\n<b>📢 Airdrop Rules:</b>\n\n<i>🔰 Join <a href='https://t.me/GWEITOKEN'>@GWEITOKEN</a></i>\n\n<b>🚨 Must Complete The Task & Click On [Continue] To Proceed</b>"

                await update.message.reply_html(text=reply_msg, reply_markup=reply_markup)
            else:
                reply_msg = f"<b>🚀 $GWEI Free Airdrop Is Live!</b>\n\n<i>🎁 Bonus: 150 $GWEI </i>\n\n<i>👨‍👨‍👦 Referral: 50 $GWEI </i>\n\n<i>🔗 Airdrop Link :- <a href='https://t.me/gwei_airdrop_bot?start={user.id}'>https://t.me/gwei_airdrop_bot?start={user.id}</a></i>\n\n<b>💰 Don't Miss This Free Income Chance!</b>"
                await update.message.reply_html(text=reply_msg)
            
            return START
        else:
            reply_msg = "<b>🚨 This command is not used in groups</b>"
            await update.message.reply_html(text=reply_msg)

            return -1
    except Exception as e:
        print(e)
        logging.error("An error occured while processing this command.")

        reply_msg = f"<b>🚨 {user.username} An error occured while processing your request.</b>"
        await update.message.reply_html(text=reply_msg)

async def _start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        query = update.callback_query
        await query.answer()

        username = context.user_data["username"]
        user_id = context.user_data["user_id"]
        logger.info(f"{username} wants to wants to proceed after joining the required group chats.")

        chat = "@GWEITOKEN"
        done = False

        # member = await context.bot.get_chat_member(chat, user_id)
        # print(member)

        try:
            member = await context.bot.get_chat_member(chat, user_id)
            user_status = member.status
            print(f"CHAT MEMBER: {user_status}")
        except Exception as e:
            print(e)
            done = False
        else:
            if user_status in ["administrator", "member"]:
                done = True

        if done:
            keyboard = [
                [InlineKeyboardButton("📝 Submit Twitter Username", callback_data="twitter")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            reply_msg = f"<i>🔰 Follow Our <a href='https://x.com/gweitoken_eth?s=21'>$GWEI Twitter</a></i>\n\n<b>🚨 Must Complete This Task Then Submit Your Twitter Username To Proceed</b>"
            await query.message.reply_html(text=reply_msg, reply_markup=reply_markup)
        else:
            reply_msg = f"<b>🚨 Must Complete The Task Before You Can Procced</b>"
            await query.message.reply_html(text=reply_msg)

        return START
    except Exception as e:
        print(e)
        logging.error("An error occured while processing this command.")

        reply_msg = f"<b>🚨 {username}, An error occured while processing your request.</b>"
        await query.message.reply_html(text=reply_msg)

async def twitter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        query = update.callback_query
        await query.answer()

        username = context.user_data["username"]
        logger.info(f"{username} wants to enter twitter username.")

        reply_msg = f"<i>🔰 Enter Your Twitter Username.</i>\n\n<b>🚨 Make sure while entering your twitter username, it begins with '@'.</b>"

        await query.message.reply_html(reply_msg)

        return START
    except Exception as e:
        print(e)
        logging.error("An error occured while processing this command.")

        reply_msg = f"<b>🚨 {username}, An error occured while processing your request.</b>"
        await query.message.reply_html(text=reply_msg)

async def _twitter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        user = update.message.from_user
        logger.info(f"{user.username} has entered his/her twitter username.")

        context.user_data["twitter"] = update.message.text.strip()

        _user = update_user(db=db, query={"username" : user.username}, value={"$set" : {"twitter" : update.message.text.strip()}})
        print(_user)

        keyboard = [
            [InlineKeyboardButton("📝 Submit Discord Username", callback_data="discord")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        reply_msg = f"<i>🔰 Join Our <a href='https://discord.com/invite/XRUyD4mt'>$GWEI Discord</a></i>\n\n<b>🚨 Must Complete This Task Then Submit Your Discord Username To Proceed</b>"

        await update.message.reply_html(text=reply_msg, reply_markup=reply_markup)

        return START
    except Exception as e:
        print(e)
        logging.error("An error occured while processing this command.")

        reply_msg = f"<b>🚨 {user.username}, An error occured while processing your request.</b>"
        await update.message.reply_html(text=reply_msg)

async def discord(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        query = update.callback_query
        await query.answer()

        username = context.user_data["username"]
        logger.info(f"{username} wants to enter discord username.")

        reply_msg = f"<i>🔰 Enter Your Discord Username.</i>\n\n<b>🚨 Make sure while entering your discord username, it begins with '#'.</b>"

        await query.message.reply_html(reply_msg)

        return START
    except Exception as e:
        print(e)
        logging.error("An error occured while processing this command.")

        reply_msg = f"<b>🚨 {username}, An error occured while processing your request.</b>"
        await query.message.reply_html(text=reply_msg)

async def _discord(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        user = update.message.from_user
        logger.info(f"{user.username} has entered his/her discord username.")

        context.user_data["discord"] = update.message.text.strip()

        _user = update_user(db=db, query={"username" : user.username}, value={"$set" : {"discord" : update.message.text.strip()}})
        print(_user)

        reply_msg = f"<i>🔰 Enter Your Optimism Wallet Address.</i>\n\n<b>🚨 Make sure you enter the correct wallet address.</b>"

        await update.message.reply_html(text=reply_msg)

        return START
    except Exception as e:
        print(e)
        logging.error("An error occured while processing this command.")

        reply_msg = f"<b>🚨 {user.username}, An error occured while processing your request.</b>"
        await update.message.reply_html(text=reply_msg)

async def address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        user = update.message.from_user
        logger.info(f"{user.username} has entered his/her wallet address.")

        context.user_data["address"] = update.message.text.strip()

        _user = update_user(db=db, query={"username" : user.username}, value={"$set" : {"address" : update.message.text.strip()}})
        _user = update_user(db=db, query={"username" : user.username}, value={"$inc" : {"balance" : 150}})
        print(_user)

        keyboard = [
            [InlineKeyboardButton("End Conversation 👋", callback_data="end")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        reply_msg = f"<b>Congratulations {user.username} 🎉, You have successfully completed all the tasks fot the $GWEI Airdrop.</b>\n\n<i>💰 Balance : 150 $GWEI </i>\n\n<i>🔗 Your referral link is <a href='https://t.me/gwei_airdrop_bot?start={user.id}'>https://t.me/gwei_airdrop_bot?start={user.id}</a></i>\n\n<b>🚀 Please Share So Others Don't Miss This Free Income Chance!</b>"

        await update.message.reply_html(text=reply_msg, reply_markup=reply_markup)

        return START
    except Exception as e:
        print(e)
        logging.error("An error occured while processing this command.")

        reply_msg = f"<b>🚨 {user.username}, An error occured while processing your request.</b>"
        await update.message.reply_html(text=reply_msg)

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        query = update.callback_query
        await query.answer()

        username = context.user_data["username"]
        logger.info(f"{username} ended the conversation.")

        reply_msg = f"<b>See you soon {username} 👋.</b>"

        await query.message.reply_html(reply_msg)

        return END
    except Exception as e:
        print(e)
        logging.error("An error occured while processing this command.")

        reply_msg = f"<b>🚨 {username}, An error occured while processing your request.</b>"
        await update.message.reply_html(text=reply_msg)

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.message.from_user
        logger.info(f"{user.username} entered the referral command.")

        if update.message.chat.type == "private":
            _user = get_user(db=db, query={"userId" : user.id})
            print(_user)

            if not _user:
                reply_msg = "<b>🚨 You cannot use this command.</b>"
                await update.message.reply_html(text=reply_msg)
            else:
                referrals = len(_user["referrals"])
                balance = _user["referral_balance"]

                reply_msg = f"<b>🔰 Here are your Referral details:</b>\n\n<i>👨‍👨‍👦 Referrals: {referrals}</i>\n\n<i>Referral Balance: {balance} $GWEI </i>\n\n<i>🔗 Your referral link is <a href='https://t.me/gwei_airdrop_bot?start={user.id}'>https://t.me/gwei_airdrop_bot?start={user.id}</a></i>\n\n<b>🚀 Please Share So Others Don't Miss This Free Income Chance!</b>"
                await update.message.reply_html(text=reply_msg)
        else:
            reply_msg = "<b>🚨 This command is not used in groups</b>"
            await update.message.reply_html(text=reply_msg)
    except Exception as e:
        print(e)
        logging.error("An error occured while processing this command.")

        reply_msg = f"<b>🚨 {user.username}, An error occured while processing your request.</b>"
        await update.message.reply_html(text=reply_msg)

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.message.from_user
        logger.info(f"{user.username} withdrew balance.")

        if update.message.chat.type == "private":
            _user = get_user(db=db, query={"userId" : user.id})
            print(_user)

            if not _user:
                reply_msg = "<b>🚨 You cannot use this command. You have to set your address before using this command</b>"
                await update.message.reply_html(text=reply_msg)
            else:
                balance = _user["balance"]
                ref_balance = _user["referral_balance"]
                referrals = len(_user["referrals"])

                if referrals >= 1 and (balance + ref_balance) > 0:
                    _transfer = transfer(_user["address"], int(balance + ref_balance))
                    print(_transfer)

                    user_ = update_user(db=db, query={"userId" : user.id}, value={"$set" :{"balance" : 0}})
                    user_ = update_user(db=db, query={"userId" : user.id}, value={"$set" :{"referral_balance" : 0}})
                    print(user_)

                    reply_msg = f"<b>🔰 Your Total Balance Is {balance + ref_balance} $GWEI.</b>\n\n<i>🪫 Your withdrawal is been processed. This will take between 5 - 10 minutes.</i>\n\n<i>🔗 Your referral link is <a href='https://t.me/gwei_airdrop_bot?start={user.id}'>https://t.me/gwei_airdrop_bot?start={user.id}</a></i>\n\n<b>🚀 Please Share So Others Don't Miss This Free Income Chance!</b>"
                    await update.message.reply_html(text=reply_msg)
                else:
                    reply_msg = f"<b>🚨 Insufficent Funds OR You Do Not Have Enough Referrals, Your Referrals Are {referrals}.</b>"
                    await update.message.reply_html(text=reply_msg)
        else:
            reply_msg = "<b>🚨 This command is not used in groups</b>"
            await update.message.reply_html(text=reply_msg)
    except Exception as e:
        print(e)
        logging.error("An error occured while processing this command.")

        reply_msg = f"<b>🚨 {user.username}, An error occured while processing your request.</b>"
        await update.message.reply_html(text=reply_msg)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.message.from_user
        logger.info(f"{user.username} checked balance.")

        if update.message.chat.type == "private":
            _user = get_user(db=db, query={"username" : user.username})
            print(_user)

            if not _user:
                reply_msg = "<b>🚨 You cannot use this command.</b>"
                await update.message.reply_html(text=reply_msg)
            else:
                balance = _user["balance"]
                ref_balance = _user["referral_balance"]

                reply_msg = f"<b>🔰 Your Total Balance Is {balance + ref_balance} $GWEI.</b>\n\n<i>🪙 Tasks Balance: {balance} $GWEI.</i>\n\n<i>💰 Referral Balance: {ref_balance} $GWEI.</i>\n\n<i>🔗 Your referral link is <a href='https://t.me/gwei_airdrop_bot?start={user.id}'>https://t.me/gwei_airdrop_bot?start={user.id}</a></i>\n\n<b>🚀 Please Share So Others Don't Miss This Free Income Chance!</b>"
                await update.message.reply_html(text=reply_msg)
        else:
            reply_msg = "<b>🚨 This command is not used in groups</b>"
            await update.message.reply_html(text=reply_msg)
    except Exception as e:
        print(e)
        logging.error("An error occured while processing this command.")

        reply_msg = f"<b>🚨 {user.username}, An error occured while processing your request.</b>"
        await update.message.reply_html(text=reply_msg)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.message.from_user
        logger.info(f"{user.username} checked balance.")

        if update.message.chat.type == "private":
            reply_msg = f"<b>🚀 $GWEI Free Airdrop Is Live!</b>\n\n<i>🎁 Bonus: 150 $GWEI </i>\n\n<i>👨‍👨‍👦 Referral: 50 $GWEI </i>\n\n<i>🔗 Airdrop Link :- <a href='https://t.me/gwei_airdrop_bot'>https://t.me/gwei_airdrop_bot</a></i>\n\n<b>💰 Don't Miss This Free Income Chance!</b>"
            await update.message.reply_html(text=reply_msg)
        else:
            reply_msg = "<b>🚨 This command is not used in groups</b>"
            await update.message.reply_html(text=reply_msg)
    except Exception as e:
        print(e)
        logging.error("An error occured while processing this command.")

        reply_msg = f"<b>🚨 {user.username}, An error occured while processing your request.</b>"
        await update.message.reply_html(text=reply_msg)

def main() -> None:
    global db
    db = connect_db(uri=MONGO_URI)

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START: [
                CommandHandler("start", start),
                CallbackQueryHandler(_start, pattern="^continue$"),
                CallbackQueryHandler(twitter, pattern="^twitter$"),
                MessageHandler(filters.Regex("^@"), _twitter),
                CallbackQueryHandler(discord, pattern="^discord$"),
                MessageHandler(filters.Regex("^#"), _discord),
                MessageHandler(filters.Regex("^0x"), address)
            ],
            END: [
                CallbackQueryHandler(end, pattern="^end$")
            ]
        },
        fallbacks=[CallbackQueryHandler(end, pattern="^end$")]
    )
    start_handler = CommandHandler("start", start)
    referral_handler = CommandHandler("referral", referral)
    balance_handler = CommandHandler("balance", balance)
    withdraw_handler = CommandHandler("withdraw", withdraw)
    about_handler = CommandHandler("about", about)

    app.add_handler(conv_handler)
    app.add_handler(start_handler)
    app.add_handler(referral_handler)
    app.add_handler(balance_handler)
    app.add_handler(withdraw_handler)
    app.add_handler(about_handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()