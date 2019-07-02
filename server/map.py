import random
from monsters import *
from constants import *

class Map (object):
    @staticmethod
    def from_save_data(data,game,floor):
        obj = Map(game=game,floor=floor)
        obj.height = data['height']
        obj.floor = data['floor']
        obj.size_x = data['size_x']
        obj.size_y = data['size_y']
        obj.start_x = data['start_x']
        obj.start_y = data['start_y']
        obj.end_x = data['end_x']
        obj.end_y = data['end_y']
        obj.level = data['level']
        obj.tiles = data['tiles']
        obj.tiles_seen = data['tiles_seen']
        obj.tiles_trapped = data['tiles_trapped']
        obj.traps = {}
        for x,y,v in data['traps']:
            obj.traps[(x,y)] = v
        obj.border = data['border']
        obj.monsters = []
        for mob in data['monsters']:
            obj.monsters.append(Monster.from_save_data(mob, game))
        obj.scents = []
        for scent in data['scents']:
            obj.scents.append(Scent.from_save_data(scent))
        return obj
    def __init__(self,game,floor,size_x=(tile_size*16)*4,size_y=(tile_size*16)*4,height='middle',level=1): #(tile_size*16)*8 for full game
        # random.seed(20)
        self.height = height
        self.initialize_variables(game,floor,size_x,size_y,level)
        self.initialize_fill_map()
        self.initialize_set_traps()
        self.start_x,self.start_y=self.dig_initial_room()
        self.end_x = self.start_x
        self.end_y = self.start_y
        self.initialize_add_stairs_up(height)
        self.initialize_add_rooms()
        self.remove_starting_area_monsters()
        self.remove_orphaned_doors()
        self.initialize_link_floors(height)
        self.initialize_add_shop()
        self.initialize_add_boss(height)
        self.scents = []

        # for x in range(len(self.tiles)):
        #     for y in range(len(self.tiles[0])):
        #         if self.tiles_trapped[x][y] and self.tiles[x][y]==' ':
        #             self.tiles[x][y]='T'
        # print self.count_whitespace()
        # print len(self.monsters)
        # print (self.count_chests())
    # def count_chests(self):
        # count = 0
        # for x in range(self.size_x/tile_size):
            # for y in range(self.size_y/tile_size):
                # if self.tiles[x][y]=='C':
                    # count+=1
        # return count
    # def count_whitespace(self):
    #     count = 0
    #     for x in range(self.size_x/tile_size):
    #         for y in range(self.size_y/tile_size):
    #             if self.tiles[x][y]==' ':
    #                 count += 1
    #     return count
    def initialize_add_shop(self):
        roll = random.randint(0,1)
        if roll==1:
            self.add_shop()
    def add_shop(self):
        x = random.randint(1,(self.size_x/tile_size)-2)
        y = random.randint(1,(self.size_y/tile_size)-2)
        if self.tiles[x][y]==' ':
            self.tiles[x][y] = 'P'
            return
        self.add_shop()
    def initialize_add_boss(self,height):
        if height == 'bottom':
            self.add_boss()
    def initialize_link_floors(self,height):
        if height in ['top','middle']:
            self.add_stairs_down()
    def initialize_add_rooms(self):
        for i in range(30): #was 120
            for i in range(1000):
                if self.add_feature(self.game):
                    break
    def initialize_add_stairs_up(self,height):
        if height in ['middle','bottom']:
            self.add_stairs_up()
    def initialize_set_traps(self):
        for x in range(len(self.tiles_trapped)):
            for y in range(len(self.tiles_trapped[0])):
                if random.randint(0,399)==399:
                    self.tiles_trapped[x][y]=True
                    self.traps[(x,y)] = self.random_trap()
    def initialize_fill_map(self):
        self.fill_map()
        self.fill_map(target=self.tiles_seen,value=False)
        self.fill_map(target=self.tiles_trapped,value=False)
    def initialize_variables(self,game,floor,size_x,size_y,level):
        self.floor = floor
        self.size_x,self.size_y = size_x,size_y
        self.level = level
        self.game = game
        self.screen_size = 512
        self.tiles = []
        self.tiles_seen = []
        self.tiles_trapped = []
        self.traps = {}
        self.monsters = []
        self.border = 1
    def add_stairs_down(self):
        location = 'X'
        while location!=' ':
            x = random.randint(1,(self.size_x/tile_size)-2)
            y = random.randint(1,(self.size_y/tile_size)-2)
            location = self.tiles[x][y]
        self.tiles[x][y]='>'
        self.end_x = x*tile_size
        self.end_y = y*tile_size
    def add_stairs_up(self):
        self.tiles[self.start_x/tile_size][self.start_y/tile_size]='<'
    def add_monsters(self,game,x,y,length,height,level,mob_class,num):
        for i in range(num):
            try:
                self.add_monster(game,x,y,length,height,level,mob_class)
            except:
                pass
    def add_monster(self,game,x,y,length,height,level,mob_class):
            x_in = (random.randint(min(x,x+length),max(x,x+length)))*tile_size
            y_in = (random.randint(min(y,y+height),max(y,y+height)))*tile_size
            if self.check_if_wall(x_in/tile_size,y_in/tile_size) or self.check_if_monster(x_in,y_in):
                self.add_monster(game,x,y,length,height,level,mob_class)
                return
            monster = choose_monster(game,x_in,y_in,self.floor,level,mob_class)
            self.monsters.append(monster)
            if monster.level==0:
                self.add_extra_kobold(game,x,y,length,height,level,mob_class)
                self.add_extra_kobold(game,x,y,length,height,level,mob_class)
    def add_extra_kobold(self,game,x,y,length,height,level,mob_class):
            x_in = (random.randint(min(x,x+length),max(x,x+length)))*tile_size
            y_in = (random.randint(min(y,y+height),max(y,y+height)))*tile_size
            if self.check_if_wall(x_in/tile_size,y_in/tile_size) or self.check_if_monster(x_in,y_in):
                self.add_extra_kobold(game,x,y,length,height,level,mob_class)
                return
            monster = Kobold(game,x_in,y_in,self.floor,level,mob_class)
            self.monsters.append(monster)
    def check_if_monster(self,x,y):
        for mob in self.monsters:
            if mob.pos_x==x and mob.pos_y==y:
                return True
        return False
    def add_boss(self):
        x = (random.randint(0,(self.size_x-tile_size)/tile_size))
        y = (random.randint(0,(self.size_y-tile_size)/tile_size))
        if self.tiles[x][y]!=' ':
            self.add_boss()
        else:
            self.monsters.append(choose_monster(self.game,x*tile_size,y*tile_size,self.floor,self.level,4))
    def add_chest(self,game,x,y,length,height):
        x = (random.randint(min(x,x+length),max(x,x+length)))
        y = (random.randint(min(y,y+height),max(y,y+height)))
        if not self.check_if_wall(x,y):
            self.tiles[x][y] = 'C'
            roll = random.randint(1,10)
            if roll==10:
                self.tiles_trapped[x][y]=True
                self.traps[(x,y)] = self.random_trap()
            roll = random.randint(1,10)
            if roll==10:
                self.tiles[x][y] = 'H'
    def add_statue(self,game,x,y,length,height):
        x = (random.randint(min(x,x+length),max(x,x+length)))
        y = (random.randint(min(y,y+height),max(y,y+height)))
        if self.check_if_wall_adjacent(x,y):
            return
        self.tiles[x][y] = '@'
    def add_fountain(self,game,x,y,length,height):
        x = (random.randint(min(x,x+length),max(x,x+length)))
        y = (random.randint(min(y,y+height),max(y,y+height)))
        if self.check_if_wall_adjacent(x,y):
            return
        self.tiles[x][y] = 'F'
    def check_if_wall_adjacent(self,x,y):
        for x_mod in range(-1,2):
            for y_mod in range(-1,2):
                if self.check_if_wall(x+x_mod,y+y_mod):
                    return True
        return False
    def remove_orphaned_doors(self):
        for x in range(self.size_x/tile_size):
            for y in range(self.size_y/tile_size):
                if self.tiles[x][y] in ['D','O','R']:
                    if self.tiles[x-1][y]=='W' and self.tiles[x+1][y]=='W' and self.tiles[x][y-1]!='W' and self.tiles[x][y+1]!='W':
                        pass
                    elif self.tiles[x][y-1]=='W' and self.tiles[x][y+1]=='W' and self.tiles[x-1][y]!='W' and self.tiles[x+1][y]!='W':
                        pass
                    else:
                        self.tiles[x][y]=' '
    def remove_starting_area_monsters(self):
        prune_monsters = []
        for monster in self.monsters:
            if self.monsters_in_starting_area(monster):
                prune_monsters.append(monster)
        for monster in prune_monsters:
            self.monsters.remove(monster)
    def monsters_in_starting_area(self,monster):
        return (monster.pos_x>self.start_x-(tile_size*10) and monster.pos_x<self.start_x+(tile_size*10) and monster.pos_y>self.start_y-(tile_size*10) and monster.pos_y<self.start_y+(tile_size*10))
    def add_feature(self,game):
        try:
            x,y,facing = self.pick_random_wall()
        except:
            return False
        type = random.randint(0,14) #0 for corridors, 1 for rooms, 2-3 for corridor with door, 4-5 for room with door, 6 for octagon, 7-8 for octagon with door, 9 for cross, 10-11 for cross with door, 12 for diamond, 13-14 for diamond with door
        length,height,mobs = self.get_feature_parameters(type)
        length,height,door = self.get_feature_door_presence(type,length,height,facing)
        minor_axis_offset = self.get_feature_minor_axis_offset(facing,type,height)
        return self.attempt_to_dig_room(type,x,y,facing,length,height,minor_axis_offset,game,door,mobs)
    def attempt_to_dig_room(self,type,x,y,facing,length,height,minor_axis_offset,game,door,mobs):
        if self.check_if_space(x,y,facing,length,height,minor_axis_offset):
            self.dig_appropriate_room_type(type,x,y,facing,length,height,game,door,minor_axis_offset,mobs)
            return True
        else:
            return False
    def dig_appropriate_room_type(self,type,x,y,facing,length,height,game,door,minor_axis_offset,mobs):
        if type in [0,1,2,3,4,5]:
            self.dig_room(x,y,facing,length,height,game,door,minor_axis_offset,mobs)
        elif type in [6,7,8]:
            self.dig_room(x,y,facing,length,height,game,door,minor_axis_offset,mobs,octagon=True)
        elif type in [9,10,11]:
            self.dig_room(x,y,facing,length,height,game,door,minor_axis_offset,mobs,cross=True)
        elif type in [12,13,14]:
            self.dig_room(x,y,facing,length,height,game,door,minor_axis_offset,mobs,diamond=True)
    def get_feature_minor_axis_offset(self,facing,type,height):
        if facing in [1,3] and type in [0,1,2,3,4,5]:
            return random.randint(0,height-1)
        elif facing in [0,2] and type in [0,1,2,3,4,5]:
            return random.randint(0,height-2)
        elif facing in [1,3] and type in [6,7,8,9,10,11]:
            return random.randint(height/4,(height/4*3)-1)
        elif facing in [0,2] and type in [6,7,8,9,10,11]:
            return random.randint(height/4,(height/4*3)-2)
        elif type in [12,13,14]:
            # return (height+1)/2
            return (height/2)
    def get_feature_door_presence(self,type,length,height,facing):
        if type in [2,3,4,5,7,8,10,11,13,14]:
            door=True
            if facing in [0,2]:
                height+=1
            else:
                length+=1
        else:
            door=False
        return length,height,door
    def get_feature_parameters(self,type):
        if type in [0,2,3]:
            return (random.randint(4,16),random.randint(2,3),True)
        elif type in [1,4,5]:
            return (random.randint(4,16),random.randint(4,16),True)
        elif type in [6,7,8,9,10,11]:
            size = random.randint(1,4)*4
            return (size,size,True)
        elif type in [12,13,14]:
            size = (random.randint(2,7)*2)+1
            return (size,size,True)
    def dig_room(self,x,y,facing,length,height,game,door,offset,mobs,octagon=False,cross=False,diamond=False):
        x_step,y_step,room_guaranteed_chest = self.dig_room_set_up_initial_variables()
        x,y,height,length,room_guaranteed_chest = self.dig_room_add_door_if_needed(x,y,x_step,y_step,height,length,door,facing,room_guaranteed_chest)
        length,height = self.rotate_room_if_necessary(facing,length,height)
        length,height,x_step,y_step = self.flip_room_if_necessary(facing,length,height,x_step,y_step)
        x,y = self.adjust_room_for_offset(facing,x,y,x_step,y_step,offset)
        self.dig_specific_room_type(octagon,cross,diamond,x,y,length,height,x_step,y_step)
        self.possibly_add_mobs(game,x,y,length,height,mobs)
        self.possibly_add_room_details(room_guaranteed_chest,game,x,y,length,height)
    def possibly_add_room_details(self,room_guaranteed_chest,game,x,y,length,height):
        chest = random.randint(-2,1)
        if room_guaranteed_chest:
            chest=1
        if chest==1:
            self.add_chest(game,x,y,length,height)
        if random.randint(-8,1)==1:
            self.add_statue(game,x,y,length,height)
        if random.randint(-8,1)==1:
            self.add_fountain(game,x,y,length,height)
    def possibly_add_mobs(self,game,x,y,length,height,mobs):
        if mobs:
            if random.randint(0,1)==1:
                difficulty,num = self.determine_difficulty_and_number_of_mobs()
                mob_class,num = self.determine_mob_difficulty_class(num)
                level = self.determine_mob_level(difficulty)
                self.add_monsters(game,x,y,length,height,level,mob_class,num)
    def determine_mob_level(self,difficulty):
        table = [self.determine_mob_level_diff_0,self.determine_mob_level_diff_1,self.determine_mob_level_diff_2,self.determine_mob_level_diff_3]
        return table[difficulty]()
    def determine_mob_level_diff_0(self):
        if self.level==1:
            return 1
        else:
            return random.randint(1,self.level-1)
    def determine_mob_level_diff_1(self):
        return self.level
    def determine_mob_level_diff_2(self):
        level = self.level + random.randint(1,4)
        if level>self.level*2:
            level = self.level*2
        return level
    def determine_mob_level_diff_3(self):
        level = self.level + random.randint(5,6)
        if level>self.level*3:
            level = self.level*3
        return level
    def determine_mob_difficulty_class(self,num):
        class_roll = random.randint(1,100)
        if class_roll <= 50:
            #normal
            return 0,num
        elif class_roll <= 80:
            #strong
            return 1,num
        elif class_roll <= 95:
            #elite
            return 2,num
        else:
            #miniboss
            return 3,1
    def determine_difficulty_and_number_of_mobs(self):
        difficulty_roll = random.randint(1,100)
        if difficulty_roll <= 12:
            #easy
            return 0,random.randint(1,2)
        elif difficulty_roll <= 75:
            #normal
            return 1,random.randint(2,4)
        elif difficulty_roll <= 94:
            #hard - EL + 1-10 (no higher than double dungeon level)
            return 2,random.randint(2,4)
        else:
            #extreme - EL + 11+ (no higher than triple dungeon level)
            return 3,random.randint(2,4)
    def dig_specific_room_type(self,octagon,cross,diamond,x,y,length,height,x_step,y_step):
        if octagon:
            self.dig_octagon(x,y,x+length,y+height)
        elif cross:
            self.dig_cross(x,y,x+length,y+height)
        elif diamond:
            self.dig_diamond(x,y,x+length,y+height)
        else:
            self.dig_rectangle(x,y,length,height,x_step,y_step)
    def dig_rectangle(self,x,y,length,height,x_step,y_step):
        for x_in in range(x,x+length,x_step):
            for y_in in range(y,y+height,y_step):
                self.remove_wall(x_in,y_in)
        if random.randint(-18,1)==1:
            self.add_central_pillar(x,y,x+length,y+height,x_step,y_step)
    def adjust_room_for_offset(self,facing,x,y,x_step,y_step,offset):
        if facing in [0,2]:
            x-=x_step*offset
        else:
            y-=y_step*offset
        return x,y
    def flip_room_if_necessary(self,facing,length,height,x_step,y_step):
        if facing == 0:
            height = 0-height
            y_step = -1
        if facing == 3:
            length = 0-length
            x_step = -1
        return length,height,x_step,y_step
    def rotate_room_if_necessary(self,facing,length,height):
        if facing in [0,2]:
            return height,length
        return length,height
    def dig_room_set_up_initial_variables(self):
        return 1,1,False
    def dig_room_add_door_if_needed(self,x,y,x_step,y_step,height,length,door,facing,room_guaranteed_chest):
        if door:
            self.remove_wall(x,y)
            if random.randint(0,1)==1:
                room_guaranteed_chest = self.dig_room_add_door(room_guaranteed_chest,x,y)
            x,y,height,length = self.modify_room_size_for_door(x,y,height,length,facing,x_step,y_step)
        return x,y,height,length,room_guaranteed_chest
    def modify_room_size_for_door(self,x,y,height,length,facing,x_step,y_step):
        if facing in [0,2]:
            y+=y_step
            height-=y_step
        else:
            x+=x_step
            length-=x_step
        return x,y,height,length
    def dig_room_add_door(self,room_guaranteed_chest,x,y):
        self.tiles[x][y]='D'
        if random.randint(0,9)==9:
            self.tiles_trapped[x][y]=True
            self.traps[(x,y)] = self.random_trap()
        if random.randint(0,9)==9:
            self.tiles[x][y]='S'
            room_guaranteed_chest = True
        elif random.randint(0,9)==9:
            self.tiles[x][y]='O'
            room_guaranteed_chest = True
        return room_guaranteed_chest
    def add_central_pillar(self,x1,y1,x2,y2,x_step,y_step):
        x_q = min((x2-x1)/4,2)+1
        y_q = min((y2-y1)/4,2)+1
        if x1+x_q>=x2-x_q or y1+y_q>=y2-y_q:
            return
        for x_in in range(x1+x_q,x2-x_q,x_step):
            for y_in in range(y1+y_q,y2-y_q,y_step):
                self.tiles[x_in][y_in]='W'
    def is_border(self,x,y):
        return not (x>self.border-1 and y>self.border-1 and x<len(self.tiles)-self.border and y<len(self.tiles[0])-self.border)
    def remove_wall(self,x,y):
        if not self.is_border(x,y):
            self.tiles[x][y]=' '
    def remove_line(self,x1,y1,x2,y2):
        # print x1,y1,x2,y2
        if x2==x1:
            self.remove_vertical_line(x1,y1,y2)
            return
        elif x2>x1:
            step = 1
        else:
            step = -1
        prev_y_value = y1
        for x_value in range (x1,x2+step,step):
            prev_y_value = self.remove_line_step(x_value,x1,y1,x2,y2,prev_y_value)
    def remove_line_step(self,x_value,x1,y1,x2,y2,prev_y_value):
        y_value=(((float(x_value)-float(x1))/(float(x2)-float(x1)))*(float(y2)-float(y1)))+y1
        if x_value!=x1:
            if abs(int(y_value)-int(prev_y_value))>1:
                self.remove_vertical_line(int(x_value),int(prev_y_value),int(y_value))
        self.remove_wall(int(x_value),int(y_value))
        # print int(x_value),int(y_value)
        return y_value
    def remove_vertical_line(self,x,y1,y2):
        if y2==y1:
            self.remove_wall(x,y1)
            return
        elif y2>y1:
            step = 1
        else:
            step = -1
        for y_value in range (int(y1),int(y2)+step,step):
            self.remove_wall(x,y_value)
    # def flood_remove(self,x,y):
        # if self.tiles[x][y]:
            # self.remove_wall(x,y)
        # if x>0 and self.tiles[x-1][y]=='W':
            # self.flood_remove(x-1,y)
        # if y>0 and self.tiles[x][y-1]=='W':
            # self.flood_remove(x,y-1)
        # if x<len(self.tiles)-1 and self.tiles[x+1][y]=='W':
            # self.flood_remove(x+1,y)
        # if y<len(self.tiles[0])-1 and self.tiles[x][y+1]=='W':
            # self.flood_remove(x,y+1)
    def flood_remove(self,x,y):
        # print x,y
        if self.tiles[x][y] and (not self.is_border(x,y)) and self.tiles[x][y]=='W':
            self.remove_wall(x,y)
            self.flood_remove(x-1,y)
            self.flood_remove(x+1,y)
            self.flood_remove(x,y-1)
            self.flood_remove(x,y+1)
    def dig_octagon(self,x1,y1,x2,y2):
        q_x = (x2-x1)/4
        q_y = (y2-y1)/4
        self.dig_octagon_remove_lines(x1,y1,x2,y2,q_x,q_y)
        try:
            self.flood_remove(int(x1+((x2-x1)/2)),int(y1+((y2-y1)/2)))
        except Exception as e:
            # print ('Flood Overflow!')
            return
    def dig_octagon_remove_lines(self,x1,y1,x2,y2,q_x,q_y):
        self.remove_line(x1,y1+q_y,x1+q_x,y1)
        self.remove_line(x1+q_x,y1,x2-q_x,y1)
        self.remove_line(x2-q_x,y1,x2,y1+q_y)
        self.remove_line(x2,y1+q_y,x2,y2-q_y)
        self.remove_line(x2,y2-q_y,x2-q_x,y2)
        self.remove_line(x2-q_x,y2,x1+q_x,y2)
        self.remove_line(x1+q_x,y2,x1,y2-q_y)
        self.remove_line(x1,y2-q_y,x1,y1+q_y)
    def dig_diamond(self,x1,y1,x2,y2):
        h_x = (x2-x1)/2
        h_y = (y2-y1)/2
        self.remove_line(x1+h_x,y1,x2,y1+h_y)
        self.remove_line(x2,y1+h_y,x1+h_x,y2)
        self.remove_line(x1+h_x,y2,x1,y1+h_y)
        self.remove_line(x1,y1+h_y,x1+h_x,y1)
        try:
            self.flood_remove(int(x1+h_x),int(y1+h_y))
        except:
            # print ('Flood Overflow!')
            return
    def dig_cross(self,x1,y1,x2,y2):
        q_x = (x2-x1)/4
        q_y = (y2-y1)/4
        for x_in in range(x1+q_x,x2-q_x):
                for y_in in range(y1,y2):
                    self.remove_wall(x_in,y_in)
        for x_in in range(x1,x2):
                for y_in in range(y1+q_y,y2-q_y):
                    self.remove_wall(x_in,y_in)
    def check_if_space(self,x,y,facing,length,height,offset):
        x_step,y_step = 1,1
        length,height = self.rotate_room_if_necessary(facing,length,height)
        length,height,x_step,y_step = self.flip_room_if_necessary(facing,length,height,x_step,y_step)
        x,y = self.adjust_room_for_offset(facing,x,y,x_step,y_step,offset)
        if (x+length)*tile_size>=self.size_x-(tile_size*2) or (x+length)*tile_size<=(tile_size*2) or (y+height)*tile_size>=self.size_y-(tile_size*2) or (y+height)*tile_size<=(tile_size*2):
            return False
        for x_in in range(x,x+length+x_step,x_step):
            for y_in in range(y,y+height+y_step,y_step):
                if not self.check_if_wall(x_in,y_in):
                    return False
        return True
    def check_if_wall(self,x,y):
        if x<0 or y<0 or x*tile_size>=self.size_x or y*tile_size>=self.size_y:
            return False
        return (self.tiles[x][y]=='W')
    def fill_map(self,value='W',target=None):
        if target==None:
            target = self.tiles
        for i in range(0,self.size_x/tile_size):
            column = []
            for j in range(0,self.size_y/tile_size):
                column.append(value)
            target.append(column)
    def dig_initial_room(self):
        x_start = random.randint(1,(self.size_x-(tile_size*9))/tile_size)
        y_start = random.randint(1,(self.size_y-(tile_size*9))/tile_size)
        for x in range(x_start,x_start+8):
            for y in range(y_start,y_start+8):
                self.tiles[x][y]=' '
        return ((x_start*tile_size)+(tile_size*4),(y_start*tile_size)+(tile_size*4))
    def pick_random_wall(self):
        x = random.randint(1,(self.size_x/tile_size)-2)
        y = random.randint(1,(self.size_y/tile_size)-2)
        if self.tiles[x][y]=='W':
            return self.find_empty_space_adjacent_to_wall(x,y)
        else:
            return self.pick_random_wall()
    def find_empty_space_adjacent_to_wall(self,x,y):
        if self.check_north_empty(x,y):
            return (x,y,2)
        elif self.check_east_empty(x,y):
            return (x,y,3)
        elif self.check_south_empty(x,y):
            return (x,y,0)
        elif self.check_west_empty(x,y):
            return (x,y,1)
        else:
            return self.pick_random_wall()
    def check_north_empty(self,x,y):
        return (self.tiles[x][y-1]==' ')
    def check_east_empty(self,x,y):
        return (self.tiles[x+1][y]==' ')
    def check_south_empty(self,x,y):
        return (self.tiles[x][y+1]==' ')
    def check_west_empty(self,x,y):
        return (self.tiles[x-1][y]==' ')
    def random_trap(self):
        trap = {}
        roll = random.randint(0,15)
        if roll<3:
            trap['name'] = 'spike'
            trap['damage'] = 50
            trap['one_shot'] = True
        elif roll<6:
            trap['name'] = 'fireball'
            trap['damage'] = 50
            trap['one_shot'] = True
        elif roll<9:
            trap['name'] = 'arrow'
            trap['damage'] = 100
            trap['one_shot'] = True
        elif roll==9:
            if self.height=='bottom':
                return self.random_trap()
            trap['name'] = 'pit'
            trap['damage'] = 50
            trap['one_shot'] = True
        elif roll==10:
            trap['name'] = 'teleport'
            trap['damage'] = 0
            trap['one_shot'] = True
        elif roll==11:
            trap['name'] = 'arrow'
            trap['damage'] = 50
            trap['one_shot'] = False
            trap['gcd'] = 0
        elif roll==12:
            trap['name'] = 'fireball'
            trap['damage'] = 50
            trap['one_shot'] = False
            trap['gcd'] = 0
        elif roll==13:
            trap['name'] = 'lava'
            trap['damage'] = 0
            trap['one_shot'] = True
        elif roll==14:
            trap['name'] = 'arrow_spread'
            trap['damage'] = 50
            trap['one_shot'] = True
        elif roll==15:
            trap['name'] = 'arrow_spread'
            trap['damage'] = 50
            trap['one_shot'] = False
            trap['gcd'] = 0
        return trap
    def to_save_data(self):
        data = {}
        data['height'] = self.height
        data['floor'] = self.floor
        data['size_x'] = self.size_x
        data['size_y'] = self.size_y
        data['start_x'] = self.start_x
        data['start_y'] = self.start_y
        data['end_x'] = self.end_x
        data['end_y'] = self.end_y
        data['level'] = self.level
        data['tiles'] = self.tiles
        data['tiles_seen'] = self.tiles_seen
        data['tiles_trapped'] = self.tiles_trapped
        data['traps'] = []
        for k,v in self.traps.iteritems():
            x,y = k
            data['traps'].append((x,y,v))
        data['border'] = self.border
        data['monsters'] = []
        for mob in self.monsters:
            data['monsters'].append(mob.to_save_data())
        data['scents'] = []
        for scent in self.scents:
            data['scents'].append(scent.to_save_data())
        return data

class Scent (object):
    @staticmethod
    def from_save_data(data):
        scent = Scent(data['pos_x'], data['pos_y'], data['intensity'])
        scent.radius = data['radius']
        scent.type = data['type']
        return scent
    def __init__(self, x, y, intensity):
        self.pos_x = x
        self.pos_y = y
        self.intensity = intensity
        self.radius = 0
        self.type = 'player'
    def to_save_data(self):
        data = {}
        data['pos_x'] = self.pos_x
        data['pos_y'] = self.pos_y
        data['intensity'] = self.intensity
        data['radius'] = self.radius
        data['type'] = self.type
        return data
