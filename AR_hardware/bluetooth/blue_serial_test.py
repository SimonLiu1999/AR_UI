import serial

# 配置串口
ser = serial.Serial('/dev/rfcomm0', baudrate=9600, timeout=1)

print("等待蓝牙连接...")

while True:
    if ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').rstrip()
        print(f"收到数据: {data}")
        
        # 你可以在这里处理接收到的数据
        if data == "hello":
            ser.write("你好，手机!\n".encode('utf-8'))
        elif data == "exit":
            print("断开连接")
            break

ser.close()