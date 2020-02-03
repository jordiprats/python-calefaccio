# python-calefaccio

## sensor temperatura

 * [esp-01s + DHT11](https://www.amazon.es/gp/product/B0793M8LXK/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1)
 * [Connect the ESP8266 WiFi Chip to your Raspberry Pi](https://openhomeautomation.net/connect-esp8266-raspberry-pi)
 * [programar esp01](https://programarfacil.com/podcast/como-configurar-esp01-wifi-esp8266/)
 * [programar esp01 amb raspberry](https://blog.3d-logic.com/2017/12/01/using-raspberry-pi-to-flash-esp8266/)
 * [Temperature Sensor with ESP8266-01 And DS18B20](https://www.hackster.io/alessandro-bellafiore/temperature-sensor-with-esp8266-01-and-ds18b20-6a0897)
 * [demo esp01 + temperatura](https://github.com/abflower/homeass-temp_sens/blob/master/ds_sensor.py)
 * [MQTT Server Using Raspberry Pi](https://appcodelabs.com/introduction-to-iot-build-an-mqtt-server-using-raspberry-pi)

## TODO

* integració home assistant REST: https://www.home-assistant.io/integrations/switch.rest/

## telegram bot - calefacciod

### base setup

No es realment necesari:

```
echo 26 > /sys/class/gpio/export
sleep 1
echo out > /sys/class/gpio/gpio26/direction
sleep 1
echo 0 > /sys/class/gpio/gpio26/value
```
### calefacciod.config

Config telegram bot

```
[bot]

token = TOKEN_HERE
masters-id-telegram = [ "111", "222" ]
masters-groups-id-telegram = [ "-333" ]
debug = false

[adafruitio]

username = USERNAME
key = KEY

[schedule]

daily_start = "04:15"
daily_stop = "22:30"
```

### comandes
```
start - inicia bot
status - mostra estat calefacció
on - arranca calefacció
off - para calefacció
enablelockdown - activa programació
disablelockdown - desactiva programació
statuslockdown - estat del sistema
enablescheduler - habilita aturada/arranc horari
disablescheduler - deshabilita aturada/arranc horari
statusscheduler - mostra estat aturada/arranc horari
showscheduler - mostra programació horaria
debugadafruitio - info adafruit
enableadafruitio - habilita adafruit
disableadafruitio - deshabilita adafruit
statusadafruitio - estat adafruit
refreshadafruitio - força refresh adafruit
```
