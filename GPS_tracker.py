from machine import Pin, UART, I2C

#import utime, time

import time

UART_id = 0
baud = 9600
txpin = 0
rxpin = 1


gpsModule = UART(UART_id, baudrate=baud, tx=Pin(txpin), rx=Pin(rxpin))


buff = bytearray(255)

TIMEOUT = False
FIX_STATUS = False
GPS_present = False

latitude = ""
longitude = ""
satellites = ""
GPStime = ""


def fetch_GPS_message(gpsModule, timeout_sec=3, retry_period_ms = 100):
    
    global FIX_STATUS, TIMEOUT, latitude, longitude, satellites, GPStime, GPS_present
    
    t_timeout = time.time() + timeout_sec   # we will hit a timeout if we reach this time
    
    # First, check if we have hit a timeout
    while True:
        if (time.time() > t_timeout):
            TIMEOUT = True
            return False
        
        # Read a line from the GPS module
        buff = gpsModule.readline()
        if buff is None:        # most likely line not ready to read, try again in a bit
            time.sleep_ms(retry_period_ms)
            continue
        
        # Let's check if out line can be decoded from bytes (sometimes we get garbage)
        try:
            buff = buff.decode()
        except UnicodeError:      # we got a pile of garbage, try again in a bit
            time.sleep_ms(retry_period_ms)
            continue
        
        # If we reach here, we have something promising in the buffer, let's take a closer look
        # A valid message starts with "$GP" and contains only one "$" (sometimes messages get mushed together)
        # so we need to reject these invalid message
        if not (buff.startswith('$GP') and buff.count('$GP') == 1):   # in this case we got a corrupted message, try again in a bit
            time.sleep_ms(retry_period_ms)
            continue
        
        # If we reach here, we have something that looks like a message
        return buff.rstrip()
    
def parse_message(msg):
    
    parts = msg.split(',')
    
    msg_type = parts[0][1:]
    
#     # TODO: different actions depending on message type
#     
#     
# # To remove
# def getGPS(gpsModule, timeout_sec=3, retry_period_ms = 500):
#     
#     global FIX_STATUS, TIMEOUT, latitude, longitude, satellites, GPStime, GPS_present
#     
#     timeout = time.time() + timeout_sec
#     
#     while True:
#         
#         if (time.time() > timeout):
#             TIMEOUT = True
#             return False
#         
#         try:
#             buff = gpsModule.readline()
#             if buff is None:        # most likely line not ready to read, try again in a bit
#                 utime.sleep_ms(retry_period_ms)
#                 continue
#             buff = buff.decode()
#         except UnicodeError:   # we read a pile of garbage, try again in a bit
#             utime.sleep_ms(retry_period_ms)
#             continue
#         
#         # If we reach here, we have something promising in the buffer
#         if GPS_present is False and buff.startswith('$GP'):
#             print('GPS found')
#             GPS_present = True
#         
#         parts = buff.split(',')
#     
#         if (parts[0] == "b'$GPGGA" and len(parts) == 15):
#             if(parts[1] and parts[2] and parts[3] and parts[4] and parts[5] and parts[6] and parts[7]):
# #                 print(buff)
#                 
#                 latitude = convertToDegree(parts[2])
#                 if (parts[3] == 'S'):
#                     latitude = -latitude
#                 longitude = convertToDegree(parts[4])
#                 if (parts[5] == 'W'):
#                     longitude = -longitude
#                 satellites = parts[7]
#                 GPStime = parts[1][0:2] + ":" + parts[1][2:4] + ":" + parts[1][4:6]
#                 FIX_STATUS = True
#                 TIMEOUT = False
#                 return True
#                 
#         utime.sleep_ms(retry_period_ms)
        
def convertToDegree(RawDegrees):
    
#     print("c2d: " + str(RawDegrees))

    RawAsFloat = float(RawDegrees)
    firstdigits = int(RawAsFloat/100) 
    nexttwodigits = RawAsFloat - float(firstdigits*100) 
    
    Converted = float(firstdigits + nexttwodigits/60.0)
    Converted = '{0:.6f}'.format(Converted) 
    return str(Converted)





