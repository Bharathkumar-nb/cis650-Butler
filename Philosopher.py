import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal
import mraa

# Init LEDs
leds = []
for i in range(2,10):
    led = mraa.Gpio(i)
    # led.dir(mraa.DIR_OUT)
    leds.append(led)

class Philosopher(object):
    """docstring for Philosopher"""
    def __init__(self, philosopher_id, led_no, left_fork, right_fork):
        self.philosopher_id = philosopher_id
        self.led_no = int(led_no)
        self.left_fork = left_fork
        self.right_fork = right_fork

        self.isAccepted = False
        self.isWaiting = False
        self.isRightForkAccepted = False
        self.isRightForkUsed = False


        # Handle Ctrl+C
        signal.signal(signal.SIGINT, self.control_c_handler)

        # MQTT initialization
        self.mqtt_client = paho.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_log = self.on_log
        self.mqtt_topic = 'kappa/philosopher'
        self.mqtt_client.will_set(self.mqtt_topic, '______________Will of '+self.philosopher_id+' _________________\n\n', 0, False)
        self.mqtt_client.connect('sansa.cs.uoregon.edu', '1883')
        self.mqtt_client.subscribe('kappa/butler')
        self.mqtt_client.loop_start()

        # Start process
        self.sendSitRequest()

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

    def on_message(self, client, userdata, msg):
        print(msg.payload)
        philosopher_id, content = msg.payload.split('.')
        if '_' in philosopher_id:
            philosopher_id, fork_id = philosopher_id.split('_')


        if philosopher_id == self.philosopher_id:
            # print(msg.payload)
            # print("Before: isAccepted", self.isAccepted)
            # print('Before: isWaiting',self.isWaiting)
            # print('Before: isRightForkAccepted',self.isRightForkAccepted)
            if content == 'sitRequestAccepted':
                self.isAccepted = True
                self.turnOnLED()
                self.sendForkRequest(self.right_fork)
            if content == 'inQueue':
                self.isWaiting = True
            if content == 'forkAccepted':
                if not self.isRightForkAccepted:
                    self.isRightForkAccepted = True
                    self.sendForkRequest(self.left_fork)
                else:
                    self.start_eat()
            if content == 'forkDoneUsing':
                if not self.isRightForkUsed:
                    self.isRightForkUsed = True
                    self.sendPutFork(self.right_fork, 'right')
                else:
                    self.sendArise()
            if content == 'ariseAccepted':
                self.isAccepted = False
                self.isRightForkAccepted = False
                self.isRightForkUsed = False
                self.turnOffLED()
                # print(self.philosopher_id+'.sitRequest')
                self.mqtt_client.publish(self.mqtt_topic, self.philosopher_id+'.sitRequest')


            # print("After: isAccepted", self.isAccepted)
            # print('After: isWaiting',self.isWaiting)
            # print('After: isRightForkAccepted',self.isRightForkAccepted)

    # LED functions
    def turnOnLED(self):
        leds[self.led_no].write(0)

    def turnOffLED(self):
        leds[self.led_no].write(1)

    def blinkLED(self):
        for x in xrange(1,10):
            self.turnOffLED()
            time.sleep(0.5)
            self.turnOnLED()
            time.sleep(0.5)

    # Philosoher functions
    def sendSitRequest(self):
        # reset values
        self.isAccepted = False
        self.isWaiting = False
        self.isRightForkAccepted = False
        self.isRightForkUsed = False
        self.turnOffLED()
        while not self.isAccepted and not self.isWaiting:
            # print(self.philosopher_id+'.sitRequest')
            self.mqtt_client.publish(self.mqtt_topic, self.philosopher_id+'.sitRequest')
            time.sleep(5)

    def sendForkRequest(self, fork):
        while True:
            user_input = raw_input('Press y to pick {} Fork\n'.format(fork))
            if user_input.lower() == 'y':
                # print(self.philosopher_id+'_'+fork+'.forkRequest')
                self.mqtt_client.publish(self.mqtt_topic, self.philosopher_id+'_'+fork+'.forkRequest')
                return

    def start_eat(self):
        while True:
            user_input = raw_input('Press y to Eat\n')
            if user_input.lower() == 'y':
                self.blinkLED()
                self.sendPutFork(self.left_fork, 'left')
                return

    def sendPutFork(self, fork_id, fork_side):
        while True:
            user_input = raw_input('Press y to put {} fork down\n'.format(fork_id))
            if user_input.lower() == 'y':
                # print(fork_id+'.putFork')
                self.mqtt_client.publish(self.mqtt_topic,
                self.philosopher_id+'_'+fork_id+'.putFork')
                return
    
    def sendArise(self):
        while True:
            user_input = raw_input('Press y to arise\n')
            if user_input.lower() == 'y':
                # print(self.philosopher_id + '.arise')
                self.mqtt_client.publish(self.mqtt_topic, self.philosopher_id + '.arise')
                return

def main():
    arr = sys.argv
    if  len (arr) != 5 :
        print ('Please enter valid input, e.g. python Philosopher.py <Philosopher_id> <led_no> <left_fork_id> <right_fork_id>')
        sys.exit(1)
    if arr[2] not in '12345678' or len(arr[2]) > 1:
        print ('Please enter valid led number between 1 to 8')
        sys.exit(1)
    Philosopher(arr[1], arr[2], arr[3], arr[4])
    while True:
        time.sleep(10)

main()