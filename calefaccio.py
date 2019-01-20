import RPi.GPIO as GPIO

class Calefaccio:
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(26, GPIO.OUT)
        self.gpio.off()

    def on():
        GPIO.output(26, GPIO.LOW)

    def off():
        GPIO.output(26, GPIO.HIGH)
