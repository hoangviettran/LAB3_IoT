print("IoT Gateway")
import paho.mqtt.client as mqttclient
import time
import json
import serial.tools.list_ports


BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
mess = ""


#TODO: Add your token and your comport
#Please check the comport in the device manager
THINGS_BOARD_ACCESS_TOKEN = "6j8SmRfsmIyHiKmlCmGg"
bbc_port = "COM7"
if len(bbc_port) > 0:
    ser = serial.Serial(port=bbc_port, baudrate=115200)
LED = {"value": False}
FAN = {"value_1": False}
def processData(data):
    global LED, FAN
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    #TODO: Add your source code to publish data to the server
    check = 'TEMP'
    check_1 = 'LIGHT'
    check_2 = 'LED'
    check_3 = 'FAN'
    if check in data:
        temp = data.replace("1:TEMP:", "")
        collect_data = {
           'temperature': temp
        }
        client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    if check_1 in data:
        temp = data.replace("1:LIGHT:", "")
        collect_data = {
            'light': temp
        }
        client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    if check_2 in data:
        temp_data = {'value': True}
        if LED == True:
            LED = False
            temp_data = {'value': False}
            cmd = 0
            ser.write((str(cmd) + "#").encode())
        else:
            LED = True
            temp_data = {'value': True}
            cmd = 1
            ser.write((str(cmd) + "#").encode())

        client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
    if check_3 in data:
        temp_data = {'value_1': True}
        if FAN == True:
            FAN = False
            temp_data = {'value_1': False}
            cmd = 2
            ser.write((str(cmd) + "#").encode())
        else:
            FAN = True
            temp_data = {'value_1': True}
            cmd = 3
            ser.write((str(cmd) + "#").encode())

        client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)

def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")

def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    temp_data_1 = {'value_1': True}
    cmd = 1
    global FAN, LED
    #TODO: Update the cmd to control 2 devices
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLED":
            temp_data['value'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
        if jsonobj['method'] == "setFAN":
            temp_data_1['value_1'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data_1), 1)
        if jsonobj['method'] == "setLED":
            if jsonobj['params'] == False:
                LED = False
                cmd = 0
            if jsonobj['params'] == True:
                LED = True
                cmd = 1
        if jsonobj['method'] == "setFAN":
            if jsonobj['params'] == False:
                FAN = False
                cmd = 2
            if jsonobj['params'] == True:
                FAN = False
                cmd = 3
        #ser.write((str(cmd) + "#").encode())
    except:
        pass

    if len(bbc_port) > 0:
        ser.write((str(cmd) + "#").encode())

def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

temp = 20
light = 50
counter = 0
while True:
    counter = counter + 1
    if counter >= 10:
        counter = 0
#        collect_data = {
#            'temperature': temp,
#            'light': light
#        }
#        temp += 1
#        light += 1
#        client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    if len(bbc_port) >  0:
        readSerial()

    time.sleep(1)