import smbus
import time

# 设定 I2C 总线
bus = smbus.SMBus(1)

# BH1750 地址
address = 0x23

# 定义一些从 BH1750 读取数据的模式
BH1750_CONTINUOUS_HIGH_RES_MODE = 0x10
BH1750_CONTINUOUS_HIGH_RES_MODE_2 = 0x11
BH1750_CONTINUOUS_LOW_RES_MODE = 0x13
BH1750_ONE_TIME_HIGH_RES_MODE = 0x20
BH1750_ONE_TIME_HIGH_RES_MODE_2 = 0x21
BH1750_ONE_TIME_LOW_RES_MODE = 0x23

def read_light(addr=address):
    data = bus.read_i2c_block_data(addr, BH1750_ONE_TIME_HIGH_RES_MODE, 2)
    return ((data[0] << 8) + data[1]) / 1.2

try:
    while True:
        light_level = read_light()
        print("Light Level : {} lux".format(light_level))
        time.sleep(1)
except KeyboardInterrupt:
    print("Measurement stopped by User")