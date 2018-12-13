import paho.mqtt.client as mqtt
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
#import picamera
from time import sleep
import time
#import RPi.GPIO as GPIO# Import Raspberry Pi GPIO library
import requests
import json
import os
import datetime
#GPIO.setwarnings(False) # Ignore warning for now
#GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
#GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
import MySQLdb as mysql
now = datetime.datetime.now()
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe("/esp8266/smoke")
    client.subscribe("/esp8266/camera")
    

# The callback for when a PUBLISH message is received from the ESP8266.
def on_message(client, userdata, message):
    #socketio.emit('my variable')
    print("Received message '" + str(message.payload) + "' on topic '"
        + message.topic + "' with QoS " + str(message.qos))
    '''if message.topic == "/esp8266/temperature":
        print("temperature update")
        socketio.emit('dht_temperature', {'data': message.payload})  '''
    if message.topic == "/esp8266/smoke":
        print("smoke update")
        #db = mysql.connect("157.230.20.246","root","darkwolf","iot")
        socketio.emit('sensor_smoke', {'data': message.payload})
        #cur = db.cursor()
        #print("cursor created")
        #cur.execute("insert into data(smoke,object,temperature,humidity,pulse,dt) values("+str(message.payload)+",NULL,NULL,NULL,NULL,'"+now.strftime("%Y-%m-%d %H:%M")+"');")
        #print("executed")
        #db.commit()
        #print("commited")
        #db.close()
        #print("inserted")
    if message.topic == "/esp8266/camera":
    	print(message.payload)
    	#db1 = mysql.connect("157.230.20.246","root","darkwolf","iot")
    	socketio.emit('camera',{'data':message.payload})
    	#cur1 = db.cursor()
    	#cur1.execute("insert into data (smoke,object,temperature,humidity,pulse,dt) values(NULL,'"+message.payload+"',NULL,NULL,NULL,'"+now.strftime("%Y-%m-%d %H:%M")+"');")
    	#db1.commit()
    	#db1.close()





mqttc=mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username="bbhcbdgr",password="EuzikmDn_mJN")
mqttc.connect("m15.cloudmqtt.com",13038,60)
mqttc.loop_start()
'''
def button_callback(channel):
    print("Button was pushed!")
    camera = picamera.PiCamera()
    #set resolution
    camera.resolution = (1024, 768)
    camera.brightness = 60
    camera.start_preview()
    #add text on image
    camera.annotate_text = 'Hi Pi User'
    sleep(5)
    print("store image")
    camera.capture('image1.jpeg')
    camera.stop_preview()
    camera.close()
    print("hola")
    addr = 'http://157.230.20.246:5000'
    test_url = addr + '/api/test'
    # prepare headers for http request
    content_type = 'image/jpeg'
    headers = {'content-type': content_type}

    img = open("image1.jpeg","rb")
    response = requests.post(test_url, data=img, headers=headers)
    #print (json.loads(response.text))
    print("working")
    string = (json.loads(response.text))
    string = str(string['message']).split(",")
    print string
    result = ""
    for i in string:
	#print i
	stripped = i.replace("u'[INFO]","")
	#print stripped
	result+=stripped
	result+=","
    result = result.strip("[")
    result = result.replace("]","")
    result = result.replace("'","")
    result = result[:-1]
    print result
    print type(result)
    #cmd = "mosquitto_pub -h m15.cloudmqtt.com -p 13038 -u bbhcbdgr -P  EuzikmDn_mJN  -t /esp8266/camera -m "+result
    #cmd = "mosquitto_pub -h m15.cloudmqtt.com -p 13038 -u bbhcbdgr -P  EuzikmDn_mJN  -t /esp8266/camera -m '"+result+"'"
    #os.system(cmd)
    mqttc.publish("/esp8266/camera",result)
'''
#GPIO.add_event_detect(10,GPIO.RISING,callback=button_callback,bouncetime=200)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# The callback for when the client receives a CONNACK response from the server.

