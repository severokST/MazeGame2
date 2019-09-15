
from random import choice, randrange
from numpy.random import choice as weighted_choice

from math import sin, cos, pi
from operator import add


import operator

world_size = 800

blur_iterations = 3
elevation_density = 40

elevation_threshold = 2
moisture_threshould = 0.5
sea_level = 2
tree_line = 8

neighbour = [(round(2 * cos(step*pi/6 if step > 0 else 0), 2),
              round(2 * sin(step*pi/6 if step > 0 else 0), 2)) for step in range(1, 13, 2)]

# Generates new location refernce from original + displacement tuple.
def connecting_key(origin, direction_key):
    return tuple(map(add, origin, direction_key))


# Generic Hex-tile class.
class Hex(object):
    def __init__(self, position, elevation = 0):
        self.position = position
        self.gen_bias = {}
        self.tile = 'Grey'
        self.moisture = 0
        self.elevation = elevation

    def is_position(self, position):
        return position == self.position

    def delta_position(self, position):
        return tuple(map(add, self.position, position))

class Grass(Hex):
    def __init__(self, position, elevation = 0):
        Hex.__init__(self, position, elevation)

        self.type = 'Grass'
        self.tile = 'green'
        self.gen_bias.update({'Grass':1, 'Rock':0.2, 'Sand': 0.01, 'Water':0.3})

class Rock(Hex):
    def __init__(self, position, elevation = 0):
        Hex.__init__(self, position, elevation)
        self.type = 'Rock'
        self.tile = 'grey'
        self.gen_bias.update({'Grass': 0.1, 'Rock': 2, 'Sand': 0.5, 'Water':0.1})

class Sand(Hex):
    def __init__(self, position, elevation = 0):
        Hex.__init__(self, position, elevation)
        self.type = 'Sand'
        self.tile = 'yellow'
        self.gen_bias.update({'Rock': 0.5, 'Sand': 3, 'Water': -0.3})

class Water(Hex):
    def __init__(self, position, elevation = 0):
        Hex.__init__(self, position, elevation)
        self.type = 'Water'
        self.tile = 'Blue'
        self.gen_bias.update({'Rock': 0.5, 'Sand': -0.2, 'Grass': 0.5, 'Water':0.5})


class Barrier(object):
    def __init__(self, position, orientation):
        self.position = position
        self.orientation = orientation

class Rocky_Outcrop(Barrier):
    def __init__(self, position, orientation):
        Barrier.__init__(self, position, orientation)
        self.barrier = 'gray20'

class Forest(Barrier):
    def __init__(self, position, orientation):
        Barrier.__init__(self, position, orientation)
        self.barrier = 'forest green'

class Shore(Barrier):
    def __init__(self, position, orientation):
        Barrier.__init__(self, position, orientation)
        self.barrier = 'gold3'


location_types = {'Grass': Grass, 'Rock': Rock, 'Sand':Sand, 'Water': Water}

location_quota = {'Grass':[10000,10000], 'Rock': [1200,1200], 'Sand':[2000,2000], 'Water': [3000,3000]}
location_size = {'Grass':(1,2), 'Rock': (1,2), 'Sand':(1,2), 'Water':(1,2)}

