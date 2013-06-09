from random import randint, choice

def _neighbours(x,y):
    return list(filter(lambda a: a != (x,y)
                                 and a[0] > 0 and a[0] <= 10
                                 and a[1] > 0 and a[1] <= 10,
                       [(xi,yi)
                        for xi in range(x-1,x+2)
                        for yi in range(y-1,y+2)]))

def _dneighbours(x,y):
    return list(filter(lambda a: a[0] != x and a[1] != y, _neighbours(x,y)))

def _xneighbours(x,y):
    return list(filter(lambda a: a[0] == x or a[1] == y, _neighbours(x,y)))

class Cell:
    def __init__(self):
        self.the_ship = None
        self.shooted = False

    def ship(self,x,y,ship,field):
        if not self.the_ship is None:
            raise IndexError('Some ships are misplaced')
        self.the_ship = ship
        for neighbour in filter(lambda a: a.the_ship != ship,
                                [field.cell(xi,yi)
                                 for xi,yi in _neighbours(x,y)]):
            if neighbour.the_ship != None:
                raise IndexError('Some ships are misplaced')
        self.dneighbours = [field.cell(xi,yi) for xi,yi in _dneighbours(x,y)]
        return self

    def shoot(self):
        if self.shooted:
            return None
        else:
            self.shooted = True
            if self.the_ship is None:
                return None
            else:
                for cell in self.dneighbours:
                    if not cell.shooted: cell.shoot()
                return self.the_ship.shoot()

class Ship:
    def __init__(self,n,x,y,direction,field):
        self.alive = True
        self.cells = [field.cell(xi,yi).ship(xi,yi,self,field)
                      for xi in range(x,x+n*direction+(1-direction))
                      for yi in range(y,y+n*(1-direction)+direction)]
        self.neighbours = [field.cell(xi,yi) for xi,yi in _xneighbours(x,y)] + \
                          [field.cell(xi,yi)
                           for xi,yi in _xneighbours(x+(n-1)*direction,
                                                     y+(n-1)*(1-direction))]

    def shoot(self):
        if all(map(lambda cell: cell.shooted, self.cells)):
            self.alive = False
            for cell in self.neighbours:
                if not cell.shooted: cell.shoot()
            return True
        else:
            return False

class Field:
    def __init__(self,ships):
        self.field = [[Cell() for i in range(0,10)] for j in range(0,10)]
        self.good = True
        try:
            self.ships = [Ship(n,x,y,d,self) for n,x,y,d in ships]
        except:
            self.good = False

    def shoot(self,x,y):
        result = self.cell(x,y).shoot()
        if   result is None: return False
        elif result == True: return True
        else:                return (x,y)

    def cell(self,x,y):
        return self.field[y-1][x-1]

    def cleared(self):
        return not any(map(lambda ship: ship.alive, self.ships))
    
    def serialize(self,openp=False):
        if openp:
            return [[0 if self.cell(x,y).shooted and
                     self.cell(x,y).the_ship is None else
                     1 if self.cell(x,y).shooted and
                     self.cell(x,y).the_ship is not None else
                     -0.5 if not self.cell(x,y).shooted and
                     self.cell(x,y).the_ship is None else -1
                     for x in range(1,11)]
                    for y in range(1,11)]
        else:
            return [[0.5 if not self.cell(x,y).shooted else
                     0 if self.cell(x,y).the_ship is None else 1
                     for x in range(1,11)]
                    for y in range(1,11)]

def randomPlace():
    placement = []
    for ship in [4,3,3,2,2,2,1,1,1,1]:
        while True:
            temp_ship = (ship,randint(1,10),randint(1,10),randint(0,1))
            temp_field = Field(placement + [temp_ship])
            if temp_field.good:
                placement.append(temp_ship)
                break
    return placement

