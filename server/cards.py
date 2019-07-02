import random

class Card (object):
    def __init__(self,type,temp=False):
        self.type = type
        self.counters = 0
        self.temp = temp
        table = [0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,2,2,2,2,2,3,3,3,3,3,4,4,4,4,4,5,5,5,5,5,6,6,6,7,7,8,2,1,2,3,4,5,1,2,3,4,0,0,0,3,7]
        self.cost = table[type]
    def to_JSON(self):
        return '{0},{1}'.format(self.type,self.counters)
class Deck (object):
    @staticmethod
    def from_save_data(data):
        deck = Deck()
        deck.draw_pile = []
        deck.discard_pile = []
        deck.hand = []
        deck.in_play = []
        for item in data['draw_pile']:
            type, temp = item
            deck.draw_pile.append(Card(type,temp=temp))
        for item in data['discard_pile']:
            type, temp = item
            deck.discard_pile.append(Card(type,temp=temp))
        for item in data['hand']:
            type, temp = item
            deck.hand.append(Card(type,temp=temp))
        for item in data['in_play']:
            type, temp = item
            deck.in_play.append(Card(type,temp=temp))
        return deck
    def __init__(self,class_name='Archer'):
        self.max_cards = 12
        self.draw_pile = []
        archer_deck = [Card(0),Card(0),Card(0),Card(0),Card(0),Card(0),Card(0),Card(0),Card(0),Card(1),Card(1),Card(1)]
        inferno_mage_deck = [Card(2),Card(2),Card(2),Card(2),Card(2),Card(2),Card(2),Card(2),Card(3),Card(3),Card(3),Card(3)]
        balance_mage_deck = [Card(4),Card(4),Card(4),Card(4),Card(4),Card(4),Card(4),Card(4),Card(4),Card(5),Card(5),Card(5)]
        paladin_deck = [Card(6),Card(6),Card(6),Card(6),Card(6),Card(6),Card(7),Card(7),Card(7),Card(7),Card(7),Card(7)]
        fighter_deck = [Card(8),Card(8),Card(8),Card(8),Card(8),Card(8),Card(9),Card(9),Card(9),Card(9),Card(9),Card(9)]
        cleric_deck = [Card(8),Card(8),Card(8),Card(8),Card(8),Card(8),Card(8),Card(8),Card(8),Card(10),Card(10),Card(10)]
        table = {'Archer':archer_deck,'Inferno Mage':inferno_mage_deck,'Balance Mage':balance_mage_deck,'Paladin':paladin_deck,'Fighter':fighter_deck,'Cleric':cleric_deck}
        self.discard_pile = table[class_name]
        self.hand = [None,None,None,None,None,None]
        self.in_play = []
        self.initial_draw()
    def initial_draw(self):
        for i in range(6):
            self.draw(i)
    def draw(self,slot):
        if self.hand[slot]:
            return
        if not self.draw_pile:
            self.draw_pile = self.discard_pile
            self.discard_pile = []
            random.shuffle(self.draw_pile)
        if self.draw_pile:
            self.hand[slot] = self.draw_pile.pop()
    def count_permanent_cards(self):
        count = 0
        for card in self.draw_pile:
            count+=self.count_if_permanent(card)
        for card in self.discard_pile:
            count+=self.count_if_permanent(card)
        for card in self.hand:
            count+=self.count_if_permanent(card)
        for card in self.in_play:
            count+=self.count_if_permanent(card)
        return count
    def count_if_permanent(self,card):
        if not card.temp:
            return 1
        return 0
    def count_temp_cards(self):
        count = 0
        for card in self.draw_pile:
            count+=self.count_if_temp(card)
        for card in self.discard_pile:
            count+=self.count_if_temp(card)
        for card in self.hand:
            count+=self.count_if_temp(card)
        for card in self.in_play:
            count+=self.count_if_temp(card)
        return count
    def count_if_temp(self,card):
        if card.temp:
            return 1
        return 0
    def add_cards_from_table(self,table):
        for i in range(len(table)):
            if table[i]:
                for j in range(int(table[i])):
                    self.discard_pile.append(Card(i))
    def to_save_data(self):
        data = {}
        data['draw_pile'] = []
        data['discard_pile'] = []
        data['hand'] = []
        data['in_play'] = []
        for item in self.draw_pile:
            data['draw_pile'].append((item.type, item.temp))
        for item in self.discard_pile:
            data['discard_pile'].append((item.type, item.temp))
        for item in self.hand:
            data['hand'].append((item.type, item.temp))
        for item in self.in_play:
            data['in_play'].append((item.type, item.temp))
        return data
