from socket import AF_INET, SOCK_DGRAM
from emoji import emojize

import timeout_decorator
import datetime
import struct
import socket
import sys

@timeout_decorator.timeout(5, use_signals=False)
def getNTPseason(host = "pool.ntp.org", winter_months = [11, 12, 1, 2, 3]):
    port = 123
    buf = 1024
    address = (host,port)
    msg = '\x1b' + 47 * '\0'

    # reference time (in seconds since 1900-01-01 00:00:00)
    TIME1970 = 2208988800 # 1970-01-01 00:00:00

    try:
        # connect to server
        client = socket.socket( AF_INET, SOCK_DGRAM)
        client.sendto(msg.encode('utf-8'), address)
        msg, address = client.recvfrom( buf )

        t = struct.unpack( "!12I", msg )[10]
        t -= TIME1970
        # print(t)

        month = int(datetime.datetime.fromtimestamp(t).strftime('%m'))
        # print(month)

        if month not in winter_months:
            return "summer"
        else:
            return "winter"

    except Exception as e:
        print(e)
        return None

@timeout_decorator.timeout(5, use_signals=False)
def getScammersPriceTag(host = "pool.ntp.org"):
    port = 123
    buf = 1024
    address = (host,port)
    msg = '\x1b' + 47 * '\0'

    # reference time (in seconds since 1900-01-01 00:00:00)
    TIME1970 = 2208988800 # 1970-01-01 00:00:00

    try:
        # connect to server
        client = socket.socket( AF_INET, SOCK_DGRAM)
        client.sendto(msg.encode('utf-8'), address)
        msg, address = client.recvfrom( buf )

        t = struct.unpack( "!12I", msg )[10]
        t -= TIME1970
        # print(t)

        weekday = int(datetime.datetime.fromtimestamp(t).strftime('%w'))
        hour = int(datetime.datetime.fromtimestamp(t).strftime('%H'))
        # print(hour)

        if weekday in (0, 6):
            return emojize(':moneybag:', use_aliases=True)
        else:
            if hour < 8:
                return emojize(':moneybag:', use_aliases=True)
            elif hour < 10:
                return emojize(':moneybag::moneybag:', use_aliases=True)
            elif hour < 14:
                return emojize(':moneybag::moneybag::moneybag:', use_aliases=True)
            elif hour < 18:
                return emojize(':moneybag::moneybag:', use_aliases=True)
            elif hour < 22:
                return emojize(':moneybag::moneybag::moneybag:', use_aliases=True)
            else:
                return emojize(':moneybag::moneybag:', use_aliases=True)

    except Exception as e:
        print(e)
        return None

if __name__ == "__main__":
    try:
        season = getNTPseason()
        print(season)
        pricetag = getScammersPriceTag()
        print(pricetag)
    except:
        print('timeout')
