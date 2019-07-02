import random
import thread
import Queue
from projectile import Projectile, DotEffect, DelayedDamageEffect
from utils import *
import math
# import cProfile
# import StringIO
# import pstats
# from multiprocessing import Process, Pipe
import uuid
# from numba import jit, jitclass, int8, int16, int32, float64, boolean
import heapq
# import time
import sys
import struct

from floating_text import FloatingText
from cards import Card
from constants import *

class Monster (object):
    @staticmethod
    def from_save_data(data, game):
        ClassNeeded = getattr(sys.modules[__name__], data['actual_python_class'])
        mob = ClassNeeded(game, data['pos_x'], data['pos_y'], data['floor'], data['level'], data['mob_class'])
        mob.damage_cushion = data['damage_cushion']
        mob.facing = data['facing']
        mob.movement_goal_x = data['movement_goal_x']
        mob.movement_goal_y = data['movement_goal_y']
        mob.ultimate_goal_x = data['ultimate_goal_x']
        mob.ultimate_goal_y = data['ultimate_goal_y']
        mob.chain = data['chain']
        mob.idle_behavior = data['idle_behavior']
        return mob

    # times = []
    idle_lock = False
    def __init__(self,game,x,y,floor,level,mob_class):
        self.initialize_passed_variables(game,x,y,floor,level,mob_class)
        self.initialize_stats()
        self.initialize_adjust_stats_for_level()
        self.initialize_adjust_stats_for_mob_class()
        self.initialize_adjust_stats_for_multiplier()
        self.initialize_secondary_stats()
        self.initialize_pathfinding_variables()
        # self.initialize_drops()
        # self.dots = [DotEffect(1,1)]
        self.dots = []
        # self.delayed_damage_effects = [DelayedDamageEffect(1,1,None, False)]
        self.delayed_damage_effects = []
        # self.parent_mgx, self.nothing1 = Pipe()
        # self.parent_mgy, self.nothing2 = Pipe()
        # self.parent_ugx, self.nothing3 = Pipe()
        # self.parent_ugy, self.nothing4 = Pipe()
        # self.parent_chain, self.nothing5 = Pipe()
        self.uuid = str(uuid.uuid4())
        # self.p = None
        self.initialize_idle_behavior()
        self.idle_move_stymied = False
        self.hearing = 15
        self.sense_of_smell = 20
    def initialize_passed_variables(self,game,x,y,floor,level,mob_class):
        self.game = game
        self.pos_x = x
        self.pos_y = y
        self.floor = floor
        self.level = level
        self.mob_class = mob_class
    def initialize_stats(self):
        self.aggro_radius = (tile_size*8)+tile_size
        # self.aggro = [AggroEntry(None, 1)]
        self.aggro = []
        self.gcd = 0
        self.hp = 40
        self.max_hp = float(40)
        self.xp = float(12)
        self.attack_power = float(8)
        self.multiplier = 0.5
        self.player_strength = 1
        self.visible = True
        self.damage_cushion = 0
    def initialize_adjust_stats_for_level(self):
        for i in range(1,self.level):
            self.max_hp=self.max_hp*1.1
            self.attack_power=self.attack_power*1.1
            self.xp=self.xp*1.1*1.1
            self.multiplier=self.multiplier+0.01
    def initialize_adjust_stats_for_mob_class(self):
        table = [self.initialize_mob_class_normal,self.initialize_mob_class_strong,self.initialize_mob_class_elite,self.initialize_mob_class_miniboss,self.initialize_mob_class_boss]
        table[self.mob_class]()
    def initialize_mob_class_normal(self):
        return
    def initialize_mob_class_strong(self):
        self.multiplier = 1-((1-self.multiplier)/2)
    def initialize_mob_class_elite(self):
        self.multiplier = 1
    def initialize_mob_class_miniboss(self):
        self.max_hp = self.max_hp*2.54
        self.attack_power = self.attack_power*2.54
        self.xp*=2.54*2.54
        self.multiplier = 1-((1-self.multiplier)/2)
    def initialize_mob_class_boss(self):
        self.max_hp = self.max_hp*3.3
        self.attack_power = self.attack_power*3.3
        self.xp*=3.3*3.3
        self.multiplier = 1
    def initialize_adjust_stats_for_multiplier(self):
        self.max_hp = int(self.max_hp * self.multiplier)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power * self.multiplier)
        self.xp = int(self.xp * self.multiplier)
    def initialize_secondary_stats(self):
        self.autoheal_cd = 0
        # self.effects = [0]
        self.effects = [] # 0 - vulnerability 15%, 1 - OLD poison, 2 - vulnerability 75%, 3 - vulnerability 70%, 4 - vulnerability 250%, 5 - paralysis
        # self.effects_duration = [0]
        self.effects_duration = [] # in ticks
    def initialize_pathfinding_variables(self):
        self.facing = 0
        self.movement_goal_x = self.pos_x
        self.movement_goal_y = self.pos_y
        self.ultimate_goal_x = self.pos_x
        self.ultimate_goal_y = self.pos_y
        self.chain_modify = False
        self.success = False
        self.processing = False
        # self.chain=[(0,0)]
        self.chain = []
        self.chosen_tick = random.randint(0,59) # 59
    # def initialize_drops(self):
    #     self.drops = []
    #     for i in range(random.randint(0,2*self.player_strength)):
    #         self.drops.append(random_drop())
    def initialize_idle_behavior(self):
        # 0 - idle (default), 1 - patrol, 2 - wanderer, 3 - explorer
        # difficulty getting patrol to work
        roll = random.randint(1,100)
        if roll<=90:
            self.idle_behavior = 0
        elif roll<=95:
            self.idle_behavior = 2
        else:
            self.idle_behavior = 3
    def initialize_patrol_routes(self):
        original_pos_x = self.pos_x
        original_pos_y = self.pos_y
        dest_x = self.pos_x
        dest_y = self.pos_y
        calc_success = False
        simple_line = False
        tries = 0
        while dest_x<tile_size or dest_y<tile_size or dest_x>self.game.map.size_x-tile_size or dest_y>self.game.map.size_y-tile_size or self.game.map.tiles[dest_x/tile_size][dest_y/tile_size]!=' ' or (dest_x==self.pos_x and dest_y==self.pos_y) or not calc_success or simple_line:
            tries += 1
            if tries>1000:
                self.idle_behavior = 0
                self.pos_x = original_pos_x
                self.pos_y = original_pos_y
                print 'failure'
                return False
            dest_x = ((self.pos_x/tile_size) + random.randint(1,(self.game.map.size_x/tile_size)-2))*tile_size
            dest_y = ((self.pos_y/tile_size) + random.randint(1,(self.game.map.size_y/tile_size)-2))*tile_size
            if dest_x<tile_size or dest_y<tile_size or dest_x>self.game.map.size_x-tile_size or dest_y>self.game.map.size_y-tile_size or self.game.map.tiles[dest_x/tile_size][dest_y/tile_size]!=' ':
                continue
            calc_success, simple_line, came_from, current, start = self.calculate_idle(dest_x,dest_y)
        self.patrol_1_data = (dest_x,dest_y)
        self.pos_x = dest_x
        self.pos_y = dest_y
        dest_x = self.pos_x
        dest_y = self.pos_y
        calc_success = False
        simple_line = False
        tries = 0
        while dest_x<tile_size or dest_y<tile_size or dest_x>self.game.map.size_x-tile_size or dest_y>self.game.map.size_y-tile_size or self.game.map.tiles[dest_x/tile_size][dest_y/tile_size]!=' ' or (dest_x==self.pos_x and dest_y==self.pos_y) or not calc_success or simple_line:
            tries += 1
            if tries>1000:
                self.idle_behavior = 0
                self.pos_x = original_pos_x
                self.pos_y = original_pos_y
                print 'failure'
                return False
            dest_x = ((self.pos_x/tile_size) + random.randint(1,(self.game.map.size_x/tile_size)-2))*tile_size
            dest_y = ((self.pos_y/tile_size) + random.randint(1,(self.game.map.size_y/tile_size)-2))*tile_size
            if dest_x<tile_size or dest_y<tile_size or dest_x>self.game.map.size_x-tile_size or dest_y>self.game.map.size_y-tile_size or self.game.map.tiles[dest_x/tile_size][dest_y/tile_size]!=' ':
                continue
            calc_success, simple_line, came_from, current, start = self.calculate_idle(dest_x,dest_y)
        self.patrol_2_data = (dest_x,dest_y)
        self.patrol_state = 2
        self.pos_x = original_pos_x
        self.pos_y = original_pos_y
        print 'success'
        return True
    def increase_player_strength(self):
        old_strength = self.player_strength
        new_strength = old_strength+1
        self.player_strength = new_strength
        self.max_hp = int(float(self.max_hp)*(math.sqrt(float(new_strength)/float(old_strength))))
        self.hp = self.max_hp
        self.attack_power = int(float(self.attack_power)*(math.sqrt(float(new_strength)/float(old_strength))))
    def decrease_player_strength(self):
        old_strength = self.player_strength
        new_strength = old_strength-1
        self.player_strength = new_strength
        self.max_hp = int(float(self.max_hp)*(math.sqrt(float(new_strength)/float(old_strength))))
        self.hp = self.max_hp
        self.attack_power = int(float(self.attack_power)*(math.sqrt(float(new_strength)/float(old_strength))))
    def left(self):
        return self.pos_x
    def right(self):
        return self.pos_x+(tile_size-1)
    def top(self):
        return self.pos_y
    def bottom(self):
        return self.pos_y+(tile_size-1)
    def take_hit(self,damage,source):
        damage = self.take_hit_damage_multipliers(damage)
        self.take_hit_apply_damage(damage,source)
    def take_hit_damage_multipliers(self,damage):
        if 0 in self.effects:
            damage=damage*1.15
        if 2 in self.effects:
            damage=damage*1.75
        if 3 in self.effects:
            damage=damage*1.7
        if 4 in self.effects:
            damage=damage*3.5
        return damage
    def take_hit_apply_damage(self,damage,source):
        self.hp-=int(damage)
        self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,str(damage),'orange'))
        if not source.improved_invisibility:
            self.aggro_increment(source,damage)
        source.target = self
    def aggro_increment(self,source,damage):
        for entry in self.aggro:
            if entry.char==source:
                entry.value+=damage
                return
        self.aggro.append(AggroEntry(source,damage))
        if self not in self.game.active_monsters:
            self.game.active_monsters.append(self)
    def aggro_increment_if_aggrod(self,source,damage):
        for entry in self.aggro:
            if entry.char==source:
                entry.value+=damage
                return
    def aggro_set(self,source,damage):
        for entry in self.aggro:
            if entry.char==source:
                entry.value=damage
                return
        self.aggro.append(AggroEntry(source,damage))
        if self not in self.game.active_monsters:
            self.game.active_monsters.append(self)
    def aggro_get(self,char):
        for entry in self.aggro:
            if entry.char==char:
                return entry.value
        return 0
    def apply_effect(self, effect, source):
        if effect==0:
            self.effects.append(0)
            self.effects_duration.append(10*60)
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'VULNERABLE','orange'))
        elif effect==1:
            self.effects.append(1)
            self.effects_duration.append(9*60)
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'POISON','orange'))
        elif effect==4:
            self.effects.append(2)
            self.effects_duration.append(10*60)
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'VULNERABLE','orange'))
        elif effect==6:
            self.effects.append(3)
            self.effects_duration.append(10*60)
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'VULNERABLE','orange'))
            self.damage_cushion = 65
            self.aggro_increment(source, 65)
        elif effect==7:
            self.effects.append(4)
            self.effects_duration.append(10*60)
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'VULNERABLE','orange'))
        elif effect==10:
            self.effects.append(5)
            self.effects_duration.append(4*60)
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'PARALYSIS','orange'))
    def attack(self,char):
        if self.gcd==0:
            self.attack_deliver_blow(char)
            self.game.sounds.append('attack')
            self.gcd=90
    def attack_deliver_blow(self,char):
        self.game.make_noise(self.pos_x,self.pos_y, 20)
        self.face_character(char)
        char.take_hit(self.damage_after_cushion())
        char.remove_stealth()
        text = 'A'
        if self.name[0] in ['A','E','I','O','U','a','e','i','o','u']:
            text+='n'
        text+=' '+self.name+' attacks you, dealing '+str(self.attack_power)+' damage.'
        char.handler.push_narration(text)
        if char.hp<=0:
            char.alive = False
    def damage_after_cushion(self):
        damage_dealt = max(self.attack_power - self.damage_cushion, 0)
        self.damage_cushion = max(self.damage_cushion - self.attack_power, 0)
        return damage_dealt
    def face_character(self,char):
        if abs(self.pos_x-char.pos_x)>abs(self.pos_y-char.pos_y):
            if self.pos_x>char.pos_x:
                self.facing=3
            else:
                self.facing=1
        else:
            if self.pos_y>char.pos_y:
                self.facing=0
            else:
                self.facing=2
    def tick(self,chars,tick):
        if self.game.floor!=self.floor:
            return
        self.tick_apply_poison_and_decrement_effects()
        if 5 not in self.effects:
            if self.aggro==[]:
                self.tick_idle(tick)
                self.tick_idle_move()
            char = self.tick_determine_target_and_move(chars,tick)
            self.tick_attempt_attack(char)
        self.tick_dots()
        self.tick_delayed_damage_effects()
    def tick_idle(self, tick):
        loops = [self.tick_idle_idle,self.tick_idle_patrol_loop,self.tick_idle_wanderer_loop,self.tick_idle_explorer_loop]
        if self.idle_behavior==1:
            print self.pos_x, self.pos_y, self.ultimate_goal_x, self.ultimate_goal_y, self.movement_goal_x, self.movement_goal_y
        if tick==self.chosen_tick and not self.processing:
            if (abs(self.pos_x-self.ultimate_goal_x)<=tile_size and abs(self.pos_y-self.ultimate_goal_y)<=tile_size) or self.idle_move_stymied:
                thread.start_new_thread(loops[self.idle_behavior],())
    def tick_idle_move(self):
        if self.movement_goal_x!=self.pos_x or self.movement_goal_y!=self.pos_y:
            self.move_x_and_y()
        else:
            self.move_get_next_destination()
    def tick_idle_idle(self):
        pass
    def tick_idle_patrol_loop(self):
        print 'ran'
        self.processing = True
        if self.patrol_state==1:
            print 'patrol_state 2'
            self.patrol_state = 2
            patrol_var = self.patrol_2_data
        elif self.patrol_state==2:
            print 'patrol_state 1'
            self.patrol_state = 1
            patrol_var = self.patrol_1_data
        print patrol_var
        calc_success, trash, came_from, current, start = self.calculate_idle(patrol_var)
        if calc_success and not simple_line:
            print 'calculate success'
            self.ultimate_goal_x, self.ultimate_goal_y = dest_x, dest_y
            self.calculate_on_success(came_from, current, start)
        elif calc_success:
            print 'calculate success'
            self.movement_goal_x = self.ultimate_goal_x = dest_x
            self.movement_goal_y = self.ultimate_goal_y = dest_y
        self.processing = False

    def tick_idle_wanderer_loop(self):
        self.processing = True
        # Monster.idle_lock = True
        dest_x = self.pos_x
        dest_y = self.pos_y
        calc_success = False
        simple_line = False
        attempts = 0
        while dest_x<tile_size or dest_y<tile_size or dest_x>self.game.map.size_x-tile_size or dest_y>self.game.map.size_y-tile_size or self.game.map.tiles[dest_x/tile_size][dest_y/tile_size]!=' ' or (dest_x==self.pos_x and dest_y==self.pos_y) or not calc_success or not simple_line:
            attempts +=1
            if attempts > 1000:
                break
            dest_x = ((self.pos_x/tile_size) + random.randint(-8,8))*tile_size
            dest_y = ((self.pos_y/tile_size) + random.randint(-8,8))*tile_size
            # calc_success, simple_line, came_from, current, start = self.calculate_idle(dest_x,dest_y)
            if self.find_line_to_position(dest_x,dest_y):
                calc_success, simple_line = True, True
        if calc_success and not simple_line and attempts <= 1000:
            # self.calculate_on_success(came_from, current, start)
            pass
        elif calc_success and attempts <= 1000:
            self.movement_goal_x = self.ultimate_goal_x = dest_x
            self.movement_goal_y = self.ultimate_goal_y = dest_y
        self.processing = False
        # Monster.idle_lock = False
    def tick_idle_explorer_loop(self):
        self.processing = True
        # Monster.idle_lock = True
        dest_x = self.pos_x
        dest_y = self.pos_y
        calc_success = False
        simple_line = False
        attempts = 0
        while dest_x<tile_size or dest_y<tile_size or dest_x>self.game.map.size_x-tile_size or dest_y>self.game.map.size_y-tile_size or self.game.map.tiles[dest_x/tile_size][dest_y/tile_size]!=' ' or (dest_x==self.pos_x and dest_y==self.pos_y):
            attempts +=1
            if attempts > 1000:
                break
            dest_x = ((self.pos_x/tile_size) + random.randint(-8,8))*tile_size
            dest_y = ((self.pos_y/tile_size) + random.randint(-8,8))*tile_size
            if dest_x<tile_size or dest_y<tile_size or dest_x>self.game.map.size_x-tile_size or dest_y>self.game.map.size_y-tile_size or self.game.map.tiles[dest_x/tile_size][dest_y/tile_size]!=' ':
                continue
            calc_success, simple_line, came_from, current, start = self.calculate_idle(dest_x,dest_y)
        if calc_success and not simple_line and attempts <= 1000:
            self.ultimate_goal_x, self.ultimate_goal_y = dest_x, dest_y
            self.calculate_on_success(came_from, current, start)
        elif calc_success and attempts <= 1000:
            self.movement_goal_x = self.ultimate_goal_x = dest_x
            self.movement_goal_y = self.ultimate_goal_y = dest_y
        self.processing = False
        # Monster.idle_lock = False
    def tick_dots(self):
        for dot in self.dots:
            dot.time = float(dot.time)-(float(1)/float(60))
            self.hp = float(self.hp) - (float(dot.dps)/float(60))
        self.prune_old_dots()
    def tick_delayed_damage_effects(self):
        for delayed_damage_effect in self.delayed_damage_effects:
            delayed_damage_effect.time = float(delayed_damage_effect.time)-(float(1)/float(60))
        self.prune_old_delayed_damage_effects()
    def prune_old_dots(self):
        go_again = False
        for dot in self.dots:
            if dot.time <= 0:
                self.dots.remove(dot)
                go_again = True
                break
        if go_again:
            self.prune_old_dots()
    def prune_old_delayed_damage_effects(self):
        go_again = False
        for delayed_damage_effect in self.delayed_damage_effects:
            if delayed_damage_effect.time <= 0:
                if delayed_damage_effect.backstab and not delayed_damage_effect.source.visible:
                    delayed_damage_effect.damage *= 4
                    delayed_damage_effect.source.visible = True
                self.hp -= delayed_damage_effect.damage
                self.delayed_damage_effects.remove(delayed_damage_effect)
                go_again = True
                break
        if go_again:
            self.prune_old_delayed_damage_effects()
    def tick_apply_poison_and_decrement_effects(self):
        if 1 in self.effects:
            if random.randint(1,1000)<=59:
                self.hp-=1
        self.decrement_effects()
    def tick_determine_target_and_move(self,chars,tick):
        for char in chars:
            self.determine_aggro(char)
        self.prune_aggro_table()
        if self.aggro == []:
            return
        char = self.determine_target()
        self.move(char,tick)
        return char
    def tick_attempt_attack(self,char):
        if char and abs(char.pos_x-self.pos_x)<=tile_size and abs(char.pos_y-self.pos_y)<=tile_size:
        # if char and (abs(self.right()-char.left())<=tile_size or abs(self.left()-char.right()<=tile_size)) and (abs(self.top()-char.bottom())<=tile_size or abs(self.bottom()-char.top()<=tile_size)):
            self.attack(char)
    def prune_aggro_table(self):
        prune_list = []
        for entry in self.aggro:
            if entry.value==0:
                prune_list.append(entry)
        for entry in prune_list:
            self.aggro.remove(entry)
    def determine_target(self):
        highest_char = None
        highest_value = 0
        for entry in self.aggro:
            if entry.value>highest_value and entry.char.visible:
                highest_value = entry.value
                highest_char = entry.char
        return highest_char
    def move(self,char,tick):
        self.move_start_calculate_thread_if_necessary(char,tick)
        # try:
        #     if self.parent_mgx.poll():
        #         self.movement_goal_x = self.parent_mgx.recv()
        #     if self.parent_mgy.poll():
        #         self.movement_goal_y = self.parent_mgy.recv()
        # except:
        #     pass
        if self.movement_goal_x!=self.pos_x or self.movement_goal_y!=self.pos_y:
            self.move_x_and_y()
        else:
            # try:
            #     if self.parent_chain.poll():
            #         self.chain = self.parent_chain.recv()
            # except:
            #     pass
            self.move_get_next_destination()
    def move_x_and_y(self):
        self.idle_move_stymied = True
        self.move_x(self.movement_goal_x)
        self.move_y(self.movement_goal_y)
    def move_get_next_destination(self):
        if len(self.chain)>0:
            item = self.chain.pop(0)
            if item:
                self.movement_goal_x,self.movement_goal_y=item
                self.move_x(self.movement_goal_x)
                self.move_y(self.movement_goal_y)
    def move_start_calculate_thread_if_necessary(self,char,tick):
        # if not self.p:
        #     self.processing = False
        # elif self.p and not self.p.is_alive():
        #     self.processing = False
        # else:
        #     self.processing = True
        if not self.processing:
            if self.game.in_line_of_sight(char,self.game.map.tiles,self.pos_x/tile_size,self.pos_y/tile_size,char_seeing=False):
                if tick==self.chosen_tick:
                    # try:
                    #     if self.parent_ugx.poll():
                    #         self.ultimate_goal_x = self.parent_ugx.recv()
                    #     if self.parent_ugy.poll():
                    #         self.ultimate_goal_y = self.parent_ugy.recv()
                    # except:
                    #     pass
                    if abs(self.ultimate_goal_x-char.pos_x)>tile_size or abs(self.ultimate_goal_y-char.pos_y)>tile_size:
                        # self.parent_mgx, child_mgx = Pipe()
                        # self.parent_mgy, child_mgy = Pipe()
                        # self.parent_ugx, child_ugx = Pipe()
                        # self.parent_ugy, child_ugy = Pipe()
                        # self.parent_chain, child_chain = Pipe()
                        # self.p = Process(target=calculate, args=(self.pos_x, self.pos_y, child_mgx, child_mgy, child_ugx, child_ugy, child_chain, char.pos_x, char.pos_y, (tile_size-1), self.uuid, self.game.mob_data(), self.game.map.tiles, tile_size))
                        # self.p.start()
                        # thread.start_new_thread(self.calculate,(char,(tile_size-1),tile_size/2))
                        thread.start_new_thread(self.calculate,(char,(tile_size-1)))
    def start_calculate_thread_for_sound(self, x, y):
        if not self.processing:
            if abs(self.ultimate_goal_x-x)>tile_size or abs(self.ultimate_goal_y-y)>tile_size:
                thread.start_new_thread(self.sound_calculate_routine,(x,y,tile_size/2))
    def sound_calculate_routine(self, x, y, step=tile_size):
        self.processing = True
        calc_success, simple_line, came_from, current, start = self.calculate_idle(x,y,step=step)
        if calc_success and not simple_line:
            self.ultimate_goal_x, self.ultimate_goal_y = x,y
            self.calculate_on_success(came_from, current, start)
        elif calc_success:
            self.movement_goal_x = self.ultimate_goal_x = x
            self.movement_goal_y = self.ultimate_goal_y = y
        self.processing = False
    # @jit(nogil=True)
    def calculate(self,char,range,step=tile_size):
        # cp = cProfile.Profile()
        # cp.enable()

        # if (not isinstance(self,GoblinArcher)):
        #     self.movement_goal_x,self.movement_goal_y = char.pos_x, char.pos_y
        #     self.ultimate_goal_x,self.ultimate_goal_y = char.pos_x, char.pos_y
        #     self.chain_modify = True
        #     self.chain = []
        #     self.chain_modify = False
        # start_time = time.time()
        if self.name!='Goblin Archer' and self.find_line_to_enemy(char):
            self.movement_goal_x,self.movement_goal_y = char.pos_x, char.pos_y
            self.ultimate_goal_x,self.ultimate_goal_y = char.pos_x, char.pos_y
            self.chain_modify = True
            self.chain = []
            self.chain_modify = False
            return
        else:
            if abs(self.pos_x-char.pos_x)> abs(self.pos_y-char.pos_y):
                try_x, try_y = char.pos_x, self.pos_y
            else:
                try_x, try_y = self.pos_x, char.pos_y
            if self.find_line_to_position(try_x,try_y):
                self.movement_goal_x,self.movement_goal_y = try_x, try_y
                self.ultimate_goal_x,self.ultimate_goal_y = try_x, try_y
                self.chain_modify = True
                self.chain = []
                self.chain_modify = False
                return
        start,goal,frontier,came_from,cost_so_far = self.calculate_set_up_variables(char)
        came_from,current = self.calculate_find_path(frontier,char,range,cost_so_far,came_from,step,goal)
        if self.success:
            self.calculate_on_success(came_from,current,start)
        self.processing = False
        # end_time = time.time()
        # Monster.times.append(end_time-start_time)
        # self.show_average_time()
        # cp.disable()
        # s = StringIO.StringIO()
        # sortby = 'cumulative'
        # ps = pstats.Stats(cp, stream=s).sort_stats(sortby)
        # ps.print_stats()
        # print s.getvalue()
    # def show_average_time(self):
    #     value = 0.0
    #     for item in Monster.times:
    #         value += item
    #     value /= len(Monster.times)
    #     print value
    def calculate_idle(self,dest_x,dest_y,step=tile_size):
        if abs(self.pos_x-dest_x)> abs(self.pos_y-dest_y):
            try_x, try_y = dest_x, self.pos_y
        else:
            try_x, try_y = self.pos_x, dest_y
        if self.find_line_to_position(try_x,try_y):
            return True,True,None,None,None
        start,goal,frontier,came_from,cost_so_far = self.calculate_idle_set_up_variables(dest_x,dest_y)
        came_from,current = self.calculate_idle_find_path(frontier,dest_x,dest_y,cost_so_far,came_from,step,goal)
        if self.success:
            return True,False,came_from,current,start
        else:
            return False,False,None,None,None
    def calculate_idle_set_up_variables(self,dest_x,dest_y):
        self.calculate_idle_set_up_instance_variables(dest_x,dest_y)
        # start = ((self.pos_x/tile_size)*tile_size,(self.pos_y/tile_size)*tile_size)
        start = (self.pos_x, self.pos_y)
        goal = (dest_x,dest_y)
        # frontier = Queue.PriorityQueue()
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        return start,goal,frontier,came_from,cost_so_far
    def calculate_idle_set_up_instance_variables(self,dest_x,dest_y):
        self.processing = True
        self.ultimate_goal_x = dest_x
        self.ultimate_goal_y = dest_y
        self.success=False
    def calculate_idle_find_path(self,frontier,dest_x,dest_y,cost_so_far,came_from,step,goal):
        current = None
        while not frontier.empty():
            current = frontier.get()
            x,y=current
            if x>=dest_x-tile_size and x<=dest_x+tile_size and y>=dest_y-tile_size and y<=dest_y+tile_size:
                self.success=True
                break
            neighbors_func = neighbors_idle
            for next in neighbors_func(current,self,self.game,dest_x,dest_y,step):
                frontier,came_from = self.calculate_step(cost_so_far,current,next,frontier,came_from,goal)
        return came_from,current
    def find_line_to_enemy(self, char):
        x1, y1 = char.pos_x/tile_size, char.pos_y/tile_size
        return (self.flte(x1,y1,1) and self.flte(x1,y1,2) and self.flte(x1,y1,3) and self.flte(x1,y1,4))
    def flte(self, x1, y1, num):
        tiles = self.game.map.tiles
        if not self:
            return False
        x0,y0,dx,dy,sx,sy,xnext,ynext,denom = self.set_up_in_line_of_sight_variables(x1,y1, num)
        while (xnext != x1 or ynext != y1):
            if xnext>=0 and ynext>=0 and xnext<len(tiles) and ynext<len(tiles[0]):
                if tiles[xnext][ynext] in ['W','S','D','@','F','Q','O','H','R']:
                    return False
                if self.mob_in_position(xnext,ynext):
                    return False
                xnext,ynext = self.increment_line_of_sight_variables(xnext,ynext,dx,dy,x0,y0,sx,sy,denom)
        return True
    def find_line_to_position(self, x1, y1):
        x1,y1 = x1/tile_size,y1/tile_size
        return (self.fltp(x1,y1,1) and self.fltp(x1,y1,2) and self.fltp(x1,y1,3) and self.fltp(x1,y1,4))
    def fltp(self, x1, y1, num):
        tiles = self.game.map.tiles
        x0,y0,dx,dy,sx,sy,xnext,ynext,denom = self.set_up_in_line_of_sight_variables(x1,y1,num)
        while (xnext != x1 or ynext != y1):
            if xnext>=0 and ynext>=0 and xnext<len(tiles) and ynext<len(tiles[0]):
                if tiles[xnext][ynext] in ['W','S','D','@','F','Q','O','H','R']:
                    return False
                if self.mob_in_position(xnext,ynext):
                    return False
                xnext,ynext = self.increment_line_of_sight_variables(xnext,ynext,dx,dy,x0,y0,sx,sy,denom)
        return True
    def mob_in_position(self, x, y):
        left = x*tile_size
        top = y*tile_size
        right = left+tile_size
        bottom = top+tile_size
        for mob in self.game.active_monsters:
            if mob == self:
                continue
            if not ((left>mob.right()) or (right<mob.left())):
                if not ((top>mob.bottom()) or (bottom<mob.top())):
                    return True
        return False
    def increment_line_of_sight_variables(self,xnext,ynext,dx,dy,x0,y0,sx,sy,denom):
        if abs(dy*(xnext-x0+sx)-dx*(ynext-y0))/denom<0.5:
            xnext+=sx
        elif abs(dy*(xnext-x0)-dx*(ynext-y0+sy))/denom<0.5:
            ynext+=sy
        else:
            xnext+=sx
            ynext+=sy
        return xnext,ynext
    def set_up_in_line_of_sight_variables(self,x1,y1,num):
        if num==1:
            x0 = (self.pos_x+2)/tile_size
            y0 = (self.pos_y+2)/tile_size
        elif num==2:
            x0 = (self.pos_x+(tile_size-3))/tile_size
            y0 = (self.pos_y+2)/tile_size
        elif num==3:
            x0 = (self.pos_x+2)/tile_size
            y0 = (self.pos_y+(tile_size-3))/tile_size
        elif num==4:
            x0 = (self.pos_x+(tile_size-3))/tile_size
            y0 = (self.pos_y+(tile_size-3))/tile_size
        dx = x1-x0
        dy = y1-y0
        sx,sy = self.set_up_line_of_sight_direction(x0,y0,x1,y1)
        xnext = x0
        ynext = y0
        denom = float(math.sqrt(float(dx)*float(dx)+float(dy)*float(dy)))
        return x0,y0,dx,dy,sx,sy,xnext,ynext,denom
    def set_up_line_of_sight_direction(self,x0,y0,x1,y1):
        if (x0<x1):
            sx=1
        else:
            sx=-1
        if y0<y1:
            sy=1
        else:
            sy=-1
        return sx,sy

    def calculate_find_path(self,frontier,char,range,cost_so_far,came_from,step,goal):
        current = None
        while not frontier.empty():
            current = frontier.get()
            x,y=current
            # if x>=char.pos_x-range+(tile_size-1) and x<=char.pos_x+range and y>=char.pos_y-range+(tile_size-1) and y<=char.pos_y+range:
            if x>=char.pos_x-range and x<=char.pos_x+range and y>=char.pos_y-range and y<=char.pos_y+range:
                self.success=True
                break
            # if monster_in_way(self,self.game,x,y):
            #     neighbors_func = classic_neighbors
            # else:
            #     neighbors_func = neighbors
            neighbors_func = classic_neighbors
            for next in neighbors_func(current,self,self.game,char,step):
                frontier,came_from = self.calculate_step(cost_so_far,current,next,frontier,came_from,goal)
        return came_from,current
    def calculate_step(self,cost_so_far,current,next,frontier,came_from,goal):
        new_cost = cost_so_far[current] + move_cost(current,next)
        if next not in cost_so_far or new_cost < cost_so_far[next]:
            cost_so_far[next] = new_cost
            priority = new_cost + heuristic(goal, next)
            frontier.put(next, priority)
            came_from[next] = current
        return frontier,came_from
    def calculate_on_success(self,came_from,current,start):
        self.chain_modify = True
        self.chain = []
        self.chain.append(current)
        previous=current
        if current!=None:
            self.calculate_build_move_chain(came_from,current,start)
        self.chain_modify = False
    def calculate_build_move_chain(self,came_from,current,start):
        while came_from[current]!=None and came_from[current]!=start:
            previous = current
            current = came_from[current]
            self.chain.append(current)
        self.chain.reverse()
        self.movement_goal_x,self.movement_goal_y = current
    def calculate_set_up_variables(self,char):
        self.calculate_set_up_instance_variables(char)
        # start = ((self.pos_x/tile_size)*tile_size,(self.pos_y/tile_size)*tile_size)
        start = (self.pos_x, self.pos_y)
        goal = (char.pos_x,char.pos_y)
        # frontier = Queue.PriorityQueue()
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        return start,goal,frontier,came_from,cost_so_far
    def calculate_set_up_instance_variables(self,char):
        self.processing = True
        self.ultimate_goal_x = char.pos_x
        self.ultimate_goal_y = char.pos_y
        self.success=False
    def move_x(self,x):
        if abs(x-self.pos_x)>0:
            if (x-self.pos_x)<0:
                for i in range(tile_size/32,1,-1):
                    if not self.game.is_wall(self.pos_x-i,self.pos_y) and not self.game.is_collision(self.pos_x-i,self.pos_y,self) and not self.game.is_door(self.pos_x-i,self.pos_y):
                        self.pos_x-=i
                        self.facing = 3
                        self.idle_move_stymied = False
                        break
            else:
                for i in range(tile_size/32,1,-1):
                    if not self.game.is_wall(self.pos_x+i,self.pos_y) and not self.game.is_collision(self.pos_x+i,self.pos_y,self) and not self.game.is_door(self.pos_x+i,self.pos_y):
                        self.pos_x+=i
                        self.facing = 1
                        self.idle_move_stymied = False
                        break
    def move_y(self,y):
        if abs(y-self.pos_y)>0:
            if (y-self.pos_y)<0:
                for i in range(tile_size/32,1,-1):
                    if not self.game.is_wall(self.pos_x,self.pos_y-i) and not self.game.is_collision(self.pos_x,self.pos_y-i,self) and not self.game.is_door(self.pos_x,self.pos_y-i):
                        self.pos_y-=i
                        self.facing = 0
                        self.idle_move_stymied = False
                        break
            else:
                for i in range(tile_size/32,1,-1):
                    if not self.game.is_wall(self.pos_x,self.pos_y+i) and not self.game.is_collision(self.pos_x,self.pos_y+i,self) and not self.game.is_door(self.pos_x,self.pos_y+i):
                        self.pos_y+=i
                        self.facing = 2
                        self.idle_move_stymied = False
                        break
    def decrement_effects(self):
        if len(self.effects)>0:
            for i in range(len(self.effects)):
                self.effects_duration[i]-=1
                if self.effects_duration[i]==0:
                    self.effects.remove(self.effects[i])
                    self.effects_duration.remove(self.effects_duration[i])
    def determine_aggro(self,char):
        if abs(char.pos_x-self.pos_x)>self.aggro_radius or abs(char.pos_y-self.pos_y)>self.aggro_radius:
            self.aggro_set(char,0)
        elif self.aggro_get(char) == 0 and char.visible and self.game.in_line_of_sight(char,self.game.tiles,self.pos_x/tile_size,self.pos_y/tile_size):
            self.aggro_set(char,1)
            char.autoheal_cd = 180
            self.autoheal_cd = 180
            self.movement_goal_x = self.pos_x
            self.movement_goal_y = self.pos_y
            self.ultimate_goal_x = self.pos_x
            self.ultimate_goal_y = self.pos_y
            self.chain = []
    def apply_dot(self, dot):
        self.dots.append(dot)
    def apply_delayed_damage_effect(self, delayed_damage_effect):
        self.delayed_damage_effects.append(delayed_damage_effect)
    def to_JSON(self):
        return '{0},{1},{2},{3},{4},{5}'.format(self.pos_x,self.pos_y,self.facing,self.mob_class,self.name,self.level)
    def to_binary(self):
        return struct.pack('!IIHh15sH',self.pos_x,self.pos_y,self.facing,self.mob_class,self.name,self.level)
    def to_save_data(self):

        strength_reduction = 0
        if self.player_strength>1:
            for i in range(player_strength-1):
                strength_reduction += 1
                self.decrease_player_strength()

        data = {}
        data['level'] = self.level
        data['mob_class'] = self.mob_class
        data['pos_x'] = self.pos_x
        data['pos_y'] = self.pos_y
        data['floor'] = self.floor
        data['damage_cushion'] = self.damage_cushion
        data['facing'] = self.facing
        data['movement_goal_x'] = self.movement_goal_x
        data['movement_goal_y'] = self.movement_goal_y
        data['ultimate_goal_x'] = self.ultimate_goal_x
        data['ultimate_goal_y'] = self.ultimate_goal_y
        data['chain'] = self.chain
        data['idle_behavior'] = self.idle_behavior
        data['actual_python_class'] = type(self).__name__

        if strength_reduction > 0:
            for i in range(strength_reduction):
                self.increase_player_strength()

        return data

