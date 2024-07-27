import sys
import random
import tkinter as tk
import tkinter.filedialog as tkfd
import tkinter.ttk as ttk

from threading import Thread, Event

from sensors import Log, BH1750, BMX160, GPS, MS5611

# 常量定义
FONT = "Arial Black"
SIZE = 25
SCRN_HEIGHT = 900
SCRN_WIDTH = 1920
LINE_WIDTH = 5
RATIO = 8.8

SCRN_WIDTH_CENTER = SCRN_WIDTH / 2
SCRN_HEIGHT_CENTER = SCRN_HEIGHT / 2

G_WARNING_THRESHOLD = 4.0

SPEED_UNITS_TEXT = "km/h"
HEIGHT_UNITS_TEXT = "m"
G_WARNING_TEXT = "G-FORCE WARNING"
FREEFALL_TIME_TEXT = "FREEFALL TIME "  # 必须有后续的空格


class FlightInstrumentCanvas(tk.Canvas):
    def __init__(self, master, size=SIZE, testing=False):
        super().__init__(master, bg="light gray" if testing else "black")
        
        # 初始化仪表参数
        self.speed = 0
        self.altitude = 0
        self.pitch = 0  # 范围 +90 ~ -90
        self.roll = 0  # 范围 +180 ~ -180, 向右倾斜为正
        self.g_force = 4.2
        self.ffl_secs = 100  # 必须大于0，小于0时显示0

        self.size = size
        self.center_width = SCRN_WIDTH_CENTER
        self.center_height = SCRN_HEIGHT_CENTER
        self.fg_color = "black" if testing else "green"
        
        self.grid()

        # 绘制各个仪表
        self.draw_speedometer()
        self.draw_altimeter()
        self.draw_horizon()
        self.draw_g_force_indicator()
        self.draw_freefall_time_indicator()

        # 更新仪表值
        self.update_values(self.speed, self.altitude, self.pitch, self.roll, self.g_force, self.ffl_secs)

    def draw_number_line(self, cur_val, cen_val, ratio, type=1):
        """绘制数值线"""
        self.create_text(
            self.center_width - type * (self.size * 23.5),
            self.center_height - (cur_val - cen_val) * ratio,
            text=int(cur_val),
            anchor=(tk.E if type == 1 else tk.W),
            fill=self.fg_color,
            tags=("spd_line" if type == 1 else "alt_line"),
            font=(FONT, int(self.size * 1.5)),
        )
        self.create_line(
            self.center_width - type * (self.size * 23),
            self.center_height - (cur_val - cen_val) * ratio,
            self.center_width - type * (self.size * 22),
            self.center_height - (cur_val - cen_val) * ratio,
            fill=self.fg_color,
            tags=("spd_line" if type == 1 else "alt_line"),
            width = LINE_WIDTH
        )

    def draw_speedometer(self):
        """绘制速度表"""
        base_size = self.size * 26

        self.create_line(
            self.center_width - base_size,
            self.center_height - self.size * 11.5,
            self.center_width - 22 * self.size,
            self.center_height - self.size * 11.5,
            self.center_width - 22 * self.size,
            self.center_height + self.size * 11.5,
            self.center_width - base_size,
            self.center_height + self.size * 11.5,
            fill=self.fg_color,
            width=LINE_WIDTH
        )
        self.create_text(
            self.center_width - self.size * 24,
            self.center_height - self.size * 13,
            text=SPEED_UNITS_TEXT,
            fill=self.fg_color, 
            font=(FONT, int(self.size * 1.5)),
        )
        self.create_polygon(
            self.center_width - self.size * 21,
            self.center_height,
            self.center_width - self.size * 20,
            self.center_height + self.size / 1.732,
            self.center_width - self.size * 20,
            self.center_height - self.size / 1.732,
            fill=self.fg_color
        )
        self.create_text(
            self.center_width - self.size * 12,
            self.center_height,
            text=self.speed,
            font=(FONT, int(self.size * 5)),
            fill=self.fg_color,
            tags="main_spd"
        )

    def update_speedometer(self):
        """更新速度表"""
        ratio = RATIO
        self.delete("spd_line")

        show_speed = (self.speed * 3.6) if SPEED_UNITS_TEXT == "km/h" else (self.speed)

        cur_spd = show_speed // 10 * 10
        self.draw_number_line(cur_spd, show_speed, ratio, 1)
        while cur_spd - show_speed >= -20:
            cur_spd -= 10
            self.draw_number_line(cur_spd, show_speed, ratio, 1)
        
        cur_spd = show_speed // 10 * 10 + 10
        self.draw_number_line(cur_spd, show_speed, ratio, 1)
        while cur_spd - show_speed <= 20:
            cur_spd += 10
            self.draw_number_line(cur_spd, show_speed, ratio, 1)
        
        self.itemconfigure("main_spd", text=int(show_speed))

    def draw_altimeter(self):
        """绘制高度表"""
        base_size = self.size * 26

        self.create_line(
            self.center_width + base_size,
            self.center_height - self.size * 11.5,
            self.center_width + 22 * self.size,
            self.center_height - self.size * 11.5,
            self.center_width + 22 * self.size,
            self.center_height + self.size * 11.5,
            self.center_width + base_size,
            self.center_height + self.size * 11.5,
            fill=self.fg_color,
            width=LINE_WIDTH
        )
        self.create_text(
            self.center_width + self.size * 24,
            self.center_height - self.size * 13,
            text=HEIGHT_UNITS_TEXT,
            fill=self.fg_color,
            font=(FONT, int(self.size * 1.5)),
        )
        self.create_polygon(
            self.center_width + self.size * 21,
            self.center_height,
            self.center_width + self.size * 20,
            self.center_height + self.size / 1.732,
            self.center_width + self.size * 20,
            self.center_height - self.size / 1.732,
            fill=self.fg_color
        )
        self.create_text(
            self.center_width + self.size * 12,
            self.center_height,
            text=self.altitude,
            font=(FONT, int(self.size * 5)),
            fill=self.fg_color,
            tags="main_alt"
        )

    def update_altimeter(self):
        """更新高度表"""
        ratio = RATIO / 50
        self.delete("alt_line")

        cur_alt = self.altitude // 500 * 500
        self.draw_number_line(cur_alt, self.altitude, ratio, -1)
        while cur_alt - self.altitude >= -1000:
            cur_alt -= 500
            self.draw_number_line(cur_alt, self.altitude, ratio, -1)
        
        cur_alt = self.altitude // 500 * 500 + 500
        self.draw_number_line(cur_alt, self.altitude, ratio, -1)
        while cur_alt - self.altitude <= 1000:
            cur_alt += 500
            self.draw_number_line(cur_alt, self.altitude, ratio, -1)
        
        self.itemconfigure("main_alt", text=int(self.altitude))
    
    def draw_horizon(self):
        """绘制地平线"""
        ''' 暂时去掉线，给字体留位置
        self.create_line(
            self.center_width - self.size * 3,
            self.center_height,
            self.center_width - self.size * 13,
            self.center_height,
            fill=self.fg_color,
            width=LINE_WIDTH
        )
        self.create_line(
            self.center_width + self.size * 3,
            self.center_height,
            self.center_width + self.size * 13,
            self.center_height,
            fill=self.fg_color,
            width=LINE_WIDTH
        )
        '''
        self.create_line(
            self.center_width - self.size * 2,
            self.center_height + self.size * 1.5,
            self.center_width - self.size * 1,
            self.center_height + self.size * 1.5,
            self.center_width - self.size * 0.5,
            self.center_height + self.size * 2.5,
            self.center_width,
            self.center_height + self.size * 1.5,
            self.center_width + self.size * 0.5,
            self.center_height + self.size * 2.5,
            self.center_width + self.size * 1,
            self.center_height + self.size * 1.5,
            self.center_width + self.size * 2,
            self.center_height + self.size * 1.5,
            fill=self.fg_color,
            width=LINE_WIDTH
        )
        for i in (5, -5):
            self.create_line(
                self.center_width - self.size * 3,
                self.center_height - self.size * 2.3 * i,
                self.center_width - self.size * 8,
                self.center_height - self.size * 2.3 * i,
                dash=1,
                fill=self.fg_color,
            )
            self.create_line(
                self.center_width + self.size * 3,
                self.center_height - self.size * 2.3 * i,
                self.center_width + self.size * 8,
                self.center_height - self.size * 2.3 * i,
                dash=1,
                fill=self.fg_color
            )
            self.create_line(
                self.center_width - self.size * 8,
                self.center_height - self.size * 2.3 * i,
                self.center_width - self.size * 8,
                self.center_height - self.size * 2.3 * i - self.size * 0.6,
                dash=1,
                fill=self.fg_color
            )
            self.create_line(
                self.center_width + self.size * 8,
                self.center_height - self.size * 2.3 * i,
                self.center_width + self.size * 8,
                self.center_height - self.size * 2.3 * i - self.size * 0.6,
                dash=1,
                fill=self.fg_color
            )
            self.create_text(
                self.center_width - self.size * 9,
                self.center_height - self.size * 2.3 * i - self.size * 0.2,
                text=i,
                anchor=tk.E,
                fill=self.fg_color
            )
            self.create_text(
                self.center_width + self.size * 9,
                self.center_height - self.size * 2.3 * i - self.size * 0.2,
                text=i,
                anchor=tk.W,
                fill=self.fg_color
            )

    def update_horizon(self):
        """更新地平线（暂未实现）"""
        pass

    def draw_g_force_indicator(self):
        """绘制G力指示器"""
        self.create_text(
            self.center_width,
            self.center_height + self.size * 22,
            text="%2.1f G" % (self.g_force),
            fill=self.fg_color,
            tags="g_num"
        )
        self.create_text(
            self.center_width,
            self.center_height + self.size * 20,
            text=G_WARNING_TEXT,
            fill="red",
            tags="g_warn"
        )

    def update_g_force_indicator(self):
        """更新G力指示器"""
        self.itemconfigure("g_num", text="%2.1f G" % (self.g_force))
        self.itemconfigure("g_warn", text=(G_WARNING_TEXT if self.g_force > G_WARNING_THRESHOLD else ""))
    
    def draw_freefall_time_indicator(self):
        """绘制自由落体时间指示器"""
        self.create_text(
            self.center_width - self.size * 27,
            self.center_height + self.size * 14,
            text=FREEFALL_TIME_TEXT + f"{max(self.ffl_secs, 0) // 60:02}:{max(self.ffl_secs, 0) % 60:02}",
            fill=self.fg_color,
            tags="ffl_time"
        )

    def update_freefall_time_indicator(self):
        """更新自由落体时间指示器"""
        self.itemconfigure("ffl_time", text=FREEFALL_TIME_TEXT + f"{max(self.ffl_secs, 0) // 60:02}:{max(self.ffl_secs, 0) % 60:02}")

    def update_values(self, speed=None, altitude=None, pitch=None, roll=None, g_force=None, ffl_secs=None):
        """更新所有仪表值"""
        self.alpha = 0.04  # 滤波权重
        
        if speed is not None:
            self.speed = self.speed * (1 - self.alpha) + speed * self.alpha
        if altitude is not None:
            self.altitude = max(altitude, 0)
        if pitch is not None:
            self.pitch = pitch
        if roll is not None:
            self.roll = roll
        if g_force is not None:
            self.g_force = g_force
        if ffl_secs is not None:
            self.ffl_secs = ffl_secs

        self.update_speedometer()
        self.update_altimeter()
        self.update_horizon()
        self.update_g_force_indicator()
        self.update_freefall_time_indicator()

