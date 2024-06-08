import tkinter as tk
import random
import datetime

class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speed and Altitude Display")
        self.root.configure(background='black')

        # 创建画布用来绘制轴和刻度
        self.canvas = tk.Canvas(root, width=300, height=400, bg='black', highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        # 绘制轴和刻度
        self.draw_axes()

        # 初始化指示器
        self.init_indicators()

        # 显示时间和加速度
        self.time_text = self.canvas.create_text(150, 190, fill="green", font=("Helvetica", 10))
        self.acceleration_text = self.canvas.create_text(150, 210, fill="green", font=("Helvetica", 10))

        # 自动更新速度和高度、时间和加速度
        self.update_values()
        self.update_time_and_acceleration()

    def draw_axes(self):
        # 绘制速度轴和高度轴
        self.canvas.create_line(50, 50, 50, 350, fill='green')
        self.canvas.create_line(250, 50, 250, 350, fill='green')

        # 绘制速度轴标题
        self.canvas.create_text(50, 30, text="Speed", fill='green', font=("Helvetica", 12, "bold"))

        # 绘制高度轴标题
        self.canvas.create_text(250, 30, text="Altitude", fill='green', font=("Helvetica", 12, "bold"))

        # 绘制速度刻度和数字
        for i in range(0, 301, 50):
            y = 350 - i
            self.canvas.create_line(45, y, 55, y, fill='green')
            self.canvas.create_text(30, y, text=str(i), fill='green', font=("Helvetica", 10))

        # 绘制高度刻度和数字
        for i in range(0, 1001, 200):
            y = 350 - (i / 1000 * 300)
            self.canvas.create_line(245, y, 255, y, fill='green')
            self.canvas.create_text(270, y, text=str(i), fill='green', font=("Helvetica", 10))

    def init_indicators(self):
        self.speed_indicator = self.canvas.create_line(50, 350, 50, 350, fill='red', width=2)
        self.speed_arrow = self.canvas.create_polygon(50, 350, 45, 360, 55, 360, fill='red')
        self.speed_value = self.canvas.create_text(70, 350, text="0 km/h", fill='green', font=("Helvetica", 10))

        self.altitude_indicator = self.canvas.create_line(250, 350, 250, 350, fill='red', width=2)
        self.altitude_arrow = self.canvas.create_polygon(250, 350, 245, 360, 255, 360, fill='red')
        self.altitude_value = self.canvas.create_text(270, 350, text="0 m", fill='green', font=("Helvetica", 10))

    def update_time_and_acceleration(self):
        # 更新时间
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.canvas.itemconfig(self.time_text, text=f"Time: {now}")
        # 更新加速度，这里假设加速度是 1.0g
        self.canvas.itemconfig(self.acceleration_text, text="Acceleration: 1.0g")
        self.root.after(1000, self.update_time_and_acceleration)

    def init_indicators(self):
        self.speed_indicator = self.canvas.create_line(50, 350, 50, 350, fill='red', width=2)
        self.speed_arrow = self.canvas.create_polygon(50, 350, 45, 360, 55, 360, fill='red')
        self.speed_value = self.canvas.create_text(90, 350, text="0 km/h", fill='green', font=("Helvetica", 10))

        self.altitude_indicator = self.canvas.create_line(150, 350, 150, 350, fill='red', width=2)
        self.altitude_arrow = self.canvas.create_polygon(150, 350, 145, 360, 155, 360, fill='red')
        self.altitude_value = self.canvas.create_text(170, 350, text="0 m", fill='green', font=("Helvetica", 10))

    def draw_axes(self):
            # 绘制速度轴和高度轴
            self.canvas.create_line(50, 50, 50, 350, fill='green')
            self.canvas.create_line(250, 50, 250, 350, fill='green')

            # 绘制速度轴标题
            self.canvas.create_text(50, 30, text="Speed", fill='green', font=("Helvetica", 12, "bold"))

            # 绘制高度轴标题
            self.canvas.create_text(250, 30, text="Altitude", fill='green', font=("Helvetica", 12, "bold"))

            # 绘制速度刻度和数字
            for i in range(0, 301, 50):
                y = 350 - i
                self.canvas.create_line(45, y, 55, y, fill='green')
                self.canvas.create_text(30, y, text=str(i), fill='green', font=("Helvetica", 10))

            # 绘制高度刻度和数字
            for i in range(0, 1001, 200):
                y = 350 - (i / 1000 * 300)
                self.canvas.create_line(245, y, 255, y, fill='green')
                self.canvas.create_text(270, y, text=str(i), fill='green', font=("Helvetica", 10))


    def draw_speed_axis(self, speed):
        y = 350 - (speed / 300 * 300)
        self.canvas.coords(self.speed_indicator, 50, y, 50, y + 10)
        self.canvas.coords(self.speed_arrow, 50, y, 45, y + 10, 55, y + 10)
        self.canvas.itemconfig(self.speed_value, text=f"{speed} km/h")
        self.canvas.coords(self.speed_value, 90, y)

    def draw_altitude_axis(self, altitude):
        y = 350 - (altitude / 1000 * 300)
        self.canvas.coords(self.altitude_indicator, 250, y, 250, y + 10)
        self.canvas.coords(self.altitude_arrow, 250, y, 245, y + 10, 255, y + 10)
        self.canvas.itemconfig(self.altitude_value, text=f"{altitude} m")
        self.canvas.coords(self.altitude_value, 220, y)

    def update_values(self):
        speed = random.randint(0, 300)
        altitude = random.randint(0, 1000)
        self.draw_speed_axis(speed)
        self.draw_altitude_axis(altitude)
        self.root.after(1000, self.update_values)

def main():
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