class Goblin(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.name = 'Goblin'
class GoblinArcher(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.name = 'Goblin Archer'
        self.max_hp = int(self.max_hp*0.7)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*0.9)
    def tick(self,chars,tick):
        if self.game.floor!=self.floor:
            return
        self.tick_apply_poison_and_decrement_effects()
        if 5 not in self.effects:
            if self.aggro==[]:
                self.tick_idle(tick)
                self.tick_idle_move()
            char = self.tick_determine_target_and_move(chars,tick)
            self.tick_attempt_attack(char)
        self.tick_dots()
        self.tick_delayed_damage_effects()
    def tick_attempt_attack(self,char):
        if char:
            if (self.pos_x+(tile_size/2)>=char.pos_x and self.pos_x+(tile_size/2)<=char.pos_x+(tile_size-1)):
                if self.pos_y+(tile_size/2)>=char.pos_y-(tile_size*8) and self.pos_y+(tile_size/2)<=char.pos_y+(tile_size*8):
                    self.attack(char)
            elif (self.pos_y+(tile_size/2)>=char.pos_y and self.pos_y+(tile_size/2)<=char.pos_y+(tile_size-1)):
                if self.pos_x+(tile_size/2)>=char.pos_x-(tile_size*8) and self.pos_x+(tile_size/2)<=char.pos_x+(tile_size*8):
                    self.attack(char)
    def attack(self,char):
        if self.gcd==0:
            self.face_character(char)
            self.game.projectiles.append(Projectile(self.pos_x+(tile_size/2),self.pos_y+(tile_size/2),self.facing,4,1,self.damage_after_cushion(),(tile_size*8),self,color='brown'))
            self.game.sounds.append('attack')
            text = 'A'
            if self.name[0] in ['A','E','I','O','U','a','e','i','o','u']:
                text+='n'
            text+=' '+self.name+' fires for '+str(self.attack_power)+' damage.'
            char.handler.push_narration(text)
            self.gcd=90
    def move(self,char,tick):
        Monster.move(self,char,tick)
        self.face_towards_character(char)
    def face_towards_character(self,char):
        x_diff = char.pos_x-self.pos_x
        y_diff = char.pos_y-self.pos_y
        if abs(x_diff)>abs(y_diff):
            self.face_towards_character_x(x_diff)
        else:
            self.face_towards_character_y(y_diff)
    def face_towards_character_x(self,x_diff):
        if x_diff>0:
            self.facing = 1
        else:
            self.facing = 3
    def face_towards_character_y(self,y_diff):
        if y_diff>0:
            self.facing = 2
        else:
            self.facing = 0
    def move_start_calculate_thread_if_necessary(self,char,tick):
        if not self.processing:
            if self.game.in_line_of_sight(char,self.game.map.tiles,self.pos_x/tile_size,self.pos_y/tile_size,char_seeing=False):
                if tick==self.chosen_tick:
                    # if self.parent_ugx.poll():
                    #     self.ultimate_goal_x = self.parent_ugx.recv()
                    # if self.parent_ugy.poll():
                    #     self.ultimate_goal_y = self.parent_ugy.recv()
                    if (self.ultimate_goal_x+(tile_size/2)>=char.pos_x and self.ultimate_goal_x+(tile_size/2)<=char.pos_x+(tile_size-1)):
                        if self.ultimate_goal_y+(tile_size/2)>=char.pos_y-(tile_size*8) and self.ultimate_goal_y+(tile_size/2)<=char.pos_y+(tile_size*8):
                            return
                    elif (self.ultimate_goal_y+(tile_size/2)>=char.pos_y and self.ultimate_goal_y+(tile_size/2)<=char.pos_y+(tile_size-1)):
                        if self.ultimate_goal_x+(tile_size/2)>=char.pos_x-(tile_size*8) and self.ultimate_goal_x+(tile_size/2)<=char.pos_x+(tile_size*8):
                            return
                thread.start_new_thread(self.calculate,(char,(tile_size-1)))
    def calculate_find_path(self,frontier,char,range,cost_so_far,came_from,step,goal):
        # step = (tile_size/2)
        while not frontier.empty():
            current = frontier.get()
            x,y=current
            if (x+(tile_size/2)>=char.pos_x and x+(tile_size/2)<=char.pos_x+(tile_size-1)):
                if y+(tile_size/2)>=char.pos_y-(tile_size*8) and y+(tile_size/2)<=char.pos_y+(tile_size*8):
                    self.success=True
                    break
            elif (y+(tile_size/2)>=char.pos_y and y+(tile_size/2)<=char.pos_y+(tile_size-1)):
                if x+(tile_size/2)>=char.pos_x-(tile_size*8) and x+(tile_size/2)<=char.pos_x+(tile_size*8):
                    self.success=True
                    break
            for next in classic_neighbors(current,self,self.game,char,step):
                frontier,came_from = self.calculate_step(cost_so_far,current,next,frontier,came_from,goal)
        return came_from,current

class Kobold(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,1,mob_class)
        self.level = 0
        self.max_hp = int(self.max_hp*0.58)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*0.58)
        self.xp = int(self.xp*0.58*0.58)
        self.name = 'Kobold'
