from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from binance.client import Client as BinanceClient
import os

# Configuração do Telegram
TELEGRAM_TOKEN = '6002886491:AAHWbdB2DyExhvnIWJOQxkd26eP7FDCP75Q'

# Configuração da API da Binance
BINANCE_API_KEY = "8jhntBVKAH5rbUmOcm7veI2O4ZND3sLyyA3ZYcwtNPcgJik1jWN28gNh8m8cK5SJ"
BINANCE_API_SECRET = "BZRgwAmarrXCFmiB1Yup7SHXPQOOuETTBiYwzw1QZVx4OdpdOvXUIEruLaB6DoFM"
client = BinanceClient(BINANCE_API_KEY, BINANCE_API_SECRET)

# Armazena o último preço verificado do Bitcoin
last_price = None

def format_usd_value(value):
    return "{:,.2f} USD".format(value)

def format_btc_value(value):
    return "{:.8f} BTC".format(value)

def format_brl_value(value):
    return "R$ {:.2f}".format(value)

def check_price(context):
    global last_price
    job = context.job
    btc_price = float(client.get_avg_price(symbol="BTCUSDT")['price'])
    if last_price is not None:
        if btc_price > last_price:
            message = f"O preço do Bitcoin subiu para {format_usd_value(btc_price)}. Devemos vender agora?"
        elif btc_price < last_price:
            message = f"O preço do Bitcoin caiu para {format_usd_value(btc_price)}. Devemos comprar agora?"
        else:
            message = f"O preço do Bitcoin se manteve em {format_usd_value(btc_price)}."
        context.bot.send_message(chat_id=job.context, text=message)
    last_price = btc_price

def start(update: Update, context):
    chat_id = update.effective_chat.id
    bot = context.bot
    btc_price = float(client.get_avg_price(symbol="BTCUSDT")['price'])
    usdt_price = float(client.get_avg_price(symbol="USDTBRL")['price'])
    message = f"Olá! Sou um robô aqui para ajudar com o valor do BTC.\n"
    message += f"O preço atual do Bitcoin é {format_usd_value(btc_price)} e o preço do USDT é {format_brl_value(usdt_price)}.\n"
    message += "Você gostaria de investir hoje?"
    context.bot.send_message(chat_id=chat_id, text=message)

def invest(update: Update, context):
    chat_id = update.effective_chat.id
    message_text = update.message.text.lower()

    if message_text == 'não' or message_text == 'obrigado':
        message = "Tudo bem, de nada! Estou aqui para ajudar. Se tiver mais alguma pergunta, é só me perguntar!"
        context.bot.send_message(chat_id=chat_id, text=message)
    else:
        try:
            investment_value = float(message_text)
            btc_price = float(client.get_avg_price(symbol="BTCBRL")['price'])
            usdt_price = float(client.get_avg_price(symbol="USDTBRL")['price'])
            btc_quantity = investment_value / btc_price
            usdt_quantity = investment_value / usdt_price

            if btc_quantity is not None:
                btc_formatted = format_btc_value(btc_quantity)
            else:
                btc_formatted = "Valor inválido"

            message = f"Com o valor de {format_brl_value(investment_value)}, você adquirirá:\n"
            message += f"{btc_formatted}\n"
            message += f"{format_brl_value(usdt_quantity)} USDT\n"
            message += "Compre Bitcoin e USDT sem taxa de câmbio aqui na Binance.com."
            context.bot.send_message(chat_id=chat_id, text=message)

            keyboard = [[InlineKeyboardButton("Binance.com", url="https://www.binance.com/")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            message = "Clique no botão abaixo para acessar a Binance.com:"
            context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
        except ValueError:
            message = "Por favor, digite um valor válido para o investimento."
            context.bot.send_message(chat_id=chat_id, text=message)

def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    updater = Updater(bot=bot, use_context=True)

    start_handler = CommandHandler('start', start)
    invest_handler = MessageHandler(Filters.text & (~Filters.command), invest)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(invest_handler)

    # Agendar a verificação do preço a cada hora
    job_queue = updater.job_queue
    job_queue.run_repeating(check_price, interval=3600, first=0, context=updater.bot.get_me().id)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
