
import pymysql
import telegram
import configparser
import redis
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
import logging
import time
import os

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

# Habilitar os logs
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()

# Configuring bot
config = configparser.ConfigParser()
config.readfp(open('config.ini'))

# Connecting to Telegram API
# Updater retrieves information and dispatcher connects commands
updater = Updater(token=config['DEFAULT']['token'])
dispatcher = updater.dispatcher

# Connecting to Redis db
db = redis.StrictRedis(host=config['DB']['host'],
                       port=config['DB']['port'],
                       db=config['DB']['db'])

def start(bot, update):
    # Mensagem de boas vindas
    msg = "Olá!\n"  # nome do usuário
    msg += "Bem-vindo a Mama Pizzaria\n"


    # Teclados a aparecerem
    main_menu_keyboard = [[telegram.KeyboardButton('/menu_pizza')],
                          [telegram.KeyboardButton('/preco_pizza')],
                          [telegram.KeyboardButton('/pedido')],
                          [telegram.KeyboardButton('/contatos')],
                          [telegram.KeyboardButton('/cancelar')]]
    reply_kb_markup = telegram.ReplyKeyboardMarkup(main_menu_keyboard,
                                                   resize_keyboard=True,
                                                   one_time_keyboard=True)

    # Send the message with menu
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg,
                     reply_markup=reply_kb_markup)


