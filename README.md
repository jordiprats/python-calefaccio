# python-calefaccio

## base setup

Not really needed but nice to have in your **/etc/rc.local** file just in case something goes wrong with the bot or the restapid:

```
echo 26 > /sys/class/gpio/export
sleep 1
echo out > /sys/class/gpio/gpio26/direction
sleep 1
echo 0 > /sys/class/gpio/gpio26/value
```

## telegram bot - calefacciod

### calefacciod.config

Config telegram bot

```
[bot]

token = TELEGRAM_TOKEN
masters-id-telegram = [ "MASTER1", "MASTER2" ]
masters-groups-id-telegram = [ "GROUP_ID" ]
debug = false

[schedule]

active_on = winter

daily_start = "04:15"
daily_stop = "08:00"
```

### list of command for the BotFather
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
getseason - get current season
getpricing - get current pricing
```

## restapi switch - restapid

### restapid

plug&play, no config needed

It will listen to any:5002 publishing the **calefaccio** resource

### Home assistant config

```
switch:
  - platform: rest
    name: calefaccio
    resource: http://1.2.3.4:5002/calefaccio
    body_on: '{"active": "true"}'
    body_off: '{"active": "false"}'
    is_on_template: "{{ value_json.is_active }}"
    headers:
      Content-Type: application/json
    verify_ssl: false

sensor:
  - platform: rest
    name: calefaccio
    resource: http://1.2.3.4:5002/calefaccio
    value_template: "{{ value_json.is_active }}"
```
