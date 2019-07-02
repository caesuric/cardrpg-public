import random
import os.path
import tornado.escape
import struct

from floating_text import FloatingText
from projectile import Projectile, DotEffect, DelayedDamageEffect
from cards import Card, Deck
from monsters import Sporeling, AggroEntry
from constants import *

class Character (object):
    @staticmethod
    def from_save_data(uuid):
        if not os.path.isfile('characters.dat'):
            return None
        char_data = None
        with open('characters.dat', 'r') as characters:
            data = tornado.escape.json_decode(characters.read())
            for item in data:
                if item['uuid']==uuid:
                    char_data = item
                    break
        if char_data==None:
            return None
        char = Character()
        char.max_hp = char_data['max_hp']
        char.max_mp = char_data['max_mp']
        char.mp_regen_rate = char_data['mp_regen_rate']
        char.xp = char_data['xp']
        char.total_xp = char_data['total_xp']
        char.level = char_data['level']
        char.starting_class = char_data['starting_class']
        char.name = char_data['name']
        char.color = char_data['color']
        char.eye_color = char_data['eye_color']
        char.uuid = char_data['uuid']
        char.deck = Deck.from_save_data(char_data['deck'])
        return char
    xp_table = [200,462,805,1254,1842,2613,3624,4950,6689,8969,11959,15880,21022,27766,36611,48212,63428,83385,109561,143894,188926,247991,325463,427078,560360,735178,964476,1265232,1659715,2177134,2855801,3745967,4913544,6444984,8453681,11088368,14544128,19076841,25022128,32820204,43048472,56464277,74060983,97141526,127414889,167122642,219204919,287518116]
    usable_during_paralysis = [1,3,34,49]
    def __init__(self):
        self.gcd = 0
        self.autoheal_cd = 0
        self.deck = Deck()
        self.shield = 0
        self.trashes_entitled = 0
        self.initialize_stats()
        self.initialize_references()
        self.initialize_lists()
        self.initialize_booleans()
        self.initialize_position()
        self.pruning = False
        self.move_counter = 0
        self.starting_class = ''
        self.name = ''
    def initialize_position(self):
        self.pos_x = 256
        self.pos_y = 256
        self.facing = 0
    def initialize_stats(self):
        self.hp = 290
        self.max_hp = 290
        self.mp = 100
        self.max_mp = 100
        self.mp_regen_rate = 11
        self.xp = 0
        self.total_xp = 0
        self.level = 1
        self.invisibility_timer = 0
    def initialize_references(self):
        self.handler = None
        self.game = None
        self.target = self
        self.friendly_target = self
        self.friendly_target_num = 0
    def initialize_booleans(self):
        self.alive = True
        self.visible = True
        self.improved_invisibility = False
    def initialize_lists(self):
        self.effects = []
        self.effects_duration = []
        self.effects_max_duration = []
        self.effects_is_buff = []
    def take_hit(self,damage):
        for i in self.deck.in_play:
            if i.type==16:
                damage = int(damage*0.6)
                break
        for i in self.deck.hand:
            if i.type==55:
                i.counters += int(damage*0.25)
                damage = int(damage*0.75)
        self.take_damage(damage)
    def take_damage(self,damage):
        if self.shield==0:
            self.hp-=damage
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,str(damage),'#FF0000'))
        elif self.shield>=damage:
            self.shield-=damage
        else:
            damage-=self.shield
            self.shield=0
            self.hp-=damage
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,str(damage),'#FF0000'))
    def check_for_level_up(self):
        target_level = self.get_target_level()
        if target_level>self.level:
            for i in range(self.level,target_level):
                self.level_up()
    def level_up(self):
        self.handler.sounds.append('level_up')
        self.level+=1
        self.handler.push_narration('Welcome to Level {0}!'.format(self.level))
        self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'LEVEL UP!','#0000FF'))
        prev_max_hp = self.max_hp
        self.max_hp = int(self.max_hp*1.1)
        self.hp = self.max_hp
        self.handler.push_narration('Your maximum HP increases from {0} to {1}.'.format(prev_max_hp, self.max_hp))
        prev_max_mp = self.max_mp
        self.max_mp = int(self.max_mp*1.1)
        self.mp_regen_rate = self.mp_regen_rate*1.05
        self.handler.push_narration('Your maximum MP increases from {0} to {1}.'.format(prev_max_mp, self.max_mp))
        if self.deck.max_cards<60:
            self.deck.max_cards+=1
    def get_target_level(self):
        target_level=1
        if self.total_xp>=Character.xp_table[0]:
            for rank in Character.xp_table:
                if self.total_xp>=rank:
                    target_level+=1
                else:
                    break
        return target_level
    def next_level_xp(self):
        return Character.xp_table[self.level-1]
    def apply_debuff(self,number):
        if number not in self.effects:
            self.effects.append(number)
            min_table = {0:int(1.5*60),1:160,2:60,3:60*10,4:60*15,5:60*180,6:60*3,7:60*10,8:60*10,9:60*10,10:60*10}
            max_table = {0:int(1.875*60),1:640,2:12*60,3:60*10,4:60*15,5:60*180,6:60*3,7:60*10,8:60*10,9:60*10,10:60*10}
            buff_table = {0:False,1:False,2:False,3:True,4:True,5:True,6:True,7:True,8:True,9:True,10:True}
            narration_table = {0:'You have been paralyzed!', 1:'You have been poisoned!', 2:'You have been blinded!', 3:'You gain the benefits of Potency, doubling all damage.', 4:'You are regenerating MP at double speed.', 5:'You are regenerating MP at a faster rate.', 6:'You gain the effects of Shadow Volley and will become invisible when it wears off.', 7:'You are regenerating MP at a faster rate.',8:'You are regenerating MP at a much faster rate.', 9:'You are regenerating MP at a moderately faster rate.',10:'Your attack damage is boosted by Aether Charge.'}
            ft_table = {0: 'PARALYZED', 1:'POISONED', 2:'BLINDED', 3:'ATTACK X2', 4:'MP REGEN X2', 5:'MP REGEN UP', 6:'SHADOW VOLLEY', 7:'MP REGEN UP', 8:'MP REGEN WAY UP', 9:'MP REGEN UP', 10:'ATTACK UP'}
            ft_color_table= {0:'#FFFF00', 1:'#551A8b', 2:'white', 3:'orange', 4:'#0000FF', 5:'#0000FF', 6:'#00FF00', 7:'#0000FF', 8:'#0000FF', 9:'#0000FF', 10:'orange'}
            roll = random.randint(min_table[number],max_table[number])
            self.effects_duration.append(roll)
            self.effects_max_duration.append(roll)
            self.effects_is_buff.append(buff_table[number])
            self.handler.push_narration(narration_table[number])
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,ft_table[number],ft_color_table[number]))
    def tick(self):
        if not self.game:
            return
        for i in self.deck.in_play:
            if i.type==56:
                self.use_thiefs_expertise()
                break
        self.game.check_for_traps_and_spring(self.pos_x,self.pos_y,self)
        self.check_for_and_apply_poison_damage()
        self.decrement_debuffs()
        if self.game.map.tiles[self.pos_x/tile_size][self.pos_y/tile_size]=='f':
            self.take_hit(1)
            if self.hp<=0:
                self.alive=False
        elif self.game.map.tiles[self.pos_x/tile_size][self.pos_y/tile_size]=='a':
            self.apply_poison()
        if self.invisibility_timer > 0:
            self.invisibility_timer -= 1
            if self.invisibility_timer == 0:
                self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'VISIBLE','#FF0000'))
                self.handler.push_narration('You are no longer hidden.')
                self.visible = True
                self.improved_invisibility = False
    def use_thiefs_expertise(self):
        x = self.pos_x/tile_size
        y = self.pos_y/tile_size
        for x_in in range(x-8,x+9):
            for y_in in range (y-8,y+9):
                self.detect_secret_door(x_in,y_in)
        for x_in in range(x-8,x+9):
            for y_in in range (y-8,y+9):
                self.detect_trap(x_in,y_in)
    def apply_poison(self):
        if 1 not in self.effects:
            self.effects.append(1)
            roll = random.randint(160,640)
            self.effects_duration.append(roll)
            self.effects_max_duration.append(roll)
            self.effects_is_buff.append(False)
    def check_for_and_apply_poison_damage(self):
        if 1 in self.effects:
            roll = random.randint(1,10)
            if roll==10:
                self.hp -= 1
                if self.hp<=0:
                    self.alive = False
    def decrement_debuffs(self):
        if len(self.effects)>0:
            for i in range(len(self.effects)):
                if i<len(self.effects_duration):
                    self.effects_duration[i]-=1
                    if self.effects_duration[i]==0:
                        temp = self.effects[i]
                        self.effects.remove(self.effects[i])
                        self.effects_duration.remove(self.effects_duration[i])
                        self.effects_max_duration.remove(self.effects_max_duration[i])
                        self.effects_is_buff.remove(self.effects_is_buff[i])
                        self.show_debuff_removed_message(temp)
    def show_debuff_removed_message(self,value):
        if value==0:
            self.handler.push_narration('You are no longer paralyzed.')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'UN-PARALYZED','#00FF00'))
        elif value==1:
            self.handler.push_narration('You are no longer poisoned.')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'UN-POISONED','#00FF00'))
        elif value==2:
            self.handler.push_narration('You are no longer blinded.')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'UN-BLINDED','#00FF00'))
        elif value==3:
            self.handler.push_narration('You are no longer under the effects of Potency.')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'ATTACK NORMAL','#FF0000'))
        elif value==4:
            self.handler.push_narration('You are no longer regenerating MP at double speed.')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'MP REGEN NORMAL','#FF0000'))
        elif value in [5,7,8,9]:
            self.handler.push_narration('You are no longer regenerating MP at an increased rate.')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'MP REGEN NORMAL','#FF0000'))
        elif value==6:
            self.handler.push_narration('You become invisible due to the effects of Shadow Volley.')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'INVISIBLE','#0000FF'))
            self.visible = False
            self.invisibility_timer = 18*60
            for mob in self.game.monsters:
                if mob.aggro_get(self) > 0:
                    mob.aggro_set(self, 0)
        elif value==10:
            self.handler.push_narration('You attack damage is no longer boosted by Aether Charge.')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'ATTACK NORMAL','#FF0000'))
    def left(self):
        return self.pos_x
    def right(self):
        return self.pos_x+tile_size-1
    def top(self):
        return self.pos_y
    def bottom(self):
        return self.pos_y+tile_size-1
    def push_tab(self):
        target_num = 0
        for i in range(len(self.game.chars)):
            if self.game.chars[i]==self.target:
                target_num=i+1
        if target_num>=len(self.game.chars):
            target_num = 0
        self.friendly_target = self.game.chars[target_num]
        self.friendly_target_num = target_num
    def push_up(self):
        if 0 in self.effects:
            return
        for i in range(tile_size/8,1,-1):
            if not self.game.is_wall(self.pos_x,self.pos_y-i) and not self.game.is_collision(self.pos_x,self.pos_y-i,self):
                self.pos_y-=i
                break
        self.facing = 0
        self.game.check_for_door_and_open(self.pos_x,self.pos_y)
        self.game.check_for_chests_and_open(self.pos_x,self.pos_y)
        self.game.check_for_traps_and_spring(self.pos_x,self.pos_y,self)
        self.move_counter += 1
        if self.move_counter>=tile_size and self.visible:
            self.game.make_noise(self.pos_x,self.pos_y, 18)
            self.move_counter = 0
    def push_down(self):
        if 0 in self.effects:
            return
        for i in range(tile_size/8,1,-1):
            if not self.game.is_wall(self.pos_x,self.pos_y+i) and not self.game.is_collision(self.pos_x,self.pos_y+i,self):
                self.pos_y+=i
                break
        self.facing = 2
        self.game.check_for_door_and_open(self.pos_x,self.pos_y)
        self.game.check_for_chests_and_open(self.pos_x,self.pos_y)
        self.game.check_for_traps_and_spring(self.pos_x,self.pos_y,self)
        self.move_counter += 1
        if self.move_counter>=tile_size and self.visible:
            self.game.make_noise(self.pos_x,self.pos_y, 18)
            self.move_counter = 0
    def push_left(self):
        if 0 in self.effects:
            return
        for i in range(tile_size/8,1,-1):
            if not self.game.is_wall(self.pos_x-i,self.pos_y) and not self.game.is_collision(self.pos_x-i,self.pos_y,self):
                self.pos_x-=i
                break
        self.facing = 3
        self.game.check_for_door_and_open(self.pos_x,self.pos_y)
        self.game.check_for_chests_and_open(self.pos_x,self.pos_y)
        self.game.check_for_traps_and_spring(self.pos_x,self.pos_y,self)
        self.move_counter += 1
        if self.move_counter>=tile_size and self.visible:
            self.game.make_noise(self.pos_x,self.pos_y, 18)
            self.move_counter = 0
    def push_right(self):
        if 0 in self.effects:
            return
        for i in range(tile_size/8,1,-1):
            if not self.game.is_wall(self.pos_x+i,self.pos_y) and not self.game.is_collision(self.pos_x+i,self.pos_y,self):
                self.pos_x+=i
                break
        self.facing = 1
        self.game.check_for_door_and_open(self.pos_x,self.pos_y)
        self.game.check_for_chests_and_open(self.pos_x,self.pos_y)
        self.game.check_for_traps_and_spring(self.pos_x,self.pos_y,self)
        self.move_counter += 1
        if self.move_counter>=tile_size and self.visible:
            self.game.make_noise(self.pos_x,self.pos_y, 18)
            self.move_counter = 0
    def push_downstairs(self):
        if 0 in self.effects:
            return
        self.game.check_for_stairs_and_use(self.pos_x,self.pos_y,'>')
    def push_upstairs(self):
        if 0 in self.effects:
            return
        self.game.check_for_stairs_and_use(self.pos_x,self.pos_y,'<')
    def push_q(self):
        if 0 in self.effects:
            return
        self.game.check_for_fountain_and_use(self,self.pos_x,self.pos_y)
    def push_b(self):
        if 0 in self.effects:
            return
        self.game.check_for_shop_and_use(self,self.pos_x,self.pos_y)
    def push_m(self):
        if self.game.should_decrement_autoheals():
            self.handler.push_narration('You take a mulligan.')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'MULLIGAN','#0000FF'))
            for i in range(len(self.deck.hand)):
                self.deck.discard_pile.append(self.deck.hand[i])
                self.deck.hand[i]=None
            for i in range(6):
                self.deck.draw(i)
        else:
            self.handler.push_narration('You attempt to take a mulligan, but there are monsters nearby.')
    def push_1(self):
        # if 0 in self.effects and self.deck.hand[0].type!=12:
        if self.check_for_curse() and not (0 in self.effects) and self.gcd==0:
            number = self.get_curse_position()
            self.gcd = 90
            self.use_ability(self.deck.hand[number].type)
            self.move_card(number)
        if not self.deck.hand[0]:
            return
        if (0 in self.effects and self.deck.hand[0].type not in Character.usable_during_paralysis) or ability_mp_cost(self.deck.hand[0].type)>self.mp:
            return
        if self.gcd==0:
            self.gcd=90
            number = 0
            self.use_ability(self.deck.hand[number].type)
            self.move_card(number)
    def push_2(self):
        if self.check_for_curse() and not (0 in self.effects) and self.gcd==0:
            number = self.get_curse_position()
            self.gcd = 90
            self.use_ability(self.deck.hand[number].type)
            self.move_card(number)
        if not self.deck.hand[1]:
            return
        if (0 in self.effects and self.deck.hand[1].type not in Character.usable_during_paralysis) or ability_mp_cost(self.deck.hand[1].type)>self.mp:
            return
        if self.gcd==0:
            self.gcd=90
            number = 1
            self.use_ability(self.deck.hand[number].type)
            self.move_card(number)
    def push_3(self):
        if self.check_for_curse() and not (0 in self.effects) and self.gcd==0:
            number = self.get_curse_position()
            self.gcd = 90
            self.use_ability(self.deck.hand[number].type)
            self.move_card(number)
        if not self.deck.hand[2]:
            return
        if (0 in self.effects and self.deck.hand[2].type not in Character.usable_during_paralysis) or ability_mp_cost(self.deck.hand[2].type)>self.mp:
            return
        if self.gcd==0:
            self.gcd=90
            number = 2
            self.use_ability(self.deck.hand[number].type)
            self.move_card(number)
    def push_4(self):
        if self.check_for_curse() and not (0 in self.effects) and self.gcd==0:
            number = self.get_curse_position()
            self.gcd = 90
            self.use_ability(self.deck.hand[number].type)
            self.move_card(number)
        if not self.deck.hand[3]:
            return
        if (0 in self.effects and self.deck.hand[3].type not in Character.usable_during_paralysis) or ability_mp_cost(self.deck.hand[3].type)>self.mp:
            return
        if self.gcd==0:
            self.gcd=90
            number = 3
            self.use_ability(self.deck.hand[number].type)
            self.move_card(number)
    def push_5(self):
        if self.check_for_curse() and not (0 in self.effects) and self.gcd==0:
            number = self.get_curse_position()
            self.gcd = 90
            self.use_ability(self.deck.hand[number].type)
            self.move_card(number)
        if not self.deck.hand[4]:
            return
        if (0 in self.effects and self.deck.hand[4].type not in Character.usable_during_paralysis) or ability_mp_cost(self.deck.hand[4].type)>self.mp:
            return
        if self.gcd==0:
            self.gcd=90
            number = 4
            self.use_ability(self.deck.hand[number].type)
            self.move_card(number)
    def push_6(self):
        if self.check_for_curse() and not (0 in self.effects) and self.gcd==0:
            number = self.get_curse_position()
            self.gcd = 90
            self.use_ability(self.deck.hand[number].type)
            self.move_card(number)
        if not self.deck.hand[5]:
            return
        if (0 in self.effects and self.deck.hand[5].type not in Character.usable_during_paralysis) or ability_mp_cost(self.deck.hand[5].type)>self.mp:
            return
        if self.gcd==0:
            self.gcd=90
            number = 5
            self.use_ability(self.deck.hand[number].type)
            self.move_card(number)
    def move_card(self,number):
        table = {52: self.move_card_self_trash}
        if self.deck.hand[number].type in table:
            table[self.deck.hand[number].type](number)
        else:
            self.move_card_generic(number)
        self.deck.hand[number] = None
        self.deck.draw(number)
    def move_card_self_trash(self, number):
        pass #literally doing nothing here will trash the card since it no longer gets a destination
    def move_card_2_counters(self,number):
        self.deck.hand[number].counters = 2
        self.deck.in_play.append(self.deck.hand[number])
    def move_card_9_seconds(self,number):
        self.deck.hand[number].counters = 9*60
        self.deck.in_play.append(self.deck.hand[number])
    def move_card_stealth(self,number):
        if self.visible==False:
            self.deck.hand[number].counters = 1
            self.deck.in_play.append(self.deck.hand[number])
        else:
            self.deck.discard_pile.append(self.deck.hand[number])
    def move_card_generic(self,number):
        self.deck.discard_pile.append(self.deck.hand[number])
    def check_for_careful_shot(self):
        careful_shot_buff=False
        for i in self.deck.in_play:
            if i and i.type==1:
                i.counters-=1
                careful_shot_buff=True
                if i.counters==0:
                    self.deck.discard_pile.append(i)
                    self.deck.in_play.remove(i)
        return careful_shot_buff
    def check_for_charge(self):
        for i in self.deck.in_play:
            if i and i.type==2:
                return True
        return False
    def remove_stealth(self):
        self.visible = True
        for i in self.deck.in_play:
            if i and i.type==9:
                self.deck.discard_pile.append(i)
                self.deck.in_play.remove(i)
                self.handler.push_narration('You are no longer under the effects of Stealth.')
                self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'VISIBLE','#FF0000'))
                break
    def damage_multiplier(self,damage):
        # careful_shot_buff = self.check_for_careful_shot()
        # charge_buff = self.check_for_charge()
        # if careful_shot_buff:
        #     damage=damage*1.4
        # if charge_buff:
        #     damage=damage*1.3
        # return int(damage)
        if 3 in self.effects:
            damage *= 2
        if 10 in self.effects:
            damage *= 1.75
        return damage
    def use_ability(self,num):
        backstab = self.use_ability_check_for_backstab_and_disable_stealth(num)
        table = [self.use_ability0, self.use_ability1, self.use_ability2, self.use_ability3, self.use_ability4, self.use_ability5, self.use_ability6, self.use_ability7, self.use_ability8, self.use_ability9, self.use_ability10, self.use_ability11, self.use_ability12, self.use_ability13, self.use_ability14, self.use_ability15, self.use_ability16, self.use_ability17, self.use_ability18, self.use_ability19, self.use_ability20, self.use_ability21, self.use_ability22, self.use_ability23, self.use_ability24, self.use_ability25, self.use_ability26, self.use_ability27, self.use_ability28, self.use_ability29, self.use_ability30, self.use_ability31, self.use_ability32, self.use_ability33, self.use_ability34, self.use_ability35, self.use_ability36, self.use_ability37, self.use_ability38, self.use_ability39, self.use_ability40, self.use_ability41, self.use_ability42, self.use_ability43, self.use_ability44, self.use_ability45, self.use_ability46, self.use_ability47, self.use_ability48, self.use_ability49, self.use_ability50, self.use_ability51, self.use_ability52, self.use_ability53, self.use_ability54, self.use_ability55, self.use_ability56]
        table[num](backstab)
    def use_ability0(self,backstab):
        damage = 12
        damage = self.damage_multiplier(damage)
        self.handler.push_narration('You Shoot for ' + str(damage) + ' damage.')
        self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),tile_size*8,self,color='brown'))
        self.game.sounds.append('attack')
        self.game.make_noise(self.pos_x,self.pos_y, 20)
    def use_ability1(self,backstab):
        if self.game.chain_timer > 0 and not self.game.should_decrement_autoheals():
            self.game.chain_timer += 2.5*60
            self.handler.push_narration('You use Keen Perception, increasing the chain timer.')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'TIMER+','#0000FF'))
        else:
            self.handler.push_narration('You use Keen Perception, which does nothing when there is no chain timer.')
    def use_ability2(self,backstab):
        if self.mp >= 44:
            self.mp -= 44
            damage = 9
            damage = self.damage_multiplier(damage)
            self.handler.push_narration('You throw a Fireball for ' + str(damage) + ' damage.')
            self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),tile_size*8,self,effect=3,color='#FF0000'))
            self.game.sounds.append('attack')
            self.game.make_noise(self.pos_x,self.pos_y, 25)
        else:
            self.handler.push_narration('You attempt to throw a Fireball, but don\'t have enough MP.')
    def use_ability3(self,backstab):
        if self.game.current_chain in [2,3]:
            self.handler.push_narration('You use Lorechannel, increasing the current chain bonus.')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'CHAIN+','#0000FF'))
            self.game.current_chain += 1
        else:
            self.handler.push_narration('You attempt to use Lorechannel, which does nothing when the chain timer isn\'t 2-3.')
    def use_ability4(self, backstab):
        if self.mp >= 44:
            self.mp -= 44
            damage = 0
            dot_dps = 4.5
            dot_time = 8
            dot_dps = self.damage_multiplier(dot_dps)
            self.handler.push_narration('You throw a Poison Bolt for '+ str(dot_dps*8) +' damage over 8 seconds.')
            self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),tile_size*8,self,dot=DotEffect(dot_dps, dot_time),color='#00FF00'))
            self.game.sounds.append('attack')
            self.game.make_noise(self.pos_x,self.pos_y, 20)
        else:
            self.handler.push_narration('You attempt to throw a Poison Bolt, but don\'t have enough MP.')
    def unlock(self,x_in,y_in):
        if x_in<0 or len(self.game.map.tiles)<=x_in or y_in<0 or len(self.game.map.tiles)<=y_in:
            return
        if self.game.map.tiles[x_in][y_in] == 'H':
            self.handler.push_narration('The chest unlocks!')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'UNLOCK','#0000FF'))
            self.game.map.tiles[x_in][y_in] = 'C'
        elif self.game.map.tiles[x_in][y_in] == 'O':
            self.handler.push_narration('The door unlocks!')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'UNLOCK','#0000FF'))
            self.game.map.tiles[x_in][y_in] = 'D'
    def disarm(self,x_in,y_in):
        if x_in<0 or len(self.game.map.tiles)<=x_in or y_in<0 or len(self.game.map.tiles)<=y_in:
            return
        if self.game.map.tiles_trapped[x_in][y_in]:
            self.handler.push_narration('You disarm a trap!')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'DISARM','#0000FF'))
            self.game.map.tiles_trapped[x_in][y_in] = False
            if self.game.map.tiles[x_in][y_in]=='T':
                self.game.map.tiles[x_in][y_in]=' '
            elif self.game.map.tiles[x_in][y_in]=='R':
                self.game.map.tiles[x_in][y_in] = 'D'
            elif self.game.map.tiles[x_in][y_in]=='E':
                self.game.map.tiles[x_in][y_in] = 'C'
    def use_ability5(self,backstab):
        self.handler.push_narration('You use Aura Cleanse.')
        highest = 0
        chosen = -1
        for i in range(len(self.friendly_target.effects_duration)):
            if self.friendly_target.effects_duration[i]>highest and self.friendly_target.effects_is_buff[i]==False:
                highest = self.friendly_target.effects_duration[i]
                chosen = i
        if chosen != -1:
            self.game.floating_text.append(FloatingText(friendly_target.pos_x,friendly_target.pos_y,'CLEANSE','#0000FF'))
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'MP UP','#0000FF'))
            self.friendly_target.effects_duration.remove(self.friendly_target.effects_duration[i])
            self.friendly_target.effects.remove(self.friendly_target.effects[i])
            self.increase_aggro_with_all_mobs(6)
            self.mp += (self.max_mp/2)
            self.mp = min(self.mp,self.max_mp)
    def detect_secret_door(self,x_in,y_in):
        if len(self.game.map.tiles)>x_in and len(self.game.map.tiles[x_in])>y_in and self.game.map.tiles[x_in][y_in]=='S' and self.game.in_line_of_sight(self,self.game.map.tiles,x_in,y_in):
            self.game.map.tiles[x_in][y_in]='D'
            self.handler.push_narration('You discover a secret door!')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'DETECT','#0000FF'))
    def detect_trap(self,x_in,y_in):
        if len(self.game.map.tiles_trapped)>x_in and len(self.game.map.tiles_trapped[x_in])>y_in and self.game.map.tiles_trapped[x_in][y_in] and self.game.in_line_of_sight(self,self.game.map.tiles,x_in,y_in):
            self.handler.push_narration('You discover a trap!')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'DETECT','#0000FF'))
            if self.game.map.tiles[x_in][y_in]=='D':
                self.game.map.tiles[x_in][y_in]='R'
            elif self.game.map.tiles[x_in][y_in]=='C':
                self.game.map.tiles[x_in][y_in]='E'
            elif self.game.map.tiles[x_in][y_in]==' ':
                self.game.map.tiles[x_in][y_in]='T'
    def use_ability6(self,backstab):
        if self.mp >= 44:
            self.mp -= 44
            damage = self.damage_multiplier(24)
            self.handler.push_narration('You Smite for ' + str(damage) + ' damage.')
            self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),int(float(tile_size)*1.5),self))
            self.game.sounds.append('attack')
            self.game.make_noise(self.pos_x,self.pos_y, 20)
        else:
            self.handler.push_narration('You attempt to Smite, but dont\'t have enough MP.')
    def use_ability7(self,backstab):
        damage = self.damage_multiplier(8)
        self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),int(float(tile_size)*1.5),self,effect=2))
        self.game.sounds.append('attack')
        self.handler.push_narration('You Shimmerstrike for {0} damage.'.format(damage))
        self.game.make_noise(self.pos_x,self.pos_y, 20)
    def use_ability8(self,backstab):
        damage = self.damage_multiplier(16)
        self.handler.push_narration('You Strike for '+str(damage)+' damage.')
        self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),int(float(tile_size)*1.5),self))
        self.game.sounds.append('attack')
        self.game.make_noise(self.pos_x,self.pos_y, 20)
    def use_ability9(self,backstab):
        damage = self.damage_multiplier(8)
        self.handler.push_narration('You use Sword and Board for '+str(damage)+' damage, defending yourself in the process.')
        self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),int(float(tile_size)*1.5),self))
        self.game.sounds.append('attack')
        self.shield = 14
        self.increase_aggro_with_all_mobs(7)
        self.game.make_noise(self.pos_x,self.pos_y, 20)
    def use_ability10(self,backstab):
        if self.mp >= 44:
            self.mp -= 44
            healing = 28
            self.handler.push_narration('You use Lesser Healing for {0} HP.'.format(healing))
            self.game.floating_text.append(FloatingText(friendly_target.pos_x,friendly_target.pos_y,str(healing),'#00FF00'))
            self.friendly_target.hp+=healing
            if self.friendly_target.hp>self.friendly_target.max_hp:
                self.friendly_target.hp = self.friendly_target.max_hp
            self.increase_aggro_with_all_mobs(healing)
        else:
            self.handler.push_narration('You attempt to Heal, but don\'t have enough MP')
    def use_ability11(self,backstab):
        if self.mp >= 44:
            self.mp -= 44
            damage = 10
            dot_dps = 3
            dot_time = 8
            damage = self.damage_multiplier(damage)
            dot_dps = self.damage_multiplier(dot_dps)
            self.handler.push_narration('You throw a Firebolt for '+str(damage)+' and '+ str(dot_dps*8) +' damage over 8 seconds.')
            self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),tile_size*8,self,dot=DotEffect(dot_dps, dot_time),color='#FF0000'))
            self.game.sounds.append('attack')
            self.game.make_noise(self.pos_x,self.pos_y, 20)
        else:
            self.handler.push_narration('You attempt to throw a Firebolt, but don\'t have enough MP.')
    def USE_OLD_ABILITY_STEALTH(self,backstab):
        if self.game.should_decrement_autoheals():
            self.handler.push_narration('You activate Stealth.')
            self.visible = False
        else:
            self.handler.push_narration('You fail to activate Stealth because there are monsters nearby.')
    def use_ability12(self,backstab):
        if self.game.should_decrement_autoheals() and self.mp >= 88:
            self.handler.push_narration('You cast Invisibility.')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'INVISIBLE','#0000FF'))
            self.mp -= 88
            self.visible = False
            self.invisibility_timer = 60*25
        elif not self.game.should_decrement_autoheals():
            self.handler.push_narration('You fail to cast Invisibility because there are monsters nearby.')
        elif self.mp < 88:
            self.handler.push_narration('You fail to cast Invisibility because you don\'t have enough MP.')
    def use_ability13(self,backstab):
        if self.mp >= 44:
            self.mp -= 44
            damage = 18
            damage = self.damage_multiplier(damage)
            self.handler.push_narration('You throw a Shadow Bomb for ' + str(damage) + ' damage. Damage will not trigger for 5 seconds.')
            self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,0,tile_size*8,self,delayed_damage_effect=DelayedDamageEffect(int(damage),5,self,True),color='#551A8b'))
            self.game.sounds.append('attack')
            self.game.make_noise(self.pos_x,self.pos_y, 20)
        else:
            self.handler.push_narration('You attempt to throw a Shadow Bomb, but don\'t have enough MP.')
    def use_ability14(self,backstab):
        if self.mp >= 44:
            self.mp -= 44
            for mob in self.game.monsters:
                if abs(self.pos_x+tile_size/2-mob.pos_x)<=(tile_size*2) and abs(self.pos_y+tile_size/2-mob.pos_y)<=16:
                    mob.aggro_increment_if_aggrod(self,11)
                    mob.apply_effect(0,self)
            self.handler.push_narration('You use Holy Aura.')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'HOLY AURA','white'))
        else:
            self.handler.push_narration('You attempt to use Holy Aura, but don\'t have enough MP.')
    def use_ability15(self,backstab):
        if self.mp >= 88:
            self.mp -= 88
            damage = self.damage_multiplier(15)
            for mob in self.game.monsters:
                if abs(self.pos_x+tile_size/2-mob.pos_x)<=(tile_size*3) and abs(self.pos_y+tile_size/2-mob.pos_y)<=(tile_size*3):
                    mob.take_hit(damage,self)
            self.handler.push_narration('You use Lightning Cowl for {0} damage'.format(damage))
            left = self.pos_x+tile_size/2-(tile_size*3)
            right = self.pos_x+tile_size/2+(tile_size*3)
            top = self.pos_y+tile_size/2-(tile_size*3)
            bottom = self.pos_y+tile_size/2+(tile_size*3)
            animation_text = str(left)+','+str(right)+','+str(top)+','+str(bottom)+','+'#FFFF00'
            for handler in self.game.handlers:
                handler.animations.append(animation_text)
            self.game.make_noise(self.pos_x,self.pos_y, 25)
        else:
            self.handler.push_narration('You attempt to use Lightning Cowl, but don\'t have enough MP.')
    def use_ability16(self,backstab):
        self.handler.push_narration('You use Legerdemain, disabling nearby mechanisms and reducing aggro.')
        for mob in self.game.monsters:
            if mob.aggro_get(self) > 0:
                mob.aggro_set(self, int(mob.aggro_get(self)/2))
        x = self.pos_x/tile_size
        y = self.pos_y/tile_size
        for x_in in range(x-1,x+2):
            for y_in in range(y-1,y+2):
                self.unlock(x_in,y_in)
        for x_in in range(x-1,x+2):
            for y_in in range(y-1,y+2):
                self.disarm(x_in,y_in)
    def use_ability17(self, backstab):
        if self.mp >= 44:
            self.mp -= 44
            healing = 28
            self.handler.push_narration('You use Blessing for {0} HP.'.format(healing))
            self.game.floating_text.append(FloatingText(friendly_target.pos_x,friendly_target.pos_y,str(healing),'#00FF00'))
            self.friendly_target.hp+=healing
            if self.friendly_target.hp>self.friendly_target.max_hp:
                self.friendly_target.hp = self.friendly_target.max_hp
            self.increase_aggro_with_all_mobs(healing)
            if self.game.current_chain in [2,3]:
                self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'CHAIN+','#0000FF'))
                self.handler.push_narration('The current chain bonus increases.')
                self.game.current_chain += 1
        else:
            self.handler.push_narration('You attempt to use Blessing, but don\'t have enough MP')
    def use_ability18(self, backstab):
        if self.mp >= 22:
            self.mp -= 22
            damage = 26
            damage = self.damage_multiplier(damage)
            self.handler.push_narration('You cast Cinder Toss for ' + str(damage) + ' damage.')
            self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),tile_size*8,self,color='#FF0000'))
            self.game.sounds.append('attack')
            self.game.make_noise(self.pos_x,self.pos_y, 20)
        else:
            self.handler.push_narration('You attempt to use Cinder Toss, but don\'t have enough MP')
    def use_ability19(self, backstab):
        self.handler.push_narration('You use Shout, increasing your aggro with all nearby monsters.')
        self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'SHOUT','white'))
        self.increase_aggro_with_all_mobs(21)
        self.game.make_noise(self.pos_x,self.pos_y, 25)
    def use_ability20(self,backstab):
        if self.game.should_decrement_autoheals():
            self.handler.push_narration('You use Caution, entering Stealth.')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'STEALTH','#0000FF'))
            self.visible = False
            self.invisibility_timer = 60*10
        else:
            self.handler.push_narration('You fail to enter Stealth because there are monsters nearby.')
        x = self.pos_x/tile_size
        y = self.pos_y/tile_size
        for x_in in range(x-8,x+9):
            for y_in in range (y-8,y+9):
                self.detect_secret_door(x_in,y_in)
        for x_in in range(x-8,x+9):
            for y_in in range (y-8,y+9):
                self.detect_trap(x_in,y_in)
    def use_ability21(self, backstab):
        if self.mp >= 44:
            if self.game.chain_timer and not self.game.should_decrement_autoheals > 0:
                self.mp -= 44
                self.game.chain_timer += 562
                self.handler.push_narration('You cast Augury, increasing the chain timer.')
                self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'TIMER+','#0000FF'))
            else:
                self.handler.push_narration('You cast Augury, which does nothing when there is no chain timer.')
        else:
            self.handler.push_narration('You attempt to cast Augury, but don\'t have enough MP.')
    def use_ability22(self, backstab):
        self.handler.push_narration('You use Find Weakness, increasing the vulnerability of an enemy if it hits.')
        self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,0,tile_size*8,self,effect=4))
        self.game.sounds.append('attack')
        self.game.make_noise(self.pos_x,self.pos_y, 20)
    def use_ability23(self, backstab):
        if self.mp >= 100:
            self.mp -= 100
            damage = 35
            if self.mp >= 76:
                self.mp -= 76
                damage += 21
            damage = self.damage_multiplier(damage)
            self.handler.push_narration('You cast Immolate for '+str(damage)+' damage.')
            self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),tile_size*8,self,color='#FF0000'))
            self.game.sounds.append('attack')
            self.game.make_noise(self.pos_x,self.pos_y, 20)
        else:
            self.handler.push_narration('You attempt to cast Immolate, but don\'t have enough MP.')
    def use_ability24(self, backstab):
        damage = self.damage_multiplier(30)
        self.handler.push_narration('You fire a Fusillade for '+str(damage)+' damage.')
        self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),tile_size*8,self,color='brown'))
        self.game.sounds.append('attack')
        self.game.make_noise(self.pos_x,self.pos_y, 20)
    def use_ability25(self,backstab):
        damage = self.damage_multiplier(15)
        self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),tile_size*8,self,effect=2,color='brown'))
        self.game.sounds.append('attack')
        self.handler.push_narration('You fire a Vexing Shot for {0} damage.'.format(damage))
        self.game.make_noise(self.pos_x,self.pos_y, 20)
    def use_ability26(self,backstab):
        damage = self.damage_multiplier(28)
        self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),tile_size*8,self,effect=5,color='#551A8b'))
        self.game.sounds.append('attack')
        self.handler.push_narration('You use Essence Theft for {0} damage.'.format(damage))
        self.game.make_noise(self.pos_x,self.pos_y, 20)
    def use_ability27(self,backstab):
        damage = 0
        self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),int(float(tile_size)*1.5),self,effect=6))
        self.game.sounds.append('attack')
        self.handler.push_narration('You use Distract.')
    def use_ability28(self,backstab):
        if self.mp >= 44:
            self.mp -= 44
            self.handler.push_narration('You use Make Right, disabling nearby mechanisms in sight and healing allies.')
            for char in self.game.chars:
                char.hp = min(char.hp+25, char.max_hp)
                self.game.floating_text.append(FloatingText(char.pos_x,char.pos_y,'25','#00FF00'))
            x = self.pos_x/tile_size
            y = self.pos_y/tile_size
            for x_in in range(x-8,x+9):
                for y_in in range (y-8,y+9):
                    self.unlock(x_in,y_in)
            for x_in in range(x-8,x+9):
                for y_in in range (y-8,y+9):
                    self.disarm(x_in,y_in)
        else:
            self.handler.push_narration('You attempt to cast Make Right, but don\'t have enough MP.')
    def use_ability29(self,backstab):
        #ability 29 trashes on buy so should be unusable, but this is included as a safety
        self.handler.push_narration('WARNING: FOCUS SHOULD NEVER MAKE IT INTO YOUR DECK. SOMETHING HAS GONE WRONG!')
    def use_ability30(self,backstab):
        self.handler.push_narration('You use Noisy Search, annoying nearby monsters and detecting mechanisms!')
        self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'NOISY SEARCH','white'))
        self.increase_aggro_with_all_mobs(32)
        self.game.make_noise(self.pos_x,self.pos_y, 25)
        x = self.pos_x/tile_size
        y = self.pos_y/tile_size
        for x_in in range(x-8,x+9):
            for y_in in range (y-8,y+9):
                self.detect_secret_door(x_in,y_in)
        for x_in in range(x-8,x+9):
            for y_in in range (y-8,y+9):
                self.detect_trap(x_in,y_in)
    def use_ability31(self,backstab):
        if self.mp >= 44:
            self.mp -= 44
            self.handler.push_narration('You cast War Blessing, greatly boosting ally damage!')
            for char in self.game.chars:
                char.apply_debuff(3)
        else:
            self.handler.push_narration('You attempt to cast War Blessing, but don\'t have enough MP.')
    def use_ability32(self,backstab):
        if self.mp >= 44:
            self.mp -= 44
            self.handler.push_narration('You cast Shadowmeld, becoming invisible and losing all aggro.')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'INVISIBLE','#0000FF'))
            self.visible = False
            self.invisibility_timer = 60*15
            self.improved_invisibility = True
            for mob in self.game.monsters:
                if mob.aggro_get(self) > 0:
                    mob.aggro_set(self, 0)
        else:
            self.handler.push_narration('You attempt to cast Shadowmeld, but don\'t have enough MP.')
    def use_ability33(self,backstab):
        if self.mp >= 44:
            self.mp -= 44
            self.handler.push_narration('You cast Perfect Knowledge, detecting mechanisms and boosting your damage.')
            self.apply_debuff(3)
            x = self.pos_x/tile_size
            y = self.pos_y/tile_size
            for x_in in range(x-8,x+9):
                for y_in in range (y-8,y+9):
                    self.detect_secret_door(x_in,y_in)
            for x_in in range(x-8,x+9):
                for y_in in range (y-8,y+9):
                    self.detect_trap(x_in,y_in)
        else:
            self.handler.push_narration('You attempt to cast Perfect Knowledge, but don\'t have enough MP.')
    def use_ability34(self,backstab):
        self.handler.push_narration('You use Tranquil Meditation, boosting the chain bonus if it is 1 or higher and dropping all aggro.')
        if self.game.current_chain > 0:
            self.game.current_chain += 2
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'CHAIN+','#0000FF'))
        for mob in self.game.monsters:
            if mob.aggro_get(self) > 0:
                mob.aggro_set(self, 0)
    def use_ability35(self, backstab):
        if self.mp >= 22:
            self.handler.push_narration('You use Kindling Strike, increasing the vulnerability of an enemy if it hits.')
            self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,0,int(float(tile_size)*1.5),self,effect=7,color='#FF0000'))
            self.game.sounds.append('attack')
            self.game.make_noise(self.pos_x,self.pos_y, 20)
        else:
            self.handler.push_narration('You attempt to use Kindling Strike, but don\'t have enough MP.')
    def use_ability36(self,backstab):
        if self.mp >= 88:
            self.mp -= 88
            self.handler.push_narration('You cast Greater Invisibility, becoming invisible and rapidly regenerating MP')
            self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'INVISIBLE','#0000FF'))
            self.visible = False
            self.invisibility_timer = 60*15
            self.improved_invisibility = True
            self.apply_debuff(4)
        else:
            self.handler.push_narration('You attempt to cast Greater Invisibility, but don\'t have enough MP.')
    def use_ability37(self,backstab):
        self.handler.push_narration('You use Void Rage, boosting your damage.')
        self.apply_debuff(3)
        self.game.make_noise(self.pos_x,self.pos_y, 20)
    def use_ability38(self,backstab):
        damage = self.damage_multiplier(32)
        self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),tile_size*8,self,effect=8))
        self.game.sounds.append('attack')
        if self.game.chain_timer > 0 and not self.game.should_decrement_autoheals:
            self.game.chain_timer += 5*60
        self.handler.push_narration('You use Uncanny Expertise for {0} damage, boosting the chain timer and adding a completed chain if it hits.'.format(damage))
    def use_ability39(self,backstab):
        if self.mp >= 44:
            self.mp -= 44
            self.handler.push_narration('You cast Breaker of Chains.')
            for char in self.game.chars:
                self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'FREEDOM','#0000FF'))
                char.effects = []
                char.effects_duration = []
                char.effects_is_buff = []
            for mob in self.game.monsters:
                if mob.aggro_get(self) > 0:
                    mob.aggro_set(self, 0)
            self.apply_debuff(5)
        else:
            self.handler.push_narration('You attempt to cast Breaker of Chains, but don\'t have enough MP.')
    def use_ability40(self,backstab):
        damage = 34
        damage = self.damage_multiplier(damage)
        if backstab:
            damage*=4
        self.handler.push_narration('You fire a Shadow Volley for '+str(damage)+' damage. You will become invisible in 3 seconds.')
        self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),tile_size*8,self,color='#551A8b'))
        self.game.sounds.append('attack')
        self.apply_debuff(6)
    def use_ability41(self,backstab):
        if self.mp >= 88:
            self.mp -= 88
            damage = self.damage_multiplier(24)
            dot_damage = self.damage_multiplier(3)
            self.handler.push_narration('You launch a Star Breach for ' + str(damage) + ' and '+ str(dot_damage*8) +' damage over 8 seconds.')
            self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),tile_size*8,self,effect=9,dot=DotEffect(dot_damage,8),color='#FFFF00'))
            self.game.sounds.append('attack')
            self.game.make_noise(self.pos_x,self.pos_y, 25)
        else:
            self.handler.push_narration('You attempt to launch a Star Breach, but don\'t have enough MP.')
    def use_ability42(self,backstab):
        damage = self.damage_multiplier(22)
        if backstab:
            damage*=4
        self.handler.push_narration('You Backstab for '+str(damage)+' damage.')
        self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),int(float(tile_size)*1.5),self))
        self.game.sounds.append('attack')
    def use_ability43(self,backstab):
        self.handler.push_narration('You use Sanctuary, reducing aggro and increasing MP restoration rate.')
        self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'AGGRO DOWN','white'))
        self.apply_debuff(7)
        for mob in self.game.monsters:
            if mob.aggro_get(self) > 0:
                mob.aggro_set(self, int(mob.aggro_get(self)*0.65))
    def use_ability44(self,backstab):
        self.handler.push_narration('You use Aether Channel, greatly increasing your MP restoration rate.')
        self.apply_debuff(8)
    def use_ability45(self,backstab):
        self.handler.push_narration('You call upon Ancient Knowledge, moderately increasing your MP restoration rate.')
        self.apply_debuff(9)
    def use_ability46(self,backstab):
        if self.mp >= 44:
            self.mp -= 44
            damage = self.damage_multiplier(63)
            self.handler.push_narration('You cast Roast for '+str(damage)+' damage.')
            self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),tile_size*8,self,color='#FF0000'))
            self.game.sounds.append('attack')
            self.game.make_noise(self.pos_x,self.pos_y, 20)
        else:
            self.handler.push_narration('You attempt to cast Roast, but don\'t have enough MP.')
    def use_ability47(self,backstab):
        if self.mp >= 44:
            self.mp -= 44
            damage = 0
            dot_time = 8
            dot_dps = self.damage_multiplier(11)
            self.handler.push_narration('You cast Halt and Catch Fire for ' + str(dot_dps*8) +' damage over 8 seconds.')
            self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),tile_size*8,self,effect=10,dot=DotEffect(dot_dps, dot_time),color='#FF0000'))
            self.game.sounds.append('attack')
            self.game.make_noise(self.pos_x,self.pos_y, 20)
        else:
            self.handler.push_narration('You attempt to cast Halt and Catch Fire, but don\'t have enough MP.')
    def use_ability48(self,backstab):
        self.handler.push_narration('You use Second Wind, healing yourself for 35.')
        self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'35','#00FF00'))
        self.hp = min(self.hp+35, self.max_hp)
        self.increase_aggro_with_all_mobs(35)
    def use_ability49(self,backstab):
        if self.mp >= 44:
            self.mp -= 44
            self.handler.push_narration('You cast Aether Charge, greatly boosting your attack damage.')
            self.apply_debuff(10)
        else:
            self.handler.push_narration('You attempt to cast Aether Charge, but don\'t have enough MP.')
    def use_ability50(self,backstab):
        damage = self.damage_multiplier(20)
        self.handler.push_narration('You use Honed Strike for '+str(damage)+' damage.')
        self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(damage),int(float(tile_size)*1.5),self))
        self.game.sounds.append('attack')
        self.game.make_noise(self.pos_x,self.pos_y, 20)
    def use_ability51(self,backstab):
        if self.mp >= 100:
            self.mp -= 100
            self.handler.push_narration('You cast Resurrection, attempting to bring a party member back to life!')
            if not self.friendly_target.alive:
                self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'RESURRECTION','#00FF00'))
                self.friendly_target.alive = True
                self.friendly_target.hp = 1
                self.friendly_target.handler.push_narration('You have been resurrected!')
        else:
            self.handler.push_narration('You attempt to cast Resurrection, but don\'t have enough MP.')
    def use_ability52(self,backstab):
        self.handler.push_narration('You use a healing potion, healing yourself for 28 HP.')
        self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'28','#00FF00'))
        self.hp += 28
        if self.hp > self.max_hp:
            self.hp = self.max_hp
    def use_ability53(self,backstab):
        self.handler.push_narration('You are cursed and do nothing. NOTHING.')
    def use_ability54(self,backstab):
        self.handler.push_narration('Your inventory infection spawns a Sporeling.')
        self.game.floating_text.append(FloatingText(self.pos_x,self.pos_y,'SPAWN','#551A8b'))
        self.attempt_to_spawn_sporeling()
    def attempt_to_spawn_sporeling(self):
        for i in range(-1,2):
            for j in range(-1,2):
                if i==0 and j==0:
                    continue
                if (not self.game.is_collision_mobs_only(self.pos_x+(i*tile_size),self.pos_y+(j*tile_size),self)) and (not self.game.is_wall(self.pos_x+(i*tile_size),self.pos_y+(j*tile_size))):
                    self.spawn_sporeling(i,j)
                    return
        for i in range(-2,3):
            for j in range(-2,3):
                if i==0 and j==0:
                    continue
                if (not self.game.is_collision_mobs_only(self.pos_x+(i*tile_size),self.pos_y+(j*tile_size),self)) and (not self.game.is_wall(self.pos_x+(i*tile_size),self.pos_y+(j*tile_size))):
                    self.spawn_sporeling(i,j)
                    return
    def spawn_sporeling(self, i, j):
        for char in self.game.chars:
            char.handler.push_narration('A sporeling spawns from a player\'s inventory!')
        sporeling = Sporeling(self.game,self.pos_x+(i*tile_size),self.pos_y+(j*tile_size),self.game.floor,self.level,0)
        sporeling.xp = 0
        sporeling.autoheal_cd = 180
        new_entry = AggroEntry(self, 1)
        sporeling.aggro.append(new_entry)
        self.game.map.monsters.append(sporeling)
        self.game.active_monsters.append(sporeling)
    def use_ability55(self,backstab):
        counters = 0
        self.handler.push_narration('You release a Karmic Aura.')
        for i in self.deck.hand:
            if i.type==55:
                counters = i.counters
                i.counters = 0
                break
        self.game.projectiles.append(Projectile(self.pos_x+tile_size/2,self.pos_y+tile_size/2,self.facing,4,0,int(counters/10),tile_size*8,self))
    def use_ability56(self,backstab):
        self.handler.push_narration('You use Thief\'s Expertise, disarming all nearby traps and unlocking all nearby doors and chests.')
        x = self.pos_x/tile_size
        y = self.pos_y/tile_size
        for x_in in range(x-8,x+9):
            for y_in in range (y-8,y+9):
                self.unlock(x_in,y_in)
        for x_in in range(x-8,x+9):
            for y_in in range (y-8,y+9):
                self.disarm(x_in,y_in)
    def use_ability_check_for_backstab_and_disable_stealth(self,num):
        backstab = False
        if self.visible == False:
            backstab = True
            if num not in [13]:
                if not self.improved_invisibility:
                    self.visible = True
                    self.handler.push_narration('You are no longer hidden.')
        return backstab
    def increase_aggro_with_all_mobs(self,number):
        for mob in self.game.monsters:
            mob.aggro_increment_if_aggrod(self,number)
    def get_number_of_temp_cards_to_keep(self):
        if self.level<9:
            return 1
        return Math.ceil(float(self.level)-float(4))
    def determine_if_trasher(self, card_num):
        trash_num = 0
        if card_num==29:
            for item in self.deck.discard_pile:
                if item.type == 29:
                    self.deck.discard_pile.remove(item)
                    break
            trash_num = 2
        elif card_num==37:
            trash_num = 2
        elif card_num==41:
            trash_num = 5
        elif card_num in [45,50]:
            trash_num = 1
        if trash_num > 0:
            for item in self.deck.hand:
                self.deck.discard_pile.append(item)
            for item in self.deck.draw_pile:
                self.deck.discard_pile.append(item)
            # self.deck.hand = []
            self.deck.draw_pile = []
            numbers = []
            for item in self.deck.discard_pile:
                numbers.append(item.type)
            self.handler.write_message({'message': 'initiate_trash', 'number': trash_num, 'deck': numbers})
            self.trashes_entitled = trash_num
    def trash(self, trash_num):
        for item in self.deck.hand:
            self.deck.discard_pile.append(item)
        for item in self.deck.draw_pile:
            self.deck.discard_pile.append(item)
        # self.deck.hand = []
        self.deck.draw_pile = []
        numbers = []
        for item in self.deck.discard_pile:
            numbers.append(item.type)
        self.handler.write_message({'message': 'initiate_trash', 'number': trash_num, 'deck': numbers})
        self.trashes_entitled = trash_num
    def to_JSON_first(self):
        types = self.get_types()
        return '{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16}'.format(self.pos_x,self.pos_y,self.gcd,types[0],types[1],types[2],types[3],types[4],types[5],self.hp,self.max_hp,self.facing,int(self.mp),self.max_mp,self.color,self.eye_color,self.name)
    def to_JSON(self):
        types = self.get_types()
        return '{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13}'.format(self.pos_x,self.pos_y,self.gcd,types[0],types[1],types[2],types[3],types[4],types[5],self.hp,self.max_hp,self.facing,int(self.mp),self.max_mp)
    def to_JSON_light_first(self):
        return '{0},{1},{2},{3},{4},{5},{6},{7}'.format(self.pos_x,self.pos_y,self.hp,self.max_hp,self.facing,self.color,self.eye_color,self.name)
    def to_JSON_light(self):
        return '{0},{1},{2},{3},{4}'.format(self.pos_x,self.pos_y,self.hp,self.max_hp,self.facing)
    def to_binary_first(self):
        types = self.get_types()
        return struct.pack('!IIHIIIIIIIIHII7s7s15s',self.pos_x,self.pos_y,self.gcd,types[0],types[1],types[2],types[3],types[4],types[5],self.hp,self.max_hp,self.facing,int(self.mp),self.max_mp,str(self.color),str(self.eye_color),str(self.name))
    def to_binary(self):
        types = self.get_types()
        return struct.pack('!IIHIIIIIIIIHII',int(self.pos_x),int(self.pos_y),self.gcd,int(types[0]),int(types[1]),int(types[2]),int(types[3]),int(types[4]),int(types[5]),int(self.hp),int(self.max_hp),self.facing,int(self.mp),int(self.max_mp))
    def to_binary_light_first(self):
        return struct.pack('!IIIIH7s7s15s',self.pos_x,self.pos_y,self.hp,self.max_hp,self.facing,self.color,self.eye_color,self.name)
    def to_binary_light(self):
        return struct.pack('!IIIIH',self.pos_x,self.pos_y,self.hp,self.max_hp,self.facing)
    def to_save_data(self):
        data = {}
        data['deck'] = self.deck.to_save_data()
        data['max_hp'] = self.max_hp
        data['max_mp'] = self.max_mp
        data['mp_regen_rate'] = self.mp_regen_rate
        data['xp'] = self.xp
        data['total_xp'] = self.total_xp
        data['level'] = self.level
        data['starting_class'] = self.starting_class
        data['name'] = self.name
        data['color'] = self.color
        data['eye_color'] = self.eye_color
        data['uuid'] = self.uuid
        return data
    def get_types(self):
        items = []
        for i in range(6):
            items.append(self.get_type(i))
        return items
    def get_type(self, num):
        if self.deck.hand[num]:
            return self.deck.hand[num].type
        else:
            return None
    def verify_prune(self, prune):
        kept_new_num = self.get_number_of_temp_cards_to_keep()
        kept_start_num = 12-kept_new_num
        start_available = self.deck.count_permanent_cards()
        new_available = self.deck.count_temp_cards()
        while new_available<kept_new_num:
            kept_start_num += 1
            kept_new_num -= 1

        discard_copy = []
        for item in self.deck.discard_pile:
            discard_copy.append(item)
        pruning = []
        for item in prune:
            pruning.append(self.find_card_by_number(discard_copy,item))
            discard_copy.remove(self.find_card_by_number(discard_copy,item))
        keeping = discard_copy
        keeping_perm = []
        keeping_temp = []
        for item in keeping:
            if item.temp:
                keeping_temp.append(item)
            else:
                keeping_perm.append(item)
        if len(keeping_temp)!=kept_new_num:
            print 'Wrong number of temp cards'
            return False
        if len(keeping_perm)!=kept_start_num:
            print 'Wrong number of permanent cards'
            print len(keeping_perm), kept_start_num
            return False
        return True

    def find_card_by_number(self, collection, num):
        for item in collection:
            if item.type==num:
                return item
        return None
    def xp_current_level(self):
        if self.level==1:
            return self.xp
        return self.xp-Character.xp_table[self.level-2]
    def next_level_xp_current_level(self):
        if self.level==1:
            return Character.xp_table[self.level-1]
        return Character.xp_table[self.level-1]-Character.xp_table[self.level-2]
    def check_for_curse(self):
        if self.get_curse_position()==-1:
            return False
        return True
    def get_curse_position(self):
        for i in range(6):
            if self.deck.hand[i] and self.deck.hand[i].type in [53,54]:
                return i
        return -1

def ability_mp_cost(num):
    table = [0,0,44,0,44,0,44,0,0,0,44,44,88,44,44,88,0,44,22,0,0,44,0,100,0,0,0,0,44,0,0,44,44,44,0,22,88,0,0,44,0,88,0,0,0,0,44,44,0,44,0,100,0,0]
    return table[num]
