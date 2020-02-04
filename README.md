# python-calefaccio

## restapi switch - restapid

### restapid

### Home assistant config

```
switch:
  - platform: rest
    name: calefaccio
    resource: http://1.2.3.4:5002/calefaccio
    body_on: '{"active": "true"}'
    body_off: '{"active": "false"}'
    is_on_template: '{{ value_json.is_active }}'
    headers:
      Content-Type: application/json
    verify_ssl: false
```

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
