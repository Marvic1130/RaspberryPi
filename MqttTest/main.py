import os
import RPi.GPIO as gpio
import fcntl
import asyncio
import ssl
import adafruit_dht
from paho import mqtt
from paho.mqtt import client as paho
from paho.mqtt import publish as publish
from hx711 import HX711



dht_device = adafruit_dht.DHT22(4) # 4는 pin번호
hx711 = HX711(21, 20)
 # use TLS for secure connection with HiveMQ Cloud
sslSettings = ssl.SSLContext(mqtt.client.ssl.PROTOCOL_TLS)
# put in your cluster credentials and hostname
auth = {'username': "test", 'password': "1111"}

I2C_SLAVE = 0x703
PM2008 = 0x28

fd = os.open('/dev/i2c-1',os.O_RDWR)
if fd < 0 :
    print("Failed to open the i2c bus\n")
io = fcntl.ioctl(fd,I2C_SLAVE,PM2008)
if io < 0 :
    print("Failed to acquire bus access/or talk to salve\n")
    
    
async def getDHT(pre_temp: int = -999, pre_humid: int = -999):
    temperature, humidity = pre_temp, pre_humid
    try:
        temperature = dht_device.temperature # 온도값 가져오기
        humidity = dht_device.humidity # 습도값 가져오기
        
    except RuntimeError as error:

        print(error.args[0])

    except Exception as error:
        dht_device.exit()
        raise error
    
    finally:
        return temperature, humidity
    
    
async def getPM(pre_velue = -1):
    try:
        pm0_1, pm2_5, pm10 = pre_velue
        data = os.read(fd,32)
        # print("Status=",int(data[2]),", MeasuringMode=",256*int(data[3])+int(data[4]),", CalibCoeff=",256*int(data[5])+int(data[6]),"\n")

        # print("GRIM: PM0.1=",256*int(data[7])+int(data[8]),",PM2.5= ",256*int(data[9])+int(data[10]),",PM10=",256*int(data[11])+int(data[12]),"\n")

        # print("-------------------------------------------------------------------------------------------------------------")
        pm0_1 = 256*int(data[7])+int(data[8])
        pm2_5= 256*int(data[9])+int(data[10])
        pm10= 256*int(data[11])+int(data[12])
            
        
        
    except OSError as e:
        print(e)
        data = e.__str__
    
    finally:
        return data, pm0_1, pm2_5, pm10

async def main():
    temperature = humidity = -999
    data = pm0_1 = pm2_5 = pm10 = None
    while True:
        
        result = await asyncio.gather(*[
            # 온습도
            getDHT(temperature, humidity),
            # 미세먼지
            getPM((pm0_1, pm2_5, pm10)),
            hx711.async_getWeight()
        ])
        
        temperature, humidity = result[0]
        data, pm0_1, pm2_5, pm10 = result[1]
        weight = result[2]

        print(temperature, humidity)
        print(pm0_1, pm2_5, pm10)
        print(weight)
        print('___________________________')
    
        await asyncio.sleep(1)
        # create a set of 2 test messages that will be published at the same time
        msgs = [{'topic': "devtest_topic/temp", 'payload': str(temperature)},
            {'topic': "devtest_topic/humid", 'payload': str(humidity)},
            {'topic': "devtest_topic/pm0.1", 'payload': str(pm0_1)},
            {'topic': "devtest_topic/pm2.5", 'payload': str(pm2_5)},
            {'topic': "devtest_topic/pm10", 'payload': str(pm10)},
            {'topic': "devtest_topic/weight", 'payload': str(weight)}]
 
        publish.multiple(msgs, hostname="broker.mqttdashboard.com", port=8883, auth=auth,
                 tls=sslSettings, protocol=paho.MQTTv31)

asyncio.run(main())
