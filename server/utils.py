import random
import struct
# from numba import jit

from constants import *

# @jit
def serialize_list(list):
    return_list = []
    for i in list:
        if i!=None:
            return_list.append(i.to_JSON())
        else:
            return_list.append(None)
    return return_list
def serialize_char_list(list, main_char):
    return_list = []
    for i in list:
        if i!=None and i==main_char:
            return_list.append(i.to_JSON())
        elif i!=None:
            return_list.append(i.to_JSON_light())
        else:
            return_list.append(None)
    return return_list
def serialize_char_list_full(list, main_char):
    return_list = []
    for i in list:
        if i!=None and i==main_char:
            return_list.append(i.to_JSON_first())
        elif i!=None:
            return_list.append(i.to_JSON_light_first())
        else:
            return_list.append(None)
    return return_list
def serialize_char_list_to_binary(list, main_char):
    data = struct.pack('!I',len(list))
    for i in list:
        if i!=None and i==main_char:
            data += struct.pack('cc','F','F')
            data += i.to_binary()
        elif i!=None:
            data += struct.pack('cc','T','F')
            data += i.to_binary_light()
    return data
def serialize_char_list_to_binary_full(list, main_char):
    data = struct.pack('!I',len(list))
    for i in list:
        if i!=None and i==main_char:
            data += struct.pack('cc','F','T')
            data += i.to_binary_first()
        elif i!=None:
            data += struct.pack('cc','T','T')
            data += i.to_binary_light_first()
    return data
# @jit
def serialize_2d_boolean_list(list):
    return_list = []
    for i in list:
        return_sub_list = []
        for j in i:
            if j:
                return_sub_list.append('T')
            else:
                return_sub_list.append('F')
        return_list.append(return_sub_list)
    return return_list
neighbors_has_run = False
neighbors_answers = {}
# @jit
def neighbors(source,mob,game,char,step=tile_size):
    if not neighbors_has_run:
        run_neighbors(game, step=step)
    x,y=source
    return neighbors_answers[(x,y)]
# @jit
def run_neighbors(game, step=tile_size):
    global neighbors_has_run
    global neighbors_answers
    for x in range(0,(tile_size*8)*4,step):
        for y in range(0,(tile_size*8)*4,step):
            value = []
            value = neighbors_step(x+step,y,value,game)
            value = neighbors_step(x-step,y,value,game)
            value = neighbors_step(x,y+step,value,game)
            value = neighbors_step(x,y-step,value,game)
            neighbors_answers[(x,y)] = value
    neighbors_has_run = True
# @jit
def classic_neighbors(source, mob, game, char, step=tile_size):
    x,y=source
    value = []
    value = classic_neighbors_step(x+step,y,value,mob,game,char)
    value = classic_neighbors_step(x-step,y,value,mob,game,char)
    value = classic_neighbors_step(x,y+step,value,mob,game,char)
    value = classic_neighbors_step(x,y-step,value,mob,game,char)
    return value
# @jit
def neighbors_step(x,y,value,game):
    if not game.is_wall(x,y):
        if not game.is_door(x,y):
            value.append((x,y))
    return value
# @jit
def classic_neighbors_step(x,y,value,mob,game,char):
    if not game.is_wall(x,y):
        if not game.is_door(x,y):
            if not game.is_collision_mobs_only(x,y,mob):
                value.append((x,y))
    return value
def neighbors_idle(source, mob, game, dest_x, dest_y, step=tile_size):
    x,y=source
    value = []
    value = neighbors_idle_step(x+step,y,value,mob,game,dest_x,dest_y)
    value = neighbors_idle_step(x-step,y,value,mob,game,dest_x,dest_y)
    value = neighbors_idle_step(x,y+step,value,mob,game,dest_x,dest_y)
    value = neighbors_idle_step(x,y-step,value,mob,game,dest_x,dest_y)
    return value
