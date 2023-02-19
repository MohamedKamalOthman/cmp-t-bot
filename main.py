import json

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


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    # just to make sure the bot is alive
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(content_types=['document'])
def echo_files(message):
    # Only upload media from materials group
    if message.chat.id != GROUP_ID:
        return
    print(message.document)
    doc = message.document
    file_name, file_id, mime_type = doc.file_name, doc.file_id, doc.mime_type
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
    print(r.text)
    # Send me a message with status code to the user id
    bot.send_message(chat_id=USER_ID, text=f'Trying to upload {file_name} ended with status {r.status_code}', )


print("bot has started")

# poll every 10 seconds
bot.polling(interval=10)
