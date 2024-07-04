import sys
if sys.version_info[0] == 2:
    import Tkinter as tk
    import tkFileDialog as tkfd
if sys.version_info[0] == 3:
    import tkinter as tk
    import tkinter.filedialog as tkfd
    import tkinter.ttk as ttk
# from math import sin, cos, tan, radians

import random

FONT = "Times New Roman"

SIZE = 10
SCRN_HEIGHT = 1080
SCRN_HEIGHT = 540 # testing, comment out for production
SCRN_WIDTH = 1920
SCRN_WIDTH = 960 # testing, comment out for production

SCRN_WIDTH_CENTER = SCRN_WIDTH/2
SCRN_HEIGHT_CENTER = SCRN_HEIGHT/2

G_WARNING_THRESHOLD = 4.0

SPEED_UNITS_TEXT = "m/s"
HEIGHT_UNITS_TEXT = "m"
G_WARNING_TEXT = "G-FORCE WARNING"
FREEFALL_TIME_TEXT = "FREEFALL TIME " # must have following space

root = tk.Tk()

class gui_1(tk.Canvas):
    def __init__(self, master, size=SIZE, testing=False):
        tk.Canvas.__init__(self, master, bg="light gray" if testing else "black")
        
        self.speed = 0
        self.altitude = 0
        self.pitch = 0 # limit +90 ~ -90
        self.roll = 0 # limit +180 ~ -180, bank to right is positive
        self.g_force = 4.2
        self.ffl_secs = 100 # should be greater than 0, less than 0 force display 0

        self.size = size
        self.center_width=SCRN_WIDTH_CENTER
        self.center_height=SCRN_HEIGHT_CENTER
        self.fg_color = "black" if testing else "green"
        
        self.grid()

        # self.create_text(self.center_width, self.center_height, text="CENTER")
        self.draw_speedometer(self.speed)
        self.draw_altimeter(self.altitude)
        self.draw_horizon()
        self.draw_g_force_indic()
        self.draw_ffl_time_indic()

        self.update_vals(self.speed, self.altitude, self.pitch, self.roll, self.g_force, self.ffl_secs)

    def draw_numline(self, cur_val, cen_val, ratio, type=1):
        self.create_text(self.center_width-type*(self.size*23.5), self.center_height-(cur_val-cen_val)*ratio, text=int(cur_val), anchor=(tk.E if type==1 else tk.W), fill=self.fg_color, tags=("spd_line" if type==1 else "alt_line"))
        self.create_line(self.center_width-type*(self.size*23), self.center_height-(cur_val-cen_val)*ratio, self.center_width-type*(self.size*22), self.center_height-(cur_val-cen_val)*ratio, fill=self.fg_color, tags=("spd_line" if type==1 else "alt_line"))

    def draw_speedometer(self, speed=0):
        base_size = self.size*26

        self.create_line(self.center_width-(base_size), self.center_height-(self.size*11.5), self.center_width-(22*self.size),self.center_height-(self.size*11.5), self.center_width-(22*self.size),self.center_height+(self.size*11.5), self.center_width-(base_size),self.center_height+(self.size*11.5), fill=self.fg_color)
        self.create_text(self.center_width-(self.size*24),self.center_height-(self.size*13), text="m/s", fill=self.fg_color)
        self.create_polygon(self.center_width-(self.size*21), self.center_height, self.center_width-(self.size*20), self.center_height+(self.size/1.732),self.center_width-(self.size*20), self.center_height-(self.size/1.732), fill=self.fg_color)
        self.create_text(self.center_width-(self.size*16.5), self.center_height, text=speed, font=(FONT, self.size*2), fill=self.fg_color, tags="main_spd")

    def update_speedometer(self):
        ratio = 3.5

        self.delete("spd_line")

        cur_spd = self.speed//10*10
        self.draw_numline(cur_spd, self.speed, ratio, 1)
        while cur_spd-self.speed >= -20:
            cur_spd -= 10
            self.draw_numline(cur_spd, self.speed, ratio, 1)
        cur_spd = self.speed//10*10 + 10
        self.draw_numline(cur_spd, self.speed, ratio, 1)
        while cur_spd-self.speed <= 20:
            cur_spd += 10
            self.draw_numline(cur_spd, self.speed, ratio, 1)
        
        self.itemconfigure("main_spd", text=int(self.speed))

    def draw_altimeter(self, altitude=0):
        base_size = self.size*26

        self.create_line(self.center_width+(base_size), self.center_height-(self.size*11.5), self.center_width+(22*self.size),self.center_height-(self.size*11.5), self.center_width+(22*self.size),self.center_height+(self.size*11.5), self.center_width+(base_size),self.center_height+(self.size*11.5), fill=self.fg_color)
        self.create_text(self.center_width+(self.size*24),self.center_height-(self.size*13), text="m", fill=self.fg_color)
        self.create_polygon(self.center_width+(self.size*21), self.center_height, self.center_width+(self.size*20), self.center_height+(self.size/1.732),self.center_width+(self.size*20), self.center_height-(self.size/1.732), fill=self.fg_color)
        self.create_text(self.center_width+(self.size*16.5), self.center_height, text=altitude, font=(FONT, self.size*2), fill=self.fg_color, tags="main_alt")

    def update_altimeter(self):
        ratio = 3.5/50

        self.delete("alt_line")

        cur_alt = self.altitude//500*500
        self.draw_numline(cur_alt, self.altitude, ratio, -1)
        while cur_alt-self.altitude >= -1000:
            cur_alt -= 500
            self.draw_numline(cur_alt, self.altitude, ratio, -1)
        cur_alt = self.altitude//500*500 + 500
        self.draw_numline(cur_alt, self.altitude, ratio, -1)
        while cur_alt-self.altitude <= 1000:
            cur_alt += 500
            self.draw_numline(cur_alt, self.altitude, ratio, -1)
        
        self.itemconfigure("main_alt", text=int(self.altitude))
    
    def draw_horizon(self): # temporary, will be depreciated when update_horizon() works
        self.create_line(self.center_width-(self.size*3), self.center_height, self.center_width-(self.size*13), self.center_height, fill=self.fg_color)
        self.create_line(self.center_width+(self.size*3), self.center_height, self.center_width+(self.size*13), self.center_height, fill=self.fg_color)
        self.create_line(self.center_width-(self.size*2), self.center_height+(self.size*1.5), self.center_width-(self.size*1), self.center_height+(self.size*1.5), self.center_width-(self.size*0.5), self.center_height+(self.size*2.5), self.center_width, self.center_height+(self.size*1.5), self.center_width+(self.size*0.5), self.center_height+(self.size*2.5), self.center_width+(self.size*1), self.center_height+(self.size*1.5), self.center_width+(self.size*2), self.center_height+(self.size*1.5), fill=self.fg_color)
        for i in (5, -5):
            self.create_line(self.center_width-(self.size*3), self.center_height-(self.size*2.3*i), self.center_width-(self.size*8), self.center_height-(self.size*2.3*i), dash=1, fill=self.fg_color)
            self.create_line(self.center_width+(self.size*3), self.center_height-(self.size*2.3*i), self.center_width+(self.size*8), self.center_height-(self.size*2.3*i), dash=1, fill=self.fg_color)
            self.create_line(self.center_width-(self.size*8), self.center_height-(self.size*2.3*i), self.center_width-(self.size*8), self.center_height-(self.size*2.3*i)-self.size*0.6, dash=1, fill=self.fg_color)
            self.create_line(self.center_width+(self.size*8), self.center_height-(self.size*2.3*i), self.center_width+(self.size*8), self.center_height-(self.size*2.3*i)-self.size*0.6, dash=1, fill=self.fg_color)
            self.create_text(self.center_width-(self.size*9), self.center_height-(self.size*2.3*i)-self.size*0.2, text=i, anchor=tk.E, fill=self.fg_color)
            self.create_text(self.center_width+(self.size*9), self.center_height-(self.size*2.3*i)-self.size*0.2, text=i, anchor=tk.W, fill=self.fg_color)

    def update_horizon(self):
        pass

    def draw_g_force_indic(self):
        self.create_text(self.center_width, self.center_height+(self.size*22), text="%2.1f G"%(self.g_force), fill=self.fg_color, tags="g_num")
        self.create_text(self.center_width, self.center_height+(self.size*20), text=G_WARNING_TEXT, fill="red", tags="g_warn")

    def update_g_force_indic(self):
        self.itemconfigure("g_num", text="%2.1f G"%(self.g_force))
        self.itemconfigure("g_warn", text=(G_WARNING_TEXT if self.g_force > G_WARNING_THRESHOLD else ""))
    
    def draw_ffl_time_indic(self):
        self.create_text(self.center_width-self.size*27, self.center_height+self.size*14, text=FREEFALL_TIME_TEXT + f"{max(self.ffl_secs, 0)//60:02}:{max(self.ffl_secs, 0)%60:02}", fill=self.fg_color, tags="ffl_time")

    def update_ffl_time_indic(self):
        self.itemconfigure("ffl_time", text=FREEFALL_TIME_TEXT + f"{max(self.ffl_secs, 0)//60:02}:{max(self.ffl_secs, 0)%60:02}")

    def update_vals(self, speed, altitude, pitch, roll, g_force, ffl_secs):
        self.alpha = 0.01 # filtering weight

        self.speed = self.speed*(1-self.alpha) + speed*self.alpha
        self.altitude = max(altitude, 0)
        self.pitch = pitch
        self.roll = roll
        self.g_force = g_force
        self.ffl_secs = ffl_secs
        
        self.update_speedometer()
        self.update_altimeter()
        self.update_horizon()
        self.update_g_force_indic()
        self.update_ffl_time_indic()

