import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal
import mraa

# Init LEDs
leds = []
for i in range(2,10):
    led = mraa.Gpio(i)
    led.dir(mraa.DIR_OUT)
    led.write(1)
    leds.append(led)

class Fluents(object):
    
    """docstring for Fluents"""

    def __init__(self, philosopher_id):
        self.MY_NAME = 'Fluents'
        self.philosopher_id = philosopher_id
       
        # Handle Ctrl+C
        signal.signal(signal.SIGINT, self.control_c_handler)

        # MQTT initialization
        self.mqtt_client = paho.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_log = self.on_log
        self.mqtt_topic = 'kappa/fluents'
        self.mqtt_client.will_set(self.mqtt_topic, '______________Will of '+self.MY_NAME+' _________________\n\n', 0, False)
        self.mqtt_client.connect('sansa.cs.uoregon.edu', '1883')
        self.mqtt_client.subscribe('kappa/philosopher', 0)
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
        print(msg.payload)
        philosopher_id, content = msg.payload.split('.')
        if '_' in philosopher_id:
            philosopher_id, led_no = philosopher_id.split('_')

        if self.philosopher_id == philosopher_id:
            if content == 'startedEating':
                self.turnOnLED(led_no)
            if content == 'stoppedEating':
                self.turnOffLED(led_no)
        
    # LED functions
    def turnOnLED(self,led_no):
        led_no = int(led_no)
        leds[led_no].write(0)

    def turnOffLED(self,led_no):
        led_no = int(led_no)
        leds[led_no].write(1)

def main():
    arr = sys.argv
    if  len (arr) != 2 :
        print ('Please enter valid input, e.g. python Fluents.py <philosopher_id>')
        sys.exit(1)
    Fluents(arr[1])    
    while True:
        time.sleep(10)

main()