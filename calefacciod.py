import sys
import time
import json
import logging
import schedule
import telegram
import calefaccio
import datetime, time

from pid import PidFile
from threading import Thread
from ConfigParser import SafeConfigParser
from telegram.ext import Updater, CommandHandler

timeformat = '%Y-%m-%d %H:%M:%S'

def scheduled_start_calefaccio():
    if in_range:
        calefaccio.on()
        logging.debug("*X "+datetime.datetime.fromtimestamp(time.time()).strftime(timeformat)+" set to "+calefaccio.status())
        telegram_motify("AUTOMATIC STATUS: "+calefaccio.status())

def scheduled_stop_calefaccio():
    if in_range:
        calefaccio.off()
        logging.debug("*X "+datetime.datetime.fromtimestamp(time.time()).strftime(timeformat)+" set to "+calefaccio.status())
        telegram_motify("AUTOMATIC STATUS: "+calefaccio.status())

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def telegram_motify(str):
    global masters_groups_id_telegram, updater
    for chat_id in masters_groups_id_telegram:
        updater.bot.send_message(chat_id=int(chat_id), text=str)

def telegram_preauth(user_id, chat_id):
    global masters_id_telegram, masters_groups_id_telegram
    # restrictiu
    # return str(user_id) in masters_id_telegram and (str(chat_id) in masters_id_telegram or str(chat_id) in masters_groups_id_telegram)
    return str(user_id) in masters_id_telegram or str(chat_id) in masters_groups_id_telegram

def telegram_start(bot, update):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not telegram_preauth(user_id, chat_id):
        update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
        return
    update.message.reply_text("AUTH OK "+str(user_id)+" "+str(chat_id), use_aliases=True)

def telegram_show_status(bot, update):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not telegram_preauth(user_id, chat_id):
        update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
        return
    update.message.reply_text("STATUS: "+calefaccio.status(), use_aliases=True)

def telegram_on(bot, update):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not telegram_preauth(user_id, chat_id):
        update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
        return
    in_range=True
    calefaccio.on()
    update.message.reply_text("STATUS: "+calefaccio.status(), use_aliases=True)

def telegram_off(bot, update):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not telegram_preauth(user_id, chat_id):
        update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
        return
    in_range=False
    calefaccio.off()
    update.message.reply_text("STATUS: "+calefaccio.status(), use_aliases=True)

BOT_TOKEN = ""
in_range = True

# main
if __name__ == "__main__":
    with PidFile('calefacciod') as pidfile:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        try:
            configfile = sys.argv[1]
        except IndexError:
            configfile = './calefacciod.config'

        config = SafeConfigParser()
        config.read(configfile)

        BOT_TOKEN = config.get('bot', 'token').strip('"').strip("'").strip()
        try:
            debug = config.getboolean('bot', 'debug')
        except:
            debug = False

        if not debug:
            logging.setLevel(logging.WARNING)

        masters_id_telegram = json.loads(config.get('bot','masters-id-telegram'))
        masters_groups_id_telegram = json.loads(config.get('bot','masters-groups-id-telegram'))

        schedule.every().day.at(config.get('schedule', 'daily_stop').strip('"').strip("'").strip()).do(scheduled_stop_calefaccio)
        schedule.every().day.at(config.get('schedule', 'daily_start').strip('"').strip("'").strip()).do(scheduled_start_calefaccio)

        updater = Updater(token=BOT_TOKEN)

        calefaccio.init()
        time.sleep(1)
        scheduled_start_calefaccio()

        scheduler_thread = Thread(target = run_scheduler, args = ())
        scheduler_thread.daemon = True
        scheduler_thread.start()

        dp = updater.dispatcher

        updater.dispatcher.add_handler(CommandHandler('start', telegram_start))
        updater.dispatcher.add_handler(CommandHandler('status', telegram_show_status))
        updater.dispatcher.add_handler(CommandHandler('on', telegram_on))
        updater.dispatcher.add_handler(CommandHandler('off', telegram_off))

        updater.start_polling()

        updater.idle()
