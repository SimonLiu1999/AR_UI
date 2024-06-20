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
SCRN_HEIGHT = 540
SCRN_WIDTH = 1920
SCRN_WIDTH = 960

SCRN_WIDTH_CENTER = SCRN_WIDTH/2
SCRN_HEIGHT_CENTER = SCRN_HEIGHT/2

G_WARNING_THRESHOLD = 4.0

G_WARNING_TEXT = "G-FORCE WARNING"
FREEFALL_TIME_TEXT = "FREEFALL TIME " # must have following space

root = tk.Tk()

class gui_1(tk.Canvas):
    def __init__(self, master):
        tk.Canvas.__init__(self, master)
        
        self.speed = 0
        self.altitude = 3500
        self.pitch = 0 # limit +90 ~ -90
        self.roll = 0 # limit +180 ~ -180, bank to right is positive
        self.g_force = 4.2
        self.ffl_secs = 100
        
        self.spd_list = []
        
        self.grid()

        # self.create_text(SCRN_WIDTH_CENTER, SCRN_HEIGHT_CENTER, text="CENTER")
        self.draw_speedometer(self.speed)
        self.draw_altimeter(self.altitude)
        self.draw_horizon()
        self.draw_g_force_indic()
        self.draw_ffl_time_indic()

        self.update_vals(self.speed, self.altitude, self.pitch, self.roll, self.g_force, self.ffl_secs)

    def draw_numline(self, cur_val, cen_val, ratio, type=1):
        self.create_text(SCRN_WIDTH_CENTER-type*(SIZE*23.5), SCRN_HEIGHT_CENTER-(cur_val-cen_val)*ratio, text=cur_val, anchor=(tk.E if type==1 else tk.W), tags=("spd_line" if type==1 else "alt_line"))
        self.create_line(SCRN_WIDTH_CENTER-type*(SIZE*23), SCRN_HEIGHT_CENTER-(cur_val-cen_val)*ratio, SCRN_WIDTH_CENTER-type*(SIZE*22), SCRN_HEIGHT_CENTER-(cur_val-cen_val)*ratio, tags=("spd_line" if type==1 else "alt_line"))

    def draw_speedometer(self, speed=0):
        base_size = SIZE*26

        self.create_line(SCRN_WIDTH_CENTER-(base_size), SCRN_HEIGHT_CENTER-(SIZE*11.5), SCRN_WIDTH_CENTER-(22*SIZE),SCRN_HEIGHT_CENTER-(SIZE*11.5), SCRN_WIDTH_CENTER-(22*SIZE),SCRN_HEIGHT_CENTER+(SIZE*11.5), SCRN_WIDTH_CENTER-(base_size),SCRN_HEIGHT_CENTER+(SIZE*11.5))
        self.create_text(SCRN_WIDTH_CENTER-(SIZE*24),SCRN_HEIGHT_CENTER-(SIZE*13), text="km/h")
        self.create_polygon(SCRN_WIDTH_CENTER-(SIZE*21), SCRN_HEIGHT_CENTER, SCRN_WIDTH_CENTER-(SIZE*20), SCRN_HEIGHT_CENTER+(SIZE/1.732),SCRN_WIDTH_CENTER-(SIZE*20), SCRN_HEIGHT_CENTER-(SIZE/1.732), fill="green")
        self.create_text(SCRN_WIDTH_CENTER-(SIZE*16.5), SCRN_HEIGHT_CENTER, text=speed, font=(FONT, SIZE*2), tags="main_spd")

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
        
        self.itemconfigure("main_spd", text=self.speed)

    def draw_altimeter(self, altitude=0):
        base_size = SIZE*26

        self.create_line(SCRN_WIDTH_CENTER+(base_size), SCRN_HEIGHT_CENTER-(SIZE*11.5), SCRN_WIDTH_CENTER+(22*SIZE),SCRN_HEIGHT_CENTER-(SIZE*11.5), SCRN_WIDTH_CENTER+(22*SIZE),SCRN_HEIGHT_CENTER+(SIZE*11.5), SCRN_WIDTH_CENTER+(base_size),SCRN_HEIGHT_CENTER+(SIZE*11.5))
        self.create_text(SCRN_WIDTH_CENTER+(SIZE*24),SCRN_HEIGHT_CENTER-(SIZE*13), text="ft")
        self.create_polygon(SCRN_WIDTH_CENTER+(SIZE*21), SCRN_HEIGHT_CENTER, SCRN_WIDTH_CENTER+(SIZE*20), SCRN_HEIGHT_CENTER+(SIZE/1.732),SCRN_WIDTH_CENTER+(SIZE*20), SCRN_HEIGHT_CENTER-(SIZE/1.732), fill="green")
        self.create_text(SCRN_WIDTH_CENTER+(SIZE*16.5), SCRN_HEIGHT_CENTER, text=altitude, font=(FONT, SIZE*2), tags="main_alt")

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
        
        self.itemconfigure("main_alt", text=self.altitude)
    
    def draw_horizon(self): # temporary, will be depreciated when update_horizon() works
        self.create_line(SCRN_WIDTH_CENTER-(SIZE*3), SCRN_HEIGHT_CENTER, SCRN_WIDTH_CENTER-(SIZE*13), SCRN_HEIGHT_CENTER)
        self.create_line(SCRN_WIDTH_CENTER+(SIZE*3), SCRN_HEIGHT_CENTER, SCRN_WIDTH_CENTER+(SIZE*13), SCRN_HEIGHT_CENTER)
        self.create_line(SCRN_WIDTH_CENTER-(SIZE*2), SCRN_HEIGHT_CENTER+(SIZE*1.5), SCRN_WIDTH_CENTER-(SIZE*1), SCRN_HEIGHT_CENTER+(SIZE*1.5), SCRN_WIDTH_CENTER-(SIZE*0.5), SCRN_HEIGHT_CENTER+(SIZE*2.5), SCRN_WIDTH_CENTER, SCRN_HEIGHT_CENTER+(SIZE*1.5), SCRN_WIDTH_CENTER+(SIZE*0.5), SCRN_HEIGHT_CENTER+(SIZE*2.5), SCRN_WIDTH_CENTER+(SIZE*1), SCRN_HEIGHT_CENTER+(SIZE*1.5), SCRN_WIDTH_CENTER+(SIZE*2), SCRN_HEIGHT_CENTER+(SIZE*1.5))
        for i in (5, -5):
            self.create_line(SCRN_WIDTH_CENTER-(SIZE*3), SCRN_HEIGHT_CENTER-(SIZE*2.3*i), SCRN_WIDTH_CENTER-(SIZE*8), SCRN_HEIGHT_CENTER-(SIZE*2.3*i), dash=1)
            self.create_line(SCRN_WIDTH_CENTER+(SIZE*3), SCRN_HEIGHT_CENTER-(SIZE*2.3*i), SCRN_WIDTH_CENTER+(SIZE*8), SCRN_HEIGHT_CENTER-(SIZE*2.3*i), dash=1)
            self.create_line(SCRN_WIDTH_CENTER-(SIZE*8), SCRN_HEIGHT_CENTER-(SIZE*2.3*i), SCRN_WIDTH_CENTER-(SIZE*8), SCRN_HEIGHT_CENTER-(SIZE*2.3*i)-SIZE*0.6, dash=1)
            self.create_line(SCRN_WIDTH_CENTER+(SIZE*8), SCRN_HEIGHT_CENTER-(SIZE*2.3*i), SCRN_WIDTH_CENTER+(SIZE*8), SCRN_HEIGHT_CENTER-(SIZE*2.3*i)-SIZE*0.6, dash=1)
            self.create_text(SCRN_WIDTH_CENTER-(SIZE*9), SCRN_HEIGHT_CENTER-(SIZE*2.3*i)-SIZE*0.2, text=i, anchor=tk.E)
            self.create_text(SCRN_WIDTH_CENTER+(SIZE*9), SCRN_HEIGHT_CENTER-(SIZE*2.3*i)-SIZE*0.2, text=i, anchor=tk.W)

    def update_horizon(self):
        pass

    def draw_g_force_indic(self):
        self.create_text(SCRN_WIDTH_CENTER, SCRN_HEIGHT_CENTER+(SIZE*22), text="%2.1f G"%(self.g_force), tags="g_num")
        self.create_text(SCRN_WIDTH_CENTER, SCRN_HEIGHT_CENTER+(SIZE*20), text=G_WARNING_TEXT, fill="red", tags="g_warn")

    def update_g_force_indic(self):
        self.itemconfigure("g_num", text="%2.1f G"%(self.g_force))
        self.itemconfigure("g_warn", text=(G_WARNING_TEXT if self.g_force > G_WARNING_THRESHOLD else ""))
    
    def draw_ffl_time_indic(self):
        self.create_text(SCRN_WIDTH_CENTER-SIZE*27, SCRN_HEIGHT_CENTER+SIZE*14, text=FREEFALL_TIME_TEXT + f"{self.ffl_secs//60:02}:{self.ffl_secs%60:02}", tags="ffl_time")

    def update_ffl_time_indic(self):
        self.itemconfigure("ffl_time", text=FREEFALL_TIME_TEXT + f"{self.ffl_secs//60:02}:{self.ffl_secs%60:02}")

    def update_vals(self, speed, altitude, pitch, roll, g_force, ffl_secs):
        self.speed = speed
        self.altitude = altitude
        self.pitch = pitch
        self.roll = roll
        self.g_force = g_force
        self.ffl_secs = ffl_secs
        
        self.update_speedometer()
        self.update_altimeter()
        self.update_horizon()
        self.update_g_force_indic()
        self.update_ffl_time_indic()
        

if __name__ == "__main__":
    # root.configure(height=1080, width=1920)
    one = gui_1(master=root)
    one.configure(height=SCRN_HEIGHT, width=SCRN_WIDTH)
    one.grid_propagate(0)


    test_but = tk.Button(text="Random", command=lambda: one.update_vals(speed=random.randint(0, 1000), altitude=random.randint(0,10000), pitch=random.randint(-90, 90), g_force=random.randint(0,100)/10, roll=random.randint(0,0), ffl_secs=random.randint(0,1200)))
    test_but.grid(row=10)

    root.mainloop()