class Wolf(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = int(self.max_hp*0.8)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*1)
        self.name = 'Wolf'
        self.sense_of_smell = 1
    def move_x(self,x):
        if abs(x-self.pos_x)>0:
            if (x-self.pos_x)<0:
                for i in range(tile_size/16,1,-1):
                    if not self.game.is_wall(self.pos_x-i,self.pos_y) and not self.game.is_collision(self.pos_x-i,self.pos_y,self) and not self.game.is_door(self.pos_x-i,self.pos_y):
                        self.pos_x-=i
                        self.facing = 3
                        self.idle_move_stymied = False
                        break
            else:
                for i in range(tile_size/16,1,-1):
                    if not self.game.is_wall(self.pos_x+i,self.pos_y) and not self.game.is_collision(self.pos_x+i,self.pos_y,self) and not self.game.is_door(self.pos_x+i,self.pos_y):
                        self.pos_x+=i
                        self.facing = 1
                        self.idle_move_stymied = False
                        break
    def move_y(self,y):
        if abs(y-self.pos_y)>0:
            if (y-self.pos_y)<0:
                for i in range(tile_size/16,1,-1):
                    if not self.game.is_wall(self.pos_x,self.pos_y-i) and not self.game.is_collision(self.pos_x,self.pos_y-i,self) and not self.game.is_door(self.pos_x,self.pos_y-i):
                        self.pos_y-=i
                        self.facing = 0
                        self.idle_move_stymied = False
                        break
            else:
                for i in range(tile_size/16,1,-1):
                    if not self.game.is_wall(self.pos_x,self.pos_y+i) and not self.game.is_collision(self.pos_x,self.pos_y+i,self) and not self.game.is_door(self.pos_x,self.pos_y+i):
                        self.pos_y+=i
                        self.facing = 2
                        self.idle_move_stymied = False
                        break