# Essa função mostra o cardápio, bem como os seus preços
def menu_pizza(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Olá, segue abaixo o nosso menu: ")

    file = open('data.txt', 'r')
    bot.send_message(chat_id=update.message.chat_id,
                     text=txt_menu)


support_handler = CommandHandler('menu_pizza', menu_pizza)
dispatcher.add_handler(support_handler)


# Função do comando *Preços*
def preco_pizza(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Olá, segue abaixo os nossos preços: ")

    bot.send_message(chat_id=update.message.chat_id,
                     text=txt_preco)

    # return comando_adicional(bot, update)


support_handler = CommandHandler('preco_pizza', preco_pizza)
dispatcher.add_handler(support_handler)


class Ask:
    def pagamento(bot, update):
        logger.info('O método de pagamento é: {0}'.format(update.message.text))

        dispatcher.add_handler(MessageHandler(Filters.text, pagamento))

    # Função do comando *Pedido*
    def pedido(bot, update):
        logger.info('Text: {0}'.format(update.message.text))

        reply_keyboard = [['Cartão', 'Dinheiro']]
        reply_keyboard_tamanho = [['Pequeno', 'Médio', 'Grande', 'Gigante']]

        reply_keyboard_tamanho_pizza = [['Pequena - 4 Pedaços', 'Média - 6 Pedaços'],
                                        ['Grande - 8 Pedaços', 'Gigante - 12 Pedaços']]
        reply_keyboard_pizza = [['Portuguesa', 'Calabressa'],
                                ['Milho Verde', 'Especial']]

        markup_tamanho_pizza = ReplyKeyboardMarkup(reply_keyboard_tamanho_pizza, one_time_keyboard=True)
        markup_pizza = ReplyKeyboardMarkup(reply_keyboard_pizza, one_time_keyboard=True)

        # Mensagem de boas vindas
        msg = "Olá!\n"
        msg += "vamos começar com o seu pedido\n\n?"

        update.message.reply_text("Selecione o tamanho da Pizza: ", reply_markup=markup_tamanho_pizza)
        # update.message.reply_text("Selecione o tamanho da Pizza: ", reply_markup=markup_pizza)
        return CHOOSING

    # bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING) # Está mostrando que está escrevendo
    # bot.send_message(chat_id=update.message.chat_id, text=msg)
    # bot.send_message(chat_id=update.message.chat_id, text="Oual o tamanho da Pizza?",reply_markup=ReplyKeyboardMarkup(reply_keyboard_tamanho, one_time_keyboard=False, selective=False))
    # time.sleep(5)
    # bot.send_message(chat_id=update.message.chat_id, text="Olá, o qual será o método de pagamento?",reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, selective=False))
    # time.sleep(5)
    # bot.send_message(chat_id=update.message.chat_id, text="Certo, agora nos envie o seu pedido com o código do produto desejado e espere.")
    # time.sleep(5)
    # bot.send_message(chat_id=update.message.chat_id, text="Ou envia sua localização com o comando /local e seu numero e complemento(se houver)")


    pedido_handler = CommandHandler('pedido', pedido)
    dispatcher.add_handler(pedido_handler)


def comando_adicional(bot, update):
    msg = "Olá!\n"
    msg += "O que você gostaria de fazer?\n\n"
    msg += "/cardapio - Verificar o cardápio\n"
    msg += "/preco - Verificar os nossos preços\n"
    msg += "/pedido - fazer seu pedido\n\n"

    # Teclados a aparecerem
    main_menu_keyboard = [[telegram.KeyboardButton('/cardapio')],
                          [telegram.KeyboardButton('/preco')],
                          [telegram.KeyboardButton('/pedido')]
                          [telegram.KeyboardButton('/contatos')]
                          [telegram.KeyboardButton('/cancelar')]]
    reply_kb_markup = telegram.ReplyKeyboardMarkup(main_menu_keyboard,
                                                   resize_keyboard=True,
                                                   one_time_keyboard=True)

    # Send the message with menu
    user = update.message.text
    # logger.info("O método do pagamento é: %s.", user)
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg,
                     reply_markup=reply_kb_markup)


comando_add = CommandHandler('comando_adicional', comando_adicional)
dispatcher.add_handler(comando_add)


def local(bot, update):
    bot.sendMessage(update.message.chat_id,
                    text='Olá, me envie o seu local para onde você vai pedir ou escreve o seu endereço.')
    user = update.message.from_user
    user_location = update.message.location
    log = logger.info("A localização é: %s: %f / %f"
                      % (user.username, user_location.latitude, user_location.longitude))

    # command = "echo %s > /Linux/Python/robotelegram/pizaria/pedido.txt"%(log)
    # os.system(command)


comando_local = CommandHandler('local', local)
dispatcher.add_handler(comando_local)
dispatcher.add_handler(MessageHandler(Filters.location, local))


# Função que chama, quando um comando não é encontrado.
def unknown(bot, update):
    msg = "Desculpe, esse não é um comando válido."
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg)
    bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    bot.sendPhoto(chat_id=update.message.chat_id, photo=open('imagens/oi.jpg', 'rb'))
    bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)

    return start(bot, update)  # chama a função start


def contatos(bot, update):
    user = update.message.from_user
    bot.sendMessage(update.message.chat_id,
                    text='Olá, segue o nosso contato!')
    time.sleep(1)

    # text = "O nosso telefone é: 11-449871820\n"
    text = "O nosso telefone é: 11-449436493\n"
    text += "e nosso endereço é: Rua dos Autonomistas\n\n"

    bot.sendMessage(update.message.chat_id, text)

    bot.sendLocation(chat_id=update.message.chat_id, latitude=-23.550520, longitude=-46.633309)

    return comando_adicional


contato_add = CommandHandler('contatos', contatos)
dispatcher.add_handler(contato_add)


def cancelar(bot, update):
    user = update.message.from_user
    bot.sendMessage(update.message.chat_id,
                    text='Até logo! Esperamos que você volte!')
    return ConversationHandler.END


cancel_add = CommandHandler('cancelar', cancelar)
dispatcher.add_handler(cancel_add)

# Função que começa o bot
start_handler = CommandHandler('start', start)

# Adicionando os hadlers
dispatcher.add_handler(start_handler)
# Envia MSG quando não for um comando com '/'
dispatcher.add_handler(MessageHandler(Filters.text, start))
unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)
updater.start_polling()
updater.idle()
