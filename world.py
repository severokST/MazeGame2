
from random import choice, randrange
from numpy.random import choice as weighted_choice

from math import sin, cos, pi
from operator import add

world_size = 1000

elevation_density = 60

neighbour = [(round(2 * cos(step*pi/6 if step > 0 else 0), 2),
              round(2 * sin(step*pi/6 if step > 0 else 0), 2)) for step in range(1, 13, 2)]

# Generates new location refernce from original + displacement tuple.
def connecting_key(origin, direction_key):
    return tuple(map(add, origin, direction_key))


# Generic Hex-tile class.
class Hex(object):
    def __init__(self, position):
        self.position = position
        self.gen_bias = {}
        self.tile = 'Grey'
        self.moisture = 1
        self.elevation = 1

    def is_position(self, position):
        return position == self.position

    def delta_position(self, position):
        return tuple(map(add, self.position, position))


class Grass(Hex):
    def __init__(self, position):
        Hex.__init__(self, position)
        self.tile = 'Green'
        self.gen_bias.update({'Grass':1, 'Rock':0.2, 'Sand': 0.01, 'Water':0.3})


class Rock(Hex):
    def __init__(self, position):
        Hex.__init__(self, position)
        self.tile = 'Grey'
        self.gen_bias.update({'Grass': 0.1, 'Rock': 2, 'Sand': 0.5, 'Water':0.1})


class Sand(Hex):
    def __init__(self, position):
        Hex.__init__(self, position)
        self.tile = 'Yellow'
        self.gen_bias.update({'Rock': 0.5, 'Sand': 3, 'Water': -0.3})

class Water(Hex):
    def __init__(self, position):
        Hex.__init__(self, position)
        self.tile = 'Blue'
        self.gen_bias.update({'Rock': 0.5, 'Sand': -0.2, 'Grass': 0.5, 'Water':0.5})


location_types = {'Grass': Grass, 'Rock': Rock, 'Sand':Sand, 'Water': Water}

location_quota = {'Grass':[10000,10000], 'Rock': [1200,1200], 'Sand':[2000,2000], 'Water': [3000,3000]}
location_size = {'Grass':(1,2), 'Rock': (1,2), 'Sand':(1,2), 'Water':(1,2)}

class Map(object):
    def __init__(self, max_hex_count=world_size):
        self.graph = []
        self.map = []

        new_hex = [(0, 0)]

        # Trialing removal of generation phase biomes
        #biome_current, biome_remaining = 'Grass', 10


        while len(self.map) < max_hex_count and len(new_hex) > 0:
            print(len(self.map), len(new_hex))

            # Get index of next hex
            next_id = len(self.map)

            # Get position and parent of next hex
            new_position = new_hex.pop(0)


            # Make hex and ammend graph
            #self.map.append(location_types[biome_current](new_position))
            self.map.append(Hex(new_position))
            self.graph.append([])

            #biome_remaining-=1
            #if biome_remaining <1:
            #    biome_current, biome_remaining = self.biome_selection(next_id)

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
        position_list = [tile.position for tile in self.map]

        # Filter graph and initialise tiles for biome selection
        for index in range(0,len(self.graph)):
            # Remove connections not created due to map size limit reached, remove connection.
            self.graph[index] = list(x for x in self.graph[index] if x < len(self.graph) )

            #Randomly apply elevation to selected tiles
            if randrange(0,100) < elevation_density:
                self.map[index].elevation = randrange(10,100)

            # Apply increased moisture levels in tiles neighbouring water (None existant tile positions)
            for direction in neighbour:
                if self.map[index].delta_position(direction) not in position_list:
                    self.map[index].moisture += randrange(10,30)

        # 3x blur filter pass on each tile to smooth

        for iteration in range(0,100):
            update_list_elevation, update_list_moisture = [], []
            for index in range(0, len(self.graph)):
                current_tile = self.map[index]
                set_locations = set()

                list_to_check = [index]
                next_step_list_to_check = []

                # Iterate though graph of connected cells for up to 3 steps

                for iteration in range(0, 5):
                    while len(list_to_check) > 0:
                        target_cell = list_to_check.pop()
                        for index in range(0, len(self.map)):
                            if index not in set_locations and target_cell in self.graph[index]:
                                set_locations.add(index)
                                next_step_list_to_check.append(index)

                    for blur_index in set_locations:
                        try:
                            update_list_elevation[index] += (self.map[blur_index].elevation - current_tile.elevation) * 0.05
                            update_list_moisture[index] += (self.map[blur_index].moisture - current_tile.moisture) * 0.05
                        except IndexError:
                            pass

            for index in range(0, len(self.map)):
                try:
                    self.map[index].moisture += update_list_moisture[index]
                    self.map[index].elevation += update_list_elevation[index]
                except IndexError:
                    pass

        for index in range(0, len(self.map)):
            current_tile = self.map[index]
            moisture, elevation = current_tile.moisture, current_tile.elevation

            if elevation  < 10:
                self.map[index] = Water(current_tile.position)
                continue

            if moisture > 20:
                self.map[index] = Grass(current_tile.position)
                continue

            if elevation >40:
                self.map[index] = Rock(current_tile.position)
                continue

            self.map[index] = Sand(current_tile.position)





            # Remove any links created that do not have valid return path (if any)
            #self.graph[index] = list(x for x in self.graph[index] if index in self.graph[x])



    def biome_selection(self, current_id):

        set_neighbour = set()

        list_to_check = [current_id]
        next_step_list_to_check = []

        # Iterate though graph of connected cells for up to 3 steps

        for iteration in range(0, 6):
            while len(list_to_check) > 0:
                target_cell = list_to_check.pop()

                for index in range(0, len(self.graph)):

                    if index not in set_neighbour and target_cell in self.graph[index]:
                        set_neighbour.add(index)
                        next_step_list_to_check.append(index)



            list_to_check = next_step_list_to_check.copy()
            next_step_list_to_check.clear()

        print(set_neighbour)

        # Initialise biome selection weightings
        selection_bias = {'Grass': 1, 'Sand': 1, 'Rock':1, 'Water':1}


        # Step though listed neighbouring cells, accumulate biases where avaliable
        for cell_id in set_neighbour:
            cell_gen_bias = self.map[cell_id]
            for biome_entry, value in cell_gen_bias.gen_bias.items():
                selection_bias[biome_entry] += value

        # Scale calculated weights against quota tally, Tapers off terrain selection if one type becomes too common.
        for terrain, quota in location_quota.items():
            selection_bias[terrain] *= quota[1]/quota[0]

        print(selection_bias)

        biome_list = [(terrain, weight) for terrain, weight in selection_bias.items()]
        biome_choices = [biome[0] for biome in biome_list]
        biome_chance = [biome[1] for biome in biome_list]
        biome_chance = [biome if biome > 0 else 0 for biome in biome_chance]
        biome_chance = [biome/sum(biome_chance) for biome in biome_chance]

        selection = weighted_choice(biome_choices, 1, p=biome_chance)[0]
        size_start, size_stop = location_size[selection]
        biome_count = randrange(size_start, size_stop)

        location_quota[selection][1] -= biome_count
        if  location_quota[selection][1] <0:
            location_quota[selection][1] = 1


        return selection, biome_count


    def print_graph(self):
        for index in range(0,len(self.graph)):
            print ('{}, {}: {}'.format(index, self.map[index].position, self.graph[index]))