class BlinkDog(Wolf):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = int(self.max_hp*0.7)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*0.9)
        self.name = 'Blink Dog'
        self.blinkCD = 60
        self.sense_of_smell = 1
    def tick(self,chars,tick):
        if self.game.floor!=self.floor:
            return
        self.tick_apply_poison_and_decrement_effects()
        if 5 not in self.effects:
            if self.aggro==[]:
                self.tick_idle(tick)
                self.tick_idle_move()
            char = self.tick_determine_target_and_move(chars,tick)
            self.tick_attempt_attack(char)
        if self.blinkCD>0:
            self.blinkCD-=1
        self.tick_dots()
        self.tick_delayed_damage_effects()
    def move(self,char,tick):
        self.move_x(char.pos_x)
        self.move_y(char.pos_y)
        if self.blinkCD==0:
            self.blink(char)
    def blink(self,char):
        if not self.game.is_wall(char.pos_x,char.pos_y-tile_size) and not self.game.is_collision(char.pos_x,char.pos_y-tile_size,self) and not self.game.is_door(char.pos_x,char.pos_y-tile_size):
            self.blink_up(char)
        elif not self.game.is_wall(char.pos_x,char.pos_y+tile_size) and not self.game.is_collision(char.pos_x,char.pos_y+tile_size,self) and not self.game.is_door(char.pos_x,char.pos_y+tile_size):
            self.blink_down(char)
        elif not self.game.is_wall(char.pos_x-tile_size,char.pos_y) and not self.game.is_collision(char.pos_x-tile_size,char.pos_y,self) and not self.game.is_door(char.pos_x-tile_size,char.pos_y):
            self.blink_left(char)
        elif not self.game.is_wall(char.pos_x+tile_size,char.pos_y) and not self.game.is_collision(char.pos_x+tile_size,char.pos_y,self) and not self.game.is_door(char.pos_x+tile_size,char.pos_y):
            self.blink_right(char)
    def blink_up(self,char):
        self.pos_x = char.pos_x
        self.pos_y = char.pos_y-tile_size
        self.blink_reset_CD_and_set_goal(char)
    def blink_down(self,char):
        self.pos_x = char.pos_x
        self.pos_y = char.pos_y+tile_size
        self.blink_reset_CD_and_set_goal(char)
    def blink_left(self,char):
        self.pos_x = char.pos_x-tile_size
        self.pos_y = char.pos_y
        self.blink_reset_CD_and_set_goal(char)
    def blink_right(self,char):
        self.pos_x = char.pos_x+tile_size
        self.pos_y = char.pos_y
        self.blink_reset_CD_and_set_goal(char)
    def blink_reset_CD_and_set_goal(self,char):
        self.blinkCD=90
        self.chain = []
        self.movement_goal_x = char.pos_x
        self.movement_goal_y = char.pos_y
