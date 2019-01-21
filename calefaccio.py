try:
    import RPi.GPIO as GPIO
    sample_mode=False
except:
    sample_mode=True

status_bool=False

def init():
    if not sample_mode:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(26, GPIO.OUT)
        GPIO.output(26, GPIO.LOW)

def on():
    if not sample_mode:
        GPIO.output(26, GPIO.LOW)

def off():
    if not sample_mode:
    GPIO.output(26, GPIO.HIGH)

def status():
    if not sample_mode:
        status_bool=GPIO.input(26)
    else:
        status_bool=not status_bool
    if status_bool:
        return "off"
    else:
        return "on"
