import random
import tkinter as tk
import tkinter.ttk as ttk
import math

from threading import Thread, Event

# from sensors import Log, BH1750, BMX160, GPS, MS5611

# 常量定义
FONT = "Arial"
SIZE = 12.5
SCRN_HEIGHT = 1080
SCRN_WIDTH = 1920

SCRN_HEIGHT = 540
SCRN_WIDTH = 960

LINE_WIDTH = SIZE * 0.2
RATIO = SIZE * 0.352

SCRN_WIDTH_CENTER = SCRN_WIDTH / 2
SCRN_HEIGHT_CENTER = SCRN_HEIGHT / 2

BLACK_COLOR = "#000000"
GREEN_COLOR = "#00FF00"

G_WARNING_THRESHOLD = 4.0

SPEED_UNITS_TEXT = "km/h"
HEIGHT_UNITS_TEXT = "m"
G_WARNING_TEXT = "G-FORCE WARNING"
FREEFALL_TIME_TEXT = "FREEFALL TIME "  # 必须有后续的空格


class FlightInstrumentCanvas(tk.Canvas):
    def __init__(self, master, size=SIZE, testing=False):
        super().__init__(master, bg=BLACK_COLOR)
        
        # 初始化仪表参数
        self.vspeed = 0
        self.altitude = 0
        self.pitch = 0  # 范围 +90 ~ -90
        self.roll = 0  # 范围 +180 ~ -180, 向右倾斜为正
        self.heading = 0 # 范围 [0, 360)
        self.gspeed = 0
        self.g_force = 4.2
        self.ffl_secs = 100  # 必须大于0，小于0时显示0

        self.size = size
        self.center_width = SCRN_WIDTH_CENTER
        self.center_height = SCRN_HEIGHT_CENTER
        self.fg_color = GREEN_COLOR
        
        self.grid()

        # 绘制各个仪表
        self.draw_speedometer()
        self.draw_altimeter()
        self.draw_horizon()
        self.draw_heading_wheel()
        self.draw_gspeed_display()
        self.draw_g_force_indicator()
        # self.draw_freefall_time_indicator()

        # 更新仪表值
        self.update_values(self.vspeed, self.altitude, self.pitch, self.roll, self.gspeed, self.g_force, self.ffl_secs)

    def draw_minor_line(self, cur_val, cen_val, ratio, type=1):
        y_pos = self.center_height - (cur_val - cen_val) * ratio
        self.create_line(
            self.center_width - type * (self.size * 25.5),
            y_pos,
            self.center_width - type * (self.size * 25),
            y_pos,
            fill=self.fg_color,
            tags=("spd_line" if type == 1 else "alt_line"),
            width=LINE_WIDTH
        )
        self.tag_lower("spd_line", "speedometer")
        self.tag_lower("alt_line", "altimeter")

    def draw_number_line(self, cur_val, cen_val, ratio, type=1):
        """绘制数值线"""
        y_pos = self.center_height - (cur_val - cen_val) * ratio
        self.create_text(
            self.center_width - type * (self.size * 26.5),
            y_pos,
            text=int(cur_val),
            anchor=(tk.E if type == 1 else tk.W),
            fill=self.fg_color,
            tags=("spd_line" if type == 1 else "alt_line"),
            font=(FONT, int(self.size * 1.5)),
        )
        self.create_line(
            self.center_width - type * (self.size * 26),
            y_pos,
            self.center_width - type * (self.size * 25),
            y_pos,
            fill=self.fg_color,
            tags=("spd_line" if type == 1 else "alt_line"),
            width=LINE_WIDTH
        )
        self.tag_lower("spd_line", "speedometer")
        self.tag_lower("alt_line", "altimeter")

    def draw_speedometer(self):
        """绘制速度表"""
        base_size = self.size * 26

        arrow_center_width = self.center_width - self.size * 24
        arrow_center_height = self.center_height + self.size * 0

        self.create_rectangle(
            self.center_width - 30 * self.size,
            self.center_height - self.size * 13,
            self.center_width - 22 * self.size,
            self.center_height - self.size * 15, 
            fill=BLACK_COLOR,
            tags="speedometer"
        )
        self.create_rectangle(
            self.center_width - 30 * self.size,
            self.center_height + self.size * 19,
            self.center_width - 22 * self.size,
            self.center_height + self.size * 21, 
            fill=BLACK_COLOR,
            tags="speedometer"
        )
        self.create_text(
            self.center_width - self.size * 26.5,
            self.center_height - self.size * 14,
            text=SPEED_UNITS_TEXT,
            fill=self.fg_color, 
            font=(FONT, int(self.size * 1.5)), 
            tags="speedometer"
        )
        self.create_rectangle(
            arrow_center_width - 3,
            arrow_center_height + self.size * 1.5 + 3,
            arrow_center_width + self.size * 9.5 + 3,
            arrow_center_height - self.size * 1.5 - 3,
            fill=BLACK_COLOR
        )
        self.create_polygon(
            arrow_center_width,
            arrow_center_height,
            arrow_center_width + self.size * 1.5,
            arrow_center_height + self.size * 1.5,
            arrow_center_width + self.size * 9.5,
            arrow_center_height + self.size * 1.5,
            arrow_center_width + self.size * 9.5,
            arrow_center_height - self.size * 1.5,
            arrow_center_width + self.size * 1.5,
            arrow_center_height - self.size * 1.5,
            outline=self.fg_color,
            fill=''
        )
        self.create_text(
            self.center_width - self.size * 16,
            self.center_height,
            anchor=tk.E,
            text=self.vspeed,
            font=(FONT, int(-self.size * 3)),
            fill=BLACK_COLOR,
            tags="main_spd"
        )
        self.create_text(
            self.center_width - self.size * 16,
            self.center_height,
            text="0",
            font=(FONT, int(-self.size * 3)),
            fill=self.fg_color,
            tags="main_spd_0_t"
        )
        self.create_text(
            self.center_width - self.size * 16,
            self.center_height - self.size * 2.6,
            text="1",
            font=(FONT, int(-self.size * 3)),
            fill=self.fg_color,
            tags="main_spd_0_b"
        )
        self.create_text(
            self.center_width - self.size * 17.7,
            self.center_height,
            text="0",
            font=(FONT, int(-self.size * 3)),
            fill=self.fg_color,
            tags="main_spd_1_t"
        )
        self.create_text(
            self.center_width - self.size * 17.7,
            self.center_height - self.size * 2.6,
            text="1",
            font=(FONT, int(-self.size * 3)),
            fill=self.fg_color,
            tags="main_spd_1_b"
        )
        self.create_text(
            self.center_width - self.size * 19.4,
            self.center_height,
            text="0",
            font=(FONT, int(-self.size * 3)),
            fill=self.fg_color,
            tags="main_spd_2"
        )
        self.create_rectangle(
            arrow_center_width,
            arrow_center_height + self.size * 1.5 + LINE_WIDTH/2,
            arrow_center_width + self.size * 9.5,
            arrow_center_height + self.size * 4,
            fill=BLACK_COLOR,
        )
        self.create_rectangle(
            arrow_center_width,
            arrow_center_height - self.size * 1.5 - LINE_WIDTH/2,
            arrow_center_width + self.size * 9.5,
            arrow_center_height - self.size * 4,
            fill=BLACK_COLOR,
        )

    def update_speedometer(self):
        """更新速度表"""
        ratio = RATIO
        self.delete("spd_line")

        show_speed = (self.vspeed * 3.6) if SPEED_UNITS_TEXT == "km/h" else (self.speed)

        cur_spd = show_speed // 10 * 10
        self.draw_number_line(cur_spd, show_speed, ratio, 1)
        while cur_spd - show_speed >= -55:
            cur_spd -= 2
            if not (cur_spd % 10):
                self.draw_number_line(cur_spd, show_speed, ratio, 1)
            else:
                self.draw_minor_line(cur_spd, show_speed, ratio, 1)
                
        cur_spd = show_speed // 10 * 10
        self.draw_number_line(cur_spd, show_speed, ratio, 1)
        while cur_spd - show_speed <= 35:
            cur_spd += 2
            if not (cur_spd % 10):
                self.draw_number_line(cur_spd, show_speed, ratio, 1)
            else:
                self.draw_minor_line(cur_spd, show_speed, ratio, 1)
        
        self.itemconfigure("main_spd", text=int(show_speed))

        # print(show_speed)
        offset = show_speed - show_speed // 1
        self.coords("main_spd_0_t", self.center_width - self.size * 16, self.center_height - offset * 30)
        self.itemconfigure("main_spd_0_t", text=int(show_speed % 10 // 1))
        self.coords("main_spd_0_b", self.center_width - self.size * 16, self.center_height + self.size * 2.6 - offset * 30)
        self.itemconfigure("main_spd_0_b", text=int((show_speed+1) % 10 // 1))
        offset = show_speed - show_speed // 10 * 10
        self.coords("main_spd_1_t", self.center_width - self.size * 17.7, self.center_height - offset * 3)
        self.itemconfigure("main_spd_1_t", text=int(show_speed % 100 // 10))
        self.coords("main_spd_1_b", self.center_width - self.size * 17.7, self.center_height + self.size * 2.6 - offset * 3)
        self.itemconfigure("main_spd_1_b", text=int((show_speed+10) % 100 // 10))
        self.itemconfigure("main_spd_2", text=int(max(show_speed // 100, 0)))

    def draw_altimeter(self):
        """绘制高度表"""
        base_size = self.size * 26

        arrow_center_width = self.center_width + self.size * 24
        arrow_center_height = self.center_height + self.size * 0

        self.create_polygon(
            self.center_width + self.size * 14.5 - 3, 
            self.center_height - self.size * 1.5 - 3,
            self.center_width + self.size * 14.5 - 3, 
            self.center_height + self.size * 1.5 + 3,
            self.center_width + self.size * 24,
            self.center_height + self.size * 1.5 + 3,
            self.center_width + self.size * 24,
            self.center_height + self.size * 19,
            self.center_width + self.size * 32,
            self.center_height + self.size * 19,
            self.center_width + self.size * 32,
            self.center_height - self.size * 15,
            self.center_width + self.size * 24,
            self.center_height - self.size * 15,
            self.center_width + self.size * 24,
            self.center_height - self.size * 1.5 - 3,
            fill="black",
            tags="alt_base"
        )
        self.create_rectangle(
            self.center_width + 34 * self.size,
            self.center_height - self.size * 13,
            self.center_width + 22 * self.size,
            self.center_height - self.size * 15, 
            fill=BLACK_COLOR,
            tags="altimeter"
        )
        self.create_rectangle(
            self.center_width + 34 * self.size,
            self.center_height + self.size * 19,
            self.center_width + 22 * self.size,
            self.center_height + self.size * 21, 
            fill=BLACK_COLOR,
            tags="altimeter"
        )
        self.create_text(
            self.center_width + self.size * 26.55,
            self.center_height - self.size * 14,
            text=HEIGHT_UNITS_TEXT,
            fill=self.fg_color,
            font=(FONT, int(self.size * 1.5)), 
            tags="altimeter"
        )
        self.create_polygon(
            arrow_center_width,
            arrow_center_height,
            arrow_center_width - self.size * 1.5,
            arrow_center_height + self.size * 1.5,
            arrow_center_width - self.size * 9.5,
            arrow_center_height + self.size * 1.5,
            arrow_center_width - self.size * 9.5,
            arrow_center_height - self.size * 1.5,
            arrow_center_width - self.size * 1.5,
            arrow_center_height - self.size * 1.5,
            outline=self.fg_color
        )
        self.create_text(
            self.center_width + self.size * 22,
            self.center_height,
            text=self.altitude,
            anchor=tk.E,
            font=(FONT, int(-self.size * 3)),
            fill=BLACK_COLOR,
            tags="main_alt"
        )
        self.create_text(
            self.center_width + self.size * 21.5,
            self.center_height,
            text="0",
            font=(FONT, int(-self.size * 3)),
            fill=self.fg_color,
            tags="main_alt_0_t"
        )
        self.create_text(
            self.center_width + self.size * 21.5,
            self.center_height - self.size * 2.6,
            text="1",
            font=(FONT, int(-self.size * 3)),
            fill=self.fg_color,
            tags="main_alt_0_b"
        )
        self.create_text(
            self.center_width + self.size * 19.8,
            self.center_height,
            text="0",
            font=(FONT, int(-self.size * 3)),
            fill=self.fg_color,
            tags="main_alt_1_t"
        )
        self.create_text(
            self.center_width + self.size * 19.8,
            self.center_height - self.size * 2.6,
            text="1",
            font=(FONT, int(-self.size * 3)),
            fill=self.fg_color,
            tags="main_alt_1_b"
        )
        self.create_text(
            self.center_width + self.size * 18.1,
            self.center_height,
            text="0",
            font=(FONT, int(-self.size * 3)),
            fill=self.fg_color,
            tags="main_alt_2"
        )
        self.create_text(
            self.center_width + self.size * 16.4,
            self.center_height,
            text="0",
            font=(FONT, int(-self.size * 3)),
            fill=self.fg_color,
            tags="main_alt_3"
        )
        self.create_rectangle(
            arrow_center_width,
            arrow_center_height + self.size * 1.5 + LINE_WIDTH/2,
            arrow_center_width - self.size * 9.5,
            arrow_center_height + self.size * 4,
            fill=BLACK_COLOR,
        )
        self.create_rectangle(
            arrow_center_width,
            arrow_center_height - self.size * 1.5 - LINE_WIDTH/2,
            arrow_center_width - self.size * 9.5,
            arrow_center_height - self.size * 4,
            fill=BLACK_COLOR,
        )

    def update_altimeter(self):
        """更新高度表"""
        ratio = RATIO / 50
        self.delete("alt_line")

        show_altitude = self.altitude

        cur_alt = show_altitude // 500 * 500
        self.draw_number_line(cur_alt, show_altitude, ratio, -1)
        while cur_alt - show_altitude >= -2750:
            cur_alt -= 100
            if not (cur_alt % 500):
                self.draw_number_line(cur_alt, show_altitude, ratio, -1)
            else:
                self.draw_minor_line(cur_alt, show_altitude, ratio, -1)

        cur_alt = show_altitude // 500 * 500
        self.draw_number_line(cur_alt, show_altitude, ratio, -1)
        while cur_alt - show_altitude <= 1750:
            cur_alt += 100
            if not (cur_alt % 500):
                self.draw_number_line(cur_alt, show_altitude, ratio, -1)
            else:
                self.draw_minor_line(cur_alt, show_altitude, ratio, -1)

        self.itemconfigure("main_alt", text=int(show_altitude))

        # Calculate the rolling effect for the last two digits
        offset = show_altitude % 1
        self.coords("main_alt_0_t", self.center_width + self.size * 21.5, self.center_height + offset * 30)
        self.itemconfigure("main_alt_0_t", text=int(show_altitude % 10))
        self.coords("main_alt_0_b", self.center_width + self.size * 21.5, self.center_height - self.size * 2.6 + offset * 30)
        self.itemconfigure("main_alt_0_b", text=int((show_altitude + 1) % 10))

        offset = show_altitude - show_altitude // 10 * 10
        self.coords("main_alt_1_t", self.center_width + self.size * 19.8, self.center_height + offset * 3)
        self.itemconfigure("main_alt_1_t", text=int((show_altitude // 10) % 10))
        self.coords("main_alt_1_b", self.center_width + self.size * 19.8, self.center_height - self.size * 2.6 + offset * 3)
        self.itemconfigure("main_alt_1_b", text=int((show_altitude // 10 + 1) % 10))
        self.itemconfigure("main_alt_2", text=int((show_altitude // 100) % 10))
        self.itemconfigure("main_alt_3", text=int((show_altitude // 1000) % 10))
    
    def draw_horizon(self): #先留一会
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

    def draw_horizon(self):
        """绘制地平线"""
        # Draw the initial horizon line extended beyond the screen width
        self.horizon_line = self.create_line(
            -SCRN_WIDTH,
            self.center_height,
            2 * SCRN_WIDTH,
            self.center_height,
            fill=self.fg_color,
            width=LINE_WIDTH,
            tags="horizon"
        )

    def update_horizon(self):
        """更新地平线"""
        # Calculate the new position and rotation based on pitch and roll
        pitch_offset = self.pitch * SCRN_HEIGHT / 60
        roll_angle = math.radians(self.roll)

        # Calculate the new coordinates for the horizon line
        x1 = self.center_width - 2 * SCRN_WIDTH * math.cos(roll_angle)
        y1 = self.center_height - 2 * SCRN_WIDTH * math.sin(roll_angle) - pitch_offset
        x2 = self.center_width + 2 * SCRN_WIDTH * math.cos(roll_angle)
        y2 = self.center_height + 2 * SCRN_WIDTH * math.sin(roll_angle) - pitch_offset

        # Move and rotate the horizon line based on pitch and roll
        self.coords(self.horizon_line, x1, y1, x2, y2)

        self.delete("hdg_line")
        show_hdg = self.heading
        cur_hdg = (show_hdg // 10 * 10 - 50)
        for i in range(11):
            x = (x1 + x2) / 2 + (cur_hdg - show_hdg) * SCRN_WIDTH / 60 * math.cos(roll_angle)
            y = (y1 + y2) / 2 + (cur_hdg - show_hdg) * SCRN_WIDTH / 60 * math.sin(roll_angle)

            self.create_line(x, y, x + 15 * math.sin(roll_angle), y - 15 * math.cos(roll_angle), width=LINE_WIDTH, fill=GREEN_COLOR, tags=("hdg_line", "horizon"))
            
            self.create_text(x + 20 * math.sin(roll_angle), y - 20 * math.cos(roll_angle) - 10, text=cur_hdg%360//10, font=(FONT, 18), fill=GREEN_COLOR, tags=("hdg_line", "horizon"))

            cur_hdg += 10
            # cur_hdg %= 360
        
        self.tag_lower("horizon", "alt_base")

    def draw_heading_wheel(self):
        pass

    def update_heading_wheel(self):
        self.delete("hdg_whl")

        wheel_center = self.center_height + self.size * 25

        show_hdg = self.heading
        cur_hdg = (show_hdg // 10 * 10 - 90)

        for i in range(19):
            if cur_hdg % 30:
                self.create_line(
                    self.center_width + math.sin(math.radians(cur_hdg - show_hdg)) * 11 * self.size,
                    wheel_center - math.cos(math.radians(cur_hdg - show_hdg)) * 11 * self.size,
                    self.center_width + math.sin(math.radians(cur_hdg - show_hdg)) * 12 * self.size,
                    wheel_center - math.cos(math.radians(cur_hdg - show_hdg)) * 12 * self.size,
                    width=LINE_WIDTH,
                    fill=self.fg_color,
                    tags="hdg_whl"
                )
            else:
                self.create_line(
                    self.center_width + math.sin(math.radians(cur_hdg - show_hdg)) * 10 * self.size,
                    wheel_center - math.cos(math.radians(cur_hdg - show_hdg)) * 10 * self.size,
                    self.center_width + math.sin(math.radians(cur_hdg - show_hdg)) * 12 * self.size,
                    wheel_center - math.cos(math.radians(cur_hdg - show_hdg)) * 12 * self.size,
                    width=LINE_WIDTH,
                    fill=self.fg_color,
                    tags="hdg_whl"
                )
                self.create_text(
                    self.center_width + math.sin(math.radians(cur_hdg - show_hdg)) * 13.2 * self.size,
                    wheel_center - math.cos(math.radians(cur_hdg - show_hdg)) * 13.2 * self.size,
                    text=cur_hdg % 360 // 10,
                    font=(FONT, int(-self.size * 2)),
                    angle=show_hdg - cur_hdg,
                    fill=self.fg_color,
                    tags="hdg_whl"
                )
                if not(cur_hdg % 90):
                    self.create_text(
                        self.center_width + math.sin(math.radians(cur_hdg - show_hdg)) * 9 * self.size,
                        wheel_center - math.cos(math.radians(cur_hdg - show_hdg)) * 9 * self.size,
                        text=('N','E','S','W')[cur_hdg%360//90],
                        font=(FONT, int(-self.size * 2)),
                        angle=show_hdg - cur_hdg,
                        fill=self.fg_color,
                        tags="hdg_whl"
                    )
            cur_hdg += 10

    def draw_gspeed_display(self):
        self.create_text(
            self.center_width,
            self.center_height + self.size * 20,
            text=000,
            fill=self.fg_color,
            font=(FONT, int(-SIZE * 2)),
            tags="gspeed"
        )
    
    def update_gspeed_display(self):
        self.itemconfigure("gspeed", text=f"{self.gspeed:03}")

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
        self.itemconfigure("g_warn", text="") #临时
    
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

    def update_values(self, vspeed=None, altitude=None, pitch=None, roll=None, gspeed=None, g_force=None, ffl_secs=None, heading=None):
        """更新所有仪表值"""
        self.alpha = 0.04  # 滤波权重
        
        if vspeed is not None:
            self.vspeed = self.vspeed * (1 - self.alpha) + vspeed * self.alpha
        if altitude is not None:
            self.altitude = max(altitude, 0)
        if pitch is not None:
            self.pitch = pitch
        if roll is not None:
            self.roll = roll
        if gspeed is not None:
            self.gspeed = gspeed
        if g_force is not None:
            self.g_force = g_force
        if ffl_secs is not None:
            self.ffl_secs = ffl_secs
        if heading is not None:
            self.heading = heading

        self.update_speedometer()
        self.update_altimeter()
        self.update_horizon()
        self.update_heading_wheel()
        self.update_gspeed_display()
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
            vspeed=random.randint(0, 1000),
            altitude=random.randint(0, 1000000)/100,
            pitch=random.randint(-30, 30),
            roll=random.randint(-90, 90),
            gspeed=random.randint(0,999),
            g_force=random.randint(0, 100) / 10,
            ffl_secs=random.randint(0, 1200),
            heading=random.randint(0,359)
        )
    )
    log_button = UpdateButton(text="记录更新", command=lambda: log_button.update(heights[time]))
    test_button.grid(row=10)
    log_button.grid(row=11)
    instrument.create_window(30, 20, window=test_button)
    instrument.create_window(30, 50, window=log_button)

    # bmx160 = BMX160()
    # gps = GPS()
    # ms5611 = MS5611()
    # bh1750 = BH1750()
    # # 启动4个线程，每个线程更新一个text widget
    # threads = []
    # entry_func_list = [bmx160.run, gps.run, ms5611.run, bh1750.run,]
    # for i in range(4):
    #     thread = Thread(target=entry_func_list[i], args=(instrument.update_values,))
    #     thread.daemon = True
    #     thread.start()
    #     threads.append(thread)

    root.mainloop()