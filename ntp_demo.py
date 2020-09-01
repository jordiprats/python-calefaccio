from socket import AF_INET, SOCK_DGRAM
import sys
import socket
import struct, time
import timeout_decorator

@timeout_decorator.timeout(5, use_signals=False)
def getNTPseason(host = "pool.ntp.org"):
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
        ntp_time = time.ctime(t).replace("  "," ")

        print(ntp_time.month)
    except:
        return None


if __name__ == "__main__":
    try:
        season = getNTPseason()
        print(season)
    except:
        print('timeout')
