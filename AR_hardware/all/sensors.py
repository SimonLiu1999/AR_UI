import tkinter as tk
from threading import Thread, Event
import time
import random

import ms5611spi
import smbus
import serial

import os
import datetime

class Log:
    def __init__(self, device, directory="/home/pi/logs" ):
        """初始化日志类，创建日志目录和文件"""
        self.directory = directory
        self.device = device
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        
        # 获取当前时间并格式化为字符串
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.file_path = os.path.join(self.directory, device + f"_log_{current_time}.txt")
        
        # 打开文件进行写入
        self.file = open(self.file_path, 'a')
    
    def write(self, *args, sep=' ', end='\n'):
        """类似print的功能，将数据写入日志文件"""
        message = sep.join(map(str, args)) + end
        self.file.write(message)
        self.file.flush()  # 确保数据及时写入文件
    
    def close(self):
        """关闭日志文件"""
        self.file.close()

    def __enter__(self):
        """支持上下文管理"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动关闭文件"""
        self.close()

class BH1750:
    def __init__(self):
        # 设定 I2C 总线
        self.bus = smbus.SMBus(1)

        #log 
        self.log = Log(device="BH1750")

        # BH1750 地址
        self.address = 0x23
        # 定义一些从 BH1750 读取数据的模式
        self.BH1750_CONTINUOUS_HIGH_RES_MODE = 0x10
        self.BH1750_CONTINUOUS_HIGH_RES_MODE_2 = 0x11
        self.BH1750_CONTINUOUS_LOW_RES_MODE = 0x13
        self.BH1750_ONE_TIME_HIGH_RES_MODE = 0x20
        self.BH1750_ONE_TIME_HIGH_RES_MODE_2 = 0x21
        self.BH1750_ONE_TIME_LOW_RES_MODE = 0x23

    def read_light(self, addr):
        data = self.bus.read_i2c_block_data(addr, self.BH1750_ONE_TIME_HIGH_RES_MODE, 2)
        return ((data[0] << 8) + data[1]) / 1.2

    def run(self, update_method):
        try:
            while True:
                light_level = self.read_light(self.address)
                #widget.insert(tk.END, "Light Level : {} lux".format(light_level) + '\n')
                #widget.see(tk.END)
                #print("Light Level : {} lux".format(light_level))
                self.log.write("Light Level : {} lux".format(light_level))
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Measurement stopped by User")


class MS5611:
    def __init__(self):
        self.log = Log(device="MS5611")
    def pressure_to_altitude(self, pressure_mbar):
        """
        将气压（单位为毫巴）转换为相对于海平面的高度（单位为米）。
        参数:
        pressure_mbar -- 气压（毫巴）
        
        返回:
        altitude_m -- 高度（米）
        """
        # 标准海平面平均气压
        P0 = 1000  # 单位：毫巴
        # 标准大气下，气压随高度的变化常数
        L = 0.0065    # 温度随高度的递减率，单位：K/m
        T0 = 288.15   # 标准海平面温度，单位：K
        g = 9.80665   # 重力加速度，单位：m/s^2
        R = 287.05    # 理想气体常数，单位：J/(kg·K)

        # 根据气压公式计算高度
        if pressure_mbar<200:
            #超出量程
            pressure_mbar = 200
        altitude_m = (T0 / L) * ((pressure_mbar / P0) ** (-L * R / g) - 1)
        return altitude_m
    
    def run(self, update_method):
        altitude_m = 0
        prev_altitude_m = 0
        alpha = 0.2
        stop_event = Event()
        reader = ms5611spi.MS5611SPI(stop_event)
        try:
            reader.start()
            while True:
                timestamp, pressure = reader.readRaw()
                prev_altitude_m = altitude_m
                new_altitude_m = self.pressure_to_altitude(pressure)
                # 经过一个更新滤波器
                altitude_m = altitude_m*(1-alpha) + new_altitude_m*alpha
                s = str.format("{:.3f}, {:.2f}mbar, {:.2f}m\n", timestamp, pressure, altitude_m)
                #print(s)
                self.log.write(s)
                #widget.insert(tk.END, s + '\n')
                #widget.see(tk.END)
                altitude_m = int(altitude_m)
                update_method(speed = prev_altitude_m - altitude_m, altitude = altitude_m)
                time.sleep(1/10.0)
        except KeyboardInterrupt as e:
            stop_event.set()
            reader.join()