class test_but_one(tk.Button):
    def __init__(self, text, command):
        tk.Button.__init__(self, text=text, command=command)
        self.prev_alt = 0

    def update_(self, altitude):
        global time
        one.update_vals((self.prev_alt - altitude)*10,altitude,3,4,5,6)
        self.prev_alt = altitude
        time += 1
        self.after(100, self.update_, float(heights[time].split()[2][:-1]))

if __name__ == "__main__":
    
    data = open("test.txt", "r")
    heights = data.readlines()

    while True:
        try:
            heights.remove('\n')
        except:
            break

    # root.configure(height=1080, width=1920)
    one = gui_1(master=root, size=SIZE, testing=True)
    one.configure(height=SCRN_HEIGHT, width=SCRN_WIDTH)
    one.grid_propagate(0)

    time = 0

    test_but = tk.Button(text="Random", command=lambda: one.update_vals(speed=random.randint(0, 1000), altitude=random.randint(0,10000), pitch=random.randint(-90, 90), roll=random.randint(0,0), g_force=random.randint(0,100)/10, ffl_secs=random.randint(0,1200)))
    test_but_1 = test_but_one(text="Log", command=lambda: test_but_1.update_(float(heights[time].split()[2][:-1])))
    test_but.grid(row=10)
    test_but_1.grid(row=11)

    root.mainloop()