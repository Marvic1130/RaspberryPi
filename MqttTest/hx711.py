import RPi.GPIO as gpio
import time

class HX711:
    
    __HIGH=1
    __LOW=0

    __sample=0
    __val=0

    def __setCursor(self, x, y):
        if y == 0:
            n=128+x
        elif y == 1:
            n=192+x
        self.lcdcmd(n)

    def __readCount(self):
        i=0
        Count=0
        gpio.setup(self.__DT, gpio.OUT)
        gpio.output(self.__DT,1)
        gpio.output(self.__SCK,0)
        gpio.setup(self.__DT, gpio.IN)

        while gpio.input(self.__DT) == 1:
            i=0
        for i in range(24):
            gpio.output(self.__SCK,1)
            Count=Count<<1

            gpio.output(self.__SCK,0)
            #time.sleep(0.001)
            if gpio.input(self.__DT) == 0: 
                Count=Count+1
                #print Count

        gpio.output(self.__SCK,1)
        Count=Count^0x800000
        #time.sleep(0.001)
        gpio.output(self.__SCK,0)
        return Count  
    
    def __init__(self, DT: int, SCK: int):
        self.__DT = DT
        self.__SCK = SCK
        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)
        gpio.setup(SCK, gpio.OUT)
        time.sleep(3)
        self.sample= self.__readCount()
        self.flag=0

    def getWeight(self):
        count= self.__readCount()
        w=0
        w=round((self.sample-count)/1230, 2)
        return w

            
    async def async_getWeight(self):
        count= self.__readCount()
        w=0
        w=round((self.sample-count)/1230, 2)
        return w
    