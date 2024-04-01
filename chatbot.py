## this file is based on version 13.7 of python telegram chatbot and version 1.26.18 of u
## chatbot.py
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
CallbackContext, ConversationHandler)
from telegram import ParseMode, ReplyKeyboardRemove
from ChatGPT_HKBU import HKBU_ChatGPT
# The messageHandler is used for all message updaters
import configparser
import logging
import os
import requests
import json
import argparse

global redis1
# # 设置http代理
# os.environ['http_proxy'] = 'http://127.0.0.1:7890'
 
# # 设置https代理（可选）
# os.environ['https_proxy'] = 'http://127.0.0.1:7890'

# r = redis.Redis(
#   host='redis-13632.c323.us-east-1-2.ec2.cloud.redislabs.com',
#   port=13632,
#   password='zu3haYJIeB6TyqNVkvDAbVyARZp4eFKv')

# 常用工具查询逻辑：首先在数据库内模糊查询，如果查不到的话那就调用GPT

# 数据库账号：tgbot
# 数据库密码：4NXNxaN6z7Mnstpw

# def login(updater: Updater, context: CallbackContext) -> None: 
    
be_host = "http://127.0.0.1:6000"
headers = {'Content-Type': 'application/json'}

GPT_Disabled = False

class PwdInfo:
  def __init__(self, args, note):
    self.account = args.account
    self.password = args.password
    self.email = args.email
    self.note = note

class UtilInfo:
  def __init__(self, args, name):
    self.name = name
    self.lang = args.lang

def parse_args_util(args):

  parser = argparse.ArgumentParser()

  parser.add_argument("-n", "--name", nargs="+", type=str)
  parser.add_argument("-l", "--lang")

  parsed_args = parser.parse_args(args)
  if isinstance(parsed_args.name, list):
    name = " ".join(parsed_args.name)
  else: 
    name = parsed_args.name
  return UtilInfo(parsed_args, name=name)

def parse_args(args):

  parser = argparse.ArgumentParser()

  parser.add_argument("-a", "--account")
  parser.add_argument("-p", "--password")
  parser.add_argument("-e", "--email")
  parser.add_argument("-n", "--note", nargs="+", type=str) 

  parsed_args = parser.parse_args(args)
  if isinstance(parsed_args.note, list):
    note = " ".join(parsed_args.note)
  else: 
    note = parsed_args.note

  return PwdInfo(parsed_args, note=note)

def format_pwds(json_str):
  pwds = json.loads(json_str)
  
  result = ""
  
  for pwd in pwds:
    result += "\n"
    
    for field in ["id", "account", "password", "email", "note"]:  
      if field in pwd:
        result += f"{field}: {pwd[field]}\n"
    
    result += "\n"
    
  return result

def format_utils(json_str):
  utils = json.loads(json_str)
  
  result = ""
  
  for util in utils:
    result += "\n"
    
    for field in ["id", "name", "content", "lang"]:  
        if field in util:
            if field == "name":
                    result += f"*{util[field]}*\n"
            elif field == "content" and "lang" in util:
                result += "```{lang}\n{content}\n```\n\n".format(lang=util["lang"], content=util["content"])
            else:
                result += f"{field}: {util[field]}\n\n"
    
    result += "\n"
    
  return result

