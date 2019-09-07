from random import choice, randrange
from math import sin, cos, pi

from gui import GUIWindow
from objects import Player


neighbour = [(round(2 * cos(step*pi/6 if step > 0 else 0), 2),
              round(2 * sin(step*pi/6 if step > 0 else 0), 2)) for step in range(1, 13, 2)]
# neighbour = [(1,-1), (0,-2), (-1,-1), (-1,1), (0,2), (1,1)]

class World(object):
    def __init__(self, save):
        #self.position = (0,0)
        feature_list = {}

        if save is None:
            self.map = Map()
            self.location = 0


class Map(object):
    def __init__(self, max_hex_count=200):
        self.graph = []
        self.map = []

        new_hex = [(0, 0)]

        while len(self.map) < max_hex_count and len(new_hex) > 0:

            # Get index of next hex
            next_id = len(self.map)

            # Get position and parent of next hex
            new_position = new_hex.pop(0)

            # Make hex and ammend graph
            self.map.append(Hex(new_position))
            self.graph.append([])

            # Search graphs for existing nodes connecting to this id
            # can have 1-6 parents
            for existing_graph_entries in self.graph:
                if next_id in existing_graph_entries:
                    self.graph[next_id].append(self.graph.index(existing_graph_entries))

            # Pick connections
            directions = neighbour.copy()

            #remove direction items already taken
            for existing_connection in self.graph[next_id]:
                try:
                    directions.pop(directions.index(self.map[existing_connection].delta_position(new_position)))
                except ValueError:
                    pass

            for connection in range(0, randrange(1, 6-len(self.graph[next_id]))):

                location_delta = directions.pop(directions.index(choice(directions)))
                next_position = (round(new_position[0]+location_delta[0], 2), round(new_position[1]+location_delta[1], 2))

                connecting_index = None

                # Search if new hex wants to connect to existing
                for hex in self.map:
                    #If found, make note of connecting ID, and ammend targets graph array with new ID
                    if hex.is_position(next_position):
                        connecting_index = self.map.index(hex)
                        if next_id not in self.graph[connecting_index]:
                            self.graph[connecting_index].append(next_id)

                # Search if new hex wants to connect to hex already scheduled for creation
                for hex in new_hex:
                    if next_position == hex:
                        connecting_index = next_id + new_hex.index(hex)+1

                # If hit not yet found, schedule new hex creation and link to calculated future tile ID.
                if connecting_index is None:
                    new_hex.append(next_position)
                    connecting_index = next_id + len(new_hex)

                # New tiles graph array appended with new connection
                self.graph[-1].append(connecting_index)


            #Graph cleanup to remove orphaned links (if any)
        for index in range(0,len(self.graph)):
            # Remove connection to self?
            #self.graph[index] = list(x for x in self.graph[index] if x != index)

            # Remove connections not created due to map size limit reached, remove connection.
            self.graph[index] = list(x for x in self.graph[index] if x < len(self.graph) )

            # Remove any links created that do not have valid return path (if any)
            #self.graph[index] = list(x for x in self.graph[index] if index in self.graph[x])


    def print_graph(self):
        for index in range(0,len(self.graph)):
            print ('{}, {}: {}'.format(index, self.map[index].position, self.graph[index]))


class Hex(object):
    def __init__(self, position):
        self.position = position

    def is_position(self, position):
        return position == self.position

    def delta_position(self, position):
        return (self.position[0] - position[0], self.position[1] - position[1])


class Engine(object):
    def __init__(self, save):
        # If save is NONE, __init__ is called for default values, otherwise data are loaded from file.
        self.player = Player(save)
        self.world = World(save)

        #Build GUI
        self.gui = GUIWindow()
        self.gui.map.map_local(self.world.map)

        self.gui.after(int(1000 / 20), self.call)
        self.gui.bind('<Key>', self.keypress)

        self.gui.run()

    def new_game(self):
        self.world = World(None)
        self.player = Player(None)


    def keypress(self, event):
        #Key press macros
        pass

    def call(self):
        # Todo Engine update hooks here
        self.gui.after(int(1000/20), self.call)