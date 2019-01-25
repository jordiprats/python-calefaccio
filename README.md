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

[schedule]

daily_start = "05:00"
daily_stop = "00:00"
```