class Map(object):
    def __init__(self, max_hex_count=world_size):

        print('Starting map generation')

        self.map = []
        self.graph = []
        self.terrain_features = []
        self.terrain_graph = []

        new_hex = [(0, 0)]

        # Trialing removal of generation phase biomes
        #biome_current, biome_remaining = 'Grass', 10

        print('placing tiles')
        while len(self.map) < max_hex_count and len(new_hex) > 0:

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


        print('Seeding initial elevations')
        # Filter graph and initialise tiles for biome selection
        for index in range(0,len(self.map)):
            # Remove connections not created due to map size limit reached, remove connection.
            self.graph[index] = list(x for x in self.graph[index] if x < len(self.graph) )

            #Randomly apply elevation to selected tiles
            if randrange(0,100) < elevation_density:
                self.map[index].elevation = randrange(10,20)
                self.map[index].moisture = -2


        print('Bluring tile elevation with connecting neighbours')

        # 3x blur filter pass on each tile to smooth
        blur_magnitude = 1 / blur_iterations



        # Elevation level blur
        dictionary_blur_magnitudes = {cell: {cell: 10} for cell in range(0, len(self.map))}

        for graph_link_weight in range(2,4):
            for cell in range(0, len(self.map)):
                blur_element_list = [blur_element for blur_element in dictionary_blur_magnitudes[cell].keys()]
                for blur_element in blur_element_list:

                    dictionary_blur_magnitudes[cell].update(
                        {neighbour_cell: 10/graph_link_weight
                         for neighbour_cell in self.graph[blur_element]
                         if neighbour_cell not in dictionary_blur_magnitudes[cell].keys()})


        for cell in range(0, len(self.map)):
            cell_normalise = sum(list(x for key,x in dictionary_blur_magnitudes[cell].items()))
            dictionary_blur_magnitudes[cell] = {key: weight/cell_normalise
                                                for key,weight in dictionary_blur_magnitudes[cell].items()}


        for iteration in range(0,blur_iterations):
            update_list_elevation = [0] * len(self.map)
            for index in dictionary_blur_magnitudes.keys():
                update_list_elevation[index] = sum(list(self.map[blur_cell].elevation * dictionary_blur_magnitudes[index][blur_cell]
                                            for blur_cell in dictionary_blur_magnitudes[index].keys()))

            for index in dictionary_blur_magnitudes.keys():
                self.map[index].elevation = update_list_elevation[index]

        print('Purging tiles below sea level')

        self.purge_sea_level()

        print('Initialing tile moisture (tiles bordering water')

        # Apply increased moisture levels in tiles neighbouring water (None existant tile positions)
        position_list = [cell.position for cell in self.map if cell is not None]
        for cell in self.map:
            if cell is not None:
                for direction in neighbour:
                    if cell.delta_position(direction) not in position_list:
                        cell.moisture += randrange(1, 3)


        print('Bluring tile moisture levels')
            # Moisture level blur
        dictionary_blur_magnitudes = {cell: {cell: 10} for cell in range(0, len(self.map)) if self.map[cell] is not None}

        for graph_link_weight in range(2, 4):
            for cell in range(0, len(self.map)):
                if self.map[cell] is not None:

                    blur_element_list = [blur_element for blur_element in dictionary_blur_magnitudes[cell].keys() if self.map[blur_element] is not None]
                    for blur_element in blur_element_list:
                        dictionary_blur_magnitudes[cell].update(
                                {neighbour_cell: 10 / graph_link_weight
                                for neighbour_cell in self.graph[blur_element]
                                if neighbour_cell not in dictionary_blur_magnitudes[cell].keys()})

        for cell in range(0, len(self.map)):
            if self.map[cell] is not None:
                cell_normalise = sum(list(x for key, x in dictionary_blur_magnitudes[cell].items()))
                dictionary_blur_magnitudes[cell] = {key: weight / cell_normalise
                                                        for key, weight in dictionary_blur_magnitudes[cell].items()}


        for iteration in range(0, blur_iterations):
            update_list_moisture = [0] * len(self.map)
            for index in dictionary_blur_magnitudes.keys():
                update_list_moisture[index] = sum(
                    list(self.map[blur_cell].moisture * dictionary_blur_magnitudes[index][blur_cell]
                             for blur_cell in dictionary_blur_magnitudes[index].keys() if self.map[blur_cell] is not None))

            for index in dictionary_blur_magnitudes.keys():
                self.map[index].moisture = update_list_moisture[index]

        print('Applying tile biomes')

        # Apply tile values to select terrain.
        for index in range(0, len(self.map)):
            if self.map[index] is not None:
                current_tile = self.map[index]
                moisture, elevation = current_tile.moisture, current_tile.elevation

                if elevation < sea_level:
                    self.map[index] = None
                    continue

                if elevation > tree_line:
                    self.map[index] = Rock(current_tile.position, elevation = elevation)
                    continue

                if moisture > moisture_threshould:
                    self.map[index] = Grass(current_tile.position, elevation = elevation)
                    continue

                if moisture < moisture_threshould:
                    self.map[index] = Sand(current_tile.position, elevation = elevation)

                self.map[index].elevation = elevation


        # Generate terrain barriers/features

        print('generating / linking terrain features')

        for cell in self.map:
            if cell is not None:
                cell_id = self.map.index(cell)
                # If all directions already connected, no barriers to generate
                #if len(self.graph[cell_id]) + len([x for x in self.terrain_graph if cell_id in x]) >= 6:
                #    continue

                for direction in neighbour:
                    test_location = cell.delta_position(direction)

                    barrier_pos = (round(cell.position[0] + test_location[0] / 2, 2), round(cell.position[1] + test_location[1] / 2,2) )
                    detected_cell = self.cell_at_position(test_location)
                    detected_cell_id = None if detected_cell is None else self.map.index(detected_cell)

                    # If this barrier has already been registered (Other neighbour processing)
                    # or detected cell is connected, move to next candidate
                    if barrier_pos in [x.position for x in self.terrain_features] or \
                            detected_cell_id in self.graph[cell_id]:
                        continue

                    if detected_cell not in self.graph[cell_id]:
                        barrier_orientation = neighbour.index(direction)
                        terrain_mix = (None if cell is None else cell.type, None if detected_cell is None else detected_cell.type)
                        if None not in terrain_mix:
                            # Default terrain barrier (Cells are Mountain or Desert ONLY)
                            barrier_type = Rocky_Outcrop

                            # Override if grass is present, Forest generates at higher priority than Rock
                            if 'Grass' in terrain_mix:
                                barrier_type = Forest

                            # Override if cell neighbours water, Shore generates at highest priority
                            if None in terrain_mix:
                                barrier_type = Shore


                            new_graph_entry = [cell_id] if detected_cell is None else [cell_id, detected_cell_id]


                            self.terrain_features.append(barrier_type(barrier_pos, barrier_orientation))
                            self.terrain_graph.append(new_graph_entry)



            # Remove any links created that do not have valid return path (if any)
            #self.graph[index] = list(x for x in self.graph[index] if index in self.graph[x])


    def map_neighbours(self, cell, distance):
        neighbour_map = {cell: 0}
        for graph_link in range(1,distance+1):
            for cell_key in neighbour_map.keys():
                neighbour_map.update({neighbour_cell: graph_link} for neighbour_cell in self.graph[cell_key]
                                     if neighbour_cell not in neighbour_map.keys())

        return neighbour_map


    def cell_at_position(self, position):
        for cell in self.map:
            if cell is None:
                continue
            if cell.position == position:
                return cell
        return None


    def purge_sea_level(self):
        # Remove tiles calculated to be below sea level
        self.map = [x if x.elevation > sea_level else None for x in self.map]
        # Update graph for removed tiles
        self.graph = [self.graph[x] if self.map[x] is not None else [] for x in range(0, len(self.map))]
        for index in range(0, len(self.graph)):
            self.graph[index] = [x for x in self.graph[index] if self.map[index] is not None]


    def print_graph(self):
        for index in range(0, len(self.graph)):
            if self.map[index] is not None:
                print ('{}, {}: {}'.format(index, self.map[index].position, self.graph[index]))