class RandomShooter:
    def __init__(self):
        self.toshoot = []

    def shoot(self,field,last=None):
        if last is not None:
            self.toshoot = self.toshoot + _xneighbours(last[0],last[1])
        if any(map(lambda cell: field[cell[1]-1][cell[0]-1] == 0.5,
                   self.toshoot)):
            while True:
                x,y = choice(self.toshoot)
                if field[y-1][x-1] == 0.5:
                    return (x,y)
        else:
            self.toshoot = []
            while True:
                x = randint(1,10)
                y = randint(1,10)
                if field[y-1][x-1] == 0.5:
                    return (x,y)

def _my_net(n,startx):
    starty = 1
    a = []
    for pos in range(0,10):
        the_min = min(10-startx,10-starty)
        for inc in range(0,the_min+1):
            a.append((startx+inc,starty+inc))
        startx = startx - starty + 1 - n
        if startx < 1:
            starty = 2 - startx
            startx = 1
    return a

class SystematicShooter:
    def __init__(self):
        startx = [(7,9), (8,10)]
        seed1 = randint(0,1)
        seed2 = randint(0,1)
        self.toshoot = _my_net(4,startx[seed1][seed2]) + \
                       _my_net(4,startx[seed1][1 - seed2]) + \
                       _my_net(4,startx[1 - seed1][seed2]) + \
                       _my_net(4,startx[1 - seed1][1 - seed2])
        if randint(0,1): self.toshoot = [(cell[1],cell[0])
                                      for cell in self.toshoot]
        if randint(0,1): self.toshoot = list(reversed(self.toshoot))
        self.toshootfirst = []

    def shoot(self,field,last=None):
        if last is not None:
            self.toshootfirst = self.toshootfirst + \
                                _xneighbours(last[0],last[1])
        if any(map(lambda cell: field[cell[1]-1][cell[0]-1] == 0.5,
                   self.toshootfirst)):
            while True:
                x,y = self.toshootfirst[0]
                self.toshootfirst = self.toshootfirst[1:]
                if field[y-1][x-1] == 0.5:
                    return (x,y)
        else:
            self.toshootfirst = []
            while True:
                x,y = self.toshoot[0]
                self.toshoot = self.toshoot[1:]
                if field[y-1][x-1] == 0.5:
                    return (x,y)

def _consistent_ships(ships):
    return len(ships) == 10 and\
           all(map(lambda x: len(x) == 4, ships)) and\
           [1,1,1,1,2,2,2,3,3,4] == list(sorted(map(lambda x: x[0],ships))) and\
           Field(ships).good

class Player:
    def __init__(self,shooter=None,ships=None):
        self.shooter = shooter
        if ships == None:
            ships = randomPlace()
        elif not _consistent_ships(ships):
            raise RuntimeError('Ships placement is wrong')
        self.field = Field(ships)

class Game:
    def __init__(self,player1,player2):
        if player1 == player2:
            raise RuntimeError('You can not play with yourself')
        self.players = (player1,player2)
        self.winner = None
        self.current = player1
        self.other = player2
        if randint(0,1) == 1:
            self.current, self.other = self.other, self.current
        self.turn_n = 0
        self.ask(self.current,self.other.field.serialize())

    def ask(self,player,field,last=None):
        if player.shooter is not None:
            tx,ty = player.shooter.shoot(field,last)
            self.turn(player,tx,ty)

    def turn(self,player,x,y):
        if self.winner is not None or player != self.current:
            return
        result = self.other.field.shoot(x,y)
        if result == False:
            result = None
            self.turn_n += 0.5
            self.current, self.other = self.other, self.current
        if result == True:
            result = None
            if self.other.field.cleared():
                self.winner = self.current
                return
        self.ask(self.current,self.other.field.serialize(),result)

    def watch(self,player=None):
        if self.current == player:
            return (True,
                    self.current.field.serialize(True),
                    self.other.field.serialize())
        elif self.other == player:
            return (False,
                    self.other.field.serialize(True),
                    self.current.field.serialize())
        else:
            return (self.current == self.players[0],
                    self.players[0].field.serialize(),
                    self.players[1].field.serialize())
