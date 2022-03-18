import sys
import time
import json
import logging
import schedule
import telegram
import ntpseason
import calefaccio
import datetime, time

from pid import PidFile
from threading import Thread
from configparser import SafeConfigParser
from telegram.ext import Updater, CommandHandler

timeformat = '%Y-%m-%d %H:%M:%S'

previous_pricetag = None

def send_current_price_tag(force=False, dryrun=False):
  global previous_pricetag
  if force:
    previous_pricetag = ntpseason.getScammersPriceTag()
    telegram_motify(previous_pricetag)
  elif dryrun:
    telegram_motify(ntpseason.getScammersPriceTag())
  else:
    if calefaccio.status() == "on":
      current_pricetag = ntpseason.getScammersPriceTag()
      if previous_pricetag != current_pricetag:
        previous_pricetag = current_pricetag
        telegram_motify(current_pricetag)

def enable_lockdown():
  global enabled_scheduler, enabled_lockdown
  enabled_scheduler = False
  enabled_lockdown = False
  calefaccio.off()

def disable_lockdown():
  global enabled_scheduler, enabled_lockdown
  enabled_scheduler = True
  enabled_lockdown = True

def is_locked_down():
  global enabled_lockdown
  return enabled_lockdown

def status_lockdown():
  if is_locked_down():
    return "LOCKDOWN ENABLED"
  else:
    return "LOCKDOWN DISABLED"

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
    send_current_price_tag(force=True)

def scheduled_stop_calefaccio():
  if enabled_scheduler:
    calefaccio.off()
    logging.debug("*X "+datetime.datetime.fromtimestamp(time.time()).strftime(timeformat)+" set to "+calefaccio.status())
    telegram_motify("AUTOMATIC ACTION - STATUS: "+calefaccio.status())

def report_pricing_while_on():
  global previous_pricetag
  if calefaccio.status() == "on":
    send_current_price_tag(force=False, dryrun=False)
  else:
    previous_pricetag = None

def scheduled_get_season():
  global season, enabled_lockdown, enabled_scheduler
  for i in range(0,10):
    while True:
      try:
        season_candidate = ntpseason.getNTPseason()

        if season_candidate:
          if not season or season != season_candidate:
            telegram_motify("INFO - set season to "+season_candidate)
          season = season_candidate

          if not enabled_lockdown:
            if season == schedule_active_on:
              if not enabled_scheduler:
                telegram_motify("AUTOMATIC ACTION - ENABLED SCHEDULER due to season")
              enabled_scheduler = True
            else:
              if enabled_scheduler:
                telegram_motify("AUTOMATIC ACTION - DISABLED SCHEDULER due to season")
              enabled_scheduler = False
          return True
        else:
          continue
      except:
        time.sleep(i*3)
        continue
  telegram_motify("!! WARNING !!")
  telegram_motify("UNABLE TO GET SEASON")
  telegram_motify("!! WARNING !!")
  return False

def run_scheduler():
  while True:
    idle_sec = 1
    try:
      schedule.run_pending()
      idle_sec = schedule.idle_seconds()
    except:
      pass
    time.sleep(idle_sec)

def telegram_getseason(update, context):
  global season
  user_id = update.message.from_user.id
  chat_id = update.message.chat_id
  if not telegram_preauth(user_id, chat_id):
    update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
    return
  else:
    if season:
      update.message.reply_text("current season is set to: "+season)

def telegram_getpricing(update, context):
  global season
  user_id = update.message.from_user.id
  chat_id = update.message.chat_id
  if not telegram_preauth(user_id, chat_id):
    update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
    return
  send_current_price_tag(dryrun=True)

