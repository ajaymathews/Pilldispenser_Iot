from lcd import *
import BlynkLib
import time
import datetime
import serial
import binascii


BLYNK_AUTH='34dca7ebf6a54958a74c94e39d9904d6'
blynk = BlynkLib.Blynk(BLYNK_AUTH)

now = datetime.datetime.now()
strt_tym=now.minute
hr=now.hour
mt=now.minute    
tym=[strt_tym+1,strt_tym+3,strt_tym+5,strt_tym+7,strt_tym+9,strt_tym+11,strt_tym+13]
rot=12.5;
data=str(00)
inv_data=str('ff')
null_data=str('')
i=0
flag=0
count=0
pillflag=0;
icheck=0


def serl_read():
    ser = serial.Serial(
      
       port='/dev/ttyUSB0',
       baudrate = 9600,
       parity=serial.PARITY_NONE,
       stopbits=serial.STOPBITS_ONE,
       bytesize=serial.EIGHTBITS,
       timeout=1
    )
    counter=0
    x=ser.readline()
    hex_string = binascii.hexlify(x).decode('utf-8')
    print(hex_string)
    return hex_string

def next_corse():
    now = datetime.datetime.now()
    lcd_string("Next_Course:",1,1)
    lcd_string("%s" %(tym[i]),1,13)
    print("next course",tym[i])
    icheck=0
    count=0


def curr_tym():
    now = datetime.datetime.now()
    hr=now.hour
    mt=now.minute
    print(mt)
    return mt

def notify():
    blynk.notify('ALERT')
    print('alert')
    

while 1:
    if(curr_tym()==tym[i]):
        lcd_string("                ",1,1)

        ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate = 9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        counter=0
        x=ser.readline()
        hex_string = binascii.hexlify(x).decode('utf-8')
        print(hex_string)
        
        while(hex_string=='' and count<70):
            ser = serial.Serial(
                port='/dev/ttyUSB0',
                baudrate = 9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1                                             
            )
            counter=0
            x=ser.readline()
            hex_string = binascii.hexlify(x).decode('utf-8')
            print(hex_string)
            lcd_string("place ur Finger",1,1)
            print("place ur Finger")
            count=count+1
            time.sleep(.1)
            if(count>60):
                if(icheck==0):
                    icheck=1
                    i=i+1
                print("alert triggered")
                notify()
                next_corse()
            blynk.run()
          
        if(hex_string=='00'):
            print("finger identified")
            lcd_string("          ",1,1)
            lcd_string("Successful",1,1)
            print((i+1),"forward")
            time.sleep(.5)
            print("next pill box i*12.5")
            pillflag=1
            time.sleep(1)
##            flag=1
            i=i+1
            
        elif(hex_string=='ff'):
            lcd_string("             ",1,1)
            lcd_string("Invalid",1,1)
            print("invalid")
            time.sleep(1)
##            flag=0
                           
            
    else:
        if(pillflag==1):
            print("pill box reset");
            time.sleep(.5)
            print((i+1),"reverse")
            pillflag=0;
            
        next_corse()
        blynk.run()

blynk.run()

    
        





  



##lcd_string("Date: %s" %time.strftime("%m/%d/%Y"),1,1) #date
## print(datetime.time(now.hour, now.minute, now.second)) #time
    
    
