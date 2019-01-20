import schedule
import time
import calefaccio
import datetime, time

timeformat = '%Y-%m-%d %H:%M:%S'

def start_calefaccio():
    calefaccio.on()
    print datetime.datetime.fromtimestamp(time.time()).strftime(timeformat)+" "+calefaccio.status()

def stop_calefaccio():
    calefaccio.off()
    print datetime.datetime.fromtimestamp(time.time()).strftime(timeformat)+" "+calefaccio.status()

schedule.every().day.at("00:00").do(stop_calefaccio)
schedule.every().day.at("04:00").do(start_calefaccio)

calefaccio.init()

stop_calefaccio()
start_calefaccio()

while True:
    schedule.run_pending()
    time.sleep(1)