def telegram_show_scheduler(update, context):
  user_id = update.message.from_user.id
  chat_id = update.message.chat_id
  if not telegram_preauth(user_id, chat_id):
    update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
    return

  update.message.reply_text("active on: "+schedule_active_on)

  try:
    array_schedules_start_calefaccio = json.loads(config.get('schedule','daily_start'))
    for start_calefaccio_at in array_schedules_start_calefaccio:
      update.message.reply_text("daily start at: "+start_calefaccio_at)
  except:
    update.message.reply_text("daily start at: /"+config.get('schedule', 'daily_start').strip('"').strip("'").strip()+"/")

  try:
    array_schedules_stop_calefaccio = json.loads(config.get('schedule','daily_stop'))
    for stop_calefaccio_at in array_schedules_stop_calefaccio:
      update.message.reply_text("daily stop at: "+stop_calefaccio_at)
  except:
    update.message.reply_text("daily stop at: /"+config.get('schedule', 'daily_stop').strip('"').strip("'").strip()+"/")

  # python 3
  # try:
  #   all_jobs = schedule.get_jobs()
  #   logging.debug(str(all_jobs))
  # except Exception as e:
  #   logging.debug(">>>>>> EXCEPTION: "+str(e))

def telegram_motify(str):
  global masters_groups_id_telegram, updater
  for chat_id in masters_groups_id_telegram:
    updater.bot.send_message(chat_id=int(chat_id), text=str)

def telegram_preauth(user_id, chat_id):
  global masters_id_telegram, masters_groups_id_telegram
  # restrictiu
  # return str(user_id) in masters_id_telegram and (str(chat_id) in masters_id_telegram or str(chat_id) in masters_groups_id_telegram)
  return str(user_id) in masters_id_telegram or str(chat_id) in masters_groups_id_telegram

def telegram_start(update, context):
  user_id = update.message.from_user.id
  chat_id = update.message.chat_id
  if not telegram_preauth(user_id, chat_id):
    update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
    return
  update.message.reply_text("AUTH OK "+str(user_id)+" "+str(chat_id))

def telegram_show_status(update, context):
  user_id = update.message.from_user.id
  chat_id = update.message.chat_id
  if not telegram_preauth(user_id, chat_id):
    update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
    return
  update.message.reply_text("STATUS: "+calefaccio.status())
  if calefaccio.status() == "on":
    send_current_price_tag(force=True)

def telegram_on(update, context):
  global circuitbreaker_status
  user_id = update.message.from_user.id
  chat_id = update.message.chat_id
  if not telegram_preauth(user_id, chat_id):
    update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
    return
  circuitbreaker_status = True
  calefaccio.on()
  update.message.reply_text("STATUS: "+calefaccio.status())
  send_current_price_tag(force=True)

def telegram_off(update, context):
  global circuitbreaker_status
  user_id = update.message.from_user.id
  chat_id = update.message.chat_id
  if not telegram_preauth(user_id, chat_id):
    update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
    return
  circuitbreaker_status = False
  calefaccio.off()
  update.message.reply_text("STATUS: "+calefaccio.status())

def telegram_enable_scheduler(update, context):
  global enabled_scheduler
  user_id = update.message.from_user.id
  chat_id = update.message.chat_id
  if not telegram_preauth(user_id, chat_id):
    update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
    return
  enabled_scheduler = True
  update.message.reply_text("SHEDULER STATUS: "+get_scheduler_status())

def telegram_disable_scheduler(update, context):
  global enabled_scheduler
  user_id = update.message.from_user.id
  chat_id = update.message.chat_id
  if not telegram_preauth(user_id, chat_id):
    update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
    return
  enabled_scheduler = False
  update.message.reply_text("SHEDULER STATUS: "+get_scheduler_status())

def telegram_status_scheduler(update, context):
  global enabled_scheduler
  user_id = update.message.from_user.id
  chat_id = update.message.chat_id
  if not telegram_preauth(user_id, chat_id):
    update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
    return
  update.message.reply_text("SHEDULER STATUS: "+get_scheduler_status())

def telegram_enable_lockdown(update, context):
  user_id = update.message.from_user.id
  chat_id = update.message.chat_id
  if not telegram_preauth(user_id, chat_id):
    update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
    return
  enable_lockdown()
  update.message.reply_text(status_lockdown())

def telegram_disable_lockdown(update, context):
  user_id = update.message.from_user.id
  chat_id = update.message.chat_id
  if not telegram_preauth(user_id, chat_id):
    update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
    return
  disable_lockdown()
  update.message.reply_text(status_lockdown())

