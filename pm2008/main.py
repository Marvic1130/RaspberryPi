import os
import fcntl
import time

I2C_SLAVE = 0x703
PM2008 = 0x28

fd = os.open('/dev/i2c-1',os.O_RDWR)
if fd < 0 :
    print("Failed to open the i2c bus\n")
io = fcntl.ioctl(fd,I2C_SLAVE,PM2008)
if io < 0 :
    print("Failed to acquire bus access/or talk to salve\n")

try:
    while True:
        data = os.read(fd,32)
        print("Status=",int(data[2]),", MeasuringMode=",256*int(data[3])+int(data[4]),", CalibCoeff=",256*int(data[5])+int(data[6]),"\n")

        print("GRIM: PM0.1=",256*int(data[7])+int(data[8]),",PM2.5= ",256*int(data[9])+int(data[10]),",PM10=",256*int(data[11])+int(data[12]),"\n")

        print("-------------------------------------------------------------------------------------------------------------")
        time.sleep(2)
except KeyboardInterrupt:
    os.close(fd)