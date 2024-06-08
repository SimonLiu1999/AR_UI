import serial
import time

# 设置串行端口
SERIAL_PORT = '/dev/serial0'
BAUD_RATE = 9600

def read_gps_data():
    try:
        ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
    except serial.SerialException as e:
        print(f"无法打开串行端口: {e}")
        return

    try:
        while True:
            try:
                line = ser.readline().decode('utf-8', 'ignore').strip()
                print("Received:", line)  # 打印所有接收的数据
                if line:
                    parse_nmea_sentence(line)
            except serial.SerialException as e:
                print(f"串行读取错误: {e}")
                # 增加错误处理和重连逻辑
    except KeyboardInterrupt:
        print("程序已停止")
    finally:
        ser.close()

def parse_nmea_sentence(sentence):
    """
    检查NMEA句子类型并进行解析
    """
    if sentence.startswith('$GNGLL') or sentence.startswith('$GPGLL'):
        parse_gpgll(sentence)

def parse_gpgll(data):
    """
    解析GLL句子以获取经纬度和时间
    """
    parts = data.split(',')
    if parts[6] == 'A':  # 确保数据有效
        latitude = parts[1]
        longitude = parts[3]
        time = parts[5]
        print(f"Time: {time[:2]}:{time[2:4]}:{time[4:6]}")
        print(f"Latitude: {latitude[:2]}°{latitude[2:]}\' {parts[2]}")
        print(f"Longitude: {longitude[:3]}°{longitude[3:]}\' {parts[4]}")

if __name__ == "__main__":
    read_gps_data()