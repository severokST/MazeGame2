from random import choice, randrange

from gui import GUIWindow

neighbour = [(1,-1), (0,-2), (-1,-1), (-1,1), (0,2), (1,1)]




class Map(object):
    def __init__(self, max_hex_count=100):
        self.graph = []

        self.map = []

        new_hex = [(0,0)]

        while len(self.map) < max_hex_count and len(new_hex)>0:

            # Get index of next hex
            next_id = len(self.map)

            #Get position and parent of next hex
            new_position = new_hex.pop(0)

            # Make hex and ammend graph
            self.map.append(Hex(new_position))
            self.graph.append([])

            # Search graphs for existing nodes connecting to this id
                # can have 1-6 parents
            for existing_graph_entries in self.graph:
                if next_id in existing_graph_entries:
                    self.graph[next_id].append(self.graph.index(existing_graph_entries))

            #Pick connections

            directions = neighbour.copy()

            #remove direction items already taken
            for existing_connection in self.graph[next_id]:
                try:
                    directions.pop(directions.index(self.map[existing_connection].delta_position(new_position)))
                except ValueError:
                    pass


            for connection in range(0, randrange(1, 5-len(self.graph[next_id]))):

                location_delta = directions.pop(directions.index(choice(directions)))
                next_position = (new_position[0]+location_delta[0], new_position[1]+location_delta[1])

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
                        connecting_index = next_id + new_hex.index(hex)

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
            self.graph[index] = list(x for x in self.graph[index] if index in self.graph[x])


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


map = Map()

map.print_graph()

window = GUIWindow()
window.map.map_local(map)
window.run()