class UpdateButton(tk.Button):
    def __init__(self, text, command):
        super().__init__(text=text, command=command)
        self.prev_alt = heights[0]

    def update(self, altitude):
        global time
        instrument.update_values((self.prev_alt - altitude) * 10, altitude, 3, 4, 5, 6)
        self.prev_alt = altitude
        time += 1
        self.after(100, self.update, float(heights[time])) # 刷新率100ms

if __name__ == "__main__":
    # 创建主窗口
    root = tk.Tk()
    # 设置全屏
    # root.attributes("-fullscreen", True)

    # 读取测试数据
    with open("test.txt", "r") as data:
        heights = data.readlines()

    heights = [height for height in heights if height != '\n']
    # 将heights转为浮点数组，heights采样率为0.1s
    heights = [float(height.split()[2][:-1]) for height in heights]
    alpha = 0.2
    filtered_heights = [heights[0]]  # Initialize with the first height

    for new_height in heights[1:]:
        current_height = filtered_heights[-1]
        filtered_height = (1 - alpha) * current_height + alpha * new_height
        filtered_heights.append(filtered_height)
    heights = filtered_heights

    # 创建仪表画布
    instrument = FlightInstrumentCanvas(master=root, size=SIZE, testing=False)
    instrument.configure(height=SCRN_HEIGHT, width=SCRN_WIDTH)
    instrument.grid_propagate(0)

    time = 0

    # 创建测试按钮
    test_button = tk.Button(
        text="随机更新",
        command=lambda: instrument.update_values(
            speed=random.randint(0, 1000),
            altitude=random.randint(0, 10000),
            pitch=random.randint(-90, 90),
            roll=random.randint(0, 0),
            g_force=random.randint(0, 100) / 10,
            ffl_secs=random.randint(0, 1200)
        )
    )
    log_button = UpdateButton(text="记录更新", command=lambda: log_button.update(heights[time]))
    test_button.grid(row=10)
    log_button.grid(row=11)

    bmx160 = BMX160()
    gps = GPS()
    ms5611 = MS5611()
    bh1750 = BH1750()
    # 启动4个线程，每个线程更新一个text widget
    threads = []
    entry_func_list = [bmx160.run, gps.run, ms5611.run, bh1750.run,]
    for i in range(4):
        thread = Thread(target=entry_func_list[i], args=(instrument.update_values,))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    root.mainloop()