class CaveCheetah(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = int(self.max_hp*0.7)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*0.9)
        self.name = 'Cave Cheetah'
        self.sense_of_smell = 5
    def move_x(self,x):
        if abs(x-self.pos_x)>0:
            if (x-self.pos_x)<0:
                self.move_x_left()
            else:
                self.move_x_right()
    def move_x_right(self):
        for step in range(tile_size/8,1,-1):
            if not self.game.is_wall(self.pos_x+step,self.pos_y) and not self.game.is_collision(self.pos_x+step,self.pos_y,self) and not self.game.is_door(self.pos_x+step,self.pos_y):
                self.pos_x+=step
                self.facing = 1
                break
    def move_x_left(self):
        for step in range(tile_size/8,1,-1):
            if not self.game.is_wall(self.pos_x-step,self.pos_y) and not self.game.is_collision(self.pos_x-step,self.pos_y,self) and not self.game.is_door(self.pos_x-step,self.pos_y):
                self.pos_x-=step
                self.facing = 3
                break
    def move_y(self,y):
        if abs(y-self.pos_y)>0:
            if (y-self.pos_y)<0:
                self.move_y_up()
            else:
                self.move_y_down()
    def move_y_down(self):
        for step in range(tile_size/8,1,-1):
            if not self.game.is_wall(self.pos_x,self.pos_y+step) and not self.game.is_collision(self.pos_x,self.pos_y+step,self) and not self.game.is_door(self.pos_x,self.pos_y+step):
                self.pos_y+=step
                self.facing = 2
                break
    def move_y_up(self):
        for step in range(tile_size/8,1,-1):
            if not self.game.is_wall(self.pos_x,self.pos_y-step) and not self.game.is_collision(self.pos_x,self.pos_y-step,self) and not self.game.is_door(self.pos_x,self.pos_y-step):
                self.pos_y-=step
                self.facing = 0
                break
class Ghoul(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = int(self.max_hp*0.7)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*0.9)
        self.name = 'Ghoul'
    def attack(self,char):
        if self.gcd==0:
            self.attack_deliver_blow(char)
            self.game.sounds.append('attack')
            roll = random.randint(0,1)
            if roll==1:
                char.apply_debuff(0)
            self.gcd=90
class Spider(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = int(self.max_hp*0.9)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*0.7)
        self.name = 'Giant Spider'
    def attack(self,char):
        if self.gcd==0:
            self.attack_deliver_blow(char)
            self.game.sounds.append('attack')
            roll = random.randint(1,10)
            if roll<=4:
                char.apply_debuff(1)
            self.gcd=90
class LandSquid(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = int(self.max_hp*0.8)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*0.8)
        self.name = 'Land Squid'
        self.used_blind = False
    def attack(self,char):
        if self.gcd==0:
            self.attack_deliver_blow(char)
            self.game.sounds.append('attack')
            if not self.used_blind:
                char.apply_debuff(2)
                self.used_blind = True
            self.gcd=90
class YoungDragon(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = int(self.max_hp*0.8)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*0.8)
        self.name = 'Young Dragon'
        self.breath_CD=0
        self.cleanup_CD=-1
    def tick(self,chars,tick):
        if self.game.floor!=self.floor:
            return
        self.tick_apply_poison_and_decrement_effects()
        self.tick_decrement_breath_CD_and_use(chars)
        self.tick_decrement_cleanup_CD_and_cleanup()
        if 5 not in self.effects:
            if self.aggro==[]:
                self.tick_idle(tick)
                self.tick_idle_move()
            char = self.tick_determine_target_and_move(chars,tick)
            self.tick_attempt_attack(char)
        self.tick_dots()
        self.tick_delayed_damage_effects()
    def tick_decrement_breath_CD_and_use(self,chars):
        if self.breath_CD>0:
            self.breath_CD-=1
        if self.breath_CD==0:
            for char in chars:
                if self.game.in_line_of_sight(self,self.game.map.tiles,char.pos_x/tile_size,char.pos_y/tile_size,char_seeing=False) and char.visible:
                    self.use_breath_weapon(char)
                    break
    def tick_decrement_cleanup_CD_and_cleanup(self):
        if self.cleanup_CD>0:
            self.cleanup_CD-=1
        if self.cleanup_CD==0:
            self.clean_up_fire()
    def use_breath_weapon(self,char):
        if self.breath_CD==0:
            self.use_breath_weapon_setup(char)
            facing = self.use_breath_weapon_determine_facing(char)
            table = [self.use_breath_weapon_up,self.use_breath_weapon_right,self.use_breath_weapon_down,self.use_breath_weapon_left]
            table[facing]()
    def use_breath_weapon_up(self):
        width=-1
        for y in range((self.pos_y/tile_size)-1,(self.pos_y/tile_size)-9,-1):
            width+=1
            for x in range((self.pos_x/tile_size)-width,(self.pos_x/tile_size)+width+1):
                if self.game.in_line_of_sight(self,self.game.map.tiles,x,y,char_seeing=False) and x>=0 and y>=0 and len(self.game.map.tiles)>x and len(self.game.map.tiles[x])>y and self.game.map.tiles[x][y] in [' ','D','O','R']:
                    self.game.map.tiles[x][y] = 'f'
    def use_breath_weapon_down(self):
        width=-1
        for y in range((self.pos_y/tile_size)+1,(self.pos_y/tile_size)+9):
            width+=1
            for x in range((self.pos_x/tile_size)-width,(self.pos_x/tile_size)+width+1):
                if self.game.in_line_of_sight(self,self.game.map.tiles,x,y,char_seeing=False) and x>=0 and y>=0 and len(self.game.map.tiles)>x and len(self.game.map.tiles[x])>y and self.game.map.tiles[x][y] in [' ','D','O','R']:
                    self.game.map.tiles[x][y] = 'f'
    def use_breath_weapon_right(self):
        width=-1
        for x in range((self.pos_x/tile_size)+1,(self.pos_x/tile_size)+9):
            width+=1
            for y in range((self.pos_y/tile_size)-width,(self.pos_y/tile_size)+width+1):
                if self.game.in_line_of_sight(self,self.game.map.tiles,x,y,char_seeing=False) and x>=0 and y>=0 and len(self.game.map.tiles)>x and len(self.game.map.tiles[x])>y and self.game.map.tiles[x][y] in [' ','D','O','R']:
                    self.game.map.tiles[x][y] = 'f'
    def use_breath_weapon_left(self):
        width=-1
        for x in range((self.pos_x/tile_size)-1,(self.pos_x/tile_size)-9,-1):
            width+=1
            for y in range((self.pos_y/tile_size)-width,(self.pos_y/tile_size)+width+1):
                if self.game.in_line_of_sight(self,self.game.map.tiles,x,y,char_seeing=False) and x>=0 and y>=0 and len(self.game.map.tiles)>x and len(self.game.map.tiles[x])>y and self.game.map.tiles[x][y] in [' ','D','O','R']:
                    self.game.map.tiles[x][y] = 'f'
    def use_breath_weapon_setup(self,char):
        self.face_character(char)
        char.handler.push_narration('The Young Dragon breathes fire!')
        self.breath_CD=150
        self.cleanup_CD=30
    def use_breath_weapon_determine_facing(self,char):
        if abs(char.pos_x-self.pos_x)>abs(char.pos_y-self.pos_y):
            if char.pos_x-self.pos_x>0:
                return 1
            else:
                return 3
        else:
            if char.pos_y-self.pos_y>0:
                return 2
            else:
                return 0
    def clean_up_fire(self):
        self.cleanup_CD-=1
        for x in range(len(self.game.map.tiles)):
            for y in range(len(self.game.map.tiles[x])):
                if self.game.map.tiles[x][y]=='f':
                    self.game.map.tiles[x][y] = ' '
