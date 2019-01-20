import RPi.GPIO as GPIO

def init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(26, GPIO.OUT)
    GPIO.output(26, GPIO.LOW)

def on():
    GPIO.output(26, GPIO.LOW)

def off():
    GPIO.output(26, GPIO.HIGH)

def status():
    if GPIO.input(26):
        return "off"
    else:
        return "on"
