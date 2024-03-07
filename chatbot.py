## this file is based on version 13.7 of python telegram chatbot and version 1.26.18 of u
## chatbot.py
import telegram
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
CallbackContext)
from ChatGPT_HKBU import HKBU_ChatGPT
# The messageHandler is used for all message updaters
import configparser
import logging
import os
import redis

global redis1
# # 设置http代理
# os.environ['http_proxy'] = 'http://127.0.0.1:7890'
 
# # 设置https代理（可选）
# os.environ['https_proxy'] = 'http://127.0.0.1:7890'

# r = redis.Redis(
#   host='redis-13632.c323.us-east-1-2.ec2.cloud.redislabs.com',
#   port=13632,
#   password='zu3haYJIeB6TyqNVkvDAbVyARZp4eFKv')
 

# 然后就可以正常运行其他需要网络连接的操作了
def main():
    # Load your token and create an updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(os.environ['TELEGRAM_ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    global redis1
    redis1 = redis.Redis(host=(os.environ['REDIS_HOST']),
        password=(os.environ['REDIS_PASSWORD']),
        port=(os.environ['REDIS_PORT']))
    
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello))
    # To start the bot:
    updater.start_polling()
    updater.idle()

# Define a few command handlers. These usually take the two arguments updater and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(updater: Updater, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    updater.message.reply_text('Helping you helping you.')
def add(updater: Updater, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0] # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        updater.message.reply_text('You have said ' + msg + ' for ' +
            redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        updater.message.reply_text('Usage: /add <keyword>')
        
def equiped_chatgpt(updater, context):
    global chatgpt
    wating_message = "Drenal Bot is working hard to solve your problem!"
    # 由于GPT回消息太慢，调用功能时先添加一个回复语，随后修改消息
    current_message = context.bot.send_message(chat_id = updater.effective_chat.id, text = wating_message)
    reply_message = chatgpt.submit(updater.message.text)
    logging.info("updater: " + str(updater))
    logging.info("context: " + str(context))
    logging.info("msg: " + str(reply_message))
    context.bot.edit_message_text(reply_message, updater.effective_chat.id, current_message.message_id)
    # context.bot.send_message(chat_id=updater.effective_chat.id, text=reply_message)

def hello(updater: Updater, context: CallbackContext) -> None:
    s = ""
    i = 0
    for i in range(len(context.args)):
        if i != 0:
            s += " "
        s += context.args[i]
    updater.message.reply_text('Good day, ' + s + '.')
if __name__ == '__main__':
    main()