import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal

class Assert(object):
    """docstring for Fluents"""

    def __init__(self, expr1, expr2):
        self.MY_NAME = 'Asserts'

        self.expr1 = expr1
        self.expr2 = expr2
        self.isExpr1 = False
        self.isExpr2 = False
       
        # Handle Ctrl+C
        signal.signal(signal.SIGINT, self.control_c_handler)

        # MQTT initialization
        self.mqtt_client = paho.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_log = self.on_log
        self.mqtt_topic = 'kappa/asserts'
        self.mqtt_client.will_set(self.mqtt_topic, '______________Will of '+self.MY_NAME+' _________________\n\n', 0, False)
        self.mqtt_client.connect('sansa.cs.uoregon.edu', '1883')
        self.mqtt_client.subscribe([('kappa/philosopher', 0),('kappa/butler', 0)])
        self.mqtt_client.loop_start()

    # Deal with control-c
    def control_c_handler(self, signum, frame):
        self.isDisconnected = True
        self.mqtt_client.disconnect()
        self.mqtt_client.loop_stop()  # waits until DISCONNECT message is sent out
        print ("Exit")
        sys.exit(0)

    # MQTT Handlers
    def on_connect(self, client, userdata, flags, rc):
        pass

    def on_disconnect(self, client, userdata, rc):
        pass

    def on_log(self, client, userdata, level, buf):
        pass

    # Fluents functions
    def on_message(self, client, userdata, msg):
        if(msg.payload == self.expr1) :
            if self.isExpr1 == True:
                print('Assert1')
            else:
                self.isExpr1 = True
        elif(msg.payload == self.expr2):
            if not self.isExpr1:
                # assert
                print("Assert2")
            else:
                self.isExpr1 = False

def main():
    arr = sys.argv
    if  len (arr) != 3 :
        print ('Please enter valid input, e.g. python weak_until.py <expr1> <expr2>')
        sys.exit(1)
    Assert(arr[1], arr[2])
    while True:
        time.sleep(10)

main()