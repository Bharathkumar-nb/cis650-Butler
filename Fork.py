import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal
#import mraa

leds = []
'''for i in range(2,10):
    led = mraa.Gpio(i)
    led.dir(mraa.DIR_OUT)
    led.write(1)
    leds.append(led)
'''

class Fork(object):
    """docstring for Fork"""
    def __init__(self, id, led_no):
        self.fork_id = id
        self.led_no = led_no
        signal.signal(signal.SIGINT, self.control_c_handler)

        # MQTT initialization
        self.mqtt_client = paho.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_log = self.on_log
        self.mqtt_topic = 'kappa/fork'
        self.mqtt_client.will_set(self.mqtt_topic, '______________Will of '+self.fork_id+' _________________\n\n', 0, False)
        self.mqtt_client.connect('sansa.cs.uoregon.edu', '1883',keepalive=300)
        self.mqtt_client.subscribe('kappa/butler')
        self.mqtt_client.loop_start()

        self.isRegistered = False


        # Start process
        self.register()

    def register(self):
        while not self.isRegistered:
            print(self.fork_id+'.register')
            self.mqtt_client.publish(self.mqtt_topic, self.fork_id+'.register')
            time.sleep(3)


    def on_message(self, client, userdata, msg):
        fork_id, content = msg.payload.split('.')
        if fork_id == self.fork_id:
            print(msg.payload)
            if content=='forkRegistered':
                self.isRegistered=True


    # Deal with control-c
    def control_c_handler(self, signum, frame):
        self.isDisconnected = True
        self.mqtt_client.disconnect()
        self.mqtt_client.loop_stop()  # waits until DISCONNECT message is sent out
        print ("Exit")
        sys.exit(0)

    def on_connect(self, client, userdata, flags, rc):
        pass

    def on_disconnect(self, client, userdata, rc):
        pass

    def on_log(self, client, userdata, level, buf):
        #print("log: {}".format(buf)) # only semi-useful IMHO
        pass

def main():
    arr = sys.argv
    if  len (arr) != 3 :
        print ('Please enter valid input, e.g. python Fork.py <Fork_id> <led_no>')
        sys.exit(1)
    if arr[2] not in '12345678' or len(arr[2]) > 1:
        print ('Please enter valid led number between 1 to 8')
        sys.exit(1)
    Fork(arr[1], arr[2])
    while True:
        time.sleep(10)

main()