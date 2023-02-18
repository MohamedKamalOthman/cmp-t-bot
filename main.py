import keys

import telebot

BOT_TOKEN = keys.token

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(content_types=['text'])
def echo_all(message):
    bot.reply_to(message, message.text)
    # print(message.photo[-1].file_id)


# @bot.message_handler(content_types=['audio', 'document', 'photo', 'video', 'video_note', 'voice'])
# def echo_files(message):
#     bot.reply_to(message, 'file')
# print(message.photo[-1].file_id)

@bot.message_handler(content_types=['document'])
def echo_files(message):
    bot.reply_to(message, 'file')
    # print(message.photo[-1].file_id)


print("bot has started")

bot.infinity_polling()
