
# import modules
import time
import board
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull
#import all the devices
import adafruit_am2320
import busio
import neopixel

pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, auto_write=False, brightness=0.5)
tem = AnalogIn(board.A1)

colors = [(0, 0, 0), (0, 0, 0),
        (0, 0, 0), (0, 0, 0),
        (0, 0, 0), (0, 0, 0),
        (0, 0, 0), (0, 0, 0),
        (0, 0, 0), (0, 0, 0)]

# create the I2C shared bus
i2c = busio.I2C(board.SCL, board.SDA)
am = adafruit_am2320.AM2320(i2c)
switch = DigitalInOut(board.BUTTON_A)
switch.direction = Direction.INPUT
switch.pull = Pull.DOWN



Period = 1
Timer = 0
# start to count time
cycle_count = 0
# analyzing the time
current_temperature = int(am.temperature)
print("Current Temperature:", current_temperature)
StartRedValue = int (255 - (30 - current_temperature)*30)
StartBlueValue = int( (30 - current_temperature) * 30 )
if (StartBlueValue <= 1): StartBlueValue = 1
if (StartBlueValue >= 254): StartBlueValue = 254
if (StartRedValue <= 1): StartRedValue = 1
if (StartRedValue >= 254): StartRedValue = 254
# breathe period: how many seconds --- breath
period = (30 - current_temperature)*0.1 + 0.5
RedSleepTime = int ((period/(StartRedValue)) / 0.001)
BlueSleepTime = int ((period/(StartBlueValue)) / 0.001)
if (RedSleepTime <= 0): RedSleepTime = 1
if (BlueSleepTime <= 0): BlueSleepTime = 1

# define the variables
pixelRedValue = StartRedValue
pixelBlueValue = StartBlueValue

# direction means the light off or on
direction = -1
# define the humidity variables
current_humidity = int(am.relative_humidity)
while True:
    if switch.value is False:
        if (cycle_count % 1000 == 0):
            # analyzing the time
            current_temperature = int (am.temperature)
            print("Current Temperature:", current_temperature)
            # breathe period: how many seconds --- breath
            period = (30 - current_temperature)*0.1 + 0.5
            # the equations to determind the red and blue value
            StartRedValue = int (255 - (30 - current_temperature)*30)
            StartBlueValue = int ( (30 - current_temperature) * 30 )
            # protect the program
            if (StartBlueValue <= 1): StartBlueValue = 1
            # incase of the bug, dont go to 255
            if (StartBlueValue >=254): StartBlueValue = 254
            if (StartRedValue <= 1): StartRedValue = 1
            if (StartRedValue >= 254): StartRedValue = 254
            # every value needs how much time to reduce / every 1ms
            RedSleepTime = int ((period/(StartRedValue)) / 0.001)
            BlueSleepTime = int ((period/(StartBlueValue)) / 0.001)
            # protect the program
            if (RedSleepTime <= 0): RedSleepTime = 1
            if (BlueSleepTime <= 0): BlueSleepTime = 1

        # light off process
        if ((pixelBlueValue >= 1 and direction == -1) or (pixelBlueValue <= StartBlueValue and direction == 1)):
            if (cycle_count % BlueSleepTime == 0):
                pixelBlueValue = pixelBlueValue + direction
            #print("Blue:", pixelBlueValue)
        if ((pixelRedValue >= 1 and direction == -1) or (pixelRedValue <= StartRedValue and direction == 1)):
            if (cycle_count % RedSleepTime == 0):
                pixelRedValue = pixelRedValue + direction
            #print("Red:", pixelRedValue)

        # light on process
        if ((pixelRedValue <= 1 and pixelBlueValue <= 1 and direction == -1) or \
            (pixelRedValue >= StartRedValue and pixelBlueValue >= StartBlueValue and direction == 1)):
            # direction goes opposite
            direction = -1 * direction

        # for loop, controling the pixels light
        for x in range(len(pixels)):
            #controlling the numbers of pixels ( every 5C = 1 pixel )
            if x <= (current_temperature / 5 - 1):
                pixels[x] = (pixelRedValue, 0, pixelBlueValue)
            else:
                # turn off other pixels
                if (x == int (current_temperature / 5)):
                    pixels[x] = ( int (pixelRedValue * (current_temperature % 5) / 5), 0, int(pixelBlueValue * (current_temperature % 5) / 5))
                else:
                    pixels[x] = (0, 0, 0)

        pixels.show()


    else:
        # humidity mode
        if cycle_count % 1000 == 0:
            current_humidity = int(am.relative_humidity)
            print("Current Humidity:", current_humidity)
        for x in range(len(pixels)):
            if x <= (current_humidity / 10 - 1):
                # dont make the pixel too bright
                pixels[x] = (0, 50, 0)
            else:
                # pixels turn off
                if (x == int (current_humidity / 10)):
                    pixels[x] = ( 0, int(50 * (current_humidity % 10) / 10), 0)
                else:
                    pixels[x] = (0, 0, 0)

        pixels.show()

    cycle_count = cycle_count + 1
    time.sleep(0.001) #sleep every 1ms

# Write your code here :-)
# Write your code here :-)
