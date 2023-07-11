from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from binance.client import Client as BinanceClient
import utf8_locale

# Configuração do Telegram
TELEGRAM_TOKEN = '6002886491:AAHWbdB2DyExhvnIWJOQxkd26eP7FDCP75Q'

# Configuração da API da Binance
BINANCE_API_KEY = "8jhntBVKAH5rbUmOcm7veI2O4ZND3sLyyA3ZYcwtNPcgJik1jWN28gNh8m8cK5SJ"
BINANCE_API_SECRET = "BZRgwAmarrXCFmiB1Yup7SHXPQOOuETTBiYwzw1QZVx4OdpdOvXUIEruLaB6DoFM"
client = BinanceClient(BINANCE_API_KEY, BINANCE_API_SECRET)

# Armazena o último preço verificado do Bitcoin
last_price = None

def format_brl_value(value):
    value_float = float(value)
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    formatted_value = locale.currency(value_float, grouping=True, symbol='R$')
    return f" {formatted_value} "

def format_btc_value(value):
    return f"{value:.8f}"

def check_price(context):
    global last_price
    job = context.job
    btc_price = float(client.get_avg_price(symbol="BTCBRL")['price'])
    if last_price is not None:
        if btc_price > last_price:
            message = f"O preço do Bitcoin subiu para {format_brl_value(btc_price)}. Vamos vender agora?"
        elif btc_price < last_price:
            message = f"O preço do Bitcoin baixou para {format_brl_value(btc_price)}. Vamos comprar agora?"
        else:
            message = f"O preço do Bitcoin se manteve em {format_brl_value(btc_price)}."
        context.bot.send_message(chat_id=job.context, text=message)
    last_price = btc_price

def start(update: Update, context):
    global chat_id
    chat_id = update.effective_chat.id
    chat_id = update.effective_chat.id
    bot = context.bot
    btc_price = client.get_avg_price(symbol="BTCBRL")['price']
    usdt_price = client.get_avg_price(symbol="USDTBRL")['price']
    message = f"Olá! Sou um robô estou aqui para te ajudar com o valor do BTC.\n"
    message += f"O preço atual do Bitcoin é {format_brl_value(btc_price)} BRL e o preço do Dólar é {format_brl_value(usdt_price)} BRL.\n"
    message += "Você gostaria de investir hoje?"
    context.bot.send_message(chat_id=chat_id, text=message)

def invest(update: Update, context):
    chat_id = update.effective_chat.id
    message_text = update.message.text.lower()

    if message_text == 'não' or message_text == 'agradecido':
        message = "Tudo bem, por nada! Estou aqui para ajudar. Se tiver alguma outra pergunta, é só me perguntar!"
        context.bot.send_message(chat_id=chat_id, text=message)
    else:
        try:
            investment_value = float(message_text)
            btc_price = float(client.get_avg_price(symbol="BTCBRL")['price'])
            usdt_price = float(client.get_avg_price(symbol="USDTBRL")['price'])
            btc_quantity = investment_value / btc_price
            usdt_quantity = investment_value / usdt_price
            message = f"Com o valor de {format_brl_value(investment_value)}, você adquirirá:\n"
            message += f"{format_btc_value(btc_quantity)} BTC\n"
            message += f"{format_brl_value(usdt_quantity)} USDT\n"
            message += "Compre Bitcoin e Dólar sem taxa de câmbio aqui no Binance.com."
            context.bot.send_message(chat_id=chat_id, text=message)

            keyboard = [[InlineKeyboardButton("Binance.com", url="https://www.binance.com/pt-BR/activity/referral-entry/CPA?ref=CPA_00YRJDOZZV")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            message = "Clique no botão abaixo para acessar o Binance.com:"
            context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
        except ValueError:
            message = "Por favor, digite um valor válido para investimento."
            context.bot.send_message(chat_id=chat_id, text=message)

def notify():
    chat_id = globals().get('chat_id')

    btc_price = float(client.get_avg_price(symbol="BTCBRL")['price'])
    if btc_price > last_price:
        message = f"O preço do Bitcoin subiu para {format_brl_value(btc_price)} BRL. Vamos vender agora?"
    elif btc_price < last_price:
        message = f"O preço do Bitcoin baixou para {format_brl_value(btc_price)} BRL. Vamos comprar agora?"
    else:
        return  # Não enviar notificação se o preço não mudou

    context.bot.send_message(chat_id=chat_id, text=message)
    last_price = btc_price

    # Agendar a função notify() para ser executada a cada hora
    schedule.every(1).hours.do(notify)

    # Executar o agendador em segundo plano
    while True:
             schedule.run_pending()
             time.sleep(1)   

def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    updater = Updater(bot=bot, use_context=True)

    start_handler = CommandHandler('start', start)
    invest_handler = MessageHandler(Filters.text & (~Filters.command), invest)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(invest_handler)

    # Agenda a verificação do preço a cada hora
    job_queue = updater.job_queue
    job_queue.run_repeating(check_price, interval=3600, first=0, context=updater.bot.get_me().id)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':

    main()
