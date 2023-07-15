from threading import Lock

try:
    import RPi.GPIO as GPIO
    sample_mode=False
except:
    sample_mode=True

status_bool=False

mutex = Lock()

def init():
    global status_bool
    global sample_mode
    with mutex:
        if not sample_mode:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(26, GPIO.OUT)
            GPIO.output(26, GPIO.LOW)

def off():
    global status_bool
    global sample_mode
    with mutex:
        if not sample_mode:
            GPIO.output(26, GPIO.LOW)
        else:
            status_bool=False

def on():
    global status_bool
    global sample_mode
    with mutex:
        if not sample_mode:
            GPIO.output(26, GPIO.HIGH)
        else:
            status_bool=True

def status():
    global status_bool
    global sample_mode
    with mutex:
        if not sample_mode:
            status_bool=GPIO.input(26)
        if status_bool:
            return "on"
        else:
            return "offs"
