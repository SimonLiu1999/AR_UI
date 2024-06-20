import sys
if sys.version_info[0] == 2:
    import Tkinter as tk
    import tkFileDialog as tkfd
if sys.version_info[0] == 3:
    import tkinter as tk
    import tkinter.filedialog as tkfd
    import tkinter.ttk as ttk
from math import sin, cos, tan, radians, pi

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

class gui_2(tk.Canvas):
    def __init__(self, master):
        tk.Canvas.__init__(self, master)

        self.altitude = 1000
        self.heading = 180 # limit 0 ~ 360
        self.center_width=SCRN_WIDTH_CENTER
        self.center_height=SCRN_HEIGHT_CENTER

        self.grid()

        self.draw_height_disp()
        
        self.update_disp(self.altitude)
    
    def draw_height_disp(self):
        self.create_line(self.center_width+SIZE*1, self.center_height, self.center_width-SIZE*1, self.center_height)
        self.create_line(self.center_width, self.center_height+SIZE*1, self.center_width, self.center_height-SIZE*1)
        self.create_text(self.center_width-SIZE*1, self.center_height+SIZE*13, text="00.0", font=(FONT, SIZE*3), tags="alt_l")
        self.create_text(self.center_width+SIZE*3.8, self.center_height+SIZE*13.8, text="00", font=(FONT, int(SIZE*1.5)), tags="alt_s")        
        for tick in range(0,12):
            ang = tick/6 * pi
            ang_2 = (tick+0.5)/6*pi
            self.create_line(self.center_width+sin(ang)*SIZE*20, self.center_height-cos(ang)*SIZE*20, self.center_width+sin(ang)*SIZE*18, self.center_height-cos(ang)*SIZE*18)
            self.create_line(self.center_width+sin(ang_2)*SIZE*20, self.center_height-cos(ang_2)*SIZE*20, self.center_width+sin(ang_2)*SIZE*19, self.center_height-cos(ang_2)*SIZE*19)
            self.create_text(self.center_width+sin(ang)*SIZE*22, self.center_height-cos(ang)*SIZE*22, text=tick, font=(FONT, SIZE*2))
        
    def update_height_disp(self):
        self.itemconfigure("alt_l", text=f"{self.altitude/1000:04.1f}")
        self.itemconfigure("alt_s", text=f"{self.altitude%100:02}")

        self.delete("triangle")
        ang = self.altitude/6000 * pi
        self.create_polygon(self.center_width+sin(ang)*SIZE*17, self.center_height-cos(ang)*SIZE*17,
                            self.center_width+sin(ang)*SIZE*17-sin(ang+pi/6)*SIZE*3, self.center_height-cos(ang)*SIZE*17-cos(ang+pi+pi/6)*SIZE*3, 
                            self.center_width+sin(ang)*SIZE*17-sin(ang-pi/6)*SIZE*3, self.center_height-cos(ang)*SIZE*17-cos(ang+pi-pi/6)*SIZE*3, 
                            fill="green", tags="triangle")
    
    def update_disp(self, altitude):
        self.altitude = altitude

        self.update_height_disp()
    
    def update(self): # testing only
        self.altitude += random.randint(0,30)
        self.update_disp(self.altitude)
        self.after(100, self.update)
        
        

if __name__ == "__main__":
    # root.configure(height=1080, width=1920)
    one = gui_2(master=root)
    one.configure(height=SCRN_HEIGHT, width=SCRN_WIDTH)
    one.grid_propagate(0)

    test_but = tk.Button(text="Test", command=one.update)
    test_but.grid(row=10)

    root.mainloop()