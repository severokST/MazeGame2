import tkinter
from tkinter import Tk
from math import sin, cos, pi

from tkinter import ttk, StringVar


class Shape(object):
    def __init__(self, position, target_canvas, radius = 20):
        self.positon_x, self.positon_y = position
        self.radius = radius
        self.canvas = target_canvas



class Hex(Shape):
    def __init__(self, position, target_canvas, radius = 20):
        Shape.__init__(self, position, target_canvas, radius)
        self.vertex = [(self.radius * cos(step*pi/3 if step > 0 else 0)+self.positon_x,
                        self.radius * sin(step*pi/3 if step > 0 else 0)+self.positon_y) for step in range(0,7)]
        self.object = [self.canvas.create_line(self.vertex[step][0], self.vertex[step][1],
                                               self.vertex[(step+1)%7][0], self.vertex[(step+1)%7][1])
                        for step in range(0,7)]



class Circle(Shape):
    def __init__(self, position, target_canvas, radius = 20):
        Shape.__init__(self, position, target_canvas, radius)
        self.object = self.canvas.create_oval((self.positon_x - self.radius), (self.positon_y - self.radius),
                                              (self.positon_x + self.radius), (self.positon_y + self.radius))







class Map(tkinter.Canvas):
    def __init__(self, master, size = (800,800), density=101):
        self.x, self.y = size
        self.cells = []
        tkinter.Canvas.__init__(self, master, width = self.x, height = self.y)



    def map_local(self, local):
        radius = 20
        origin_x, origin_y = int(self.x/2), int(self.y/2)
        for cell in local.map:
            self.cells.append(Hex(self.canvas_position(cell.position, radius), self))

    def canvas_position(self, position, radius):
        return (position[0]*radius+ self.x/2, position[1]*radius+self.y/2)






class GUIWindow(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("GUI window")
        self.geometry('800x600')
        display = {'width': self.winfo_screenwidth(), 'height': self.winfo_screenmmheight()}

        self.map = Map(self)
        self.map.pack(expand=1, fill='both')


    def run(self):
        self.mainloop()

