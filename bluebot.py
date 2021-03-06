#!/usr/bin/env python

"""
This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and the CLI-Loop is entered, where all text inputs are
inserted into the update queue for the bot to handle.

Usage:
Basic Echobot example, repeats messages. Reply to last chat from the command
line by typing "/reply <text>"
Type 'stop' on the command line to stop the bot.
"""

from telegram import Updater
from telegram.dispatcher import run_async
from time import sleep
import logging
import sys
import os
import requests

root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = \
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

last_chat_id = 0

logger = logging.getLogger(__name__)


# Command Handlers
def start(bot, update):
    """ Answer in Telegram """
    bot.sendMessage(update.message.chat_id, text='Bienvenido! Podes pedir el valor actual del Dolar Blue con el comando /blue')


@run_async
def blue(bot, update):
    """
    Example for an asynchronous handler. It's not guaranteed that replies will
    be in order when using @run_async.
    """

    r = requests.get('http://api.bluelytics.com.ar/v2/latest')

    if r.status_code == 200:
        res = r.json()

        bot.sendMessage(update.message.chat_id, text='Dolar Oficial - Venta: %.2f, Compra: %.2f\n' % (res['oficial']['value_sell'], res['oficial']['value_buy']) \
                                                    + 'Dolar Blue - Venta: %.2f, Compra: %.2f\n' % (res['blue']['value_sell'], res['blue']['value_buy'])
                                                 )
    else:
        bot.sendMessage(update.message.chat_id, text="Error intentando obtener el valor del Dolar Blue, por favor intente mas tarde")


def error(bot, update, error):
    """ Print error to console """
    logger.warn('Update %s caused error %s' % (update, error))


def cli_reply(bot, update, args):
    """
    For any update of type telegram.Update or str, you can get the argument
    list by appending args to the function parameters.
    Here, we reply to the last active chat with the text after the command.
    """
    if last_chat_id is not 0:
        bot.sendMessage(chat_id=last_chat_id, text=' '.join(args))


def cli_noncommand(bot, update, update_queue):
    """
    You can also get the update queue as an argument in any handler by
    appending it to the argument list. Be careful with this though.
    Here, we put the input string back into the queue, but as a command.
    """
    update_queue.put('/%s' % update)


def unknown_cli_command(bot, update):
    logger.warn("Command not found: %s" % update)


def main():
    # Create the EventHandler and pass it your bot's token.
    token = os.environ['TOKEN']
    updater = Updater(token, workers=10)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.addTelegramCommandHandler("start", start)
    dp.addTelegramCommandHandler("blue", blue)

    dp.addStringCommandHandler('reply', cli_reply)
    dp.addUnknownStringCommandHandler(unknown_cli_command)
    dp.addStringRegexHandler('[^/].*', cli_noncommand)

    dp.addErrorHandler(error)

    # Start the Bot and store the update Queue, so we can insert updates
    update_queue = updater.start_polling(poll_interval=0.1, timeout=20)

    # Start CLI-Loop
    while True:
        try:
            text = raw_input()
        except NameError:
            text = input()

        # Gracefully stop the event handler
        if text == 'stop':
            updater.stop()
            break

        # else, put the text into the update queue
        elif len(text) > 0:
            update_queue.put(text)  # Put command into queue

if __name__ == '__main__':
    main()
