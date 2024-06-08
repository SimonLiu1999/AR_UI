import time
import array
import os
from timeit import default_timer as timer
import ms5611spi
import threading
import string

def pressure_to_altitude(pressure_mbar):
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

altitude_m = 0
stop_event = threading.Event()
reader = ms5611spi.MS5611SPI(stop_event)
try:
    reader.start()
    while True:
        timestamp, pressure = reader.readRaw()
        altitude_m = pressure_to_altitude(pressure)
        s = str.format("{:.3f}, {:.2f}mbar, {:.2f}m\n", timestamp, pressure, altitude_m)
        print(s)
        time.sleep(1/50.0)
except KeyboardInterrupt as e:
    stop_event.set()
    reader.join()