class AnimatedStatue(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = int(self.max_hp*1.3)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*0.9)
        self.name = 'Animated Statue'
        self.mob_class = -1
        self.aggro_radius = tile_size*3
    def take_hit(self,damage,source=None):
        self.aggro_radius = (tile_size*8)+tile_size
        self.take_hit_damage_multipliers(damage)
        damage = max(damage-6,0)
        self.take_hit_apply_damage(damage,source)
class Imp(GoblinArcher):
    def __init__(self,game,x,y,floor,level,mob_class):
        GoblinArcher.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = int(self.max_hp/0.7*0.6)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power/0.9*0.8)
        self.name = 'Imp'
        self.summon_attempted = False
    def attack(self,char):
        if self.gcd==0:
            self.face_character(char)
            self.game.projectiles.append(Projectile(self.pos_x+(tile_size/2),self.pos_y+(tile_size/2),self.facing,4,1,self.damage_after_cushion(),(tile_size*8),self,color='#FF0000'))
            self.game.sounds.append('attack')
            text = 'A'
            if self.name[0] in ['A','E','I','O','U','a','e','i','o','u']:
                text+='n'
            text+=' '+self.name+' fires for '+str(self.attack_power)+' damage.'
            char.handler.push_narration(text)
            self.gcd=90
    def tick(self,chars,tick):
        if self.game.floor!=self.floor:
            return
        self.tick_apply_poison_and_decrement_effects()
        if 5 not in self.effects:
            if self.aggro==[]:
                self.tick_idle(tick)
                self.tick_idle_move()
            char = self.tick_determine_target_and_move(chars,tick)
            self.tick_attempt_attack(char)
        self.tick_attempt_summon(char)
        self.tick_dots()
        self.tick_delayed_damage_effects()
    def tick_attempt_summon(self,char):
        if self.hp<=self.max_hp/2 and not self.summon_attempted:
            self.summon_attempted = True
            if random.randint(1,10) >= 8:
                char.handler.push_narration('The Imp attempts to summon another Imp... and succeeds.')
                self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'SUMMON','white'))
                self.summon()
            else:
                char.handler.push_narration('The Imp attempts to summon another Imp... and fails.')
    def summon(self):
        for i in range(-1,2):
            for j in range(-1,2):
                if i==0 and j==0:
                    continue
                if (not self.game.is_collision_mobs_only(self.pos_x+(i*tile_size),self.pos_y+(j*tile_size),self)) and (not self.game.is_wall(self.pos_x+(i*tile_size),self.pos_y+(j*tile_size))):
                    imp = Imp(self.game,self.pos_x+(i*tile_size),self.pos_y+(j*tile_size),self.floor,self.level,self.mob_class)
                    self.game.map.monsters.append(imp)
                    self.game.active_monsters.append(imp)
                    return
class Ghost(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = int(self.max_hp*1)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*0.6)
        self.name = 'Ghost'
    def move(self,char,tick):
        self.move_x(char.pos_x)
        self.move_y(char.pos_y)
    def move_x(self,x):
        if abs(x-self.pos_x)>0:
            if (x-self.pos_x)<0:
                self.pos_x-=tile_size/32
                self.facing = 3
            else:
                self.pos_x+=tile_size/32
                self.facing = 1
    def move_y(self,y):
        if abs(y-self.pos_y)>0:
            if (y-self.pos_y)<0:
                self.pos_y-=tile_size/32
                self.facing = 0
            else:
                self.pos_y+=tile_size/32
                self.facing = 2
class Ogre(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = int(self.max_hp*0.8)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*0.8)
        self.name = 'Ogre'
    def tick(self,chars,tick):
        if self.game.floor!=self.floor:
            return
        self.tick_apply_poison_and_decrement_effects()
        if 5 not in self.effects:
            if self.aggro==[]:
                self.tick_idle(tick)
                self.tick_idle_move()
            char = self.tick_determine_target_and_move(chars,tick)
            self.tick_attempt_attack(char)
        self.tick_dots()
        self.tick_delayed_damage_effects()
    def tick_attempt_attack(self,char):
        if not char:
            return
        if abs(char.pos_x-self.pos_x)<=(tile_size*2) and abs(char.pos_y-self.pos_y)<=(tile_size*2):
            self.attack(char)
    def attack(self,char):
        if self.gcd==0:
            self.face_character(char)
            for char2 in self.game.chars:
                if abs(char2.pos_x-self.pos_x)<=(tile_size*2) and abs(char2.pos_y-self.pos_y)<=(tile_size*2):
                    self.attack_deliver_blow_without_facing(char2)
                    self.game.sounds.append('attack')
            self.gcd=90
    def attack_deliver_blow_without_facing(self,char2):
        self.game.make_noise(self.pos_x,self.pos_y, 20)
        char2.take_hit(self.damage_after_cushion())
        text = 'A'
        if self.name[0] in ['A','E','I','O','U','a','e','i','o','u']:
            text+='n'
        text+=' '+self.name+' attacks you, dealing '+str(self.attack_power)+' damage.'
        char2.handler.push_narration(text)
        if char2.hp<=0:
            char2.alive = False
class Cockatrice(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = int(self.max_hp*0.9)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*0.1)
        self.name = 'Cockatrice'
    def attack(self,char):
        if self.gcd==0:
            self.attack_deliver_blow(char)
            self.game.sounds.append('attack')
            roll = random.randint(1,10)
            if roll<=2:
                char.handler.push_narration('You have been turned to stone!')
                self.game.floating_text.append(FloatingText(char.pos_x,char.pos_y,'DEATH','#FF0000'))
                char.hp = 0
            if char.hp<=0:
                char.alive = False
            self.gcd=90
class PhantomFungus(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = int(self.max_hp*0.8)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*0.8)
        self.name = 'Phantom Fungus'
        self.visible = False
class FireElemental(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = int(self.max_hp*0.9)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*0.7)
        self.name = 'Fire Elemental'
        self.fire_CD=0
        self.cleanup_CD=-1
    def tick(self,chars,tick):
        if self.game.floor!=self.floor:
            return
        self.tick_apply_poison_and_decrement_effects()
        self.tick_decrement_fire_CD_and_use_fire(chars)
        self.tick_decrement_cleanup_CD_and_cleanup()
        if 5 not in self.effects:
            if self.aggro==[]:
                self.tick_idle(tick)
                self.tick_idle_move()
            char = self.tick_determine_target_and_move(chars,tick)
            self.tick_attempt_attack(char)
        self.tick_dots()
        self.tick_delayed_damage_effects()
    def tick_decrement_fire_CD_and_use_fire(self,chars):
        if self.fire_CD>0:
            self.fire_CD-=1
        if self.fire_CD==0 and 5 not in self.effects:
            for char in chars:
                if self.game.in_line_of_sight(self,self.game.map.tiles,char.pos_x/tile_size,char.pos_y/tile_size,char_seeing=False):
                    self.use_fire(char)
                    break
    def tick_decrement_cleanup_CD_and_cleanup(self):
        if self.cleanup_CD>0:
            self.cleanup_CD-=1
        if self.cleanup_CD==0:
            self.clean_up_fire()
    def use_fire(self,char):
        pass
        if self.fire_CD==0:
            self.face_character(char)
            char.handler.push_narration('The Fire Elemental spews fire everywhere!')
            self.fire_CD=150
            self.cleanup_CD=30
            for y in range((self.pos_y/tile_size)-6,(self.pos_y/tile_size)+6):
                for x in range((self.pos_x/tile_size)-6,(self.pos_x/tile_size)+6):
                    if self.game.in_line_of_sight(self,self.game.map.tiles,x,y,char_seeing=False) and x>=0 and y>=0 and len(self.game.map.tiles)>x and len(self.game.map.tiles[x])>y and self.game.map.tiles[x][y] in [' ','D','O','R']:
                        dx = abs((self.pos_x/tile_size)-x)
                        dy = abs((self.pos_y/tile_size)-y)
                        d = math.sqrt(float(dx)*float(dx)+float(dy)*float(dy))
                        if d<=4:
                            self.game.map.tiles[x][y] = 'f'
    def clean_up_fire(self):
        self.cleanup_CD-=1
        for x in range(len(self.game.map.tiles)):
            for y in range(len(self.game.map.tiles[x])):
                if self.game.map.tiles[x][y]=='f':
                    self.game.map.tiles[x][y] = ' '
