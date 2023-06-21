from telegram import Bot
from telegram import Update
from queue import Queue
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher
from binance import Client as BinanceClient
import requests
import httpx
import decimal

def get_bot_info(bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    response = requests.get(url)
    data = response.json()
    return data

# Configuração do Telegram
TELEGRAM_TOKEN = '6002886491:AAHWbdB2DyExhvnIWJOQxkd26eP7FDCP75Q'

# Configuração da API da Binance
BINANCE_API_KEY = "8jhntBVKAH5rbUmOcm7veI2O4ZND3sLyyA3ZYcwtNPcgJik1jWN28gNh8m8cK5SJ"
BINANCE_API_SECRET = "BZRgwAmarrXCFmiB1Yup7SHXPQOOuETTBiYwzw1QZVx4OdpdOvXUIEruLaB6DoFM"
client = BinanceClient(BINANCE_API_KEY, BINANCE_API_SECRET)

# Números de telefone cadastrados
numeros_cadastrados = {}

def cadastrar_numero(numero):
    if numero in numeros_cadastrados:
        return False
    numeros_cadastrados[numero] = {
        "state": "inicio",
        "confirmado": False
    }
    return True

def confirmar_acesso(numero):
    if numero not in numeros_cadastrados:
        return False
    numeros_cadastrados[numero]["confirmado"] = True
    return True

def get_binance_price(symbol):
    try:
        price_ticker = client.get_symbol_ticker(symbol=symbol)
        return price_ticker['price']
    except:
        return None

def format_btc_value(value):
    return f"{value:.8f}"

def format_brl_value(value):
    return f"R${value:,.2f}"

def format_usd_value(value):
    return f"${value:,.2f}"

def calculate_investment(investment_value, price):
    invested = decimal.Decimal(investment_value) / decimal.Decimal(price)
    return invested.quantize(decimal.Decimal('0.00000000'))

def start(update: Update, context):
    chat_id = update.effective_chat.id
    message = "Olá! Sou um bot do Telegram."
    context.bot.send_message(chat_id=chat_id, text=message)

def echo(update: Update, context):
    chat_id = update.effective_chat.id
    message_text = update.message.text.lower()
    numero_telefone = str(update.message.from_user.id)

    if numero_telefone not in numeros_cadastrados:
        cadastrar_numero(numero_telefone)

    user_state = numeros_cadastrados[numero_telefone]["state"]
    confirmado = numeros_cadastrados[numero_telefone]["confirmado"]

    if user_state == "inicio":
        if confirmado:
            message = "Seu número já está cadastrado e confirmado."
        elif "oi" in message_text or "olá" in message_text:
            numeros_cadastrados[numero_telefone]["state"] = "btc_dolar"
            btc_price = get_binance_price("BTCBRL")
            usd_price = get_binance_price("BRLBUSD")
            message = f"Olá! O preço atual do Bitcoin é {btc_price} BRL e o preço do Dólar é {usd_price} BRL. Quanto você gostaria de investir hoje?"
        else:
            message = "Olá! Para iniciar, por favor, digite 'oi' ou 'olá'."
    elif user_state == "btc_dolar":
        try:
            investment_value = float(message_text)
            btc_price = get_binance_price("BTCBRL")
            btc_quantity = calculate_investment(investment_value, btc_price)
            message = f"Com o valor de R${investment_value:,.2f}, você adquirirá {format_btc_value(btc_quantity)} BTC. Compre Bitcoin e Dólar sem taxa de câmbio aqui no Binance.com."
            message += "\n\n[Visite o Binance.com](https://seu-link.com)"
            numeros_cadastrados[numero_telefone]["state"] = "finalizado"
        except ValueError:
            message = "Por favor, digite um valor válido para investimento."
    elif user_state == "finalizado":
        message = "Obrigado por utilizar nosso serviço!"
    else:
        message = "Comando inválido. Por favor, tente novamente."

    context.bot.send_message(chat_id=chat_id, text=message)

def main():
    token = '6002886491:AAHWbdB2DyExhvnIWJOQxkd26eP7FDCP75Q'
    url = f'https://api.telegram.org/bot{token}/getMe'

    httpx_client = httpx.Client()
    response = httpx_client.get(url)

    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f'Request failed with status code {response.status_code}')
        
    bot = Bot(token=TELEGRAM_TOKEN)
    update_queue = Queue()
    dispatcher = Dispatcher(bot, update_queue)

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    # Configuração do httpx com tamanho de pool de conexões ajustado
    httpx._config.DEFAULT_MAX_KEEPALIVE_CONNECTIONS = 8
    httpx._config.DEFAULT_MAX_CONNECTIONS = 40

    httpx_client = httpx.Client()
    response = httpx_client.get('https://api.telegram.org/6002886491:AAHWbdB2DyExhvnIWJOQxkd26eP7FDCP75Q/getMe')
    print(response.json())

    updater = Updater(bot=bot, use_context=True)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
