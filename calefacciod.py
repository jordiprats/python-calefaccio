import schedule
import time
import calefaccio
import datetime, time

from threading import Thread

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

schedule.every().day.at("00:00").do(stop_calefaccio)
schedule.every().day.at("04:00").do(start_calefaccio)

calefaccio.init()
time.sleep(1)
start_calefaccio()

scheduler_thread = Thread(target = run_scheduler, args = ())
scheduler_thread.start()

scheduler_thread.join()