class Ankheg(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = int(self.max_hp*0.85)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*1.05)
        self.name = 'Ankheg'
        self.acid_used = False
        self.acid_cleanup_cooldown = -1
        self.sense_of_smell = 5
    def tick(self,chars,tick):
        if self.game.floor!=self.floor:
            return
        self.tick_apply_poison_and_decrement_effects()
        if 5 not in self.effects:
            if self.aggro==[]:
                self.tick_idle(tick)
                self.tick_idle_move()
            char = self.tick_determine_target_and_move(chars,tick)
            self.tick_attempt_attack(char)
        self.tick_decrement_acid_CD_and_use_acid(char)
        self.tick_dots()
        self.tick_delayed_damage_effects()
    def tick_decrement_acid_CD_and_use_acid(self,char):
        if not char:
            return
        if abs(char.pos_x-self.pos_x)<=tile_size or abs(char.pos_y-self.pos_y)<=tile_size:
            if 5 not in self.effects:
                self.spit_acid(char)
        if self.acid_cleanup_cooldown>=0:
            self.acid_cleanup_cooldown-=1
        if self.acid_cleanup_cooldown==0:
            self.clean_up_acid()
    def spit_acid(self,char):
        if not self.acid_used:
            self.acid_used = True
            self.face_character(char)
            char.handler.push_narration('The Ankheg spits acid!')
            self.acid_cleanup_cooldown=30
            x = self.pos_x/tile_size
            y = self.pos_y/tile_size
            table = [self.spit_acid_up,self.spit_acid_right,self.spit_acid_down,self.spit_acid_left]
            table[self.facing](x,y)
    def spit_acid_up(self, x, y):
        for y in range((self.pos_y/tile_size)-1,(self.pos_y/tile_size)-9,-1):
            if self.game.in_line_of_sight(self,self.game.map.tiles,x,y,char_seeing=False) and x>=0 and y>=0 and len(self.game.map.tiles)>x and len(self.game.map.tiles[x])>y and self.game.map.tiles[x][y] in [' ','D','O','R']:
                self.game.map.tiles[x][y] = 'a'
    def spit_acid_down(self, x, y):
        for y in range((self.pos_y/tile_size)+1,(self.pos_y/tile_size)+9):
            if self.game.in_line_of_sight(self,self.game.map.tiles,x,y,char_seeing=False) and x>=0 and y>=0 and len(self.game.map.tiles)>x and len(self.game.map.tiles[x])>y and self.game.map.tiles[x][y] in [' ','D','O','R']:
                self.game.map.tiles[x][y] = 'a'
    def spit_acid_right(self, x, y):
        for x in range((self.pos_x/tile_size)+1,(self.pos_x/tile_size)+9):
            if self.game.in_line_of_sight(self,self.game.map.tiles,x,y,char_seeing=False) and x>=0 and y>=0 and len(self.game.map.tiles)>x and len(self.game.map.tiles[x])>y and self.game.map.tiles[x][y] in [' ','D','O','R']:
                self.game.map.tiles[x][y] = 'a'
    def spit_acid_left(self, x, y):
        for x in range((self.pos_x/tile_size)-1,(self.pos_x/tile_size)-9,-1):
            if self.game.in_line_of_sight(self,self.game.map.tiles,x,y,char_seeing=False) and x>=0 and y>=0 and len(self.game.map.tiles)>x and len(self.game.map.tiles[x])>y and self.game.map.tiles[x][y] in [' ','D','O','R']:
                self.game.map.tiles[x][y] = 'a'
    def clean_up_acid(self):
        self.acid_cleanup_cooldown-=1
        for x in range(len(self.game.map.tiles)):
            for y in range(len(self.game.map.tiles[x])):
                if self.game.map.tiles[x][y]=='a':
                    self.game.map.tiles[x][y] = ' '
