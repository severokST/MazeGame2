from random import randrange

# PC or NPC entity
class Actor(object):
    def __init__(self):
        self.attributes = set()
        self.health = (1,1)
        self.location = None
        self.stats = {}

    def set_location(self,location):
        self.location = location

    def update(self):
        if self.health[0] <= 0:
            return 'kill'


class Mob(Actor):
    def __init__(self):
        Actor.__init__(self)
        self.drops = {}

    def __del__(self):
        for item in self.drops:
            if randrange(100) > self.drops[item]:
                #spawn item
                pass



            



class E1(Mob):
    def __init__(self):
        self.HP = (10,10)
        self.attributes = set('Hostile')

    def update(self):
        Actor.update(self)



class Animal(Mob):
    def __init__(self):
        self.HP = (2,2)
        self.attributes = set('Passive')
        self.drops = {'fur': 20, 'meat':40}

    def update(self):
        Actor.update(self)


class Player(Actor):
    def __init__(self, load):
        Actor.__init__(self)
        if load is None:
            self.location = (0,0)
            self.HP = (5,5)
            self.skills = {}
        # Todo, Else open save file and reload player stats
