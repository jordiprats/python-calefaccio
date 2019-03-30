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
from Adafruit_IO import MQTTClient, Client
from telegram.ext import Updater, CommandHandler

timeformat = '%Y-%m-%d %H:%M:%S'

def enable_lockdown():
    global enabled_scheduler
    enabled_scheduler = False
    calefaccio.off()

def disable_lockdown():
    global enabled_scheduler
    enabled_scheduler = True
    calefaccio.on()

def is_locked_down():
    return calefaccio.status()=="off" and not enabled_scheduler

def get_scheduler_status():
    global enabled_scheduler
    if enabled_scheduler:
        return "on"
    else:
        return "off"

def scheduled_start_calefaccio():
    if enabled_scheduler:
        calefaccio.on()
        logging.debug("*X "+datetime.datetime.fromtimestamp(time.time()).strftime(timeformat)+" set to "+calefaccio.status())
        telegram_motify("AUTOMATIC ACTION - STATUS: "+calefaccio.status())

def scheduled_stop_calefaccio():
    if enabled_scheduler:
        calefaccio.off()
        logging.debug("*X "+datetime.datetime.fromtimestamp(time.time()).strftime(timeformat)+" set to "+calefaccio.status())
        telegram_motify("AUTOMATIC ACTION - STATUS: "+calefaccio.status())

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def adafruitio_connected(client):
    global masters_id_telegram
    for master_id in masters_id_telegram:
        try:
            client.subscribe(master_id)
        except:
            telegram_motify("exception subcribing to Adafruit IO / feed "+master_id)

def adafruitio_disconnected(client):
    # reconnect
    telegram_motify("Adafruit IO reconnect")
    adafruitio_thread = Thread(target = run_adafruitio_task, args = ())
    adafruitio_thread.daemon = True
    adafruitio_thread.start()

def adafruitio_message(client, feed_id, payload):
    global masters_inda_haus
    logging.debug("adafruit io message")
    print("adafruit io message: "+str(payload))

    if int(payload) > 0:
        masters_inda_haus[str(feed_id)] = True
    else:
        masters_inda_haus[str(feed_id)] = False

    master_count=0
    for master in masters_inda_haus.keys():
        if masters_inda_haus[master]:
            master_count+=1

    print("master count: "+str(master_count))

    if adafruitio_enabled:
        if master_count==0:
            telegram_motify("LOCKDOWN MODE ENABLED")
            enable_lockdown()
        elif is_locked_down():
            telegram_motify("LOCKDOWN DISABLED")
            disable_lockdown()

def run_adafruitio_task():
    global adafruitio_username, adafruitio_key, masters_inda_haus, adafruit_lastconnect

    timestamp_now = ts = time.time()
    if((timestamp_now-adafruit_lastconnect) < 300):
        return

    adafruit_lastconnect = timestamp_now

    client = MQTTClient(adafruitio_username, adafruitio_key)
    # Setup the callback functions defined above.
    client.on_connect    = adafruitio_connected
    client.on_disconnect = adafruitio_disconnected
    client.on_message    = adafruitio_message

    # Connect to the Adafruit IO server.
    client.connect()

    aio = Client(adafruitio_username, adafruitio_key)

    for master in masters_inda_haus.keys():
        data = aio.receive(master)
        if int(data.value) > 0:
            masters_inda_haus[master] = True
        else:
            masters_inda_haus[master] = False

    master_count=0
    for master in masters_inda_haus.keys():
        if masters_inda_haus[master]:
            master_count+=1

    if master_count==0:
        telegram_motify("AUTOMATIC ACTION - LOCKDOWN MODE ENABLED")
        enable_lockdown()

    # Start a message loop that blocks forever waiting for MQTT messages to be
    # received.  Note there are other options for running the event loop like doing
    # so in a background thread--see the mqtt_client.py example to learn more.
    try:
        client.loop_blocking()
    except:
        telegram_motify("ADAFRUID IO THREAD ABORTED")

    telegram_motify("RESTARTING ADAFRUID IO")
    adafruitio_thread = Thread(target = run_adafruitio_task, args = ())
    adafruitio_thread.daemon = True
    adafruitio_thread.start()