#GPIO.add_event_detect(10,GPIO.RISING,callback=button_callback)

# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
   4 : {'name' : 'GPIO 4', 'board' : 'esp8266', 'topic' : 'esp8266/4', 'state' : 'False'},
   5 : {'name' : 'GPIO 5', 'board' : 'esp8266', 'topic' : 'esp8266/5', 'state' : 'False'},
   12 : {'name' : 'GPIO 12', 'board' : 'esp8266', 'topic' : 'esp8266/12', 'state' : 'False'},
   }

# Put the pin dictionary into the template data dictionary:
templateData = {
   'pins' : pins
   }

@app.route("/")
def main():
   # Pass the template data into the template main.html and return it to the user
   #GPIO.cleanup()
   #print("mani")
   return render_template('main.html', async_mode=socketio.async_mode, **templateData)

@app.route("/new_graph")
def smoke_chart():
	db2 = mysql.connect("157.230.20.246","root","darkwolf","iot")
	db2_cur = db2.cursor()
	db2_cur.execute("select dt,smoke from data where smoke is not NULL")
	result = db2_cur.fetchall()
	values = []
	labels = []
	for i in result:
		labels.append(i[0])
		values.append(i[1])
	db2.close()
	print labels[-10:],values[-10:]
	return render_template('chart1.html',values=values[-10:],labels=labels[-10:])
	

@app.route("/temp_graph")
def temp_chart():
	db3 = mysql.connect("157.230.20.246","root","darkwolf","iot")
	db3_cur = db3.cursor()
	db3_cur.execute("select dt,temperature from data where temperature is not NULL")
	result = db3_cur.fetchall()
	values = []
	labels = []
	for i in result:
		labels.append(i[0])
		values.append(i[1])
	db3.close()
	print labels[-10:],values[-10:]
	return render_template('chart2.html',values=values[-10:],labels=labels[-10:])
	
@app.route("/hum_graph")
def hum_chart():
	db4 = mysql.connect("157.230.20.246","root","darkwolf","iot")
	db4_cur = db4.cursor()
	db4_cur.execute("select dt,humidity from data where humidity is not NULL")
	result = db4_cur.fetchall()
	values = []
	labels = []
	for i in result:
		labels.append(i[0])
		values.append(i[1])
	db4.close()
	print labels[-10:],values[-10:]
	return render_template('chart3.html',values=values[-10:],labels=labels[-10:])
	
@app.route("/pulse_graph")
def pulse_chart():
	db5 = mysql.connect("157.230.20.246","root","darkwolf","iot")
	db5_cur = db5.cursor()
	db5_cur.execute("select dt,pulse from data where pulse is not NULL")
	result = db5_cur.fetchall()
	values = []
	labels = []
	for i in result:
		labels.append(i[0])
		values.append(i[1])
	db5.close()
	print labels[-10:],values[-10:]
	return render_template('chart4.html',values=values[-10:],labels=labels[-10:])		

# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<board>/<changePin>/<action>")
def action(board, changePin, action):
   # Convert the pin from the URL into an integer:
   changePin = int(changePin)
   # Get the device name for the pin being changed:
   devicePin = pins[changePin]['name']
   # If the action part of the URL is "1" execute the code indented below:
   if action == "1" and board == 'esp8266':
      mqttc.publish(pins[changePin]['topic'],"1")
      pins[changePin]['state'] = 'True'
   if action == "0" and board == 'esp8266':
      mqttc.publish(pins[changePin]['topic'],"0")
      pins[changePin]['state'] = 'False'
   # Along with the pin dictionary, put the message into the template data dictionary:
   templateData = {
      'pins' : pins
   }
   return render_template('main.html', **templateData)

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json data here: ' + str(json))

if __name__ == "__main__":
   socketio.run(app, host='0.0.0.0', port='80', debug=True)
   #print("sffsd")
   #GPIO.cleanup()












