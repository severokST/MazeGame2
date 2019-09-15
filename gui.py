import tkinter
from tkinter import Tk
from math import sin, cos, pi

from operator import add

render_graph = True
render_barriers = True
render_hex_boundries = True

neighbour = [(round(2 * cos(step*pi/6 if step > 0 else 0),2),
              round(2 * sin(step*pi/6 if step > 0 else 0),2)) for step in range(1,13,2)]




def cell_displacement(cell_pos, neigbour_pos):
    return (round(cell_pos[0] - neigbour_pos[0],2), round(cell_pos[1] - neigbour_pos[1],2))

def _from_rgb(rgb):
    return "#%02x%02x%02x" % rgb


colour_map = {

    'green': [_from_rgb((0, int(50+(200*x/10)), 0)) for x in range(0, 10)],
    'grey': [_from_rgb((int(42+(128*x/10)), int(42+(128*x/10)), int(42+(128*x/10)))) for x in range(0, 10)],
    'yellow':[_from_rgb((int(64+(128*x/10)), int(64+(128*x/10)), 0)) for x in range(0, 10)],

}


class Shape(object):
    def __init__(self, position, target_canvas, radius = 20):
        self.positon_x, self.positon_y = position
        self.radius = radius
        self.canvas = target_canvas







class Line(Shape):
    def __init__(self, pos1, pos2, target_canvas,color='black', width=1):
        Shape.__init__(self, pos1, target_canvas, 1)

        self.object = self.canvas.create_line(pos1[0], pos1[1], pos2[0], pos2[1], fill=color, width=width)

    def move(self, delta):
        dx, dy = delta
        self.canvas.move(self.object, dx, dy)


class Barrier(Shape):
    def __init__(self, pos1, pos2, target_canvas, radius=20, color='red'):
        Shape.__init__(self, pos1, target_canvas, radius)

        self.object = Line(pos1, pos2, target_canvas, color, width= target_canvas.zoom * 4)



class Hex(Shape):
    def __init__(self, position, target_canvas, barrier_list, radius = 20, color='blue', elevation=1):
        Shape.__init__(self, position, target_canvas, radius)
        self.vertex = [(self.radius*1.2 * cos(step*pi/3 if step > 0 else 0)+self.positon_x,
                        self.radius*1.2 * sin(step*pi/3 if step > 0 else 0)+self.positon_y) for step in range(0,7)]

        self.wall_vertex = [(round((self.radius*1.15) * cos(step * pi / 3 if step > 0 else 0) + self.positon_x,2),
                             round((self.radius*1.15) * sin(step * pi / 3 if step > 0 else 0) + self.positon_y,2))
                            for step in range(0, 7)]

        vertex_arguments = []
        for point in self.vertex:
            vertex_arguments.append(point[0])
            vertex_arguments.append(point[1])

        self.object_base = self.canvas.create_polygon(*vertex_arguments,
                                                      fill=colour_map[color][elevation if elevation < 10 else 9])
        if render_hex_boundries:
            self.object = [self.canvas.create_line(self.vertex[step][0], self.vertex[step][1],
                                               self.vertex[(step+1)%7][0], self.vertex[(step+1)%7][1])
                            for step in range(0,7)]

        if render_barriers:

            self.barriers = [Barrier(self.wall_vertex[barrier.orientation],
                                     self.wall_vertex[(barrier.orientation+1) % 6],
                                     target_canvas, color=barrier.barrier) for barrier in barrier_list]

    def move(self, delta):
        dx, dy = delta
        for edge in self.object:
            self.canvas.move(edge, dx, dy)

        self.canvas.move(self.object_base, dx, dy)

        self.wall_vertex = [(round((self.radius*1.15) * cos(step * pi / 3 if step > 0 else 0) + self.positon_x,2),
                             round((self.radius*1.15) * sin(step * pi / 3 if step > 0 else 0) + self.positon_y,2))
                            for step in range(0, 7)]



class Circle(Shape):
    def __init__(self, position, target_canvas, radius = 20):
        Shape.__init__(self, position, target_canvas, radius)
        self.object = self.canvas.create_oval((self.positon_x - self.radius), (self.positon_y - self.radius),
                                              (self.positon_x + self.radius), (self.positon_y + self.radius))







class Map(tkinter.Canvas):
    def __init__(self, master, map_data, size = (800,800)):
        self.x, self.y = size
        self.pan = (0,0)
        self.zoom = 1
        self.cells = []
        self.connections = []
        self.walls = []
        self.map_data = map_data
        tkinter.Canvas.__init__(self, master, width = self.x, height = self.y, background='Blue')
        self.draw_map()



    def draw_map(self):
        # Map index of map elements used to generate shapes.
        # Some map elements are made None during generation, this list corrects index associations.
        map_cell_associations = []

        self.delete("all")
        radius = 20 * self.zoom
        for cell in self.map_data.map:
            if cell is not None:
                cell_id = self.map_data.map.index(cell)

                barrier_list = [self.map_data.terrain_features[x] for x in range(0,len(self.map_data.terrain_features))
                                if self.map_data.terrain_graph[x][0] == cell_id]


                cell_position = tuple(map(add, self.canvas_position(cell.position, radius), self.pan))

                self.cells.append(Hex(cell_position, self, barrier_list,
                                      radius=radius, color=cell.tile, elevation=int(cell.elevation)))
                map_cell_associations.append(cell_id)
                # Generate list 0-5 referencing 6 directions of hex. Purge from this list when mapping neighbours
                # to determine wall placements
                cell_walls = [True]*6

                for connection in self.map_data.graph[cell_id]:
                    connecting_cell = self.map_data.map[connection]
                    if connecting_cell is not None:
                        # Find direction of neighboring cell, remove reference from cell walls list
                        cell_walls[neighbour.index(cell_displacement(connecting_cell.position,cell.position))] = False
                        if render_graph:
                            #print('drawing graph')
                            connecting_cell_position = tuple(map(add, self.canvas_position(connecting_cell.position, radius), self.pan))
                            self.connections.append(Line(cell_position,connecting_cell_position, self))
        if False:
            for barrier in self.map_data.terrain_features:
                barrier_id = self.map_data.terrain_features.index(barrier)

                print('{}: {}'.format(barrier_id, self.map_data.terrain_graph[barrier_id]) )


                #cell_position = tuple(map(add, self.canvas_position(barrier.position, radius*.67), self.pan))
                #test = Circle(cell_position, self, radius=2)

                orientation = barrier.orientation
                parent_cell = self.cells[map_cell_associations.index(self.map_data.terrain_graph[barrier_id][0])]
                pos1, pos2 = parent_cell.wall_vertex[orientation], parent_cell.wall_vertex[orientation+1%6]

                self.walls.append(Barrier(pos1, pos2, self, color=barrier.barrier))


    # Update
    def change_zoom(self, change):
        self.zoom += change
        self.draw_map()

    def change_pan(self,delta):
        self.pan = tuple(map(add,self.pan,delta))
        self.draw_map()

    def set_pan(self, position):
        self.pan = position
        self.draw_map()


    def canvas_position(self, position, radius):
        return (position[0]*radius+ self.x/2, position[1]*radius+self.y/2)






class GUIWindow(Tk):
    def __init__(self, map):
        Tk.__init__(self)
        self.title("GUI window")
        self.geometry('800x600')
        display = {'width': self.winfo_screenwidth(), 'height': self.winfo_screenmmheight()}

        self.map = Map(self, map)
        self.map.pack(expand=1, fill='both')


    def run(self):
        self.mainloop()