def telegram_refresh_adafruit_io(bot, update):
    global adafruitio_enabled, adafruitio_adm_down, masters_inda_haus
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not telegram_preauth(user_id, chat_id):
        update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
        return
    if adafruitio_adm_down:
        update.message.reply_text("Adafruit IO administratively DOWN")
    else:
        aio = Client(adafruitio_username, adafruitio_key)

        for master in masters_inda_haus.keys():
            data = aio.receive(master)
            if int(data.value) > 0:
                masters_inda_haus[master] = True
            else:
                masters_inda_haus[master] = False

        master_count=0
        for master in masters_inda_haus.keys():
            if masters_inda_haus[master]:
                master_count+=1

        if master_count==0:
            update.message.reply_text("ADAFRUID REFRESHED - LOCKDOWN MODE ENABLED")
            enable_lockdown()
        else:
            update.message.reply_text("ADAFRUID REFRESHED - LOCKDOWN MODE DISABLED")
            disable_lockdown()

def telegram_enable_adafruit_io(bot, update):
    global adafruitio_enabled, adafruitio_adm_down
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not telegram_preauth(user_id, chat_id):
        update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
        return
    if adafruitio_adm_down:
        update.message.reply_text("Adafruit IO administratively DOWN")
    else:
        if adafruitio_enabled:
            update.message.reply_text("Adafruit IO already ONLINE")
        else:
            adafruitio_enabled = True
            if master_count==0:
                telegram_motify("LOCKDOWN MODE ENABLED")
                enable_lockdown()
            elif is_locked_down():
                telegram_motify("LOCKDOWN DISABLED")
                disable_lockdown()

            telegram_status_adafruit_io(bot, update)

def telegram_disable_adafruit_io(bot, update):
    global adafruitio_enabled, adafruitio_adm_down
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not telegram_preauth(user_id, chat_id):
        update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
        return
    if adafruitio_adm_down:
        update.message.reply_text("Adafruit IO administratively DOWN")
    else:
        if adafruitio_enabled:
            adafruitio_enabled = False
        telegram_status_adafruit_io(bot, update)

def telegram_status_adafruit_io(bot, update):
    global adafruitio_enabled, adafruitio_adm_down
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not telegram_preauth(user_id, chat_id):
        update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
        return
    if adafruitio_adm_down:
        update.message.reply_text("Adafruit IO DOWN - please check credentials")
    else:
        if adafruitio_enabled:
            update.message.reply_text("Adafruit IO ONLINE")
        else:
            update.message.reply_text("Adafruit IO OFFLINE")

def telegram_debug_adafruit_io(bot, update):
    global masters_inda_haus
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not telegram_preauth(user_id, chat_id):
        update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
        return
    for master in masters_inda_haus.keys():
        update.message.reply_text("master: "+str(master))
        update.message.reply_text("value: "+str(masters_inda_haus[master]))

def telegram_show_scheduler(bot, update):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not telegram_preauth(user_id, chat_id):
        update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
        return

    try:
        array_schedules_start_calefaccio = json.loads(config.get('bot','daily_start'))
        for start_calefaccio_at in array_schedules_start_calefaccio:
            update.message.reply_text("daily start at: "+start_calefaccio_at)
    except:
        update.message.reply_text("daily start at: "+config.get('schedule', 'daily_start').strip('"').strip("'").strip())

    try:
        array_schedules_stop_calefaccio = json.loads(config.get('bot','daily_stop'))
        for stop_calefaccio_at in array_schedules_stop_calefaccio:
            update.message.reply_text("daily stop at: "+stop_calefaccio_at)
    except:
        update.message.reply_text("daily stop at: "+config.get('schedule', 'daily_stop').strip('"').strip("'").strip())

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
    global circuitbreaker_status
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not telegram_preauth(user_id, chat_id):
        update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
        return
    circuitbreaker_status = True
    calefaccio.on()
    update.message.reply_text("STATUS: "+calefaccio.status(), use_aliases=True)

