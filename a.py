import matplotlib.pyplot as plt

# 读取文件
filename = 'test.txt'
with open(filename, 'r') as file:
    lines = file.readlines()

# 初始化时间和高度数组
time = []
height = []

# 解析数据
for line in lines:
    if line.strip():  # 跳过空行
        tokens = line.split(',')
        timestamp = float(tokens[0].strip())
        height_str = tokens[2].strip()  # 第三个数据是高度
        height_value = float(height_str[:-1])  # 去掉末尾的 'm'
        time.append(timestamp)
        height.append(height_value)

# 生成时间轴（假设采样间隔为0.1秒）
sampling_interval = 0.1
time = [i * sampling_interval for i in range(len(time))]

# 绘图
plt.figure(figsize=(10, 6))
plt.plot(time, height, '-o')
plt.title('Altitude Change During Parachuting (Raw Data)')
plt.xlabel('Time (s)')
plt.ylabel('Altitude (m)')
plt.grid(True)

plt.savefig('altitude_change.png')

# 显示图表
plt.show()