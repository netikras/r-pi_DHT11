#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import sys

def bin2dec(string_num):
    return str(int(string_num, 2))
   
data = []
effectiveData = []
bits_min=999;
bits_max=0;
HumidityBit = ""
TemperatureBit = ""
crc = ""
crc_OK = False;
Humidity = 0
Temperature = 0


pin=18


GPIO.setmode(GPIO.BCM)


def pullData():
#{{{ Pull data from GPIO
    global data
    global effectiveData
    global pin
    
    data = []
    effectiveData = []
    
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin,GPIO.HIGH)
    time.sleep(0.025)
    GPIO.output(pin,GPIO.LOW)
    time.sleep(0.14)
    
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    for i in range(0,1000):
        data.append(GPIO.input(pin))

    """   
    for i in range(0,len(data)):
        print "%d" % data[i],
    print
    """
   
#}}}


def analyzeData():
#{{{ Analyze data

#{{{ Add HI (2x8)x3 bits to array
    
    seek=0;
    bits_min=9999;
    bits_max=0;

    global HumidityBit
    global TemperatureBit
    global crc
    global Humidity
    global Temperature

    HumidityBit = ""
    TemperatureBit = ""
    crc = ""
    
    """
    Snip off the first bit - it simply says "Hello, I got your request, will send you temperature and humidity information along with checksum shortly"
    """
    while(seek < len(data) and data[seek] == 0):
        seek+=1;
    
    while(seek < len(data) and data[seek] == 1):
         seek+=1;
    
    """
    Extract all HIGH bits' blocks. Add each block as separate item in data[] 
    """
    for i in range(0, 40):
        
        buffer = "";
        
        while(seek < len(data) and data[seek] == 0):
            seek+=1;
        
        
        while(seek < len(data) and data[seek] == 1):
            seek+=1;
            buffer += "1";
        
        """
        Find the longest and the shortest block of HIGHs. Average of those two will distinct whether block represents '0' (shorter than avg) or '1' (longer than avg)
        """
        
        if (len(buffer) < bits_min):
            bits_min = len(buffer)
    
        if (len(buffer) > bits_max):
            bits_max = len(buffer)
        
        effectiveData.append(buffer);
        #print "%s " % buffer
            
#}}}



#{{{ Make effectiveData smaller
    
    """
    Replace blocks of HIs with either '1' or '0' depending on block length
    """
    for i in range(0, len(effectiveData)):
        if (len(effectiveData[i]) < ((bits_max + bits_min)/2)):
            effectiveData[i] = "0";
        else:
            effectiveData[i] = "1";
    
        #print "%s " % effectiveData[i],
   # print
    
    
#}}}


#{{{ Extract Humidity and Temperature values

    for i in range(0, 8):
        HumidityBit += str(effectiveData[i]);
    
    for i in range(16, 24):
        TemperatureBit += str(effectiveData[i]);
    
    
    for i in range(32, 40):
        crc += str(effectiveData[i]);
    
    Humidity = bin2dec(HumidityBit)
    Temperature = bin2dec(TemperatureBit)

    #print "HumidityBit=%s, TemperatureBit=%s, crc=%s" % (HumidityBit, TemperatureBit, crc)

#}}}

#}}}


#{{{ Check CRC
def isDataValid():
    
    global Humidity
    global Temperature
    global crc
    
    #print "isDataValid(): H=%d, T=%d, crc=%d"% (int(Humidity), int(Temperature), int(bin2dec(crc)))
    if int(Humidity) + int(Temperature) == int(bin2dec(crc)):
        return True;
    else:
        return False;
#}}}


#{{{ Print data
def printData():
   global Humidity
   global Temperature
   
   print "H: "+Humidity
   print "T: "+Temperature
#}}}



#{{{ Main loop

while (not crc_OK):
    pullData();
    analyzeData();
    if (isDataValid()):
        crc_OK=True;
        print "\r",
        printData();
    else:
        sys.stderr.write(".")
        time.sleep(2);
#}}}
