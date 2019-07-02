import struct

from constants import *

class Projectile (object):
    def __init__(self,x,y,facing,speed,faction,damage,distance,source,effect=-1,dot=None, delayed_damage_effect=None, color='white', move_x = 0, move_y = 0):
        self.pos_x = x
        self.pos_y = y
        self.true_pos_x = float(x)
        self.true_pos_y = float(y)
        self.facing = facing # 0 - up, 1 - right, 2 - down, 3 - left, 4 - special angle, uses coordinates
        self.move_x = float(move_x)
        self.move_y = float(move_y)
        self.speed = int(speed*(float(tile_size)/32))
        self.faction = faction #0 for player, 1 for monster
        self.damage = damage
        self.distance = distance
        self.effect = effect #0 for OLD curse, 1 for OLD poison, 2 for increased aggro, 3 for aoe 64 range, 4 for 75% vulnerability, 5 for Essence Theft (+3chain effect)
        #6 for Distract (70% vulnerability, prevents next 65 damage dealt), 7 for Kindling Strike (250% vulnerability), 8 for Uncanny Expertise (+2chain), 9 for aoe 128 range
        #10 for paralysis for 4 seconds
        self.source = source
        self.dot = dot
        self.color = color
        self.delayed_damage_effect = delayed_damage_effect
    def move(self,game):
        table = [self.move_up,self.move_right,self.move_down,self.move_left,self.move_special]
        table[self.facing](game)
        self.distance-=self.speed
    def move_up(self,game):
        if (not game.is_wall_exact(self.pos_x,self.pos_y-self.speed)) and (not game.is_door_exact(self.pos_x,self.pos_y-self.speed)):
            self.pos_y-=self.speed
        else:
            self.distance = 0
    def move_right(self,game):
        if not game.is_wall_exact(self.pos_x+self.speed,self.pos_y) and (not game.is_door_exact(self.pos_x+self.speed,self.pos_y)):
            self.pos_x+=self.speed
        else:
            self.distance = 0
    def move_down(self,game):
        if not game.is_wall_exact(self.pos_x,self.pos_y+self.speed) and (not game.is_door_exact(self.pos_x,self.pos_y+self.speed)):
            self.pos_y+=self.speed
        else:
            self.distance = 0
    def move_left(self,game):
        if not game.is_wall_exact(self.pos_x-self.speed,self.pos_y) and (not game.is_door_exact(self.pos_x-self.speed,self.pos_y)):
            self.pos_x-=self.speed
        else:
            self.distance = 0
    def move_special(self,game):
        if not game.is_wall_exact(int(self.true_pos_x+self.move_x),int(self.true_pos_y+self.move_y)) and not game.is_door_exact(int(self.true_pos_x+self.move_x),int(self.true_pos_y+self.move_y)):
            self.true_pos_x += self.move_x
            self.true_pos_y += self.move_y
            self.pos_x = int(self.true_pos_x)
            self.pos_y = int(self.true_pos_y)
        else:
            self.distance = 0
    def to_JSON(self):
        return '{0},{1},{2},{3},{4},{5},{6}'.format(self.pos_x,self.pos_y,self.facing,self.speed,self.faction,self.damage,self.color)
    def to_binary(self):
        return struct.pack('!II7s',self.pos_x,self.pos_y,self.color)
class DotEffect(object):
    def __init__(self, dps, time):
        self.dps = dps
        self.time = time
class DelayedDamageEffect(object):
    def __init__(self, damage, time, source, backstab):
        self.damage = damage
        self.time = time
        self.source = source
        self.backstab = backstab
