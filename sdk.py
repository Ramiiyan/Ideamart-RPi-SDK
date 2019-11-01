
import paho.mqtt.client as mqtt
import time
import RPi.GPIO as GPIO
import dht11


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
instance = dht11.DHT11(pin=04)
Serial="sdk123"
ports = [0 for i in xrange(27)]  #array for the ststus of the pins - not defined 0 input 1 outputHigh 2 outputLOw 3 Interupt 4
logicalout=["" for x in range(4)]  #array for the ststus of the logical out  pins
logicalin=["" for y in range(4)]  #array for the ststus of the logical in pins

def getSerial():   #function for reading serial number
    ser=""
    try:
        f=open('/proc/cpuinfo','r')
        for line in f:
            if line[0:6]=='Serial':
                ser=line[10:26]
        f.close
    except:
        ser="can't read"

    return ser

def getVersion():  #function for reading version number
    ser=""
    try:
        f=open('/proc/cpuinfo','r')
        for line in f:
            if line[0:8]=='Revision':
                ser=line[10:14]
        f.close
    except:
        ser="can't read"

    return ser

def getport():
    global ports
    st=""
    for y in range(0,27):
	st=st+str(ports[y])
    return st

def status(port):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(port,GPIO.OUT)
    return GPIO.input(port)

def con(tries):  #function for making mqtt connection - tries = number of retry if error occurs in connection
    global client
    print tries
    if tries<1 :
        return
    
    try :

        client.connect("iot.mqtt.dialog.lk", 55566, 60) ## this server and port here

    except:
        print "Can't connect to the server"
        time.sleep(5)
        
        tries=tries-1
        con(tries)

def actionfind(msg):        #function for identifying  actions form the mqtt request on topic 2
    con1=msg[0:2]
    if con1=="01":
        print "ask for port"
        action1()
    if con1=="02":
        print "Action2"
        action2(int(msg[2:4]),msg[4:6],msg[2:4]);
    if con1=="03":
        print "Action3"
        action3(int(msg[2:4]),msg[2:4])
    if con1=="04":
        print "Action4"
        print msg
        action4(int(msg[2:4]),msg[4:6],msg[2:4])
    if con1=="05":
        print "Action5"
        action5(int(msg[2:4]),msg[2:4])

    if con1=="06":
        print "Action6"
        action6(int(msg[2:4]),msg[2:4])
    if con1=="07":
        print "Action7"
        action7(int(msg[2:4]),msg[4:])
        
    
def action1():                     #function for handling action1 - get port status
    global ports
    client.publish(Serial+"/pub","0127"+getSerial())

def action2(port,action,portname): #function for handling action 2 - make output pin HIGH/LOW
    #print actionmsg
    global ports
    if (port>27) or (port<0):
	print "Invalid PORT"
	client.publish(Serial+"/pub","Invalid PORT")
	return

    if action=="01":
	ports[port-1]=2
        gpioOut(port,GPIO.OUT,GPIO.HIGH)
        GPIO.output(port,1)
        client.publish(Serial+"/pub","02"+str(portname)+"1")
    if action=="00":
	ports[port-1]=3
        gpioOut(port,GPIO.OUT,GPIO.LOW)
        GPIO.output(port,0)
        client.publish(Serial+"/pub","02"+str(portname)+"0")

def action3(port,portname):        #function for handling action 3 - Read a input pin 
    global Serial
    global ports
    if (port>27) or (port<0):
	print "Invalid PORT"
	client.publish(Serial+"/pub","Invalid PORT")
	return
    ports[port-1]=1
    gpioIn(port,GPIO.IN,GPIO.PUD_DOWN)
    print "In :"+str(GPIO.input(port))
    client.publish(Serial+"/pub","03"+str(portname)+str(GPIO.input(port)))