class BMX160:
    def __init__(self):
        # 设置I2C总线
        self.bus = bus = smbus.SMBus(1)
        self.DEVICE_ADDRESS = 0x68  # BMX160的I2C地址

        self.log = Log(device="BMX160")
        
        # BMX160寄存器地址
        self.ACC_X_LSB_REG = 0x12
        self.ACC_X_MSB_REG = 0x13
        self.ACC_Y_LSB_REG = 0x14
        self.ACC_Y_MSB_REG = 0x15
        self.ACC_Z_LSB_REG = 0x16
        self.ACC_Z_MSB_REG = 0x17
        self.CMD_REG = 0x7E
    def init_bmx160(self):
        self.bus.write_byte_data(self.DEVICE_ADDRESS, self.CMD_REG, 0x11)  # 设置加速度计为正常模式
        time.sleep(0.1)
    def twos_complement(self, val, bits):
        """计算二进制补码"""
        if val & (1 << (bits - 1)):
            val -= 1 << bits
        return val
    def read_bmx160(self):
        data_x = self.bus.read_i2c_block_data(self.DEVICE_ADDRESS, self.ACC_X_LSB_REG, 2)
        data_y = self.bus.read_i2c_block_data(self.DEVICE_ADDRESS, self.ACC_Y_LSB_REG, 2)
        data_z = self.bus.read_i2c_block_data(self.DEVICE_ADDRESS, self.ACC_Z_LSB_REG, 2)

        acc_x = (data_x[1] << 8) | data_x[0]
        acc_y = (data_y[1] << 8) | data_y[0]
        acc_z = (data_z[1] << 8) | data_z[0]

        acc_x = self.twos_complement(acc_x, 16)
        acc_y = self.twos_complement(acc_y, 16)
        acc_z = self.twos_complement(acc_z, 16)

        # 转换为g单位
        scale_factor = 2 / 32768.0
        acc_x *= scale_factor
        acc_y *= scale_factor
        acc_z *= scale_factor

        return acc_x, acc_y, acc_z
    def run(self, update_method):
        self.init_bmx160()
        while True:
            acc_x, acc_y, acc_z = self.read_bmx160()
            #widget.insert(tk.END, f"Accelerometer Data: X={acc_x:.3f}g, Y={acc_y:.3f}g, Z={acc_z:.3f}g" + '\n')
            #widget.see(tk.END)
            #print(f"Accelerometer Data: X={acc_x:.3f}g, Y={acc_y:.3f}g, Z={acc_z:.3f}g")
            self.log.write(f"Accelerometer Data: X={acc_x:.3f}g, Y={acc_y:.3f}g, Z={acc_z:.3f}g")
            time.sleep(0.1)

class GPS:
    def __init__(self):
        self.SERIAL_PORT = '/dev/serial0'
        self.BAUD_RATE = 9600
        self.update_method = None
        self.log = Log(device="GPS")
    
    def read_gps_data(self):
        try:
            ser = serial.Serial(self.SERIAL_PORT, baudrate=self.BAUD_RATE, timeout=1)
        except serial.SerialException as e:
            #print(f"无法打开串行端口: {e}")
            #self.widget.insert(tk.END, f"无法打开串行端口: {e}" + '\n')
            #self.widget.see(tk.END)
            return

        try:
            while True:
                try:
                    line = ser.readline().decode('utf-8', 'ignore').strip()
                    #print("Received:", line)  # 打印所有接收的数据
                    self.log.write("Received:"+ str(line))
                    #self.widget.insert(tk.END, "Received:" + str(line) + '\n')
                    #self.widget.see(tk.END)
                    if line:
                        self.parse_nmea_sentence(line)
                except serial.SerialException as e:
                    print(f"串行读取错误: {e}")
                    # 增加错误处理和重连逻辑
        except KeyboardInterrupt:
            print("程序已停止")
        finally:
            ser.close()
    
    def parse_nmea_sentence(self, sentence):
        """
        检查NMEA句子类型并进行解析
        """
        if sentence.startswith('$GNGLL') or sentence.startswith('$GPGLL'):
            self.parse_gpgll(sentence)
    
    def parse_gpgll(self, data):
        """
        解析GLL句子以获取经纬度和时间
        """
        parts = data.split(',')
        if parts[6] == 'A':  # 确保数据有效
            latitude = parts[1]
            longitude = parts[3]
            time = parts[5]
            #print(f"Time: {time[:2]}:{time[2:4]}:{time[4:6]}")
            #print(f"Latitude: {latitude[:2]}°{latitude[2:]}\' {parts[2]}")
            #print(f"Longitude: {longitude[:3]}°{longitude[3:]}\' {parts[4]}")
            self.log.write(f"Time: {time[:2]}:{time[2:4]}:{time[4:6]}")
            self.log.write(f"Latitude: {latitude[:2]}°{latitude[2:]}\' {parts[2]}")
            self.log.write(f"Longitude: {longitude[:3]}°{longitude[3:]}\' {parts[4]}")
            #self.widget.insert(tk.END, f"Time: {time[:2]}:{time[2:4]}:{time[4:6]}" + '\n')
            #self.widget.insert(tk.END, f"Latitude: {latitude[:2]}°{latitude[2:]}\' {parts[2]}" + '\n')
            #self.widget.insert(tk.END, f"Longitude: {longitude[:3]}°{longitude[3:]}\' {parts[4]}" + '\n')
            #self.widget.see(tk.END)

    def run(self,update_method):
        self.update_method = update_method
        self.read_gps_data()