def telegram_status_lockdown(update, context):
  user_id = update.message.from_user.id
  chat_id = update.message.chat_id
  if not telegram_preauth(user_id, chat_id):
    update.message.reply_text("I'm afraid I can't do that."+str(chat_id))
    return
  update.message.reply_text(status_lockdown())

BOT_TOKEN = ""
circuitbreaker_status = True
enabled_scheduler = False
enabled_lockdown = False
masters_inda_haus = {}
season = None
schedule_active_on = None

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

    masters_id_telegram = json.loads(config.get('bot','masters-id-telegram'))
    masters_groups_id_telegram = json.loads(config.get('bot','masters-groups-id-telegram'))

    #
    # telegram
    #

    updater = Updater(token=BOT_TOKEN)

    calefaccio.init()
    time.sleep(1)
    calefaccio.off()

    try:
      array_schedules_stop_calefaccio = json.loads(config.get('schedule','daily_stop'))
      for stop_calefaccio_at in array_schedules_stop_calefaccio:
        schedule.every().day.at(stop_calefaccio_at.strip()).do(scheduled_stop_calefaccio)
        telegram_motify("scheduled stop at "+stop_calefaccio_at.strip())
    except Exception as e:
      logging.debug(">>>>>> EXCEPTION: "+str(e))
      schedule.every().day.at(config.get('schedule', 'daily_stop').strip('"').strip("'").strip()).do(scheduled_stop_calefaccio)
      telegram_motify("scheduled stop at "+config.get('schedule', 'daily_stop').strip('"').strip("'").strip())

    try:
      array_schedules_start_calefaccio = json.loads(config.get('schedule','daily_start'))
      for start_calefaccio_at in array_schedules_start_calefaccio:
        schedule.every().day.at(start_calefaccio_at.strip()).do(scheduled_start_calefaccio)
        telegram_motify("scheduled start at "+start_calefaccio_at.strip())
    except Exception as e:
      logging.debug(">>>>>> EXCEPTION: "+str(e))
      schedule.every().day.at(config.get('schedule', 'daily_start').strip('"').strip("'").strip()).do(scheduled_start_calefaccio)
      telegram_motify("scheduled start at "+config.get('schedule', 'daily_start').strip('"').strip("'").strip())

    try:
      schedule_active_on = config.get('schedule', 'active_on').strip('"').strip("'").strip()
      scheduled_get_season()
      schedule.every().day.do(scheduled_get_season)
    except Exception as e:
      logging.debug(">>>>>> EXCEPTION: "+str(e))
      schedule_active_on = None
      enabled_scheduler = True
      telegram_motify("season detection disabled")

    schedule.every(10).minutes.do(report_pricing_while_on)

    scheduler_thread = Thread(target = run_scheduler, args = ())
    scheduler_thread.daemon = True
    scheduler_thread.start()

    telegram_motify("== scheduler configured ==")

    dp = updater.dispatcher

    updater.dispatcher.add_handler(CommandHandler('start', telegram_start))
    updater.dispatcher.add_handler(CommandHandler('status', telegram_show_status))
    updater.dispatcher.add_handler(CommandHandler('on', telegram_on))
    updater.dispatcher.add_handler(CommandHandler('off', telegram_off))
    updater.dispatcher.add_handler(CommandHandler('enablelockdown', telegram_enable_lockdown))
    updater.dispatcher.add_handler(CommandHandler('disablelockdown', telegram_disable_lockdown))
    updater.dispatcher.add_handler(CommandHandler('statuslockdown', telegram_status_lockdown))
    updater.dispatcher.add_handler(CommandHandler('enablescheduler', telegram_enable_scheduler))
    updater.dispatcher.add_handler(CommandHandler('disablescheduler', telegram_disable_scheduler))
    updater.dispatcher.add_handler(CommandHandler('statusscheduler', telegram_status_scheduler))
    updater.dispatcher.add_handler(CommandHandler('showscheduler', telegram_show_scheduler))
    updater.dispatcher.add_handler(CommandHandler('getseason', telegram_getseason))
    updater.dispatcher.add_handler(CommandHandler('getpricing', telegram_getpricing))

    updater.start_polling()

    updater.idle()
