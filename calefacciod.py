import schedule
import time
import calefaccio
import datetime, time

timeformat = '%Y%-m-%d %H:%M:%S'
global_calefaccio = calefaccio.Calefaccio()

def start_calefaccio():
    global calefaccio
    print datetime.datetime.fromtimestamp(time.time()).strftime(timeformat)+" START"
    global_calefaccio.on()

def stop_calefaccio():
    global calefaccio
    print datetime.datetime.fromtimestamp(time.time()).strftime(timeformat)+" STOP"
    global_calefaccio.off()

schedule.every().day.at("00:00").do(stop_calefaccio)
schedule.every().day.at("04:00").do(start_calefaccio)
# demo
schedule.every(1).minutes.do(stop_calefaccio)

while True:
    schedule.run_pending()
    time.sleep(1)
