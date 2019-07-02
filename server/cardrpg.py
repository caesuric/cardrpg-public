import tornado.options
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.escape
import os.path
import uuid
import time
import thread
import math
import sys
import time
import logging
import struct
import base64
from map import Map, Scent
from character import Character
from cards import Deck, Card
from utils import *
from constants import *
from floating_text import FloatingText
from projectile import Projectile
from monsters import Monster
# import base64
# import pygame.time
# import multiprocessing
# import cProfile
from passlib.hash import pbkdf2_sha256
# import pdb
tornado.options.define("port", default=8080, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", tornado.web.StaticFileHandler, {"path": "templates"}),
            (r"/mainsocket", SocketHandler)
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static")
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class LoginSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        pass
    def on_message(self,message):
        parsed = tornado.escape.json_decode(message)
        if parsed['message'] in ['login', 'register']:
            if 'password' not in parsed:
                self.send_must_have_password_error()
                return
            if 'username' not in parsed or parsed['username']=='':
                self.send_must_have_username_error()
                return
        if parsed['message']=='login':
            self.login(parsed['username'],parsed['password'])
        elif parsed['message']=='register':
            self.register(parsed['username'],parsed['password'])
        elif parsed['message']=='finalize_character':
            self.finalize_character(parsed['class_selected'],parsed['name'],parsed['color'],parsed['eye_color'])
        elif parsed['message']=='request_games':
            self.send_games()
        elif parsed['message']=='new_game':
            self.new_game(parsed['character'])
        elif parsed['message']=='load_game':
            self.load_game(parsed['character'], parsed['game'])
        elif parsed['message']=='join_game':
            self.join_game(parsed['character'], parsed['game'])
    def login(self, username, password):
        self.fetch_logins()
        login = None
        for item in self.logins:
            if item['username'] == username:
                login = item
                break
        if login==None:
            self.send_account_does_not_exist_error()
            return
        if pbkdf2_sha256.verify(password, login['password']):
            self.username = username
            self.trigger_character_select()
        else:
            self.send_password_incorrect_error()
    def register(self, username, password):
        hash = pbkdf2_sha256.hash(password)
        self.fetch_logins()
        for login in self.logins:
            if login['username'] == username:
                self.send_account_already_exists_error()
        data = {}
        self.username = data['username'] = username
        data['password'] = hash
        self.logins.append(data)
        with open('user_info.dat', 'w') as user_info:
            data = tornado.escape.json_encode(self.logins)
            user_info.write(data)
        self.trigger_character_select()
    def fetch_logins(self):
        if not os.path.isfile('user_info.dat'):
            self.logins = []
            return
        with open('user_info.dat', 'r') as user_info:
            data = tornado.escape.json_decode(user_info.read())
            self.logins = data
    def send_account_does_not_exist_error(self):
        message = {}
        message['message'] = 'error'
        message['error'] = 'Account does not exist.'
        self.attempt_to_write_message(message)
    def send_password_incorrect_error(self):
        message = {}
        message['message'] = 'error'
        message['error'] = 'Password incorrect.'
        self.attempt_to_write_message(message)
    def send_account_already_exists_error(self):
        message = {}
        message['message'] = 'error'
        message['error'] = 'Account already exists.'
        self.attempt_to_write_message(message)
    def send_must_have_password_error(self):
        message = {}
        message['message'] = 'error'
        message['error'] = 'Must type a password to proceed.'
        self.attempt_to_write_message(message)
    def send_must_have_username_error(self):
        message = {}
        message['message'] = 'error'
        message['error'] = 'Must type a username to proceed.'
        self.attempt_to_write_message(message)
    def fetch_characters(self):
        self.characters = []
        if not os.path.isfile('characters.dat'):
            return
        with open('characters.dat', 'r') as characters:
            data = tornado.escape.json_decode(characters.read())
            for item in data:
                if item['owner']==self.username:
                    self.characters.append(item)
    def fetch_all_characters(self):
        if not os.path.isfile('characters.dat'):
            self.characters = []
            return
        with open('characters.dat', 'r') as characters:
            data = tornado.escape.json_decode(characters.read())
            self.characters = data
    def trigger_character_select(self):
        self.fetch_characters()
        message = {}
        message['message'] = 'character_select'
        message['characters'] = self.characters
        self.attempt_to_write_message(message)
    def finalize_character(self,class_name,name,color,eye_color):
        char = Character()
        char.uuid = str(uuid.uuid4())
        char.deck = Deck(class_name)
        char.alive = True
        char.class_selected = True
        char.starting_class = class_name
        char.name = name
        char.color = color
        char.eye_color = eye_color
        data = char.to_save_data()
        data['owner'] = self.username
        self.fetch_all_characters()
        self.characters.append(data)
        with open('characters.dat', 'w') as characters:
            data = tornado.escape.json_encode(self.characters)
            characters.write(data)
        self.trigger_character_select()
    def send_games(self):
        self.running_games = []
        for game in Game.games:
            if game.is_public:
                self.running_games.append(game.to_save_data())
        self.saved_games = []
        if os.path.isfile('games.dat'):
            with open('games.dat', 'r') as saved_games:
                data = tornado.escape.json_decode(saved_games.read())
                for item in data:
                    if self.username in item['owners']:
                        found_in_running = False
                        for game in self.running_games:
                            if game['uuid']==item['uuid']:
                                found_in_running = True
                        if not found_in_running:
                            self.saved_games.append(item)
        message = {}
        message['message'] = 'game_select'
        message['running_games'] = self.running_games
        message['saved_games'] = self.saved_games
        message = tornado.escape.json_encode(message)
        self.attempt_to_write_message(message)
    def new_game(self, char_uuid):
        matching_char_data = None
        for char_data in self.characters:
            if char_data['uuid'] == char_uuid:
                matching_char_data = char_data
                break
        if not matching_char_data:
            return
        game = Game(chars=[Character.from_save_data(matching_char_data['uuid'])])
        game.owners = [self.username]
        self.saved_games.append(game.to_save_data())
        with open('games.dat', 'w') as games:
            data = tornado.escape.json_encode(self.saved_games)
            games.write(data)
        game.close()
        self.send_games()
    def load_game(self, char_uuid, game_uuid):
        matching_char_data = None
        for char_data in self.characters:
            if char_data['uuid'] == char_uuid:
                matching_char_data = char_data
                break
        if not matching_char_data:
            return
        matching_game_data = None
        for game_data in self.saved_games:
            if game_data['uuid'] == game_uuid:
                matching_game_data = game_data
                break
        if not matching_game_data:
            return
        game = Game.from_save_data(game_uuid, char_uuid)
        Game.games.add(game)
        self.move_player_to_game(game_uuid, char_uuid)
    def join_game(self, char_uuid, game_uuid):
        game = None
        for item in Game.games:
            if item.uuid==game_uuid:
                game = item
                break
        if not game:
            return
        for char in game.chars:
            if char.uuid==char_uuid:
                self.move_player_to_game(game_uuid, char_uuid)
                return
        matching_char_data = None
        for char_data in self.characters:
            if char_data['uuid'] == char_uuid:
                matching_char_data = char_data
                break
        if not matching_char_data:
            return
        game.chars.append(Character.from_save_data(char_uuid))
        self.move_player_to_game(game_uuid, char_uuid)
    def move_player_to_game(self, game_uuid, char_uuid):
        message = {}
        message['message'] = 'enter_game'
        message = tornado.escape.json_encode(message)
        self.attempt_to_write_message(message)
    def attempt_to_write_message(self, message):
        try:
            self.write_message(message)
        except Exception as e:
            print 'CONNECTION LOST'

class SocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()
    game = None
    lock = False
    # ips = ['abc']
    ips = []
    def open(self):
        # self.message_count = 0
        # self.set_nodelay(True)
        self.drew = True
        self.wait_for_lock()
        SocketHandler.lock = True
        SocketHandler.clients.add(self)
        # self.set_up_game()
        # self.initialize_character()
        self.increase_monster_strength()
        self.open = True
        SocketHandler.lock = False
        # self.animations = ['abc']
        self.animations = []
        # self.soudns = ['abc']
        self.sounds = []
        # self.floating_text = [FloatingText(1,1,'abc','abc')]
        self.floating_text = []
        self.char = None
    def get_compression_options(self):
        return {}
    def close(self):
        self.game.save_game()
        SocketHandler.clients.remove(self)
        if self.char in self.game.chars:
            self.game.chars.remove(self.char)
        if self in self.game.handlers:
            self.game.handlers.remove(self)
    def increase_monster_strength(self):
        if len(SocketHandler.clients)>1:
            for mob in self.game.monsters:
                mob.increase_player_strength()
            self.game.player_strength+=1
            print('Monsters grow stronger!')
            print('Strength', self.game.player_strength)
    def initialize_character(self):
        if self.request.remote_ip not in SocketHandler.ips:
            self.initialize_new_character()
            message = {"id": str(uuid.uuid4()), "message": "clear_map"}
            self.attempt_to_write_message(message)
        else:
            for char in self.game.chars:
                if char.ip == self.request.remote_ip:
                    self.char = char
        self.char.handler = self
        self.char.game = self.game
    def initialize_new_character(self):
        self.char = Character()
        self.char.game = self.game
        self.char.ip = self.request.remote_ip
        SocketHandler.ips.append(self.request.remote_ip)
        self.char.pos_x = self.game.map.start_x
        self.char.pos_y = self.game.map.start_y
        self.game.check_char_start_pos(self.char)
        self.game.chars.append(self.char)
        self.char.alive = False
        self.char.class_selected = False
        self.push_char_class_select()
    def set_up_game(self):
        if self.game==None:
            self.game = Game()
        self.game.handlers.append(self)
    def wait_for_lock(self):
        if SocketHandler.lock:
            while SocketHandler.lock:
                pass
    def on_close(self):
        self.wait_for_lock()
        SocketHandler.clients.remove(self)
        if self.game:
            self.game.handlers.remove(self)
            self.decrease_monster_strength()
    def decrease_monster_strength(self):
        if len(SocketHandler.clients)>0:
            for mob in self.game.monsters:
                mob.decrease_player_strength()
            self.game.player_strength-=1
            print('Monsters grow weaker!')
            print('Strength ',self.game.player_strength)
    def push_game_state_with_map(self):
        if self.invalid_push_state():
            return
        if not self.char:
            return
        if not self.char.class_selected:
            self.push_char_class_select()
            return
        if self.char.pruning:
            self.push_deck_prune()
            return
        SocketHandler.lock = True
        monsters,tiles,offset_x,offset_y,target,target_hp,target_max_hp,target_class,target_level,target_name,paralyzed,char_id = self.get_game_data()
        # if len(tiles)>0 and float(self.game.tick)/15.0 == self.game.tick/15:
        #     update_background = True
        # else:
        #     update_background = False

        update_background = False

        # message = {"message": "update", "projectiles": serialize_list(self.game.projectiles), "monsters": serialize_list(monsters), "target": str(target), "friendly_target": str(self.char.friendly_target_num), "tiles": tiles,"target_hp":str(target_hp),"target_max_hp":str(target_max_hp), "char_id": str(char_id), "unlock_points": self.game.unlock_points, "unlock_progress": self.game.unlock_progress, "target_class": str(target_class), "target_level": str(target_level), "total_xp": str(self.char.xp_current_level()), "level": str(self.char.level), "next_level_xp": str(self.char.next_level_xp_current_level()), "target_name": target_name, "paralyzed": paralyzed, 'won': self.game.won, 'effects': self.char.effects, 'effects_duration': self.char.effects_duration, 'effects_max_duration': self.char.effects_max_duration, 'current_chain': self.game.current_chain, 'chain_timer': humanize_time(self.game.chain_timer), 'chains': self.game.get_chains(), 'animations': self.animations, 'sounds': self.sounds, 'floating_text': serialize_list(self.floating_text), 'floor': self.game.floor, 'sight': self.game.final_sight, 'update_background': update_background}
        # if not self.game.drops_up_to_date:
        #     self.game.drops_up_to_date = True
        #     message['drops_added'] = True
        #     message['drops'] = self.game.drops
        #     message['drop_depth'] = self.game.drop_depth
        #     message['drop_unlocked'] = self.game.drop_unlocked
        # else:
        #     message['drops_added'] = False
        # if not self.game.chars_up_to_date:
        #     self.game.chars_up_to_date = True
        #     message['chars'] = serialize_char_list_full(self.game.chars,self.char)
        # else:
        #     message['chars'] = serialize_char_list(self.game.chars,self.char)

        if not self.game.drops_up_to_date:
            self.game.drops_up_to_date = True
            drops_added = True
            drops = self.game.drops
            drop_depth = self.game.drop_depth
            drop_unlocked = self.game.drop_unlocked
        else:
            drops_added = False
        if not self.game.chars_up_to_date:
            self.game.chars_up_to_date = True
            chars = serialize_char_list_to_binary_full(self.game.chars,self.char)
        else:
            chars = serialize_char_list_to_binary(self.game.chars,self.char)

        target = str(target)
        friendly_target = self.char.friendly_target_num
        unlock_points = self.game.unlock_points
        unlock_progress = self.game.unlock_progress
        total_xp = self.char.xp_current_level()
        level = self.char.level
        next_level_xp = self.char.next_level_xp_current_level()
        won = self.game.won
        current_chain = self.game.current_chain
        chain_timer = humanize_time(self.game.chain_timer)
        chains = self.game.get_chains()
        floor = self.game.floor

        binary_data = struct.pack('!15shiihhfiiLhL15scch8s30shc', target, friendly_target, target_hp, target_max_hp, char_id, unlock_points, unlock_progress, target_class, target_level, total_xp, level, next_level_xp, target_name, boolean_to_char(paralyzed), boolean_to_char(won), current_chain, chain_timer, chains, floor, boolean_to_char(update_background))
        binary_data+= serialize_list_as_binary(self.game.projectiles)
        binary_data+= serialize_list_as_binary(monsters)
        binary_data+= tiles_to_binary(tiles)
        binary_data+= sight_to_binary(self.game.final_sight)
        binary_data+= effects_to_binary(self.char.effects)
        binary_data+= effects_duration_to_binary(self.char.effects_duration)
        binary_data+= effects_duration_to_binary(self.char.effects_max_duration)
        binary_data+= string_array_to_binary(self.sounds)
        binary_data+= animations_to_binary(self.animations)
        binary_data+= serialize_list_as_binary(self.floating_text)
        binary_data+= chars
        binary_data+= struct.pack('c',boolean_to_char(drops_added))
        if drops_added:
            binary_data+= unsigned_integer_array_to_binary(drops) + unsigned_integer_array_to_binary(drop_depth) + boolean_array_to_binary(drop_unlocked)

        base64_data = base64.encodestring(binary_data)
        message = {'u': base64_data}
        # print len(tornado.escape.json_encode(message))
        # print (tornado.escape.json_encode(message))

        self.attempt_to_write_message(message)
        self.animations = []
        self.sounds = []
        self.floating_text = []
        SocketHandler.lock = False
    # def push_game_state(self):
    #     if self.invalid_push_state():
    #         return
    #     if not self.char.class_selected:
    #         self.push_char_class_select()
    #         return
    #     if self.char.pruning:
    #         self.push_deck_prune()
    #         return
    #     SocketHandler.lock = True
    #     monsters,target,target_hp,target_max_hp,target_class,target_level,target_name,paralyzed,char_id = self.get_game_data_without_tiles()
    #     message = {"message": "update", "projectiles": serialize_list(self.game.projectiles), "monsters": serialize_list(monsters), "target": str(target), "friendly_target": str(self.char.friendly_target_num), "target_hp":str(target_hp),"target_max_hp":str(target_max_hp), "char_id": str(char_id), "unlock_points": self.game.unlock_points, "unlock_progress": self.game.unlock_progress, "target_class": str(target_class), "target_level": str(target_level), "total_xp": str(self.char.xp_current_level()), "level": str(self.char.level), "next_level_xp": str(self.char.next_level_xp_current_level()), "target_name": target_name, "paralyzed": paralyzed, 'won': self.game.won, 'effects': self.char.effects, 'effects_duration': self.char.effects_duration, 'effects_max_duration': self.char.effects_max_duration, 'current_chain': self.game.current_chain, 'chain_timer': humanize_time(self.game.chain_timer), 'chains': self.game.get_chains(), 'animations': self.animations, 'sounds': self.sounds, 'floating_text': serialize_list(self.floating_text), 'floor': self.game.floor, 'update_background': False}
    #     if not self.game.drops_up_to_date:
    #         self.game.drops_up_to_date = True
    #         message['drops'] = self.game.drops
    #         message['drop_depth'] = self.game.drop_depth
    #         message['drop_unlocked'] = self.game.drop_unlocked
    #     if not self.game.chars_up_to_date:
    #         self.game.chars_up_to_date = True
    #         message['chars'] = serialize_char_list_full(self.game.chars,self.char)
    #     else:
    #         message['chars'] = serialize_char_list(self.game.chars,self.char)
    #     self.attempt_to_write_message(message)
    #     self.animations = []
    #     self.floating_text = []
    #     self.sounds = []
    #     SocketHandler.lock = False
    # def push_deck_prune(self):
    #     self.char.pruning = True
    #     number_to_keep = self.char.get_number_of_temp_cards_to_keep()
    #     if number_to_keep==0:
    #         return
    #     SocketHandler.lock = True
    #     for item in self.char.deck.hand:
    #         self.char.deck.discard_pile.append(item)
    #     for item in self.char.deck.draw_pile:
    #         self.char.deck.discard_pile.append(item)
    #     self.char.deck.hand = []
    #     self.char.deck.draw_pile = []
    #     numbers = []
    #     for item in self.char.deck.discard_pile:
    #         numbers.append(item.type)
    #     message = {"id": str(uuid.uuid4()), "message": "prune_deck", "deck": numbers, "number_to_keep": number_to_keep, "starter_number_to_keep": 12-number_to_keep}
    #     self.attempt_to_write_message(message)
    #     SocketHandler.lock = False
    def get_game_data(self):
        monsters = self.game.audited_monster_list(self.game.monsters,self.game.tiles)
        tiles,offset_x,offset_y = self.game.audited_tiles_list(self.game.tiles,self.char)
        target,target_hp,target_max_hp,target_class,target_level,target_name = self.get_target_data(monsters)
        paralyzed = self.set_paralyzed()
        char_id = self.set_char_id()
        return monsters,tiles,offset_x,offset_y,target,target_hp,target_max_hp,target_class,target_level,target_name,paralyzed,char_id
    def get_game_data_without_tiles(self):
        monsters = self.game.audited_monster_list(self.game.monsters,self.game.tiles)
        target,target_hp,target_max_hp,target_class,target_level,target_name = self.get_target_data(monsters)
        paralyzed = self.set_paralyzed()
        char_id = self.set_char_id()
        return monsters,target,target_hp,target_max_hp,target_class,target_level,target_name,paralyzed,char_id
    def invalid_push_state(self):
        if not self.drew:
            return True
        else:
            return SocketHandler.lock
    def attempt_to_write_message(self,message):
        # print ''
        # print 'Entire message: ', len(tornado.escape.json_encode(message))
        # for k,v in message.iteritems():
        #     d = {}
        #     d[k] = v
        #     print k, ': ', len(tornado.escape.json_encode(d))
        # self.message_count+= 1
        # print self.message_count, int(round(time.time() * 1000))
        try:
            # print message
            self.write_message(message)
        except:
            print('Connection lost')
    def set_char_id(self):
        for i in range(len(self.game.chars)):
            if self.game.chars[i]==self.char:
                return i
        return 0
    def set_paralyzed(self):
        return (0 in self.char.effects)
    def get_target_data(self,monsters):
        target = self.set_target(monsters)
        target_hp,target_max_hp,target_class,target_level,target_name = self.set_target_data(target)
        return target,target_hp,target_max_hp,target_class,target_level,target_name
    def set_target_data(self,target):
        if target == None:
            return 0,100,-1,-1,''
        else:
            return target.hp,target.max_hp,target.mob_class,target.level,target.name
    def set_target(self,monsters):
        for monster in monsters:
            if self.char.target == monster:
                return monster
        return None
    def push_narration(self,text):
        message = {"id": str(uuid.uuid4()), "message": "narration", "text": time.strftime('%I:%M:%S %p')+': '+text}
        self.attempt_to_write_message(message)
    def on_message(self,message):
        parsed = tornado.escape.json_decode(message)
        if parsed['message']=='loot_click':
            self.game.loot_click(parsed['num'],parsed['ctrl_click'],self.char)
        elif parsed['message']=='merge_chains':
            self.game.merge_chains(parsed['num'])
        elif parsed['message']=='request_deck':
            self.push_deck_info()
        elif parsed['message']=='request_bestiary':
            self.push_bestiary_info()
        elif parsed['message']=='shop_click':
            self.game.shop_click(parsed['num'],self.char)
        elif parsed['message']=='select_target':
            self.select_target(int(parsed['target']))
        elif parsed['message']=='drew':
            self.drew = True
        elif parsed['message']=='class_selected':
            self.select_class(parsed['class_selected'])
        elif parsed['message']=='trash_request':
            self.trash_cards(parsed['trash'])
        elif parsed['message']=='prune_request':
            self.prune_cards(parsed['prune'])
        elif parsed['message']=='request_full_map':
            self.request_full_map()
        elif parsed['message']=='connect_to_session':
            self.connect_to_session(parsed['game'],parsed['character'])
        else:
            self.parse_keypress(parsed['message'])
    def connect_to_session(self, game_uuid, character_uuid):
        game = None
        for item in Game.games:
            if item.uuid==game_uuid:
                game = item
                break
        if not game:
            self.send_back_to_login()
            return
        game.drops_up_to_date = False
        char = None
        for item in game.chars:
            if item.uuid==character_uuid:
                char = item
                break
        if not char:
            self.send_back_to_login()
            return
        self.char = char
        char.game = game
        self.game = game
        self.char.ip = self.request.remote_ip
        if self.request.remote_ip not in SocketHandler.ips:
            SocketHandler.ips.append(self.request.remote_ip)
        self.char.pos_x = self.game.map.start_x
        self.char.pos_y = self.game.map.start_y
        self.game.check_char_start_pos(self.char)
        self.char.alive = True
        self.char.class_selected = True
        self.char.handler = self
        if self not in self.game.handlers:
            self.game.handlers.append(self)
        if not self.game.mainloop_started:
            thread.start_new_thread(self.game.mainloop,())
        message = {"id": str(uuid.uuid4()), "message": "clear_map"}
        self.attempt_to_write_message(message)
        self.request_full_map()
    def send_back_to_login(self):
        message = {"id": str(uuid.uuid4()), "message": "return_to_login"}
        self.attempt_to_write_message(message)
    def request_full_map(self):
        print 'requested'
        self.game.last_tiles = set_up_empty_2d_array(self.game.map.size_x/tile_size)
        self.game.last_sight_change_map = set_up_empty_2d_array(self.game.map.size_x/tile_size)
        self.game.chars_up_to_date = False
    def push_deck_info(self):
        table = {}
        for item in self.char.deck.discard_pile:
            if item.type in table:
                table[item.type]+=1
            else:
                table[item.type]=1
        for item in self.char.deck.draw_pile:
            if item.type in table:
                table[item.type]+=1
            else:
                table[item.type]=1
        for item in self.char.deck.hand:
            if item.type in table:
                table[item.type]+=1
            else:
                table[item.type]=1
        for item in self.char.deck.in_play:
            if item.type in table:
                table[item.type]+=1
            else:
                table[item.type]=1
        # items = [1]
        items = []
        # counts = [1]
        counts = []
        for k,v in table.items():
            items.append(k)
            counts.append(v)
        message = {'id': str(uuid.uuid4()), 'message': 'deck_contents', 'items': items, 'counts': counts}
        self.attempt_to_write_message(message)
    def push_bestiary_info(self):
        message = {'id': str(uuid.uuid4()), 'message': 'bestiary_contents', 'items': self.game.bestiary}
        self.attempt_to_write_message(message)
    def select_class(self,class_name):
        if self.char.class_selected==True:
            return
        self.char.deck = Deck(class_name)
        self.char.alive = True
        self.char.class_selected = True
        self.push_narration('You have entered the game.')
    def push_char_class_select(self):
        self.char.alive = False
        self.char.class_selected = False
        message = {"id": str(uuid.uuid4()), "message": "push_class_select"}
        self.attempt_to_write_message(message)
    def trash_cards(self, list):
        if self.char.trashes_entitled < len(list):
            return
        self.char.trashes_entitled -= len(list)
        self.char.deck.hand = [None, None, None, None, None, None]
        for item in list:
            self.trash_card(item)
        self.char.deck.initial_draw()
    def trash_card(self, number):
        if len(self.char.deck.discard_pile)==1:
            return
        for item in self.char.deck.discard_pile:
            if item.type==number:
                self.char.deck.discard_pile.remove(item)
                return
    def parse_keypress(self,message):
        self.drew = False
        table = {'push_up':self.char.push_up, 'push_down':self.char.push_down, 'push_left':self.char.push_left, 'push_right':self.char.push_right, 'push_1':self.char.push_1, 'push_2':self.char.push_2, 'push_3':self.char.push_3, 'push_4':self.char.push_4, 'push_5':self.char.push_5, 'push_6':self.char.push_6, 'push_downstairs':self.char.push_downstairs, 'push_upstairs':self.char.push_upstairs, 'push_q':self.char.push_q, 'push_m':self.char.push_m, 'push_b':self.char.push_b,'push_tab':self.char.push_tab}
        if self.char.alive:
            table[message]()
    def select_target(self,target):
        if len(self.game.chars)>target:
            self.char.friendly_target_num = target
            self.char.friendly_target = self.game.chars[target]
        else:
            self.char.friendly_target = self.char
            for i in range(len(self.game.chars)):
                if self.game.chars[i]==self.char:
                    self.char.friendly_target_num = i
    def prune_cards(self,prune):
        if not self.char.verify_prune(prune):
            self.push_deck_prune()
            return
        for item in prune:
            self.prune_card(item)
        self.fill_out_deck()
        self.char.deck.hand = [None, None, None, None, None, None]
        self.char.deck.initial_draw()
        self.char.pruning = False
        if self.game.won:
            for char in self.game.chars:
                if char.pruning:
                    return
        # self.game.start_new_dungeon()
        saved_games = []
        if os.path.isfile('games.dat'):
            with open('games.dat', 'r') as savefile:
                data = tornado.escape.json_decode(savefile.read())
                saved_games = data
        for item in saved_games:
            if item['uuid']==self.uuid:
                saved_games.remove(item)
                break
        with open('games.dat', 'w') as games:
            data = tornado.escape.json_encode(saved_games)
            games.write(data)
        for handler in self.handlers:
            handler.send_back_to_login()
        saved_chars = []
        if os.path.isfile('characters.dat'):
            with open('characters.dat', 'r') as savefile:
                data = tornado.escape.json_decode(savefile.read())
                saved_chars = data
        for char in self.chars:
            owner = None
            for item in saved_chars:
                if item['uuid']==char.uuid:
                    owner = item['owner']
                    saved_chars.remove(item)
                    break
            data = char.to_save_data()
            if owner:
                data['owner'] = owner
            saved_chars.append(data)
        with open('characters.dat', 'w') as savefile:
            data = tornado.escape.json_encode(saved_chars)
            savefile.write(data)
        self.close()
        self.ongoing = False

    def prune_card(self, number):
        for item in self.char.deck.discard_pile:
            if item.type==number:
                self.char.deck.discard_pile.remove(item)
                return
    def fill_out_deck(self):
        while len(self.char.deck.discard_pile)<12:
            self.char.deck.discard_pile.append(Card(0))
class Game(object):
    @staticmethod
    def from_save_data(uuid, char_uuid):
        if not os.path.isfile('games.dat'):
            return None
        game_data = None
        with open('games.dat', 'r') as games:
            data = tornado.escape.json_decode(games.read())
            for item in data:
                if item['uuid']==uuid:
                    game_data = item
                    break
        if game_data==None:
            return None
        char = Character.from_save_data(char_uuid)
        game = Game(chars=[char])
        game.name = game_data['name']
        game.floor = game_data['current_floor']-1
        game.enemies_defeated = game_data['enemies_defeated']
        game.owners = game_data['owners']
        game.players = [char.name]
        game.is_public = game_data['is_public']
        game.unlock_points = game_data['unlock_points']
        game.unlock_progress = game_data['unlock_progress']
        game.drops = game_data['drops']
        game.drop_depth = game_data['drop_depth']
        game.drop_unlocked = game_data['drop_unlocked']
        game.chains = game_data['chains']
        game.bestiary = game_data['bestiary']
        game.uuid = game_data['uuid']
        game.maps = []
        x = 0
        for map_obj in game_data['maps']:
            game.maps.append(Map.from_save_data(map_obj,game,x))
            x+=1
        game.tiles = game.maps[game.floor].tiles
        game.last_tiles = game_data['last_tiles']
        game.last_sight_change_map = game_data['last_sight_change_map']
        game.final_sight = game_data['final_sight']
        game.map = game.maps[game.floor]
        game.monsters = game.maps[game.floor].monsters
        char.pos_x = game.map.start_x
        char.pos_y = game.map.start_y
        return game
    games = set()
    def __init__(self, chars = None):
        self.uuid = str(uuid.uuid4())
        self.is_public = True
        self.name = ''
        self.enemies_defeated = 0
        self.owners = []
        Game.games.add(self)
        self.initialize_lists(chars)
        self.initialize_stacks()
        self.initialize_values()
        self.initialize_maps()
        self.current_time = self.target_time = time.time()
        self.mainloop_started = False
        self.drops_up_to_date = False
        self.chars_up_to_date = False
        # thread.start_new_thread(self.mainloop,())
    def close(self):
        Game.games.remove(self)
    def initialize_values(self):
        self.player_strength=1
        self.view_size = tile_size*16 #512, 8192 for testing
        self.tick = 0
        self.fps = 60
        self.loop_delta = 1./self.fps
        self.current_chain = 0
        self.chain_timer = 0
        self.unlock_points = 0
        self.unlock_progress = 0.0
    def initialize_lists(self, chars):
        # self.handlers = [None]
        self.handlers = []
        # self.chars = [Character()]
        self.chars = []
        if chars:
            self.chars = chars
        # self.drops = [1]
        self.drops = []
        # self.drop_depth = [1]
        self.drop_depth = []
        # self.drop_unlocked = [False]
        self.drop_unlocked = []
        # self.projectiles = [Projectile(1,1,1,1,1,1,1,None,-1,None,None,'white')]
        self.projectiles = []
        self.chains = [0,0,0,0,0,0,0,0]
        # self.bestiary = [{'name': 'abc', 'min_level': 1, 'max_level': 1, 'min_class': 1, 'max_class': 1, 'kills': 1}]
        self.bestiary = []
        # self.sounds = ['abc']
        self.sounds = []
        # self.floating_text = [FloatingText(1,1,'TRAP','#FF0000')]
        self.floating_text = []
    def initialize_stacks(self):
        for i in range(20):
            roll = random.randint(11,56)
            while roll>=52 and roll<=54:
                roll = random.randint(11,55)
            self.drops.append(roll)
            self.drop_depth.append(10)
        for i in range(5):
            self.drop_unlocked.append(True)
        for i in range(15):
            self.drop_unlocked.append(False)
        self.organize_drops()
        self.ensure_stacks_are_unique()
        self.sort_stacks()
    def organize_drops(self):
        # temp = [1]
        temp = []
        counter = 0
        for i in range(1,6):
            matching_num = -1
            matching_j = -1
            for j in range(len(self.drops)):
                card = Card(self.drops[j])
                current_num = card.cost
                if (current_num < matching_num and current_num>=i) or (matching_num==-1 and current_num>=i):
                    matching_num = current_num
                    matching_j = j
            temp.append(self.drops[matching_j])
            del self.drops[matching_j]
        while self.drops:
            temp.append(self.drops[0])
            del self.drops[0]
        self.drops = temp
    def ensure_stacks_are_unique(self):
        for i in range(len(self.drops)-1):
            for j in range(i+1,len(self.drops)):
                if self.drops[i]==self.drops[j]:
                    self.drops[j] = random.randint(11,51)
                    self.ensure_stacks_are_unique()
                    return
    def sort_stacks(self):
        # temp = [1]
        temp = []
        # temp_depth = [1]
        temp_depth = []
        # temp_unlocked = [False]
        temp_unlocked = []
        while self.drops:
            lowest_num = -1
            lowest_i = -1
            for i in range(len(self.drops)):
                card = Card(self.drops[i])
                current_num = card.cost
                if not self.drop_unlocked[i]:
                    current_num += 100
                if current_num < lowest_num or lowest_num==-1:
                    lowest_num = current_num
                    lowest_i = i
            temp.append(self.drops[lowest_i])
            temp_depth.append(self.drop_depth[lowest_i])
            temp_unlocked.append(self.drop_unlocked[lowest_i])
            del self.drops[lowest_i]
            del self.drop_depth[lowest_i]
            del self.drop_unlocked[lowest_i]
        self.drops = temp
        self.drop_depth = temp_depth
        self.drop_unlocked = temp_unlocked
    def initialize_maps(self):
        avg_level = self.get_average_char_level()
        self.maps = [Map(self,0,height='top',level=avg_level),Map(self,1,level=avg_level+1),Map(self,2,level=avg_level+2),Map(self,3,level=avg_level+3),Map(self,4,level=avg_level+4),Map(self,5,level=avg_level+5),Map(self,6,level=avg_level+6),Map(self,7,level=avg_level+7),Map(self,8,level=avg_level+8),Map(self,9,height='bottom',level=avg_level+9)]
        # self.maps = [Map(self,0,height='top',level=avg_level),Map(self,1,height='bottom',level=avg_level+1)]
        self.map = self.maps[0]
        self.floor = 0
        self.won = False
        self.ongoing = True
        for char in self.chars:
            char.pos_x,char.pos_y = self.map.start_x,self.map.start_y
        self.monsters = self.map.monsters
        # self.active_monsters = [Monster(self, 1, 1, 1, 1, 1)]
        self.active_monsters = []
        self.tiles = self.map.tiles
        for monster in self.monsters:
            if monster.idle_behavior==1:
                monster.initialize_patrol_routes()
        self.last_tiles = set_up_empty_2d_array(self.map.size_x/tile_size)
        self.last_sight_change_map = set_up_empty_2d_array(self.map.size_x/tile_size,False)
        self.final_sight = []
    def get_average_char_level(self):
        if len(self.chars)==0:
            return 1
        count = 0
        for char in self.chars:
            count+=char.level
        count/=len(self.chars)
        return count
    def mainloop(self):
        self.mainloop_started = True
        while self.ongoing:
            try:
                self.process_tick()
                # if float(self.tick)/4.0 == self.tick/4:
                #     self.push_game_state_with_map()
                # elif float(self.tick)/2.0 == self.tick/2:
                #     self.push_game_state()
                # print self.tick
                if float(self.tick)/2.0 == self.tick/2:
                    self.push_game_state_with_map()
            except Exception:
                import traceback
                print traceback.format_exc()
    def process_tick(self):
        self.cap_framerate()
        # start_time = time.time()
        # end_time = time.time()
        # print (end_time-start_time)
        self.decrement_gcds()
        self.decrement_autoheals()
        self.autoheals()
        self.monster_tick()
        if self.tick==1:
            self.disseminate_scents()
            for char in self.chars:
                self.release_scent(char.pos_x,char.pos_y)
        self.character_tick()
        self.projectiles_move()
        self.decrement_timing_counters()
        self.decrement_chain_timer()
        if self.check_if_all_players_dead():
            self.game_over()
        for sound in self.sounds:
            for handler in self.handlers:
                handler.sounds.append(sound)
        for floating_text in self.floating_text:
            for handler in self.handlers:
                handler.floating_text.append(floating_text)
        # self.sounds = ['abc']
        self.sounds = []
        # self.floating_text = [FloatingText(1,1,'abc','abc')]
        self.floating_text = []
    def game_over(self):
        # self.push_narration('All characters are dead. The game is over.')
        # message = {"id": str(uuid.uuid4()), "message": "clear_map"}
        # for handler in self.handlers:
        #     handler.attempt_to_write_message(message)
        # self.ongoing = False
        # new_game = Game()
        # self.game = new_game
        # new_game.handlers = self.handlers
        # new_game.chars = self.chars
        # for char in new_game.chars:
        #     self.reset_character(char,new_game)
        saved_games = []
        if os.path.isfile('games.dat'):
            with open('games.dat', 'r') as savefile:
                data = tornado.escape.json_decode(savefile.read())
                saved_games = data
        for item in saved_games:
            if item['uuid']==self.uuid:
                saved_games.remove(item)
                break
        with open('games.dat', 'w') as games:
            data = tornado.escape.json_encode(saved_games)
            games.write(data)
        saved_chars = []
        if os.path.isfile('characters.dat'):
            with open('characters.dat', 'r') as savefile:
                data = tornado.escape.json_decode(savefile.read())
                saved_chars = data
        for char in self.chars:
            for item in saved_chars:
                if item['uuid']==char.uuid:
                    saved_chars.remove(item)
                    break
        with open('characters.dat', 'w') as savefile:
            data = tornado.escape.json_encode(saved_chars)
            savefile.write(data)
        for handler in self.handlers:
            handler.send_back_to_login()
        self.close()
        self.ongoing = False


    def start_new_dungeon(self):
        self.push_clear_narration()
        self.push_narration('You enter a new dungeon.')
        message = {"id": str(uuid.uuid4()), "message": "clear_map"}
        for handler in self.handlers:
            handler.attempt_to_write_message(message)
        self.initialize_maps()
        for char in self.chars:
            self.check_char_start_pos(char)
    def reset_character(self,char,new_game):
        handler = char.handler
        char.__init__()
        char.handler = handler
        char.pos_x = new_game.map.start_x
        char.pos_y = new_game.map.start_y
        char.game = self.game
        new_game.check_char_start_pos(char)
        char.handler.push_char_class_select()
    def cap_framerate(self):
        self.previous_time,self.current_time = self.current_time,time.time()
        self.time_delta = self.current_time - self.previous_time
        self.target_time+=self.loop_delta
        self.sleep_time = self.target_time - time.time()
        if self.sleep_time > 0:
            time.sleep(self.sleep_time)
        self.tick+=1
        if self.tick==60:
            self.tick=0
    def check_if_all_players_dead(self):
        for char in self.chars:
            if char.hp>0:
                return False
        return True
    def check_char_start_pos(self,char):
        for char2 in self.chars:
            if (char!=char2 and char.pos_x/tile_size==char2.pos_x/tile_size and char.pos_y/tile_size==char2.pos_y/tile_size) or self.map.tiles[char.pos_x/tile_size][char.pos_y/tile_size] in ['W','S','D','@','F','Q','O','H','R']:
                x = random.randint(-1,1)
                y = random.randint(-1,1)
                char.pos_x+=x*tile_size
                char.pos_y+=y*tile_size
                self.check_char_start_pos(char)
                break
    def merge_chains(self,num):
        if self.chains[num-1] >= 4:
            self.chains[num-1] -= 4
            self.chains[num] += 1
    def loot_click(self,num,ctrl_click,char):
        self.drops_up_to_date = False
        if ctrl_click:
            if self.unlock_points > 0 and not self.drop_unlocked[num]:
                self.sounds.append('unlock_card')
                self.drop_unlocked[num] = True
                self.unlock_points -= 1
                self.sort_stacks()
        else:
            if not self.drop_unlocked[num]:
                return
            if num < len (self.drops):
                c = Card(self.drops[num], temp=True)
                for i in range(len(self.chains)):
                    n = i+1
                    if self.chains[i]>0 and n>=c.cost:
                        self.chains[i] -= 1
                        char.deck.discard_pile.append(c)
                        self.sounds.append('purchase')
                        char.determine_if_trasher(self.drops[num])
                        self.drop_depth[num] -= 1
                        if self.drop_depth[num] == 0:
                            self.drops.remove(self.drops[num])
                            self.drop_depth.remove(self.drop_depth[num])
                            del self.drop_unlocked[num]
                            self.sort_stacks()
                        break
    def get_chains(self):
        value = ''
        first = True
        for i in range(len(self.chains)):
            if self.chains[i]>0:
                if not first:
                    value+= ' ,'
                value+= str(i+1)+'x'+str(self.chains[i])
                first = False
        return value
    def shop_click(self, num, char):
        if num==0 and self.shop_click_spend(1):
            char.deck.discard_pile.append(Card(52))
            self.sounds.append('purchase')
        elif num==1 and self.shop_click_spend(2):
            char.shield = 28
            self.sounds.append('purchase')
        elif num==2 and self.shop_click_spend(3):
            char.trash(1)
            self.sounds.append('purchase')
        elif num==3 and self.shop_click_spend(4):
            char.max_mp += 10
            self.sounds.append('purchase')
        elif num==4 and self.shop_click_spend(5):
            char.mp_regen_rate *= 1.1
            self.sounds.append('purchase')
        elif num==5 and self.shop_click_spend(6):
            char.max_hp += 30
            self.sounds.append('purchase')
        elif num==6 and self.shop_click_spend(7):
            char.xp += int(char.next_level_xp_current_level()/2)
            char.total_xp += int(char.next_level_xp_current_level()/2)
            char.check_for_level_up()
            self.sounds.append('purchase')
        elif num==7 and self.unlock_points >0:
            self.unlock_points -= 1
            self.party_descends()
            self.party_descends()
            self.sounds.append('purchase')
    def shop_click_spend(self, cost):
        for i in range(len(self.chains)):
            n = i+1
            if self.chains[i]>0 and n>=cost:
                self.chains[i] -= 1
                self.sounds.append('purchase')
                return True
        return False
    def decrement_chain_timer(self):
        if self.chain_timer > 0:
            self.chain_timer -= 1
            if self.chain_timer <= 0:
                self.chain_timer = 0
                if self.current_chain>8:
                    self.current_chain = 8
                self.chains[self.current_chain-1]+=1
                self.sounds.append('chain_complete')
                self.current_chain = 0
    def decrement_gcds(self):
        for char in self.chars:
            if char.gcd>0:
                char.gcd-=1
        self.decrement_monster_gcds()
    def decrement_monster_gcds(self):
        for monster in self.monsters:
            if monster.gcd>0:
                monster.gcd-=1
    def decrement_autoheals(self):
        for char in self.chars:
            if char.autoheal_cd>0 and self.should_decrement_autoheals():
                char.autoheal_cd-=1
        self.decrement_monster_autoheals()
    def decrement_monster_autoheals(self):
        for monster in self.monsters:
            if monster.autoheal_cd>0 and monster.aggro==[]:
                monster.autoheal_cd-=1
    def should_decrement_autoheals(self):
        value = True
        for monster in self.monsters:
            if monster.aggro!=[]:
                value = False
        return value
    def autoheals(self):
        for char in self.chars:
            if char.autoheal_cd==0 and char.hp<char.max_hp:
                char.hp+=1
            if char.mp<char.max_mp:
                multiplier = 1
                if 4 in char.effects:
                    multiplier *= 2
                if 5 in char.effects:
                    multiplier *= 1.25
                if 7 in char.effects:
                    multiplier *= 1.2
                char.mp = min(float(char.mp)+(float(char.mp_regen_rate*multiplier)/float(60)),float(char.max_mp))
        for char in self.chars:
            if char.improved_invisibility:
                return
        for monster in self.monsters:
            if monster.autoheal_cd==0 and monster.hp<monster.max_hp:
                monster.hp+=1
    def monster_tick(self):
        for monster in self.monsters:
            monster.tick(self.chars,self.tick)
            if monster.hp<=0:
                self.kill_monster(monster)
    def kill_monster(self,monster):
        if monster in self.active_monsters:
            self.active_monsters.remove(monster)
            self.enemies_defeated += 1
        # for drop in monster.drops:
        #     self.drops.append(drop)
        table = [0.516, 0.774, 1.032, 4.988, 11.18]
        amount = table[monster.mob_class]
        self.unlock_progress += amount
        if self.unlock_progress >= 16:
            self.unlock_progress -= 16
            self.unlock_points += 1
            self.sounds.append('unlock_point')
        for char in self.chars:
            char.xp+=monster.xp
            char.total_xp+=monster.xp
            char.check_for_level_up()
        if monster.mob_class==4:
            self.end_dungeon()
        self.monsters.remove(monster)
        self.current_chain += 1
        self.sounds.append('chain_increment')
        table = [3.79, 4.435, 5.08, 14.97, 30.45]
        self.chain_timer = max(table[monster.mob_class]*60, self.chain_timer)
        self.update_bestiary(monster)
    def update_bestiary(self, mob):
        for item in self.bestiary:
            if item['name'] == mob.name:
                self.update_bestiary_item(item, mob)
                return
        self.add_bestiary_item(mob)
    def add_bestiary_item(self, mob):
        item = {}
        item['name'] = mob.name
        item['min_level'] = mob.level
        item['max_level'] = mob.level
        item['min_class'] = mob.mob_class
        item['max_class'] = mob.mob_class
        item['kills'] = 1
        self.bestiary.append(item)
    def update_bestiary_item(self, item, mob):
        if item['min_level'] > mob.level:
            item['min_level'] = mob.level
        if item['max_level'] < mob.level:
            item['max_level'] = mob.level
        if item['min_class'] > mob.mob_class:
            item['min_class'] = mob.mob_class
        if item['max_class'] < mob.mob_class:
            item['max_class'] = mob.mob_class
        item['kills'] += 1
    def end_dungeon(self):
        self.won = True
        for handler in self.handlers:
            handler.push_deck_prune()
    def character_tick(self):
        for char in self.chars:
            char.tick()
    def decrement_timing_counters(self):
        for char in self.chars:
            for i in char.deck.in_play:
                if i and i.type in [2,16]:
                    i.counters-=1
                    if i.counters<=0:
                        char.deck.discard_pile.append(i)
                        char.deck.in_play.remove(i)
    def projectiles_move(self):
        for projectile in self.projectiles:
            self.projectile_tick(projectile)
    def projectile_tick(self,proj):
        proj.move(self)
        if proj.distance<=0:
            if proj.effect==3:
                self.projectile_aoe_burst_no_target(proj,tile_size*2)
            elif proj.effect==9:
                self.projectile_aoe_burst_no_target(proj,tile_size*4)
            self.projectiles.remove(proj)
            return
        if proj.faction==0:
            self.projectile_check_for_monsters_hit(proj)
        elif proj.faction==1:
            self.projectile_check_for_characters_hit(proj)
    def projectile_check_for_monsters_hit(self,proj):
        hit = False
        for monster in self.monsters:
            if not hit:
                if proj.pos_x >= monster.pos_x and proj.pos_x <= monster.pos_x+tile_size and proj.pos_y >= monster.pos_y and proj.pos_y <= monster.pos_y+tile_size:
                    self.projectile_hit_monster(proj,monster)
                    hit = True
    def projectile_hit_monster(self,proj,monster):
        if proj.effect==3:
            self.projectile_aoe_burst(proj,monster,tile_size*2)
        elif proj.effect==9:
            self.projectile_aoe_burst(proj,monster,tile_size*4)
        else:
            monster.take_hit(proj.damage,proj.source)
        if proj.effect in [0,1,4,6,7,10]:
            monster.apply_effect(proj.effect, proj.source)
        elif proj.effect==2:
            monster.aggro_increment_if_aggrod(proj.source,proj.damage*3)
        elif proj.effect==5:
            self.chains[2]+=1
        elif proj.effect==8:
            self.chains[1]+=1
        if proj.dot:
            monster.apply_dot(proj.dot)
        if proj.delayed_damage_effect:
            monster.apply_delayed_damage_effect(proj.delayed_damage_effect)
        if proj in self.projectiles:
            self.projectiles.remove(proj)
    def projectile_aoe_burst(self, proj, hit_monster, radius):
        left = hit_monster.pos_x-radius
        right = hit_monster.pos_x+tile_size+radius
        top = hit_monster.pos_y-radius
        bottom = hit_monster.pos_y+radius
        animation_text = str(left)+','+str(right)+','+str(top)+','+str(bottom)+','+'#FF0000'
        for handler in self.handlers:
            handler.animations.append(animation_text)
        for monster in self.monsters:
            if left <= monster.pos_x and right >=monster.pos_x+tile_size and top <= monster.pos_y and bottom >= monster.pos_y+tile_size:
                monster.take_hit(proj.damage, proj.source)
                if proj.dot:
                    monster.apply_dot(proj.dot)
    def projectile_aoe_burst_no_target(self, proj, radius):
        left = proj.pos_x-radius
        right = proj.pos_x+tile_size+radius
        top = proj.pos_y-radius
        bottom = proj.pos_y+radius
        animation_text = str(left)+','+str(right)+','+str(top)+','+str(bottom)+','+'#FF0000'
        for handler in self.handlers:
            handler.animations.append(animation_text)
        for monster in self.monsters:
            if left <= monster.pos_x and right >=monster.pos_x+tile_size and top <= monster.pos_y and bottom >= monster.pos_y+tile_size:
                monster.take_hit(proj.damage, proj.source)
                if proj.dot:
                    monster.apply_dot(proj.dot)
    def projectile_check_for_characters_hit(self,proj):
        hit = False
        for char in self.chars:
            if not hit:
                if proj.pos_x >= char.pos_x and proj.pos_x <= char.pos_x+tile_size and proj.pos_y >= char.pos_y and proj.pos_y <= char.pos_y+tile_size:
                    self.projectile_hit_character(proj,char)
                    hit = True
    def projectile_hit_character(self,proj,char):
        char.take_hit(proj.damage)
        char.remove_stealth()
        if char.hp<=0:
            char.alive = False
        if proj in self.projectiles:
            self.projectiles.remove(proj)
    def audited_tiles_list(self,tiles,char):
        view_size = self.determine_view_size(char)
        # value = [1,1,'abc']
        value = []
        # value2 = [1,1,'abc']
        value2 = []
        for x in range(self.map.size_x/tile_size):
            for y in range(self.map.size_y/tile_size):
                item = self.audited_tile(char,x,y,view_size,tiles)
                item2 = self.can_see_tile(char,x,y,view_size,tiles)
                if item:
                    value.append(x)
                    value.append(y)
                    value.append(item)
                value2.append(x)
                value2.append(y)
                value2.append(item2)
                # value[x][y] = self.audited_tile(char,x,y,view_size,tiles)
        value = self.tile_compare(value)
        # self.final_sight = value2
        self.final_sight = self.tile_sight_compare(value2)
        return value, 0, 0
    def tile_sight_compare(self, value):
        # final_value = [1,1,'abc']
        final_value = []
        i = 0
        while i < len(value):
            x = value[i]
            y = value[i+1]
            item = value[i+2]
            if self.last_sight_change_map[x][y]!=item:
                self.last_sight_change_map[x][y] = item
                final_value.append(x)
                final_value.append(y)
                final_value.append(item)
            i += 3
        return final_value
    def tile_compare(self, value):
        # final_value = [1,1,'abc']
        final_value = []
        i = 0
        while i < len(value):
            x = value[i]
            y = value[i+1]
            item = value[i+2]
            if self.last_tiles[x][y]!=item:
                self.last_tiles[x][y] = item
                final_value.append(x)
                final_value.append(y)
                final_value.append(item)
            i += 3
        # for x in range(len(value)):
        #     for y in range(len(value[x])):
        #         if self.last_tiles[x][y]!=value[x][y]:
        #             final_value[x][y] = value[x][y]
        #             self.last_tiles[x][y] = value[x][y]
        return final_value
    def determine_view_size(self,char):
        if 2 in char.effects:
            return tile_size*3
        else:
            return self.view_size
    def audited_tile(self,char,x,y,view_size,tiles):
        if (x*tile_size)-char.pos_x+view_size/2>=-tile_size and (x*tile_size)-char.pos_x+view_size/2<=view_size and (y*tile_size)-char.pos_y+view_size/2>=-tile_size and (y*tile_size)-char.pos_y+view_size/2<=view_size and self.in_line_of_sight(char,tiles,x,y):
            if self.map.tiles[x][y]=='S':
                return 'W'
            else:
                return tiles[x][y]
        elif self.map.tiles_seen[x][y]:
            if self.map.tiles[x][y]=='S':
                return 'X'
            else:
                if self.map.tiles[x][y]=='W':
                    return 'X'
                return tiles[x][y]
        return None
    def can_see_tile(self,char,x,y,view_size,tiles):
        if (x*tile_size)-char.pos_x+view_size/2>=-tile_size and (x*tile_size)-char.pos_x+view_size/2<=view_size and (y*tile_size)-char.pos_y+view_size/2>=-tile_size and (y*tile_size)-char.pos_y+view_size/2<=view_size and self.in_line_of_sight(char,tiles,x,y):
            return True
        return False
    def in_line_of_sight(self,char,tiles,x1,y1,char_seeing=True):
        if not char:
            return False
        x0,y0,dx,dy,sx,sy,xnext,ynext,denom = self.set_up_in_line_of_sight_variables(char,x1,y1)
        while (xnext != x1 or ynext != y1):
            if xnext>=0 and ynext>=0 and xnext<len(tiles) and ynext<len(tiles[0]):
                if tiles[xnext][ynext] in ['W','S','D','@','F','Q','O','H','R']:
                    if char_seeing:
                        self.map.tiles_seen[xnext][ynext]=True
                    return False
                xnext,ynext = self.increment_line_of_sight_variables(xnext,ynext,dx,dy,x0,y0,sx,sy,denom)
        self.map.tiles_seen[x1][y1]=True
        return True
    def increment_line_of_sight_variables(self,xnext,ynext,dx,dy,x0,y0,sx,sy,denom):
        if abs(dy*(xnext-x0+sx)-dx*(ynext-y0))/denom<0.5:
            xnext+=sx
        elif abs(dy*(xnext-x0)-dx*(ynext-y0+sy))/denom<0.5:
            ynext+=sy
        else:
            xnext+=sx
            ynext+=sy
        return xnext,ynext
    def set_up_in_line_of_sight_variables(self,char,x1,y1):
        x0 = (char.pos_x+2)/tile_size
        y0 = (char.pos_y+2)/tile_size
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
    def audited_monster_list(self,monsters,tiles):
        # value = [Monster(self, 1, 1, 1, 1, 1)]
        value = []
        for char in self.chars:
            view_size = self.determine_view_size(char)
            for monster in monsters:
                if monster.pos_x-char.pos_x+view_size/2>=-tile_size and monster.pos_x-char.pos_x+view_size/2<=view_size and monster.pos_y-char.pos_y+view_size/2>=-tile_size and monster.pos_y-char.pos_y+view_size/2<=view_size:
                    if monster not in value:
                        if self.in_line_of_sight(char,tiles,monster.pos_x/tile_size,monster.pos_y/tile_size):
                            if monster.visible:
                                value.append(monster)
        return value
    def is_wall(self,x,y):
        # if self.is_wall_exact(+,y) or self.is_wall_exact(x+(tile_size-1),y) or self.is_wall_exact(x,y+(tile_size-1)) or self.is_wall_exact(x+(tile_size-1),y+(tile_size-1)):
        if self.is_wall_exact(x+2,y+2) or self.is_wall_exact(x+(tile_size-3),y+2) or self.is_wall_exact(x+2,y+(tile_size-3)) or self.is_wall_exact(x+(tile_size-3),y+(tile_size-3)):
            return True
        # if self.is_door(x,y):
            # return True
        return False
    def is_wall_exact(self,x,y):
        if len(self.map.tiles)>x/tile_size:
            if len(self.map.tiles[x/tile_size])>y/tile_size:
                return (self.map.tiles[x/tile_size][y/tile_size] in ['W','@','F','Q','O','H'])
        return False
    def is_collision(self,x,y,actor):
        for monster in self.monsters:
            if monster!=actor:
                # if x<monster.right() and x+(tile_size-1)>=monster.left() and y<monster.bottom() and y+(tile_size-1)>=monster.top():
                if x<=monster.right() and x+(tile_size-1)>=monster.left() and y<=monster.bottom() and y+(tile_size-1)>=monster.top():
                    return True
        for char in self.chars:
            if char!=actor:
                if x<=char.right() and x+(tile_size-1)>=char.left() and y<=char.bottom() and y+(tile_size-1)>=char.top():
                    return True
        return False
    def is_collision_mobs_only(self,x,y,actor):
        for monster in self.active_monsters:
            if monster!=actor:
                if x<=monster.right() and x+(tile_size-1)>=monster.left() and y<=monster.bottom() and y+(tile_size-1)>=monster.top():
                    return True
        return False
    def push_game_state_with_map(self):
        for client in SocketHandler.clients:
            client.push_game_state_with_map()
    def push_game_state(self):
        for client in SocketHandler.clients:
            client.push_game_state()
    def check_for_door_and_open(self,x,y):
        self.check_for_door_and_open_exact(x,y)
        self.check_for_door_and_open_exact(x+(tile_size-1),y)
        self.check_for_door_and_open_exact(x,y+(tile_size-1))
        self.check_for_door_and_open_exact(x+(tile_size-1),y+(tile_size-1))
    def check_for_door_and_open_exact(self,x,y):
        if len(self.map.tiles)>x/tile_size:
            if len(self.map.tiles[x/tile_size])>y/tile_size:
                if self.map.tiles[x/tile_size][y/tile_size] in ['D','S','R']:
                    temp = self.map.tiles[x/tile_size][y/tile_size]
                    self.map.tiles[x/tile_size][y/tile_size]=' '
                    if temp in ['D','R']:
                        self.push_narration('A door is opened.')
                        self.sounds.append('door')
                    elif temp=='S':
                        self.push_narration('A secret door is found!')
                        self.sounds.append('door')
    def push_narration(self,narration):
        for handler in self.handlers:
            handler.push_narration(narration)
    def push_clear_narration(self):
        message = {"id": str(uuid.uuid4()), "message": "cls"}
        for handler in self.handlers:
            handler.attempt_to_write_message(message)
    def check_for_stairs_and_use(self,x,y,direction):
        self.check_for_stairs_and_use_exact(x,y,direction)
        self.check_for_stairs_and_use_exact(x+(tile_size-1),y,direction)
        self.check_for_stairs_and_use_exact(x,y+(tile_size-1),direction)
        self.check_for_stairs_and_use_exact(x+(tile_size-1),y+(tile_size-1),direction)
    def check_for_stairs_and_use_exact(self,x,y,direction):
        if len(self.map.tiles)>x/tile_size:
            if len(self.map.tiles[x/tile_size])>y/tile_size:
                if self.map.tiles[x/tile_size][y/tile_size] == '>' and direction == '>':
                    self.party_descends()
                elif self.map.tiles[x/tile_size][y/tile_size] == '<' and direction == '<':
                    self.party_ascends()
    def party_descends(self):
        self.floor+=1
        self.sounds.append('stairs')
        if self.floor>len(self.maps)-1:
            self.floor = len(self.maps)-1
        self.map=self.maps[self.floor]
        self.tiles = self.map.tiles
        self.last_tiles = set_up_empty_2d_array(self.map.size_x/tile_size)
        self.last_sight_change_map = set_up_empty_2d_array(self.map.size_x/tile_size)
        self.monsters = self.map.monsters
        for char in self.chars:
            char.pos_x = self.map.start_x
            char.pos_y = self.map.start_y
            self.check_char_start_pos(char)
        self.push_narration('The party descends to floor '+str(self.floor+1)+'.')
        message = {"id": str(uuid.uuid4()), "message": "clear_map"}
        for handler in self.handlers:
            handler.attempt_to_write_message(message)
        self.save_game()
    def party_ascends(self):
        self.floor-=1
        self.sounds.append('stairs')
        self.map=self.maps[self.floor]
        self.tiles = self.map.tiles
        self.last_tiles = set_up_empty_2d_array(self.map.size_x/tile_size)
        self.last_sight_change_map = set_up_empty_2d_array(self.map.size_x/tile_size)
        self.monsters = self.map.monsters
        for char in self.chars:
            char.pos_x = self.map.end_x
            char.pos_y = self.map.end_y
            self.check_char_start_pos(char)
        message = {"id": str(uuid.uuid4()), "message": "clear_map"}
        for handler in self.handlers:
            handler.attempt_to_write_message(message)
        self.push_narration('The party ascends to floor '+str(self.floor+1)+'.')
        self.save_game()
    def check_for_fountain_and_use(self,char,x,y):
        x/=tile_size
        y/=tile_size
        x-=1
        y-=1
        for x_in in range(x,x+3):
            for y_in in range(y,y+3):
                self.check_for_fountain_and_use_exact(char,x_in,y_in)
    def check_for_fountain_and_use_exact(self,char,x,y):
        if self.map.tiles[x][y]=='F':
            self.map.tiles[x][y]='Q'
            self.fountain_effects(char)
        elif self.map.tiles[x][y]=='Q':
            char.handler.push_narration('You drink from the fountain, but the fountain is depleted and has no effect.')
    def check_for_shop_and_use(self,char,x,y):
        x/=tile_size
        y/=tile_size
        x-=1
        y-=1
        for x_in in range(x,x+3):
            for y_in in range(y,y+3):
                self.check_for_shop_and_use_exact(char,x_in,y_in)
    def check_for_shop_and_use_exact(self,char,x,y):
        if self.map.tiles[x][y]=='P':
            self.go_shopping(char)
    def go_shopping(self, char):
        SocketHandler.lock = True
        message = {"id": str(uuid.uuid4()), "message": "go_shopping"}
        char.handler.attempt_to_write_message(message)
        SocketHandler.lock = False
    def check_for_traps_and_spring(self,x,y,char):
        x/=tile_size
        y/=tile_size
        if self.map.tiles_trapped[x][y]:
            self.spring_trap(char,x,y)
    def spring_trap(self,char,x,y):
        trap = self.map.traps[(x,y)]
        if not trap['one_shot'] and trap['gcd']>0:
            trap['gcd'] -= 1
            return
        if trap['one_shot']:
            self.map.tiles_trapped[x][y] = False
            if self.map.tiles[x][y]=='T':
                self.map.tiles[x][y]=' '
        if trap['name'] not in ['fireball', 'arrow']:
            char.take_hit(trap['damage'])
            char.remove_stealth()
        self.floating_text.append(FloatingText(char.pos_x,char.pos_y,'TRAP','#FF0000'))
        if char.hp<=0:
            char.alive = False
        if trap['name']=='spike':
            char.handler.push_narration('You spring a spike trap! You take {0} points of damage.'.format(trap['damage']))
            self.make_noise(x*tile_size,y*tile_size,25)
        if trap['name']=='pit':
            char.handler.push_narration('You spring a pit trap! You take {0} points of damage.'.format(trap['damage']))
            trap['dest'] = self.get_pit_trap_dest()
            x,y = trap['dest']
            self.party_descends()
            for char in self.chars:
                char.pos_x = x
                char.pos_y = y
                self.check_char_start_pos(char)
        if trap['name']=='teleport':
            char.handler.push_narration('You spring a teleport trap!')
            trap['dest_floor'], trap['dest'] = self.get_teleport_trap_dest()
            x,y = trap['dest']
            if trap['dest_floor'] == self.floor-1:
                self.party_ascends()
            elif trap['dest_floor'] == self.floor+1:
                self.party_descends()
            for char in self.chars:
                char.pos_x = x
                char.pos_y = y
                self.check_char_start_pos(char)
        if trap['name']=='fireball':
            self.detonate_fireball_trap(x*tile_size,y*tile_size,tile_size*4, trap['damage'], trap)
            self.make_noise(x*tile_size,y*tile_size,25)
        if trap['name']=='arrow':
            self.spawn_arrow_trap(x,y, trap)
            self.make_noise(x*tile_size,y*tile_size,20)
        if trap['name']=='arrow_spread':
            self.spawn_arrow_spread_trap(x,y,trap)
            self.make_noise(x*tile_size,y*tile_size,20)
        if trap['name']=='lava':
            self.spawn_lava(x,y)
            self.make_noise(x*tile_size,y*tile_size,20)
    def detonate_fireball_trap(self, x, y, radius, damage, trap):
        left = x-radius
        right = x+tile_size+radius
        top = y-radius
        bottom = y+radius
        animation_text = str(left)+','+str(right)+','+str(top)+','+str(bottom)+','+'#FF0000'
        for handler in self.handlers:
            handler.animations.append(animation_text)
        for char in self.chars:
            if left <= char.pos_x and right >=char.pos_x+tile_size and top <= char.pos_y and bottom >= char.pos_y+tile_size:
                char.take_hit(damage)
        if 'gcd' in trap:
            trap['gcd'] = 90
    def spawn_arrow_trap(self, x, y, trap):
        if 'source_x' not in trap:
             direction = random.randint(0,3)
             table = [(0,1),(-1,0),(0,-1),(1,0)]
             move_x, move_y = table[direction]
             distance = 0
             while self.map.tiles[x+move_x][y+move_y]==' ':
                 x+= move_x
                 y+= move_y
                 distance += tile_size*2
             trap['source_x'] = (x*tile_size)+tile_size/2
             trap['source_y'] = (y*tile_size)+tile_size/2
             trap['source_direction'] = direction
             trap['source_distance'] = distance
        proj = Projectile(trap['source_x'], trap['source_y'],trap['source_direction'],4,1,trap['damage'],trap['source_distance'],None,color='brown')
        if 'gcd' in trap:
            trap['gcd'] = 90
        self.projectiles.append(proj)
    def spawn_arrow_spread_trap(self, x, y, trap):
        if 'source_x' not in trap:
             direction = random.randint(0,3)
             table = [(0,1),(-1,0),(0,-1),(1,0)]
             move_x, move_y = table[direction]
             distance = 0
             while self.map.tiles[x+move_x][y+move_y]==' ':
                 x+= move_x
                 y+= move_y
                 distance += tile_size*2
             trap['source_x'] = (x*tile_size)+tile_size/2
             trap['source_y'] = (y*tile_size)+tile_size/2
             trap['source_direction'] = direction
             trap['source_distance'] = distance
        move_x_table1 = [-1,2,-1,-2]
        move_x_table2 = [1,2,1,-2]
        move_y_table1 = [-2,-1,2,-1]
        move_y_table2 = [-2,1,2,1]
        move_x1 = move_x_table1[trap['source_direction']]
        move_y1 = move_y_table1[trap['source_direction']]
        move_x2 = move_x_table2[trap['source_direction']]
        move_y2 = move_y_table2[trap['source_direction']]
        proj = Projectile(trap['source_x'], trap['source_y'],trap['source_direction'],4,1,trap['damage'],trap['source_distance'],None,color='brown')
        self.projectiles.append(proj)
        proj = Projectile(trap['source_x'], trap['source_y'],4,4,1,trap['damage'],trap['source_distance']*2,None,color='brown', move_x = move_x1, move_y = move_y1)
        self.projectiles.append(proj)
        proj = Projectile(trap['source_x'], trap['source_y'],4,4,1,trap['damage'],trap['source_distance']*2,None,color='brown', move_x = move_x2, move_y = move_y2)
        self.projectiles.append(proj)
        if 'gcd' in trap:
            trap['gcd'] = 90
    def spawn_lava(self, x, y):
        min_x = max(x-4,2)
        max_x = min(x+4,len(self.map.tiles)-2)
        min_y = max(y-4,2)
        max_y = min(y+4,len(self.map.tiles[0])-2)
        for i in range(min_x,max_x):
            for j in range(min_y,max_y):
                if self.map.tiles[i][j]==' ':
                    self.map.tiles[i][j] = 'f'
    def get_pit_trap_dest(self):
        dest_floor = self.floor+1
        x = random.randint(1,(self.maps[dest_floor].size_x-(tile_size*2))/tile_size)*tile_size
        y = random.randint(1,(self.maps[dest_floor].size_y-(tile_size*2))/tile_size)*tile_size
        if self.maps[dest_floor].tiles[x/tile_size][y/tile_size]!=' ':
            return self.get_pit_trap_dest()
        return (x,y)
    def get_teleport_trap_dest(self):
        if self.map.height=='bottom':
            dest_floor = self.floor + random.randint(-1,0)
        elif self.map.height=='top':
            dest_floor = self.floor + random.randint(0,1)
        else:
            dest_floor = self.floor + random.randint(-1,1)
        x = random.randint(tile_size,((self.maps[dest_floor].size_x-(tile_size*2))/tile_size)*tile_size)
        y = random.randint(tile_size,((self.maps[dest_floor].size_y-(tile_size*2))/tile_size)*tile_size)
        if self.maps[dest_floor].tiles[x/tile_size][y/tile_size]!=' ':
            return self.get_teleport_trap_dest()
        return (dest_floor,(x,y))
    def fountain_effects(self,char):
        char.handler.push_narration('You drink from the fountain.')
        roll = random.randint(1,2)
        if roll==1:
            char.apply_debuff(1)
            char.handler.push_narration('You are poisoned!')
        elif roll==2:
            char.hp = char.max_hp
            char.handler.push_narration('You are fully healed!')
            self.floating_text.append(FloatingText(char.pos_x,char.pos_y,'FULLY HEALED','#00FF00'))
    def is_door(self,x,y):
        return self.is_door_exact(x,y) or self.is_door_exact(x+(tile_size-1),y) or self.is_door_exact(x,y+(tile_size-1)) or self.is_door_exact(x+(tile_size-1),y+(tile_size-1))
    def is_door_exact(self,x,y):
        if len(self.map.tiles)>x/tile_size:
            if len(self.map.tiles[x/tile_size])>y/tile_size:
                return (self.map.tiles[x/tile_size][y/tile_size] in ['D','S','R'])
    def check_for_chests_and_open(self,x,y):
        self.check_for_chests_and_open_exact(x,y)
        self.check_for_chests_and_open_exact(x+(tile_size-1),y)
        self.check_for_chests_and_open_exact(x,y+(tile_size-1))
        self.check_for_chests_and_open_exact(x+(tile_size-1),y+(tile_size-1))
    def check_for_chests_and_open_exact(self,x,y):
        if len(self.map.tiles)>x/tile_size:
            if len(self.map.tiles[x/tile_size])>y/tile_size:
                if self.map.tiles[x/tile_size][y/tile_size] in ['C','E']:
                    self.map.tiles[x/tile_size][y/tile_size]=' '
                    self.push_narration('A chest is opened.')
                    self.sounds.append('chain_complete')
                    self.chains[random.randint(0,2)]+=1
                    # for i in range(random.randint(1*self.player_strength,3*self.player_strength)):
                    #     self.drops.append(random_drop())
    def mob_data(self):
        # value = [{'uuid': 'abc', 'x': 1, 'y': 1}]
        value = []
        for mob in self.active_monsters:
            item = {}
            item['uuid'] = mob.uuid
            item['x'] = mob.pos_x
            item['y'] = mob.pos_y
            value.append(item)
        return value
    def make_noise(self, x, y, volume):
        for mob in self.monsters:
            distance = max(abs(mob.pos_x-x),abs(mob.pos_y-y))/tile_size
            if distance<=volume and volume-distance-mob.hearing>0:
                if len(mob.aggro) == 0:
                    mob.start_calculate_thread_for_sound(x,y)
    def release_scent(self, x, y):
        x/=tile_size
        y/=tile_size
        for scent in self.map.scents:
            if scent.pos_x==x and scent.pos_y==y:
                return
        self.map.scents.append(Scent(x,y,10))
    def disseminate_scents(self):
        cull_list = []
        for scent in self.map.scents:
            scent.radius += 1
            scent.intensity *= 0.8
            if scent.intensity <= 1:
                cull_list.append(scent)
        for scent in cull_list:
            self.map.scents.remove(scent)
        for scent in self.map.scents:
            for mob in self.monsters:
                distance = max(abs(mob.pos_x-(scent.pos_x*tile_size)),abs(mob.pos_y-(scent.pos_y*tile_size)))/tile_size
                if distance<=scent.radius and scent.intensity>=mob.sense_of_smell:
                    if len(mob.aggro) == 0:
                        mob.start_calculate_thread_for_sound(scent.pos_x*tile_size,scent.pos_y*tile_size)
    def save_game(self):
        saved_games = []
        if os.path.isfile('games.dat'):
            with open('games.dat', 'r') as savefile:
                data = tornado.escape.json_decode(savefile.read())
                saved_games = data
        for item in saved_games:
            if item['uuid']==self.uuid:
                saved_games.remove(item)
                break
        saved_games.append(self.to_save_data())
        with open('games.dat', 'w') as games:
            data = tornado.escape.json_encode(saved_games)
            games.write(data)

        saved_chars = []
        if os.path.isfile('characters.dat'):
            with open('characters.dat', 'r') as savefile:
                data = tornado.escape.json_decode(savefile.read())
                saved_chars = data
        for char in self.chars:
            owner = None
            for item in saved_chars:
                if item['uuid']==char.uuid:
                    owner = item['owner']
                    saved_chars.remove(item)
                    break
            data = char.to_save_data()
            if owner:
                data['owner'] = owner
            saved_chars.append(data)
        with open('characters.dat', 'w') as savefile:
            data = tornado.escape.json_encode(saved_chars)
            savefile.write(data)

    def to_save_data(self):
        data = {}
        data['name'] = self.name
        data['min_level'] = self.maps[0].level
        data['max_level'] = self.maps[len(self.maps)-1].level
        data['current_floor'] = self.floor+1
        data['floors'] = len(self.maps)
        data['enemies_defeated'] = self.enemies_defeated
        data['owners'] = self.owners
        data['players'] = []
        for handler in self.handlers:
            data['players'].append(handler.char.name)
        data['is_public'] = self.is_public
        data['unlock_points'] = self.unlock_points
        data['unlock_progress'] = self.unlock_progress
        data['drops'] = self.drops
        data['drop_depth'] = self.drop_depth
        data['drop_unlocked'] = self.drop_unlocked
        data['chains'] = self.chains
        data['bestiary'] = self.bestiary
        data['uuid'] = self.uuid
        data['last_tiles'] = self.last_tiles
        data['last_sight_change_map'] = self.last_sight_change_map
        data['final_sight'] = self.final_sight
        data['maps'] = []
        for map_obj in self.maps:
            data['maps'].append(map_obj.to_save_data())
        return data
def main():
    tornado.options.parse_command_line()
    logging.getLogger('tornado.access').disabled = True
    # app = Application()
    SETTINGS = {
    "debug" : True
    }
    application = tornado.web.Application([
        (r"/mainsocket", SocketHandler),
        (r"/loginsocket", LoginSocketHandler),
        (r'/(.*)', tornado.web.StaticFileHandler, {"path": "../web/", 'default_filename': 'index.html'})
    ],**SETTINGS)
    application.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.current().start()
if __name__ == "__main__":
    # g = Game()
    # for i in range(996):
        # m = Map(g,0)

    # reload(sys)
    # sys.setdefaultencoding('utf8')
    main()
    # try:
    #     cProfile.run('main()')
    # except KeyboardInterrupt:
    #     sys.exit()