def telegram_off(bot, update):
    global circuitbreaker_status
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not telegram_preauth(user_id, chat_id):
        update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
        return
    circuitbreaker_status = False
    calefaccio.off()
    update.message.reply_text("STATUS: "+calefaccio.status(), use_aliases=True)

def telegram_enable_scheduler(bot, update):
    global enabled_scheduler
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not telegram_preauth(user_id, chat_id):
        update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
        return
    enabled_scheduler = True
    update.message.reply_text("SHEDULER STATUS: "+get_scheduler_status(), use_aliases=True)

def telegram_disable_scheduler(bot, update):
    global enabled_scheduler
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not telegram_preauth(user_id, chat_id):
        update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
        return
    enabled_scheduler = False
    update.message.reply_text("SHEDULER STATUS: "+get_scheduler_status(), use_aliases=True)

def telegram_status_scheduler(bot, update):
    global enabled_scheduler
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if not telegram_preauth(user_id, chat_id):
        update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
        return
    update.message.reply_text("SHEDULER STATUS: "+get_scheduler_status(), use_aliases=True)

BOT_TOKEN = ""
circuitbreaker_status = True
enabled_scheduler = True
masters_inda_haus = {}

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

        try:
            adafruitio_username = config.get('adafruitio', 'username').strip('"').strip("'").strip()
            adafruitio_key = config.get('adafruitio', 'key').strip('"').strip("'").strip()
            adafruitio_enabled = True
            adafruitio_adm_down = False
        except:
            adafruitio_enabled = False
            adafruitio_adm_down = True
        adafruit_lastconnect = 0

        masters_id_telegram = json.loads(config.get('bot','masters-id-telegram'))
        masters_groups_id_telegram = json.loads(config.get('bot','masters-groups-id-telegram'))

        try:
            array_schedules_stop_calefaccio = json.loads(config.get('bot','daily_stop'))
            for stop_calefaccio_at in array_schedules_stop_calefaccio:
                schedule.every().day.at(stop_calefaccio_at).do(scheduled_stop_calefaccio)
        except:
            schedule.every().day.at(config.get('schedule', 'daily_stop').strip('"').strip("'").strip()).do(scheduled_stop_calefaccio)

        try:
            array_schedules_start_calefaccio = json.loads(config.get('bot','daily_start'))
            for start_calefaccio_at in array_schedules_start_calefaccio:
                schedule.every().day.at(start_calefaccio_at).do(scheduled_start_calefaccio)
        except:
            schedule.every().day.at(config.get('schedule', 'daily_start').strip('"').strip("'").strip()).do(scheduled_start_calefaccio)

        #
        # adafruit IO
        #
        if adafruitio_enabled:
            for master_id in masters_id_telegram:
                masters_inda_haus[master_id] = True
            adafruitio_thread = Thread(target = run_adafruitio_task, args = ())
            adafruitio_thread.daemon = True
            adafruitio_thread.start()


        #
        # telegram
        #

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
        updater.dispatcher.add_handler(CommandHandler('enablescheduler', telegram_enable_scheduler))
        updater.dispatcher.add_handler(CommandHandler('disablescheduler', telegram_disable_scheduler))
        updater.dispatcher.add_handler(CommandHandler('statusscheduler', telegram_status_scheduler))
        updater.dispatcher.add_handler(CommandHandler('showscheduler', telegram_show_scheduler))
        updater.dispatcher.add_handler(CommandHandler('debugadafruitio', telegram_debug_adafruit_io))
        updater.dispatcher.add_handler(CommandHandler('enableadafruitio', telegram_enable_adafruit_io))
        updater.dispatcher.add_handler(CommandHandler('disableadafruitio', telegram_disable_adafruit_io))
        updater.dispatcher.add_handler(CommandHandler('statusadafruitio', telegram_status_adafruit_io))
        updater.dispatcher.add_handler(CommandHandler('refreshadafruitio', telegram_refresh_adafruit_io))

        updater.start_polling()

        updater.idle()