def neighbors_idle_step(x,y,value,mob,game,dest_x,dest_y):
    if not game.is_wall(x,y):
        if not game.is_door(x,y):
            if not game.is_collision_mobs_only(x,y,mob):
                value.append((x,y))
    return value
def neighbors_sound(source, game, step = tile_size):
    x,y=source
    value = []
    value = neighbors_sound_step(x+step,y,value,game)
    value = neighbors_sound_step(x-step,y,value,game)
    value = neighbors_sound_step(x,y+step,value,game)
    value = neighbors_sound_step(x,y-step,value,game)
    return value
def neighbors_sound_step(x,y,value,game):
    if not game.is_wall(x,y):
        if not game.is_door(x,y):
            value.append((x,y))
    return value

# @jit
def monster_in_way(mob,game,x,y):
    return game.is_collision_mobs_only(x,y,mob)
# @jit
def move_cost(src,dest):
    x1,y1 = src
    x2,y2 = dest
    return abs(x1-x2)+abs(y1-y2)
    # return max(abs(x1-x2),abs(y1-y2))
# @jit
def heuristic(a,b):
    (x1,y1)=a
    (x2,y2)=b
    return abs(x1-x2)+abs(y1-y2)
    # return max(abs(x1-x2),abs(y1-y2))
# @jit
def random_drop():
    # roll = random.randint(1,48)
    # return random_drop_table[roll]
    return random.randint(0,10)
# random_drop_table = [0,0,0,0,0,0,0,0,1,1,1,2,3,4,5,6,6,6,7,8,8,8,8,8,8,8,8,8,8,8,8,8,8,9,10,11,12,13,13,13,13,13,13,13,14,14,14,15,16]
def set_up_empty_2d_array(length,filler=''):
    value = []
    for x in range(length):
        column = []
        for y in range(length):
            column.append(filler)
        value.append(column)
    return value
# @jit
def count_table_items(table):
    count = 0
    for element in table:
        if element:
            count+=int(element)
    return count
# @jit
def humanize_time(time):
    seconds = int(time/60)
    decimal = time-(seconds*60)
    decimal = float(decimal) / float(60)
    time = float(seconds) + decimal
    return "%.2f" % time
def tiles_to_binary(tiles):
    data = struct.pack('!I',len(tiles)/3)
    i = 0
    while i<len(tiles):
        data += struct.pack('!IIc',tiles[i],tiles[i+1],str(tiles[i+2]))
        i+=3
    return data
def sight_to_binary(sight):
    data = struct.pack('!I',len(sight)/3)
    i = 0
    while i<len(sight):
        data += struct.pack('!IIc',sight[i],sight[i+1],boolean_to_char(sight[i+2]))
        i+=3
    return data
def effects_to_binary(effects):
    data = struct.pack('!I',len(effects))
    for item in effects:
        data += struct.pack('!H',item)
    return data
def effects_duration_to_binary(durations):
    data = struct.pack('!I',len(durations))
    for item in durations:
        data += struct.pack('!I',item)
    return data
def string_array_to_binary(array):
    data = struct.pack('!I',len(array))
    for item in array:
        data += struct.pack('15s',item)
    return data
def animations_to_binary(animations):
    data = struct.pack('!I',len(animations))
    for item in animations:
        items = item.split(',')
        data += struct.pack('!IIII7s',int(items[0]),int(items[1]),int(items[2]),int(items[3]),items[4])
    return data
def serialize_list_as_binary(items):
    data = struct.pack('!I',len(items))
    for item in items:
        data += item.to_binary()
    return data
def unsigned_integer_array_to_binary(array):
    data = struct.pack('!I',len(array))
    for item in array:
        data += struct.pack('!I',item)
    return data
def boolean_array_to_binary(array):
    data = struct.pack('!I',len(array))
    for item in array:
        data += struct.pack('c',boolean_to_char(item))
    return data
def boolean_to_char(value):
    if value:
        return 'T'
    return 'F'
