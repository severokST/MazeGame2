# Depriciated class, Kept for reference in case some features need to be re-instated.
class Location(object):
    def __init__(self, type):
        self.type = type
        self.name = ''
        self.tags = set()
        # List of dropped items in this location
        self.items = []
        # List of existing NPCs
        self.npc = []
        # List of Terrain features
        self.features = []

        # List of potential spawning Mobs, [(Reference, probability weight)]
        self.spawnlist = {'day': [], 'night': []}
        self.gen_bias = {'Grass': 0.1, 'Rock': 0.1, 'Water': 0.1}
        self.feature_spawn = {}

    def spawn_features(self):
        if len(feature_types) == 0:
            return None
        spawn_choice_list = list(key for key in self.feature_spawn.keys())
        spawn_weight_list = list(x for key, x in self.feature_spawn.items())
        spawn_chance = sum(spawn_weight_list)
        if randrange(1000) / 1000 < spawn_chance:
            return None

        return choice(spawn_choice_list, 1, spawn_weight_list)[0]

    def look_type(self):
        return self.type

    def features_none(self):
        return len(self.features) == 0


class TileFeature(object):
    def __init__(self):
        self.dx, self.dy = randrange(10), randrange(10)
        self.spawn_chance = {}

class Tree(TileFeature):
    def __init__(self):
        TileFeature.__init__(self)


class Feature_spawn():
    def __init__(self):
        self.spawn_chance = {}
        pass

    def spawn_avaliability(self, terrain):
        return self.spawn_chance(terrain,0)

class Tree_Spawn(object):
    def __init__(self):
        self.name = 'tree'
        self.spawn_chance = {'Grass': 0.001}
        self.spawn_quantity_range = (1, 50)
        self.object = Tree

# dict of potential features
feature_types = {'tree':{Tree_Spawn()}}

class World(object):
    def __init__(self, save):
        #self.position = (0,0)
        feature_list = {}

        if save is None:
            self.map = {}
            self.location = (0,0)
            self.build_new()

    def build_new(self):
        self.map = {(0,0): Grass()}
        self.enter((0,0))

        build_keys = set()
        next_build_keys = set()
        tile_feature_dict = {}

        for x, y in ndindex(3, 3):
            new_build_index = (x-1, y-1)
            if new_build_index not in self.map.keys():
                next_build_keys.add((x-1, y-1))

        build_pass = 0
        #quota_fill = sum(list(x[0] for key, x in location_quota.items()))
        while(sum(list(x[0] for key, x in location_quota.items())) > 10) and len(next_build_keys)>0:
            build_pass += 1
        #for build_pass in range(0,10):
            build_key_list = list(x for x in next_build_keys)
            if len(build_key_list) == 1:
                build_key = build_key_list[0]
            else:
                try:
                    build_key = choice(build_key_list,1)[0]
                except ValueError:
                    print(build_key_list)
            next_build_keys.remove(build_key)
            for new_build_key in self.spawn_location(build_key):
                if new_build_key not in self.map.keys():
                    next_build_keys.add(new_build_key)

            #print(build_pass, len(new_build_key), location_quota)
            #for x, y in ndindex(200, 200):
            #    self.spawn_location((100-x, 100-y))

        for key in self.map:
            terrain_type = self.map[key].type
            potential_terrains = {pt.name: pt.spawn_chance[terrain_type] for key, pt in feature_types
                                  if pt.spawn_avaliability(terrain_type) }




        print(tile_feature_dict)
        tile_feature_dict = {k:v for k,v in tile_feature_dict.items() if v is not None}

        print(tile_feature_dict)


    def enter(self, position):

        for direction_key in directions.keys():
            connect_key = connecting_key(position, direction_key)
            # Check if exists, generate if does not
            connected_cell = self.map.get(connect_key, self.spawn_location(connect_key))
            # Check for spawns, generate if empty

        try:
            if 'Impassable' not in self.map[position].tags:
                return position
        except KeyError:
            return None

            # Check surrounding areas exist
    def spawn_location(self, connect_key):

        if connect_key in self.map.keys():
            return

        probability_weight = {k:0 for k in location_types.keys()}

        for x, y in ndindex(21, 21):
            neighbour_key = (connect_key[0] + (x-10), connect_key[1] + (y-10))
            try:
                for key, weight in self.map[neighbour_key].gen_bias.items():
                    probability_weight[key] += weight
            except:
                pass

        tile_list = []
        weight_list = []
        for key, weight in probability_weight.items():
            tile_list.append(key)
            apply_quota = location_quota.get(key, (1,1))
            weight_list.append(weight * (apply_quota[0]/apply_quota[1]) if weight > 0 else 0)

        if sum(weight_list) == 0:
            return

        weight_list = [x/sum(weight_list) for x in weight_list]
        terrain = choice(tile_list,1, p=weight_list)[0]

        build_key_list = []
        build_key_list.append(connect_key)
        biome_size_range = location_size.get(terrain, (1,2))
        biome_size = randrange(biome_size_range[0], biome_size_range[1])

        for biome_step in range(0,biome_size):
            build_key = build_key_list.pop(randrange(0,len(build_key_list)))

            try:
                location_quota[terrain][0] -= 1 if location_quota[terrain][0] > 0 else 0
            except KeyError:
                pass
            self.map[build_key]=location_types[terrain]()

            for x,y in ndindex(3,3):
                neighbour_key = (build_key[0]+(x-1), build_key[1]+(y-1))
                if neighbour_key not in self.map.keys() and neighbour_key not in build_key_list:
                    build_key_list.append((build_key[0]+(x-1), build_key[1]+(y-1)))

            if len(build_key_list) == 0:
                break

        return build_key_list


    def local_map(self, location, distance):
        local = {}
        for x, y in ndindex(distance + 5, distance + 5):
            dx, dy = x - int((distance+5)/2), y - int((distance+5)/2)
            load_location = (location[0] + dx, location[1] + dy)
            local[(dx,dy)] = self.map.get(load_location, self.spawn_location(load_location))


        #local = {(key[0]-location[0],key[1]-location[1]):value for key, value in self.map.items()
        #         if -distance <= key[0] - location[0] <=distance and -distance <= key[1] - location[1] <= distance }
        return local

