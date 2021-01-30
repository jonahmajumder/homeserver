import os
import select
import socket
import struct
import sys
import time
import argparse

# On Windows, the best timer is time.clock()
# On most other platforms the best timer is time.time()
default_timer = time.clock if sys.platform == "win32" else time.time

# From /usr/include/linux/icmp.h; your milage may vary.
ICMP_ECHO_REQUEST = 8  # Seems to be the same on Solaris.


def checksum(source_string):
    """
    I'm not too confident that this is right but testing seems
    to suggest that it gives the same answers as in_cksum in ping.c
    """
    sum = 0
    countTo = (len(source_string)/2)*2
    count = 0
    while count<countTo:
        v1 = source_string[count + 1]
        if not isinstance(v1, int):
            v1 = ord(v1)
        v2 = source_string[count]
        if not isinstance(v2, int):
            v2 = ord(v2)
        thisVal = v1 * 256 + v2
        sum = sum + thisVal
        sum = sum & 0xffffffff # Necessary?
        count = count + 2

    if countTo<len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff # Necessary?

    sum = (sum >> 16)  +  (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff

    # Swap bytes. Bugger me if I know why.
    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer


def receive_one_ping(my_socket, ID, timeout):
    """
    receive the ping from the socket.
    """
    timeLeft = timeout
    while True:
        startedSelect = default_timer()
        whatReady = select.select([my_socket], [], [], timeLeft)
        howLongInSelect = (default_timer() - startedSelect)
        if whatReady[0] == []: # Timeout
            return

        timeReceived = default_timer()
        recPacket, addr = my_socket.recvfrom(1024)
        icmpHeader = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack(
            b"bbHHh", icmpHeader
        )
        # Filters out the echo request itself. 
        # This can be tested by pinging 127.0.0.1 
        # You'll see your own request
        if type != 8 and packetID == ID:
            bytesInDouble = struct.calcsize(b"d")
            timeSent = struct.unpack(b"d", recPacket[28:28 + bytesInDouble])[0]
            return timeReceived - timeSent

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return


def send_one_ping(my_socket, dest_addr, ID):
    """
    Send one ping to the given >dest_addr<.
    """
    dest_addr  =  socket.gethostbyname(dest_addr)

    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    my_checksum = 0

    # Make a dummy heder with a 0 checksum.
    header = struct.pack(b"bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
    bytesInDouble = struct.calcsize("d")
    data = (192 - bytesInDouble) * b"Q"
    data = struct.pack("d", default_timer()) + data

    # Calculate the checksum on the data and the dummy header.
    my_checksum = checksum(header + data)

    # Now that we have the right checksum, we put that in. It's just easier
    # to make up a new header than to stuff it into the dummy.
    header = struct.pack(
        b"bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1
    )
    packet = header + data
    my_socket.sendto(packet, (dest_addr, 1)) # Don't know about the 1


def do_one(dest_addr, timeout):
    """
    Returns either the delay (in seconds) or none on timeout.
    """
    icmp = socket.getprotobyname("icmp")
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, icmp)

    my_ID = os.getpid() & 0xFFFF

    send_one_ping(my_socket, dest_addr, my_ID)
    delay = receive_one_ping(my_socket, my_ID, timeout)

    my_socket.close()
    return delay


def verbose_ping(dest_addr, timeout = 2, count = 4,interval=1.0):
    """
    Send >count< ping to >dest_addr< with the given >timeout< and display
    the result.
    """
    ping_succeeded = False
    for i in range(count):
        print("ping %s..." % dest_addr, end=' ')
        try:
            delay = do_one(dest_addr, timeout)
        except socket.gaierror as e:
            print("failed. (socket error: '%s')" % e[1])
            break

        if delay == None:
            print("failed. (timeout within %ssec.)" % timeout)
        else:
            time.sleep(min(0,interval-delay))
            print("got ping in %0.4fms\n" % (delay*1000))
            ping_succeeded = True
    return ping_succeeded


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="send ICMP ECHO_REQUEST to network hosts")
    parser.add_argument("destination", help="host to ping")
    parser.add_argument("-W", "--timeout", help="specify a timeout", type=float, default=2)
    parser.add_argument("-c", "--count", help="stop after sending this much ECHO_REQUEST packkets", type=int, default=5)
    parser.add_argument("-i", "--interval", help="Wait the specified time between each ping", type=float, default=1.0)
    
    ns = parser.parse_args()

    s = verbose_ping(ns.destination, ns.timeout, ns.count ,ns.interval)
    if s:
        sys.exit(0)
    else:
        sys.exit(1)
