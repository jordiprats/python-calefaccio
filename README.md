# python-calefaccio

## base setup

No es realment necesari:

```
echo 26 > /sys/class/gpio/export
sleep 1
echo out > /sys/class/gpio/gpio26/direction
sleep 1
echo 0 > /sys/class/gpio/gpio26/value
```
## calefacciod.config

```
[bot]

token = TOKEN_HERE
masters-id-telegram = [ "111" ]
masters-groups-id-telegram = [ "-222" ]

[schedule]

daily_start = "05:00"
daily_stop = "00:00"
```

## comandes

start - inicia bot
status - mostra estat calefacció
on - arranca calefacció
off - para calefacció
enablescheduler - habilita aturada/arranc horari
disablescheduler - deshabilita aturada/arranc horari
statusscheduler - mostra estat aturada/arranc horari
showscheduler - mostra programació horaria
debugadafruitio - info adafruit
enableadafruitio - habilita adafruit
disableadafruitio - deshabilita adafruit
statusadafruitio - estat adafruit
refreshadafruitio - força refresh adafruit
