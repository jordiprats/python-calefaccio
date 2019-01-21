try:
    import RPi.GPIO as GPIO
    sample_mode=False
except:
    sample_mode=True

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
    if sample_mode:
        status_bool=sample_mode
    else:
        status_bool=GPIO.input(26)
    if status_bool:
        return "off"
    else:
        return "on"
