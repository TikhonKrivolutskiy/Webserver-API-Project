import requests
from telegram import Bot
from telegram.ext import Updater, CommandHandler

API_TOKEN = '7188072112:AAFVxbn_TVdZ9km4QoU4-Q-N8rFaRMCtu44'
bot = Bot(token=API_TOKEN)
updater = Updater(token=API_TOKEN, use_context=True)
dispatcher = updater.dispatcher

order_count = 0

def callback_request(context):
    global order_count
    data = requests.get('http://127.0.0.1:5000/api/orders').json()
    info = dict(data[-1])
    review = (
        "Заказ №{}".format(info['order_id']),
        "Дата и время заказа - {}".format(*info['date'].split('T')),
        "Тип доставки - {}".format(info['delivery_type']),
        "Имя: {}".format(info['name']),
        "Фамилия: {}".format(info['surname']),
        "Адрес: {}".format(info['adress']),
        "Номер телефона: {}".format(info['telephone']),
        "E-mail: {}".format(info['email'])
    )
    if data and order_count < len(data):
        with open("orders.txt", "a+") as f:
            f.write("\n\n")
            f.write("\n".join(review))
        context.bot.send_message(chat_id=context.job.context, text="\n".join(review))
        order_count += 1

def callback_timer(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Бот активен.')
    updater.job_queue.run_repeating(callback_request, 3, context=update.message.chat_id)


dispatcher.add_handler(CommandHandler('start', callback_timer))

updater.start_polling()
updater.idle()