class Troll(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = self.max_hp*4/5
        self.hp = self.max_hp
        self.name = 'Troll'
        self.sense_of_smell = 7
    def tick(self,chars,tick):
        self.hp = min(float(self.hp) + (float(self.max_hp)/float(300)),float(self.max_hp))
        if self.game.floor!=self.floor:
            return
        Monster.tick(self,chars,tick)
class OchreJelly(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.name = 'Ochre Jelly'
        self.max_hp = int(self.hp*1.1)
        self.hp = self.max_hp
    def take_hit_apply_damage(self,damage,source):
        self.hp-=int(damage)
        if self.hp >= 2:
            if self.attempt_to_spawn_ochre_jelly(self.hp/2):
                self.hp = self.hp/2
                self.xp = int(self.xp/2)
        if not source.improved_invisibility:
            self.aggro_increment(source,damage)
        source.target = self
    def attempt_to_spawn_ochre_jelly(self, hp):
        for i in range(-1,2):
            for j in range(-1,2):
                if i==0 and j==0:
                    continue
                if (not self.game.is_collision_mobs_only(self.pos_x+(i*tile_size),self.pos_y+(j*tile_size),self)) and (not self.game.is_wall(self.pos_x+(i*tile_size),self.pos_y+(j*tile_size))):
                    self.spawn_ochre_jelly(hp,i,j)
                    return True
        for i in range(-2,3):
            for j in range(-2,3):
                if i==0 and j==0:
                    continue
                if (not self.game.is_collision_mobs_only(self.pos_x+(i*tile_size),self.pos_y+(j*tile_size),self)) and (not self.game.is_wall(self.pos_x+(i*tile_size),self.pos_y+(j*tile_size))):
                    self.spawn_ochre_jelly(hp,i,j)
                    return True
        return False
    def spawn_ochre_jelly(self, hp, i, j):
        for char in self.game.chars:
            char.handler.push_narration('The Ochre Jelly splits!')
        self.game.floating_text.append(FloatingText(char.pos_x,char.pos_y,'SPLIT!','white'))
        jelly = OchreJelly(self.game,self.pos_x+(i*tile_size),self.pos_y+(j*tile_size),self.floor,self.level,self.mob_class)
        jelly.hp = hp
        jelly.max_hp = math.ceil(hp)
        jelly.xp = int(self.xp/2)
        jelly.autoheal_cd = self.autoheal_cd
        for entry in self.aggro:
            new_entry = AggroEntry(entry.char, entry.value)
            jelly.aggro.append(new_entry)
        self.game.map.monsters.append(jelly)
        self.game.active_monsters.append(jelly)
    def move_x(self,x):
        if random.randint(1,4/(tile_size/32))<4:
            return
        if abs(x-self.pos_x)>0:
            if (x-self.pos_x)<0:
                if not self.game.is_wall(self.pos_x-1,self.pos_y) and not self.game.is_collision(self.pos_x-1,self.pos_y,self) and not self.game.is_door(self.pos_x-1,self.pos_y):
                    self.pos_x-=1
                    self.facing = 3
            else:
                if not self.game.is_wall(self.pos_x+1,self.pos_y) and not self.game.is_collision(self.pos_x+1,self.pos_y,self) and not self.game.is_door(self.pos_x+1,self.pos_y):
                    self.pos_x+=1
                    self.facing = 1
    def move_y(self,y):
        if random.randint(1,4/(tile_size/32))<4:
            return
        if abs(y-self.pos_y)>0:
            if (y-self.pos_y)<0:
                if not self.game.is_wall(self.pos_x,self.pos_y-1) and not self.game.is_collision(self.pos_x,self.pos_y-1,self) and not self.game.is_door(self.pos_x,self.pos_y-1):
                    self.pos_y-=1
                    self.facing = 0
            else:
                if not self.game.is_wall(self.pos_x,self.pos_y+1) and not self.game.is_collision(self.pos_x,self.pos_y+1,self) and not self.game.is_door(self.pos_x,self.pos_y+1):
                    self.pos_y+=1
                    self.facing = 2
class Mimic(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = self.max_hp*5/4
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*3/4)
        self.name = 'Mimic'
        self.mob_class = -1
        self.aggro_radius = tile_size*3
class Warlock(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = int(self.max_hp*0.7)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*0.7)
        self.name = 'Warlock'
        self.used_curse = False
    def attack(self,char):
        if self.gcd==0:
            self.attack_deliver_blow(char)
            self.game.sounds.append('attack')
            if not self.used_curse:
                char.deck.discard_pile.append(Card(53,temp=True))
                self.used_curse = True
                self.game.floating_text.append(FloatingText(char.pos_x+(tile_size/2),char.pos_y+(tile_size/2),'CURSED','#551A8B'))
            self.gcd=90
class SporeLord(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = int(self.max_hp*0.5)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*0.5)
        self.name = 'Spore Lord'
        self.used_spawn = False
    def attack(self,char):
        if self.gcd==0:
            self.attack_deliver_blow(char)
            self.game.sounds.append('attack')
            if not self.used_spawn:
                char.deck.discard_pile.append(Card(54,temp=True))
                self.used_spawn = True
                self.game.floating_text.append(FloatingText(char.pos_x,char.pos_y,'INFECTED','#551A8B'))
            self.gcd=90
class Sporeling(Monster):
    def __init__(self,game,x,y,floor,level,mob_class):
        Monster.__init__(self,game,x,y,floor,level,mob_class)
        self.max_hp = int(self.max_hp*1.2)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power*0.8)
        self.name = 'Sporeling'

class AggroEntry ():
    def __init__(self,char,value):
        self.char = char
        self.value = value
def choose_monster(game,x_in,y_in,floor,level,mob_class):
    # return FireElemental(game,x_in,y_in,floor,level,mob_class)
    # return GoblinArcher(game,x_in,y_in,floor,level,mob_class))
    if level>=12:
        roll = random.randint(1,23)
        if roll==1:
            return Goblin(game,x_in,y_in,floor,level,mob_class)
        elif roll==2:
            return GoblinArcher(game,x_in,y_in,floor,level,mob_class)
        elif roll==3:
            return Wolf(game,x_in,y_in,floor,level,mob_class)
        elif roll==4:
            roll2 = random.randint(1,4)
            if roll2==4:
                return Ghoul(game,x_in,y_in,floor,level,mob_class)
            return choose_monster(game, x_in, y_in, floor, level, mob_class)
        elif roll==5:
            return Spider(game,x_in,y_in,floor,level,mob_class)
        elif roll==6:
            return LandSquid(game,x_in,y_in,floor,level,mob_class)
        elif roll==7:
            return CaveCheetah(game,x_in,y_in,floor,level,mob_class)
        elif roll==8:
            return BlinkDog(game,x_in,y_in,floor,level,mob_class)
        elif roll==9:
            return YoungDragon(game,x_in,y_in,floor,level,mob_class)
        elif roll==10:
            return AnimatedStatue(game,x_in,y_in,floor,level,mob_class)
        elif roll==11:
            return Imp(game,x_in,y_in,floor,level,mob_class)
        elif roll==12:
            return Ghost(game,x_in,y_in,floor,level,mob_class)
        elif roll==13:
            return Ogre(game,x_in,y_in,floor,level,mob_class)
        elif roll==14:
            return Ankheg(game,x_in,y_in,floor,level,mob_class)
        elif roll==15:
            return Cockatrice(game,x_in,y_in,floor,level,mob_class)
        elif roll==16:
            return PhantomFungus(game,x_in,y_in,floor,level,mob_class)
        elif roll==17:
            return FireElemental(game,x_in,y_in,floor,level,mob_class)
        elif roll==18:
            return Troll(game,x_in,y_in,floor,level,mob_class)
        elif roll==19:
            return OchreJelly(game,x_in,y_in,floor,level,mob_class)
        elif roll==20:
            return Mimic(game,x_in,y_in,floor,level,mob_class)
        elif roll==21:
            return Warlock(game,x_in,y_in,floor,level,mob_class)
        elif roll==22:
            return SporeLord(game,x_in,y_in,floor,level,mob_class)
        elif roll==23:
            return Kobold(game,x_in,y_in,floor,min(level,1),mob_class)
    elif level>=10:
        roll = random.randint(1,20)
        if roll==1:
            return Goblin(game,x_in,y_in,floor,level,mob_class)
        elif roll==2:
            return GoblinArcher(game,x_in,y_in,floor,level,mob_class)
        elif roll==3:
            return Wolf(game,x_in,y_in,floor,level,mob_class)
        elif roll==4:
            roll2 = random.randint(1,4)
            if roll2==4:
                return Ghoul(game,x_in,y_in,floor,level,mob_class)
            return choose_monster(game, x_in, y_in, floor, level, mob_class)
        elif roll==5:
            return Spider(game,x_in,y_in,floor,level,mob_class)
        elif roll==6:
            return LandSquid(game,x_in,y_in,floor,level,mob_class)
        elif roll==7:
            return CaveCheetah(game,x_in,y_in,floor,level,mob_class)
        elif roll==8:
            return BlinkDog(game,x_in,y_in,floor,level,mob_class)
        elif roll==9:
            return YoungDragon(game,x_in,y_in,floor,level,mob_class)
        elif roll==10:
            return AnimatedStatue(game,x_in,y_in,floor,level,mob_class)
        elif roll==11:
            return Imp(game,x_in,y_in,floor,level,mob_class)
        elif roll==12:
            return Ghost(game,x_in,y_in,floor,level,mob_class)
        elif roll==13:
            return Ogre(game,x_in,y_in,floor,level,mob_class)
        elif roll==14:
            return Ankheg(game,x_in,y_in,floor,level,mob_class)
        elif roll==15:
            return Cockatrice(game,x_in,y_in,floor,level,mob_class)
        elif roll==16:
            return PhantomFungus(game,x_in,y_in,floor,level,mob_class)
        elif roll==17:
            return FireElemental(game,x_in,y_in,floor,level,mob_class)
        elif roll==18:
            return Mimic(game,x_in,y_in,floor,level,mob_class)
        elif roll==19:
            return Warlock(game,x_in,y_in,floor,level,mob_class)
        elif roll==20:
            return Kobold(game,x_in,y_in,floor,min(level,1),mob_class)
    elif level>=7:
        roll = random.randint(1,18)
        if roll==1:
            return Goblin(game,x_in,y_in,floor,level,mob_class)
        elif roll==2:
            return GoblinArcher(game,x_in,y_in,floor,level,mob_class)
        elif roll==3:
            return Wolf(game,x_in,y_in,floor,level,mob_class)
        elif roll==4:
            roll2 = random.randint(1,4)
            if roll2==4:
                return Ghoul(game,x_in,y_in,floor,level,mob_class)
            return choose_monster(game, x_in, y_in, floor, level, mob_class)
        elif roll==5:
            return Spider(game,x_in,y_in,floor,level,mob_class)
        elif roll==6:
            return LandSquid(game,x_in,y_in,floor,level,mob_class)
        elif roll==7:
            return CaveCheetah(game,x_in,y_in,floor,level,mob_class)
        elif roll==8:
            return BlinkDog(game,x_in,y_in,floor,level,mob_class)
        elif roll==9:
            return YoungDragon(game,x_in,y_in,floor,level,mob_class)
        elif roll==10:
            return AnimatedStatue(game,x_in,y_in,floor,level,mob_class)
        elif roll==11:
            return Imp(game,x_in,y_in,floor,level,mob_class)
        elif roll==12:
            return Ghost(game,x_in,y_in,floor,level,mob_class)
        elif roll==13:
            return Ogre(game,x_in,y_in,floor,level,mob_class)
        elif roll==14:
            return Ankheg(game,x_in,y_in,floor,level,mob_class)
        elif roll==15:
            return Cockatrice(game,x_in,y_in,floor,level,mob_class)
        elif roll==16:
            return PhantomFungus(game,x_in,y_in,floor,level,mob_class)
        elif roll==17:
            return FireElemental(game,x_in,y_in,floor,level,mob_class)
        elif roll==18:
            return Kobold(game,x_in,y_in,floor,min(level,1),mob_class)
    elif level>=5:
        roll = random.randint(1,12)
        if roll==1:
            return Goblin(game,x_in,y_in,floor,level,mob_class)
        elif roll==2:
            return GoblinArcher(game,x_in,y_in,floor,level,mob_class)
        elif roll==3:
            return Wolf(game,x_in,y_in,floor,level,mob_class)
        elif roll==4:
            roll2 = random.randint(1,4)
            if roll2==4:
                return Ghoul(game,x_in,y_in,floor,level,mob_class)
            return choose_monster(game, x_in, y_in, floor, level, mob_class)
        elif roll==5:
            return Spider(game,x_in,y_in,floor,level,mob_class)
        elif roll==6:
            return LandSquid(game,x_in,y_in,floor,level,mob_class)
        elif roll==7:
            return CaveCheetah(game,x_in,y_in,floor,level,mob_class)
        elif roll==8:
            return BlinkDog(game,x_in,y_in,floor,level,mob_class)
        elif roll==9:
            return YoungDragon(game,x_in,y_in,floor,level,mob_class)
        elif roll==10:
            return AnimatedStatue(game,x_in,y_in,floor,level,mob_class)
        elif roll==11:
            return Imp(game,x_in,y_in,floor,level,mob_class)
        elif roll==12:
            return Kobold(game,x_in,y_in,floor,min(level,1),mob_class)
    else:
        roll = random.randint(1,7)
        if roll==1:
            return Goblin(game,x_in,y_in,floor,level,mob_class)
        elif roll==2:
            return GoblinArcher(game,x_in,y_in,floor,level,mob_class)
        elif roll==3:
            return Wolf(game,x_in,y_in,floor,level,mob_class)
        elif roll==4:
            roll2 = random.randint(1,4)
            if roll2==4:
                return Ghoul(game,x_in,y_in,floor,level,mob_class)
            return choose_monster(game, x_in, y_in, floor, level, mob_class)
        elif roll==5:
            return Spider(game,x_in,y_in,floor,level,mob_class)
        elif roll==6:
            return LandSquid(game,x_in,y_in,floor,level,mob_class)
        elif roll==7:
            return Kobold(game,x_in,y_in,floor,min(level,1),mob_class)

# p = Process(target=calculate, args=(self.pos_x, self.pos_y, child_mgx, child_mgy, child_ugx, child_ugy, child_chain, char.pos_x, char.pos_y, (tile_size-1)))
# @jit()
def calculate(pos_x, pos_y, movement_goal_x, movement_goal_y, ultimate_goal_x, ultimate_goal_y, chain, char_pos_x, char_pos_y, move_range, uuid, mob_data, tiles, step=tile_size):
    # movement_goal_x.send(char_pos_x)
    # movement_goal_y.send(char_pos_y)
    # ultimate_goal_x.send(char_pos_x)
    # ultimate_goal_y.send(char_pos_y)
    # chain.send([])

    start,goal,frontier,came_from,cost_so_far, ugx_source, ugy_source = calculate_set_up_variables(pos_x, pos_y, char_pos_x, char_pos_y)
    came_from,current,success = calculate_find_path(frontier,char_pos_x,char_pos_y,move_range,cost_so_far,came_from,step,goal,uuid,mob_data,tiles)
    if success:
        chain_source,mgx_source,mgy_source = calculate_on_success(came_from,current,start)
        movement_goal_x.send(mgx_source)
        movement_goal_y.send(mgy_source)
        ultimate_goal_x.send(ugx_source)
        ultimate_goal_y.send(ugy_source)
        chain.send(chain_source)
# @jit
def calculate_set_up_variables(pos_x, pos_y, char_pos_x, char_pos_y):
    start = (pos_x, pos_y)
    goal = (char_pos_x,char_pos_y)
    # frontier = Queue.PriorityQueue()
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0
    return start,goal,frontier,came_from,cost_so_far, char_pos_x, char_pos_y
# @jit
def calculate_find_path(frontier,char_pos_x,char_pos_y,move_range,cost_so_far,came_from,step,goal,uuid,mob_data,tiles):
    current = None
    success = False
    while not frontier.empty():
        current = frontier.get()
        x,y=current
        if x>=char_pos_x-move_range+(tile_size-1) and x<=char_pos_x+move_range and y>=char_pos_y-move_range+(tile_size-1) and y<=char_pos_y+move_range:
            success=True
            break
        neighbors_func = mp_neighbors
        for next in neighbors_func(current,uuid,mob_data,tiles,step):
            frontier,came_from = calculate_step(cost_so_far,current,next,frontier,came_from,goal)
    return came_from,current,success
# @jit
def is_wall_exact(tiles,x,y):
    if len(tiles)>x/tile_size:
        if len(tiles[x/tile_size])>y/tile_size:
            return (tiles[x/tile_size][y/tile_size] in ['W','@','F','Q','O','H'])
    return False
# @jit
def is_wall(tiles,x,y):
    if is_wall_exact(tiles,x+2,y+2) or is_wall_exact(tiles,x+(tile_size-3),y+2) or is_wall_exact(tiles,x+2,y+(tile_size-3)) or is_wall_exact(tiles,x+(tile_size-3),y+(tile_size-3)):
        return True
    return False
# @jit
def is_door_exact(tiles,x,y):
    if len(tiles)>x/tile_size:
        if len(tiles[x/tile_size])>y/tile_size:
            return (tiles[x/tile_size][y/tile_size] in ['D','S','R'])
    return False
# @jit
def is_door(tiles,x,y):
    return is_door_exact(tiles,x,y) or is_door_exact(tiles,x+(tile_size-1),y) or is_door_exact(tiles,x,y+(tile_size-1)) or is_door_exact(tiles,x+(tile_size-1),y+(tile_size-1))
# @jit
def mp_neighbors(source, uuid, mob_data,tiles, step=tile_size):
    x,y=source
    value = []
    value = mp_neighbors_step(x+step,y,value, uuid, mob_data, tiles)
    value = mp_neighbors_step(x-step,y,value, uuid, mob_data, tiles)
    value = mp_neighbors_step(x,y+step,value, uuid, mob_data, tiles)
    value = mp_neighbors_step(x,y-step,value, uuid, mob_data, tiles)
    return value
# @jit
def mp_neighbors_step(x,y,value,uuid,mob_data,tiles):
    if not is_wall(tiles,x,y):
        if not is_door(tiles,x,y):
            if not is_collision_mobs_only(x,y,uuid,mob_data):
                value.append((x,y))
    return value
# @jit
def is_collision_mobs_only(x,y,uuid,mob_data):
    for mob in mob_data:
        if mob['uuid']!=uuid:
            if x<=mob['x']+(tile_size-1) and x+(tile_size-1)>=mob['x'] and y<=mob['y']+(tile_size-1) and y+(tile_size-1)>=mob['y']:
                return True
    return False
# @jit
def calculate_step(cost_so_far,current,next,frontier,came_from,goal):
    new_cost = cost_so_far[current] + move_cost(current,next)
    if next not in cost_so_far or new_cost < cost_so_far[next]:
        cost_so_far[next] = new_cost
        priority = new_cost + heuristic(goal, next)
        frontier.put(next, priority)
        came_from[next] = current
    return frontier,came_from
# @jit
def calculate_on_success(came_from,current,start):
    chain = []
    chain.append(current)
    previous=current
    if current!=None:
        chain,mgx,mgy = calculate_build_move_chain(came_from,current,start,chain)
    return chain,mgx,mgy
# @jit
def calculate_build_move_chain(came_from,current,start,chain):
    while came_from[current]!=None and came_from[current]!=start:
        previous = current
        current = came_from[current]
        chain.append(current)
    chain.reverse()
    mgx,mgy = current
    return chain,mgx,mgy

class PriorityQueue(object):
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]
