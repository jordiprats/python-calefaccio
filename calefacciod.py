import sys
import time
import json
import logging
import schedule
import telegram
import calefaccio
import datetime, time

from threading import Thread
from telegram.ext import Updater, CommandHandler
from ConfigParser import SafeConfigParser

timeformat = '%Y-%m-%d %H:%M:%S'

def start_calefaccio():
    calefaccio.on()
    print datetime.datetime.fromtimestamp(time.time()).strftime(timeformat)+" set to "+calefaccio.status()

def stop_calefaccio():
    calefaccio.off()
    print datetime.datetime.fromtimestamp(time.time()).strftime(timeformat)+" set to "+calefaccio.status()

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def telegram_preauth(user_id):
    global amos
    return str(user_id) in amos

def telegram_start(bot, update):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not telegram_preauth(user_id):
        update.message.reply_text("I'm afraid I can't do that.")
        return
    update.message.reply_text("AUTH OK", use_aliases=True)

def telegram_show_status(bot, update):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not telegram_preauth(user_id):
        update.message.reply_text("I'm afraid I can't do that.")
        return
    update.message.reply_text("STATUS: "+calefaccio.status(), use_aliases=True)


BOT_TOKEN = ""

# main
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    try:
        basedir = sys.argv[1]
    except IndexError:
        basedir = '.'

    config = SafeConfigParser()
    config.read(basedir+'/calefacciod.config')

    BOT_TOKEN = config.get('bot', 'token').strip('"').strip("'").strip()

    logging.debug("*X - AMOS: "+str(config.get('bot','amos')))

    amos = json.loads(config.get('bot','amos'))

    logging.debug("*X - AMOS JSON: "+str(amos))

    schedule.every().day.at(config.get('schedule', 'daily_stop').strip('"').strip("'").strip()).do(stop_calefaccio)
    schedule.every().day.at(config.get('schedule', 'daily_start').strip('"').strip("'").strip()).do(start_calefaccio)

    calefaccio.init()
    time.sleep(1)
    start_calefaccio()

    scheduler_thread = Thread(target = run_scheduler, args = ())
    scheduler_thread.start()

    updater = Updater(token=BOT_TOKEN)

    dp = updater.dispatcher

    updater.dispatcher.add_handler(CommandHandler('start', telegram_start))
    updater.dispatcher.add_handler(CommandHandler('status', telegram_show_status))

    updater.start_polling()

    updater.idle()

    scheduler_thread.join()
