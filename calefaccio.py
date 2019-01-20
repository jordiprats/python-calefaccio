from gpiozero import LED

class Calefaccio:

    gpio = LED(26)

    def __init__(self):
        self.gpio.off()

    def on():
        global calefaccio
        self.gpio.off()

    def off():
        global calefaccio
        self.gpio.on()
