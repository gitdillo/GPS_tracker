from machine import Pin, UART, I2C, RTC

import utime

UART_id = 0
baud = 9600
txpin = 0
rxpin = 1


gpsModule = UART(UART_id, baudrate=baud, tx=Pin(txpin), rx=Pin(rxpin))
machine_rtc = machine.RTC()

buff = bytearray(255)

TIMEOUT = False
GPS_present = False

LATITUDE = None
LONGITUDE = None
SATELLITES = None
GPS_timestring = None
GPS_datestring = None
HDOP = None
GPS_fix_quality = None
POSITION_STATUS = None
SPEED_knots = None

def set_system_time(year, month, day, hours, minutes, seconds):
    # the arg for RTC.datetime() is tuple: (year, month, day, weekday, hours, minutes, seconds, subseconds)
    # we set weekday=0 (auto) and subseconds=0 since it is ignored anyway
    global machine_rtc
    machine_rtc.datetime((year, month, day, 0, hours, minutes, seconds, 0))    
    

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
    
    global GPS_timestring, GPS_datestring, LATITUDE, LONGITUDE, SPEED_knots, POSITION_STATUS
    
    if msg_parts[0] == '$GPRMC' and len(msg_parts) == 13:
        # we ignore msg_parts[7] (Track made good) because it is often empty
        if (msg_parts[1] and msg_parts[2] and msg_parts[3] and msg_parts[4] and msg_parts[5] and msg_parts[6] and msg_parts[7] and msg_parts[9]):
            
            LATITUDE = convertToDegree(msg_parts[3])
            if (msg_parts[4] == 'S'):
                LATITUDE = -LATITUDE
            
            LONGITUDE = convertToDegree(msg_parts[5])
            if (msg_parts[6] == 'W'):
                LONGITUDE = -LONGITUDE
            
            # Time lives in msg_parts[1]
            GPS_timestring = msg_parts[1]
            hours = int(GPS_timestring[0:2])
            minutes = int(GPS_timestring[2:4])
            seconds = int(GPS_timestring[4:6]) # ignore subsecods, not implemented
            
            # Date lives in msg_parts[9]
            GPS_datestring = msg_parts[9]
            day = int(GPS_datestring[:2])
            month = int(GPS_datestring[2:4])
            year = int('20' + GPS_datestring[4:])
            
            set_system_time(year, month, day, hours, minutes, seconds)
            
            POSITION_STATUS = msg_parts[2]
            SPEED_knots = float(msg_parts[7])
            
        else:
            pass
    else:
        pass

def _parse_GPGGA(msg_parts):
    
    global HDOP, LATITUDE, LONGITUDE, SATELLITES, GPS_timestring, GPS_fix_quality
    
    if msg_parts[0] == '$GPGGA' and len(msg_parts) == 15:
        if (msg_parts[1] and msg_parts[2] and msg_parts[3] and msg_parts[4] and msg_parts[5] and msg_parts[6] and msg_parts[7] and msg_parts[8]):
            
            LATITUDE = convertToDegree(msg_parts[2])
            if (msg_parts[3] == 'S'):
                LATITUDE = -LATITUDE
            
            LONGITUDE = convertToDegree(msg_parts[4])
            if (msg_parts[5] == 'W'):
                LONGITUDE = -LONGITUDE
            
            # msg_parts[1] contains time info
            GPS_fix_quality = int(msg_parts[6])
            SATELLITES = int(msg_parts[7])
            HDOP = float(msg_parts[8])
            print('Fix type: ' + str(GPS_fix_quality) + ', HDOP: ' + str(HDOP))
            
        else:
            pass
    else:
        pass


def convertToDegree(RawDegrees):
    
#     print("c2d: " + str(RawDegrees))

    RawAsFloat = float(RawDegrees)
    firstdigits = int(RawAsFloat/100) 
    nexttwodigits = RawAsFloat - float(firstdigits*100) 
    
    Converted = float(firstdigits + nexttwodigits/60.0)
    # Converted = '{0:.6f}'.format(Converted)
    return Converted


update_seconds = 2
t_last_update = utime.time()
print('FIX TYPE: ' + str(GPS_fix_quality) + ', HDOP: ' + str(HDOP) + ', GPS present: ' + str(GPS_present))
while True:
    
    if utime.time() - t_last_update:
        print('FIX TYPE: ' + str(GPS_fix_quality) + ', HDOP: ' + str(HDOP) + ', GPS present: ' + str(GPS_present))
        t_last_update = utime.time()
    
    m = fetch_GPS_message(gpsModule)
    parse_message(m)
    
