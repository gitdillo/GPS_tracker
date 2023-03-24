from machine import Pin, UART, I2C

import utime

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
GPS_time = ""


def fetch_GPS_message(gpsModule, timeout_sec=3, retry_period_ms = 100):
    
    global TIMEOUT, GPS_present
    
    t_timeout = utime.time() + timeout_sec   # we will hit a timeout if we reach this time
    
    # First, check if we have hit a timeout
    while True:
        if (utime.time() > t_timeout):
            TIMEOUT = True
            return False
        
        # Read a line from the GPS module
        buff = gpsModule.readline()
        if buff is None:        # most likely line not ready to read, try again in a bit
            utime.sleep_ms(retry_period_ms)
            continue
        
        # Let's check if out line can be decoded from bytes (sometimes we get garbage)
        try:
            buff = buff.decode()
        except UnicodeError:      # we got a pile of garbage, try again in a bit
            utime.sleep_ms(retry_period_ms)
            continue
        
        # If we reach here, we have something promising in the buffer, let's take a closer look
        # A valid message starts with "$GP" and contains only one "$" (sometimes messages get mushed together)
        # so we need to reject these invalid message
        if not (buff.startswith('$GP') and buff.count('$GP') == 1):   # in this case we got a corrupted message, try again in a bit
            utime.sleep_ms(retry_period_ms)
            continue
        
        # If we reach here, we have something that looks like a message
        TIMEOUT = False
        if GPS_present is False:
            GPS_present = True
        return buff.rstrip()
    
def parse_message(msg):
    
    global FIX_STATUS, TIMEOUT, latitude, longitude, satellites, GPS_time, GPS_present
    
    parts = msg.split(',')
    
    msg_type = parts[0][1:]
    
    if msg_type == 'GPGSV':
        pass
    elif msg_type == 'GPVTG':
        pass
    elif msg_type == 'GPGL':
        pass
    elif msg_type == 'GPGGA':
        _parse_GPGGA(parts)
    elif msg_type == 'GPRM':
        pass
    elif msg_type == 'GPGLL':
        pass
    elif msg_type == 'GPRMC':
        _parse_GPRMC(parts)
    elif msg_type == 'GPGSA':
        pass
    else:
        pass
    
    return msg_type

def _parse_GPRMC(msg_parts):
    
    if msg_parts[0] == '$GPRMC' and len(msg_parts) == 13:
        if (msg_parts[1] and msg_parts[2] and msg_parts[3] and msg_parts[4] and msg_parts[5] and msg_parts[6] and msg_parts[7] and msg_parts[8] and msg_parts[9]):
            
            latitude = convertToDegree(msg_parts[3])
            if (msg_parts[4] == 'S'):
                latitude = -latitude
            
        else:
            pass
    else:
        pass
    
    print(msg_parts)
    print(len(msg_parts))

def _parse_GPGGA(msg_parts):
    
    global FIX_STATUS, TIMEOUT, latitude, longitude, satellites, GPS_time
    
    if msg_parts[0] == '$GPGGA' and len(msg_parts) == 15:
        if (msg_parts[1] and msg_parts[2] and msg_parts[3] and msg_parts[4] and msg_parts[5] and msg_parts[6] and msg_parts[7]):
            
            latitude = convertToDegree(msg_parts[2])
            if (msg_parts[3] == 'S'):
                latitude = -latitude
            
            longitude = convertToDegree(msg_parts[4])
            if (msg_parts[5] == 'W'):
                longitude = -longitude
            
            satellites = msg_parts[7]
            GPS_time = msg_parts[1][0:2] + ":" + msg_parts[1][2:4] + ":" + msg_parts[1][4:6]
            FIX_STATUS = True
            
        else:
            # Inner if
            pass
    else:
        # Outer if
        pass


def convertToDegree(RawDegrees):
    
#     print("c2d: " + str(RawDegrees))

    RawAsFloat = float(RawDegrees)
    firstdigits = int(RawAsFloat/100) 
    nexttwodigits = RawAsFloat - float(firstdigits*100) 
    
    Converted = float(firstdigits + nexttwodigits/60.0)
    Converted = '{0:.6f}'.format(Converted) 
    return str(Converted)
    



while True:
    m = fetch_GPS_message(gpsModule)
    if m[1:6] == 'GPRMC':
        msg_parts = m.split(',')
        if msg_parts[0] == '$GPRMC' and len(msg_parts) == 13:
            if (msg_parts[1] and msg_parts[2] and msg_parts[3] and msg_parts[4] and msg_parts[5] and msg_parts[6] and msg_parts[7] and msg_parts[8] and msg_parts[9]):
                break
            else:
                print('Shit: ' + str(msg_parts))
        else:
            print('Crap: ' + str(msg_parts))



# log_timestamp = None
# while True:
#     m = fetch_GPS_message(gpsModule)
#     msg_type = parse_message(m)
#     if FIX_STATUS is True:
#         print("GPS has a fix")
#         log_timestamp = GPS_time
#         #break
#         
# s = GPS_time + ',' + latitude + ',' + longitude
# print(s)
    

        





