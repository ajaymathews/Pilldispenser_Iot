from lcd import *
import BlynkLib
import time
import datetime
import serial
import binascii


BLYNK_AUTH='b64ac3e1b0b44c548a052815b84b21b3'
#34dca7ebf6a54958a74c94e39d9904d6
blynk = BlynkLib.Blynk(BLYNK_AUTH)

now = datetime.datetime.now()
strt_tym=now.minute
hr=now.hour
mt=now.minute    
tym=[strt_tym+1,strt_tym+3,strt_tym+5,strt_tym+7,strt_tym+9,strt_tym+11,strt_tym+13,strt_tym+15,strt_tym+17]
print(tym)
data=str(00)
inv_data=str('ff')
null_data=str('')
flag=0
count=0
pillflag=0
c=0
icheck=0
i=1
j=0
StepPin = 7 #red
Dir = 5  #blue
ms2=11
rot=50



GPIO.setup(Dir, GPIO.OUT)
GPIO.setup(StepPin, GPIO.OUT)
GPIO.setup(StepPin, GPIO.OUT)
GPIO.setup(ms2, GPIO.OUT)

FastSpeed = 0.001 #Change this depends on your stepper motor
LowSpeed = 0.001
ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate = 9600,
            timeout=1
        )
GPIO.output(ms2, 1)

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
    global i,count
    print("Nxt Course")
    now = datetime.datetime.now()
    lcd_string("Next_Course:",1,1)
    lcd_string("%s" %(tym[i]),1,13)
    icheck=0
    count=0
##    i = i + 1
    if(curr_tym()==tym[i]):
        flag=0
    else:
        flag=0
    

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
    global i
    
    print("tym : ",tym[i])
    print("i : ",i)
    if(curr_tym()==tym[i]):
        lcd_string("                ",1,1)
        counter=0
        x=ser.readline()
        hex_string = binascii.hexlify(x).decode('utf-8')
        print(hex_string)
        count
        while(hex_string=='' and count<55):
            
            
            x=ser.readline()
            hex_string = binascii.hexlify(x).decode('utf-8')
            print(hex_string)
            lcd_string("place ur Finger",1,1)
            print("place ur Finger")
            time.sleep(.1)
            count=count+1;
            if(count>43):
                
                print("alert triggered")
                notify()
                next_corse()
                if(icheck==0):
                    print("Insuide")
                    i=i+1
                    icheck=1
                    flag=1 # just checkin
##                    next_corse()
                    break
                
            blynk.run()
          
        if((hex_string=='00')or(hex_string=='01')or(hex_string=='03')):
            print("finger identified")
            lcd_string("          ",1,1)
            lcd_string("Successful",1,1)
            print((i+1),"moving forward")
            for j in range(rot*i):
                GPIO.output(Dir, 0)
                GPIO.output(StepPin, 0)
                time.sleep(LowSpeed)
                GPIO.output(StepPin, 1)
                time.sleep(LowSpeed)
            time.sleep(3)
            
            print("next pill box i*12.5")
            pillflag=1
            time.sleep(1)
            flag=1
            for j in range(rot*i):
                GPIO.output(Dir, 1)
                GPIO.output(StepPin, 0)
                time.sleep(LowSpeed)
                GPIO.output(StepPin, 1)
                time.sleep(LowSpeed)
            time.sleep(3)
            i=i+1
            
        elif(hex_string=='ff'):
            lcd_string("             ",1,1)
            lcd_string("Invalid",1,1)
            print("invalid")
            time.sleep(1)
            flag=0
                           
            
    else:
        if(pillflag==1):
            print("pill box reset");
            time.sleep(.5)
            print((i+1),"reverse")
            pillflag=0;
            
        next_corse()
        blynk.run()

blynk.run()

    
    
