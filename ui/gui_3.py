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

NORTH_TEXT = 'N'
EAST_TEXT = 'E'
SOUTH_TEXT = 'S'
WEST_TEXT = 'W'

root = tk.Tk()

class gui_3(tk.Canvas):
    def __init__(self, master):
        tk.Canvas.__init__(self, master)

        self.heading = 180 # limit 0 ~ 360
        self.center_width=SCRN_WIDTH_CENTER
        self.center_height=SCRN_HEIGHT_CENTER

        self.grid()

        self.draw_compass()
        
        self.update_disp(self.heading)
    
    def draw_compass(self):
        for tick in range(0,12):
            ang = tick/6 * pi
            ang_2 = (tick+1/3)/6*pi
            ang_3 = (tick+2/3)/6*pi
            self.create_line(self.center_width+sin(ang)*SIZE*20, self.center_height-cos(ang)*SIZE*20, self.center_width+sin(ang)*SIZE*17, self.center_height-cos(ang)*SIZE*17)
            self.create_line(self.center_width+sin(ang_2)*SIZE*20, self.center_height-cos(ang_2)*SIZE*20, self.center_width+sin(ang_2)*SIZE*18, self.center_height-cos(ang_2)*SIZE*18)
            self.create_line(self.center_width+sin(ang_3)*SIZE*20, self.center_height-cos(ang_3)*SIZE*20, self.center_width+sin(ang_3)*SIZE*18, self.center_height-cos(ang_3)*SIZE*18)
            self.create_text(self.center_width+sin(ang)*SIZE*22, self.center_height-cos(ang)*SIZE*22, text=tick*3, font=(FONT, SIZE*2))
        self.create_text(self.center_width, self.center_height-SIZE*15, text=NORTH_TEXT, font=(FONT, SIZE*3))
        self.create_text(self.center_width+SIZE*15, self.center_height, text=EAST_TEXT, font=(FONT, SIZE*3))
        self.create_text(self.center_width, self.center_height+SIZE*15, text=SOUTH_TEXT, font=(FONT, SIZE*3))
        self.create_text(self.center_width-SIZE*15, self.center_height, text=WEST_TEXT, font=(FONT, SIZE*3))
        
    def update_compass(self):
        self.delete("arrow")
        ang = self.heading/180 * pi
        self.create_line(self.center_width+sin(ang)*SIZE*10, self.center_height-cos(ang)*SIZE*10, self.center_width-sin(ang)*SIZE*10, self.center_height+cos(ang)*SIZE*10, width=SIZE/2, arrow="last", arrowshape=(SIZE*4,SIZE*4,SIZE*2), tags="arrow")
    
    def update_disp(self, heading):
        self.heading = heading

        self.update_compass()
    
    def update(self): # testing only
        self.heading += random.random()*10-5
        self.update_disp(self.heading)
        self.after(100, self.update)
        
        

if __name__ == "__main__":
    # root.configure(height=1080, width=1920)
    one = gui_3(master=root)
    one.configure(height=SCRN_HEIGHT, width=SCRN_WIDTH)
    one.grid_propagate(0)

    test_but = tk.Button(text="Test", command=one.update)
    test_but.grid(row=10)

    root.mainloop()