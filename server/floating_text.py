import struct

class FloatingText(object):
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
    def to_JSON(self):
        return '{0},{1},{2},{3}'.format(self.x,self.y,self.text,self.color)
    def to_binary(self):
        return struct.pack('!II15s7s',self.x,self.y,self.text,self.color)