def action4(port,action,portname):     #function for handling action4 - set interupt in a pin
    global ports
    if (port>27) or (port<0):
	print "Invalid PORT"
	client.publish(Serial+"/pub","Invalid PORT")
	return

    client.publish(Serial+"/pub","04"+str(portname)+"0")
    gpioIn(port,GPIO.IN,GPIO.PUD_DOWN)
    #if ports[port-1] !=4 :
    if action=="01":
	GPIO.remove_event_detect(port)
    	GPIO.add_event_detect(port, GPIO.RISING, callback=my_callback1,bouncetime=1000)
    if action=="02":
	GPIO.remove_event_detect(port)
    	GPIO.add_event_detect(port, GPIO.FALLING, callback=my_callback2,bouncetime=1000)
    if action=="03":
	GPIO.remove_event_detect(port)
    	GPIO.add_event_detect(port, GPIO.BOTH, callback=my_callback3,bouncetime=1000)


    ports[port-1]=4

def action5(port,portname):        #function for handling action1 - get port ststus
    global ports
    client.publish(Serial+"/pub","05"+portname+str(status(port)))


#If you need to add logical(analog inputs) edit your code here

#port 28-31 are virtual logical input ports
#port 29-35 are virtual logical output ports

#code your own logic for ADC and assign the values here    

def action6(port,portname):            
    logicalout[0]="0000"   # have to assign you local port values here // Port 1
    logicalout[1]="0000"   # have to assign you local port values here // Port 2
    logicalout[2]="0000"   # have to assign you local port values here // Port 3
    logicalout[3]="0000"   # have to assign you local port values here // Port 4
    client.publish(Serial+"/pub","06"+portname+logicalout[port-1])

def action7(port,value):        #function for handling action7 - get logical port status
    global ports
    global logicalin
    print value
    logicalin[port-1]=value;    # logical in values will be stored in [localin] arary 
    client.publish(Serial+"/pub","value assigned")


def my_callback1(channel):
    print('This is a edge event callback function!')
    print('Edge detected on channel %s'%channel)
    print('This is run in a different thread to your main program')
    if GPIO.input(channel) :
        client.publish("demo/rsbry/common","#"+getSerial()+",04"+"1"+str(channel))

def my_callback2(channel):
    print('This is a edge event callback function!')
    print('Edge detected on channel %s'%channel)
    print('This is run in a different thread to your main program')
    if (GPIO.input(channel)==0) :
        client.publish("demo/rsbry/common","#"+getSerial()+",04"+"2"+str(channel))

def my_callback3(channel):
    print('This is a edge event callback function!')
    print('Edge detected on channel %s'%channel)
    print('This is run in a different thread to your main program')
    formattedChannel=channel
   # if len(str(channel))==1:
    #    formattedChannel='0'+str(channel)
    if GPIO.input(channel) :
        client.publish("demo/rsbry/common","#"+getSerial()+",04"+"1"+str(formattedChannel))
    if (GPIO.input(channel)==0) :
        client.publish("demo/rsbry/common","#"+getSerial()+",04"+"2"+str(formattedChannel))
        
    #client.publish("demo/rsbry/common","#"+getSerial()+",04"+"3"+str(channel))

    
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(Serial+"/sub")
    

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global Serial

    print msg.topic
    
    if msg.topic==Serial+"/pub":
        print "Wrong topic!!!!!"
        
    if msg.topic==Serial+"/sub":
        print(msg.topic+" "+str(msg.payload))
        actionfind(msg.payload)
    
 

def gpioOut(pin,inout,mode):  #function for set a pin as output
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, inout, initial=mode)

def gpioIn(pin,inout,mode):  #function for set a pin as input
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, inout, pull_up_down=mode)


    
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
for x in range(1,28):
    y=str(x)
    if len(str(x))==1:
        y='0'+str(x)
    actionfind("04"+y+"03")
print getVersion()
Serial="demo/rsbry/"+getSerial()
print Serial
print "Serial Number : " + getSerial()



while 1 :
    con(5)                #connecting with 5 retries
    client.loop_start()   #start mqtt loop
    time.sleep(1000)      #looping for 1000 seconds - can change if needed
    client.loop_stop()    #end mqtt loop
    client.disconnect()   #disconnect from mqtt broaker
