from gpiozero import LED

class Calefaccio:

    gpio = LED(26)

    def __init__(self):
        self.gpio.off()

    def on():
        self.gpio.off()

    def off():
        self.gpio.on()
