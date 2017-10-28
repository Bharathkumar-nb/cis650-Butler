import mraa


leds = []
for i in range(2,10):
    led = mraa.Gpio(i)
    led.dir(mraa.DIR_OUT)
    led.write(1)
    leds.append(led)


def turnOnLED(led_no):
    leds[led_no].write(0)

def turnOffLED(led_no):
    leds[led_no].write(1)

def blinkLED(led_no):
    for x in xrange(0,100):
        turnOnLED(led_no)
        time.sleep(0.1)
        turnOffLED(led_no)
        time.sleep(0.1)