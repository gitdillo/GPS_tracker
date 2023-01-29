from machine import Pin, UART, I2C

import utime, time

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


def getGPS(gpsModule, timeout_sec=3):
    global FIX_STATUS, TIMEOUT, latitude, longitude, satellites, GPStime, GPS_present
    
    timeout = time.time() + timeout_sec
    while True:
        try:
            buff = (gpsModule.readline()).decode()
        except UnicodeError:   # we read a pile of garbage, let's try again in a bit
            utime.sleep_ms(500)
            continue
        
        # If we reach here, we have something prmising in the buffer
        if GPS_present is False and buff.startswith('$GP'):
            print('GPS found')
            GPS_present = True
        # SOUP
        return buff
        # SOUP
        parts = buff.split(',')
    
        if (parts[0] == "b'$GPGGA" and len(parts) == 15):
            if(parts[1] and parts[2] and parts[3] and parts[4] and parts[5] and parts[6] and parts[7]):
#                 print(buff)
                
                latitude = convertToDegree(parts[2])
                if (parts[3] == 'S'):
                    latitude = -latitude
                longitude = convertToDegree(parts[4])
                if (parts[5] == 'W'):
                    longitude = -longitude
                satellites = parts[7]
                GPStime = parts[1][0:2] + ":" + parts[1][2:4] + ":" + parts[1][4:6]
                FIX_STATUS = True
                TIMEOUT = False
                return True
                
        if (time.time() > timeout):
            TIMEOUT = True
            return False
        utime.sleep_ms(500)
        
def convertToDegree(RawDegrees):
    
#     print("c2d: " + str(RawDegrees))

    RawAsFloat = float(RawDegrees)
    firstdigits = int(RawAsFloat/100) 
    nexttwodigits = RawAsFloat - float(firstdigits*100) 
    
    Converted = float(firstdigits + nexttwodigits/60.0)
    Converted = '{0:.6f}'.format(Converted) 
    return str(Converted)


# while True:
#     r = getGPS(gpsModule)
#     if r:
#         print(GPStime + ',' + latitude + ',' + longitude)