# 然后就可以正常运行其他需要网络连接的操作了
def main():
    # Load your token and create an updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(os.environ['TELEGRAM_ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # 添加处理器函数
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('uti', uti)],
        states={
            STEP1: [MessageHandler(Filters.text, step1)],
            STEP2: [MessageHandler(Filters.text, step2)],
            STEP3: [MessageHandler(Filters.text, step3)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)
    # on different commands - answer in Telegram
    # dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("su", su))
    dispatcher.add_handler(CommandHandler("c", check))
    dispatcher.add_handler(CommandHandler("check", check))
    dispatcher.add_handler(CommandHandler("pwd", pwd))
    # To start the bot:
    updater.start_polling()
    updater.idle()

def pwd(updater: Updater, context: CallbackContext) -> None:
    args = context.args
    try:
        if args[0] == 'add':
            args.pop(0)
            obj =  parse_args(args)
            url = '/api/acc-info/add'
            body = {
                'account': obj.account,
                'password': obj.password,
                'email': obj.email,
                'note': obj.note
            }
            response = requests.post(url=be_host + url, data=json.dumps(body), headers=headers)
            if response.status_code == 200:
                json_r = response.json()
                if json_r.get('code') == 0:
                    updater.message.reply_text("Add account info successfully!")
                else:
                    updater.message.reply_text(json_r.get('msg'))
            else: 
                updater.message.reply_text('Something went wrong!')
        elif args[0] == 'del':
            url = '/api/acc-info/del'
            body = {
                'id': args[1],
                'tgacc': str(updater.message.from_user.id)
            }
            response = requests.post(url=be_host + url, data=json.dumps(body), headers=headers)
            if response.status_code == 200:
                json_r = response.json()
                if json_r.get('code') == 0:
                    updater.message.reply_text("Delete account info successfully!")
                else:
                    updater.message.reply_text(json_r.get('msg'))
            else: 
                updater.message.reply_text('Something went wrong!')
        elif args[0] == 'ps':
            args.pop(0)
            obj =  parse_args(args)
            url = '/api/acc-info/ps'
            body = {
                'account': obj.account,
                'email': obj.email,
                'note': obj.note
            }
            response = requests.post(url=be_host + url, data=json.dumps(body), headers=headers)
            if response.status_code == 200:
                json_r = response.json()
                if json_r.get('code') == 0:
                    updater.message.reply_text("Relevant Information:\n" + format_pwds(json.dumps(json_r.get('data'))))
                else:
                    updater.message.reply_text(json_r.get('msg'))
            else: 
                updater.message.reply_text('Something went wrong!')
        elif args[0] == 'update':
            args.pop(0)
            id = args[0]
            args.pop(0)
            obj =  parse_args(args)
            url = '/api/acc-info/update'
            body = {
                'id': id,
                'account': obj.account,
                'password': obj.password,
                'email': obj.email,
                'note': obj.note
            }
            response = requests.post(url=be_host + url, data=json.dumps(body), headers=headers)
            if response.status_code == 200:
                json_r = response.json()
                if json_r.get('code') == 0:
                    updater.message.reply_text("Update account info successfully!")
                else:
                    updater.message.reply_text(json_r.get('msg'))
            else: 
                updater.message.reply_text('Something went wrong!')
        else:
            updater.message.reply_text("Useage:\n/pwd add -a <account> -p <password> -e <email> -n <note>, to add a password info\n/pwd del <id>, to delete an info, need su permission\n/pwd ps -a <account> -e <email> -n <note>, to get the info list\n/pwd update <id> -a <account> -p <password> -e <email> -n <note>, to update the info, need su permission")
    except Exception:
        updater.message.reply_text("Useage:\n/pwd add -a <account> -p <password> -e <email> -n <note>, to add a password info\n/pwd del <id>, to delete an info, need su permission\n/pwd ps -a <account> -e <email> -n <note>, to get the info list\n/pwd update <id> -a <account> -p <password> -e <email> -n <note>, to update the info, need su permission")
    


def check(updater: Updater, context: CallbackContext) -> None:
    try: 
        if (len(context.args) < 1): 
            updater.message.reply_text("Useage: /c <code> or /check <code> to get the su permission.")
        else: 
            url = '/api/user/check'
            body = {
                'tgacc': str(updater.message.from_user.id),
                'code': context.args[0]
            }
            response = requests.post(url=be_host + url, data=json.dumps(body), headers=headers)
            if response.status_code == 200:
                json_r = response.json()
                if json_r.get('code') == 0 and json_r.get('data') == True:
                    updater.message.reply_text("You are in the su mode.")
                elif json_r.get('code') == 0 and json_r.get('data') == False:
                    updater.message.reply_text('The code is invalid!')
                else:
                    updater.message.reply_text(json_r.get('msg'))
            else: 
                updater.message.reply_text('Something went wrong!')
    except Exception:
        updater.message.reply_text("Useage: /c <code> or /check <code> to get the su permission.")

def su(updater: Updater, context: CallbackContext) -> None:
    try: 
        if (len(context.args) < 1): 
            updater.message.reply_text("Useage: /su a, to get the verification code; /su e, to quit the su mode.")
        elif context.args[0] == 'a':
            url = '/api/user/su-a'
            body = {
                'tgacc': updater.message.from_user.id
            }
            response = requests.post(url=be_host + url, data=json.dumps(body), headers=headers)
            if response.status_code == 200:
                json_r = response.json()
                if json_r.get('code') == 0:
                    updater.message.reply_text("Please go to your email to obtain the verification code. And use /c <code> or /check <code> to active the su mode.")
                else:
                    updater.message.reply_text(json_r.get('msg'))
            else: 
                updater.message.reply_text('Something went wrong!')
        elif context.args[0] == 'e':
            url = '/api/user/su-e'
            body = {
                'tgacc': updater.message.from_user.id
            }
            response = requests.post(url=be_host + url, data=json.dumps(body), headers=headers)
            if response.status_code == 200:
                json_r = response.json()
                if json_r.get('code') == 0:
                    if json_r.get('data') == False:
                        updater.message.reply_text("You need not quit the su mode.")
                    else:
                        updater.message.reply_text("Quit successfully.")
                else:
                    updater.message.reply_text(json_r.get('msg'))
            else: 
                updater.message.reply_text('Something went wrong!')
    except Exception:
        updater.message.reply_text("Useage: /su a, to get the verification code; /su e, to quit the su mode.")
        
def equiped_chatgpt(updater, context):
    global chatgpt
    global GPT_Disabled
    if GPT_Disabled == True:
        return
    wating_message = "Drenal Bot is using ChatGPT to solve your problem..."
    # 由于GPT回消息太慢，调用功能时先添加一个回复语，随后修改消息
    current_message = context.bot.send_message(chat_id = updater.effective_chat.id, text = wating_message)
    reply_message = chatgpt.submit(updater.message.text)
    logging.info("updater: " + str(updater))
    logging.info("context: " + str(context))
    logging.info("msg: " + str(reply_message))
    context.bot.edit_message_text(reply_message, updater.effective_chat.id, current_message.message_id)
    # context.bot.send_message(chat_id=updater.effective_chat.id, text=reply_message)

STEP1, STEP2, STEP3 = range(3)

def uti(updater, context):
    global GPT_Disabled
    chat_id = updater.effective_chat.id
    try: 
        if context.args[0] == 'add':
            GPT_Disabled = True
            context.bot.send_message(chat_id=chat_id, text="Please input name: ")
            return STEP1
        elif context.args[0] == 'ps':
            args = context.args;
            args.pop(0)
            obj = parse_args_util(args)

            url = '/api/util/ps'
            body = {
                'name': obj.name,
                'lang': obj.lang
            }
            response = requests.post(url=be_host + url, data=json.dumps(body), headers=headers)
            if response.status_code == 200:
                json_r = response.json()
                if json_r.get('code') == 0:
                    context.bot.send_message(chat_id=chat_id, text="*Relevant Information*:\n", parse_mode=ParseMode.MARKDOWN)
                    datas = json_r.get('data')
                    if (len(datas)) == 0:
                        context.bot.send_message(chat_id=chat_id, text="I couldn't find a similar util. Here, I'll use ChatGPT to help you find it")
                        wating_message = "Drenal Bot is using ChatGPT to solve your problem..."
                        # 由于GPT回消息太慢，调用功能时先添加一个回复语，随后修改消息
                        current_message = context.bot.send_message(chat_id = updater.effective_chat.id, text = wating_message)
                        reply_message = chatgpt.submit(updater.message.text)
                        context.bot.edit_message_text(reply_message, updater.effective_chat.id, current_message.message_id)
                        return
                    for data in datas:
                        print(data)
                        context.bot.send_message(chat_id=chat_id, text=format_utils(json.dumps([data])), parse_mode=ParseMode.MARKDOWN)
                else:
                    updater.message.reply_text(json_r.get('msg'))
            else: 
                updater.message.reply_text('Something went wrong!')
        elif context.args[0] == 'del':
            url = '/api/util/del'
            body = {
                'id': context.args[1],
                'tgacc': str(updater.message.from_user.id)
            }
            response = requests.post(url=be_host + url, data=json.dumps(body), headers=headers)
            if response.status_code == 200:
                json_r = response.json()
                if json_r.get('code') == 0:
                    updater.message.reply_text("Delete info successfully!")
                else:
                    updater.message.reply_text(json_r.get('msg'))
            else: 
                updater.message.reply_text('Something went wrong!')
        else:
            updater.message.reply_text("Useage: \n/uti add, to add an util\n/uti ps -n <name> -l <language>, to get util list\n/uti del <id>, to delete a util with the su permission")
    except Exception:
            updater.message.reply_text("Useage: \n/uti add, to add an util\n/uti ps -n <name> -l <language>, to get util list\n/uti del <id>, to delete a util with the su permission")
    
    

    
def step1(update, context):
    chat_id = update.effective_chat.id
    text = update.message.text

    context.user_data['param1'] = text

    context.bot.send_message(chat_id=chat_id, text="Please input content: ")

    return STEP2

def step2(update, context):
    chat_id = update.effective_chat.id
    text = update.message.text

    context.user_data['param2'] = text

    context.bot.send_message(chat_id=chat_id, text="Please inpt language: ")

    return STEP3

def step3(update, context):
    global GPT_Disabled

    chat_id = update.effective_chat.id
    text = update.message.text

    context.user_data['param3'] = text

    # 打印参数
    param1 = context.user_data['param1']
    param2 = context.user_data['param2']
    param3 = context.user_data['param3']
    context.bot.send_message(chat_id=chat_id, text=f"您输入的参数是：\n\nname: *{param1}*\n\ncontent: ```{param3}\n{param2}\n```\n\nlanguage: {param3}", parse_mode=ParseMode.MARKDOWN)
    url = '/api/util/add'
    body = {
        'name': param1,
        'content': param2,
        'lang': param3
    }
    response = requests.post(url=be_host + url, data=json.dumps(body), headers=headers)
    if response.status_code == 200:
        json_r = response.json()
        if json_r.get('code') == 0:
            update.message.reply_text("Add successfully!")
        else:
            update.message.reply_text(json_r.get('msg'))
    else: 
        update.message.reply_text('Something went wrong!')

    GPT_Disabled = False
    return ConversationHandler.END

def cancel(update, context):
    global GPT_Disabled
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="Conversation canceled",
                             reply_markup=ReplyKeyboardRemove())
    GPT_Disabled = False
    return ConversationHandler.END


if __name__ == '__main__':
    main()