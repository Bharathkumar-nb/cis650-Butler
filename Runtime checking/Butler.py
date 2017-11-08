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

class Butler(object):
    """docstring for Butler"""
    def __init__(self, max_counter):
        self.MY_NAME = 'Butler'
        self.led_no = 7
        self.semaphore = int(max_counter)
        self.philosophers_queue = []
        self.forkStatuses = {}
        self.fork_queue = {}

        # Handle Ctrl+C
        signal.signal(signal.SIGINT, self.control_c_handler)

        # MQTT initialization
        self.mqtt_client = paho.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.message_callback_add('kappa/philosopher', self.on_message_from_philosopher)
        self.mqtt_client.message_callback_add('kappa/fork', self.on_message_from_fork)
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_log = self.on_log
        self.mqtt_topic = 'kappa/butler'
        self.mqtt_client.will_set(self.mqtt_topic, '______________Will of '+self.MY_NAME+' _________________\n\n', 0, False)
        self.mqtt_client.connect('sansa.cs.uoregon.edu', '1883')
        self.mqtt_client.subscribe([('kappa/philosopher', 0), ('kappa/fork', 0)])
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

    # Butler functions
    def on_message_from_philosopher(self, client, userdata, msg):
        print(msg.payload)
        # print('Before: Semaphore', self.semaphore)
        # print('Before: philosophers_queue', self.philosophers_queue)
        # print('Before: forkStatuses', self.forkStatuses)
        # print('Before: fork_queue', self.fork_queue)
        
        philosopher_id, content = msg.payload.split('.')
        if '_' in philosopher_id:
            philosopher_id, fork_id = philosopher_id.split('_')

        if content == 'sitRequest':
            if self.semaphore > 0:
                self.semaphore -= 1
                if self.semaphore == 0:
                    self.turnOnLED(self.led_no)
                # print(philosopher_id+'.sitRequestAccepted')
                self.mqtt_client.publish(self.mqtt_topic, philosopher_id+'.sitRequestAccepted')
            else:
                self.philosophers_queue.append(philosopher_id)
                # print(philosopher_id+'.inQueue')
                self.mqtt_client.publish(self.mqtt_topic, philosopher_id+'.inQueue')
        if content == 'forkRequest':
            if not self.forkStatuses[fork_id]:
                self.forkStatuses[fork_id] = True
                # print(philosopher_id+'.forkAccepted')
                self.mqtt_client.publish(self.mqtt_topic, 
                    philosopher_id+'_'+fork_id+'.forkAccepted')
            else:
                self.fork_queue[fork_id].append(philosopher_id)
            # print(self.forkStatuses)
        if content == 'putFork':
            # print(philosopher_id+'_'+fork_id+'.forkDoneUsing')
            self.mqtt_client.publish(self.mqtt_topic, philosopher_id+'_'+fork_id+'.forkDoneUsing')
            self.forkStatuses[fork_id] = False
            if len(self.fork_queue[fork_id])>0:
                philosopher_id = self.fork_queue[fork_id].pop(0)
                self.forkStatuses[fork_id] = True
                # print(philosopher_id+'.forkAccepted')
                self.mqtt_client.publish(self.mqtt_topic, philosopher_id+'.forkAccepted')
        if content == 'arise':
            self.semaphore += 1
            self.turnOffLED(self.led_no)
            # print(philosopher_id+'.ariseAccepted')
            self.mqtt_client.publish(self.mqtt_topic, philosopher_id+'.ariseAccepted')
            time.sleep(1)
            self.handleQueue()

        # print('After: Semaphore', self.semaphore)
        # print('After: philosophers_queue', self.philosophers_queue)
        # print('After: forkStatuses', self.forkStatuses)
        # print('After: fork_queue', self.fork_queue)

    def on_message_from_fork(self, client, userdata, msg):
        print(msg.payload)
        key, content = msg.payload.split('.')
        if content == 'register':
            self.forkStatuses[key] = False
            self.fork_queue[key] = []
            # print(key+'.forkRegistered')
            self.mqtt_client.publish(self.mqtt_topic, key+'.forkRegistered')

    def handleQueue(self):
        if len(self.philosophers_queue) != 0:
            philosopher_id = self.philosophers_queue.pop(0)
            self.turnOffLED(self.semaphore)
            self.semaphore -= 1
            if self.semaphore == 0:
                self.turnOnLED(self.led_no)
            #print(philosopher_id+'.sitRequestAccepted')
            self.mqtt_client.publish(self.mqtt_topic, philosopher_id+'.sitRequestAccepted')
    
    

    # LED functions
    def turnOnLED(self,led_no):
        leds[led_no].write(0)

    def turnOffLED(self,led_no):
        leds[led_no].write(1)

    

def main():
    arr = sys.argv
    if  len (arr) != 2 :
        print ('Please enter valid input, e.g. python Butler.py <Max_counter>')
        sys.exit(1)
    Butler(arr[1])    
    while True:
        time.sleep(10)

main()