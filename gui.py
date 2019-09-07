import tkinter
from tkinter import Tk
from math import sin, cos, pi

from tkinter import ttk, StringVar

neighbour = [(round(2 * cos(step*pi/6 if step > 0 else 0),2),
              round(2 * sin(step*pi/6 if step > 0 else 0),2)) for step in range(1,13,2)]


def cell_displacement(cell_pos, neigbour_pos):
    return (round(cell_pos[0] - neigbour_pos[0],2), round(cell_pos[1] - neigbour_pos[1],2))

class Shape(object):
    def __init__(self, position, target_canvas, radius = 20):
        self.positon_x, self.positon_y = position
        self.radius = radius
        self.canvas = target_canvas





class Line(Shape):
    def __init__(self, pos1, pos2, target_canvas,color='black'):
        Shape.__init__(self, pos1, target_canvas, 1)

        self.object = self.canvas.create_line(pos1[0], pos1[1], pos2[0], pos2[1], fill=color, width=2)


class Hex(Shape):
    def __init__(self, position, target_canvas, radius = 20, color='blue'):
        Shape.__init__(self, position, target_canvas, radius)
        self.vertex = [(self.radius * cos(step*pi/3 if step > 0 else 0)+self.positon_x,
                        self.radius * sin(step*pi/3 if step > 0 else 0)+self.positon_y) for step in range(0,7)]

        self.wall_vertex = [((self.radius*1.18) * cos(step * pi / 3 if step > 0 else 0) + self.positon_x,
                             (self.radius*1.18) * sin(step * pi / 3 if step > 0 else 0) + self.positon_y)
                            for step in range(0, 7)]

        vertex_arguments = []
        for point in self.vertex:
            vertex_arguments.append(point[0])
            vertex_arguments.append(point[1])

        self.object = self.canvas.create_polygon(*vertex_arguments, fill=color)




        #self.object = [self.canvas.create_line(self.vertex[step][0], self.vertex[step][1],
        #                                       self.vertex[(step+1)%7][0], self.vertex[(step+1)%7][1])
        #                for step in range(0,7)]



class Circle(Shape):
    def __init__(self, position, target_canvas, radius = 20):
        Shape.__init__(self, position, target_canvas, radius)
        self.object = self.canvas.create_oval((self.positon_x - self.radius), (self.positon_y - self.radius),
                                              (self.positon_x + self.radius), (self.positon_y + self.radius))







class Map(tkinter.Canvas):
    def __init__(self, master, size = (800,800), density=101):
        self.x, self.y = size
        self.cells = []
        self.connections = []
        self.walls = []
        tkinter.Canvas.__init__(self, master, width = self.x, height = self.y)



    def map_local(self, local):
        radius = 20
        origin_x, origin_y = int(self.x/2), int(self.y/2)
        for cell in local.map:
            cell_id = local.map.index(cell)

            cell_position = self.canvas_position(cell.position, radius)

            self.cells.append(Hex(cell_position, self))

            # Generate list 0-5 referencing 6 directions of hex. Purge from this list when mapping neighbours
            # to determine wall placements
            cell_walls = [True]*6

            for connection in local.graph[cell_id]:
                connecting_cell = local.map[connection]
                # Find direction of neighboring cell, remove reference from cell walls list
                cell_walls[neighbour.index(cell_displacement(connecting_cell.position,cell.position))] = False
                connecting_cell_position = self.canvas_position(connecting_cell.position, radius)
                self.connections.append(Line(cell_position,connecting_cell_position, self))

            for direction in range(0,6):
                if cell_walls[direction]:
                    self.walls.append(Line(self.cells[-1].wall_vertex[direction],
                                           self.cells[-1].wall_vertex[direction+1%6],self, color='Red'))


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

