import json
import time

import keys
import requests
import telebot
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

TELEGRAM_BOT_TOKEN = keys.telegram_token
GROUP_ID = keys.group_id
USER_ID = keys.user_id
folder = keys.folder_id

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
g_auth = GoogleAuth()
g_auth.LocalWebserverAuth()
g_drive: GoogleDrive = GoogleDrive(g_auth)


@bot.message_handler(commands=['up', 'start', 'hi', 'hello'])
def send_welcome(message):
    # just to make sure the bot is alive
    bot.reply_to(message,
                 "Hi, I'm CMP-T-bot!\nI am here to assist the material team with automatic materials uploading.")


@bot.message_handler(content_types=['document'])
def upload_documents(message):
    # Only upload media from materials group
    # Be careful because telegram char groups ids may change
    if message.chat.id != GROUP_ID:
        return

    # logs for monitoring
    print(message.document)
    doc = message.document
    file_name, file_id = doc.file_name, doc.file_id

    # reply in chat the that the bot has received the message remove this if you want the bot to be silent
    bot.reply_to(message, f'Got it {file_name}')
    file_path = bot.get_file(file_id).file_path

    # download the file from telegram
    url = f'https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}'
    response = requests.get(url)

    # preparing the file for sending
    param = {
        "name": file_name,
        "parents": [folder]  # google drive folder id
    }
    file = {
        'data': ('metadata', json.dumps(param), 'application/json;charset=UTF-8'),
        'file': response.content
    }

    # upload file to drive
    r = requests.post("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
                      headers={"Authorization": "Bearer " + g_auth.credentials.access_token},
                      files=file
                      )

    # Refresh google token if expired then try again (Unauthorized)
    if r.status_code == 401:
        g_auth.Refresh()
        r = requests.post("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
                          headers={"Authorization": "Bearer " + g_auth.credentials.access_token},
                          files=file
                          )

    # logs for monitoring
    print(r.text)

    # Send me a message with status code to the user id
    bot.send_message(chat_id=USER_ID,
                     text=f'Trying to upload {file_name} ended with status {r.status_code} was sent'
                          f' from {message.chat.first_name} {message.chat.last_name}', )

    # have some rest we don't want our free server to crash :)
    time.sleep(5)


print("bot has started")

# poll infinitely
bot.infinity_polling()
