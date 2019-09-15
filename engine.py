

from gui import GUIWindow
from objects import Player
from world import Map



# neighbour = [(1,-1), (0,-2), (-1,-1), (-1,1), (0,2), (1,1)]

class World(object):
    def __init__(self, save):
        #self.position = (0,0)
        feature_list = {}

        if save is None:
            self.map = Map()
            self.location = 0




class Engine(object):
    def __init__(self, save):
        # If save is NONE, __init__ is called for default values, otherwise data are loaded from file.
        self.player = Player(save)
        self.world = World(save)

        #Build GUI
        self.gui = GUIWindow(self.world.map)

        self.gui.after(int(1000 / 20), self.call)
        self.gui.bind('<Key>', self.keypress)
        self.gui.map.bind('<B1-Motion>', self.map_pan)
        self.gui.map.bind('<MouseWheel>', self.map_zoom)

        self.gui.run()

    def new_game(self):
        self.world = World(None)
        self.player = Player(None)


    def keypress(self, event):
        #Key press macros
        pass

    def map_pan(self, event):
        self.gui.map.set_pan((event.x, event.y))

    def map_zoom(self, event):


        self.gui.map.change_zoom(0.1 if event.delta > 0 else -0.1)


    def call(self):
        # Todo Engine update hooks here
        self.gui.after(int(1000/20), self.call)