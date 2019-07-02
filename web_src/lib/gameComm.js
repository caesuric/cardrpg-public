import {guid, stripOutZeros} from 'utils'
import * as constants from 'cardrpgConstants'
import * as modalLaunchers from 'modalLaunchers'
import * as input from 'input'
import * as wireProcessor from 'wireProcessor'
import * as graphics from 'graphics'

export var updater = {
  socket: null,
  start: function() {
    updater.socket = new WebSocket(constants.url)
    updater.socket.onmessage = function(event) {
      try {
        updater.processMessage(JSON.parse(event.data))
      }
      catch (error) {
        console.log(error)
        // console.log(event.data)
      }
    }
    updater.socket.onopen = updater.initialize
    updater.socket.onclose = updater.close
    window.updater = this
  },
  close: function() {
    console.log('CONNECTION CLOSED')
    return setTimeout((function() {
      updater.socket = new WebSocket(constants.url)
      updater.socket.onmessage = function(event) {
        try {
          updater.processMessage(JSON.parse(event.data))
        } catch (error) {
          console.log(error)
          // console.log(event.data)
        }
      }
      updater.socket.onopen = updater.initialize
      updater.socket.onclose = updater.close
    }), 0.5 * 1000)
  },
  initialize: function() {
    updater.initVariables()
    var message = {}
    message.message = 'connect_to_session'
    message.character = localStorage.getItem('cardrpg_character')
    message.game = localStorage.getItem('cardrpg_game')
    updater.socket.send(JSON.stringify(message))
  },
  initVariables: function() {
    updater.initMiscVars()
  },
    initMiscVars: function() {
    updater.drawing = false
    updater.drops_length = 0
    updater.counter = 0
    updater.update_count_divisor = 0
    updater.background_counter = 0
    updater.background_count_divisor = 16
  },
  sendSimpleMessage: function(text) {
    var message
    message = {}
    message.message = text
    updater.socket.send(JSON.stringify(message))
  },
  processMessage: function(message) {
    if (message.update_background === true) {
      updater.background_counter = updater.background_count_divisor
    }
    if (message.message === 'narration') {
      updater.processNarrationMessage(message)
      return
    }
    if (message.message === 'push_class_select') {
      if (window.selectingClass === false) {
        updater.initClassSelectionMenu()
      }
      return
    }
    if (message.message === 'prune_deck') {
      if (window.pruningDeck === false) {
        modalControllers.initPruneDeckMenu(message)
      }
      return
    }
    if (message.message === 'cls') {
      updater.clearNarrationLog()
      return
    }
    if (message.message === 'initiate_trash') {
      modalLaunchers.initTrash(message)
      return
    }
    if (message.message === 'clear_map') {
      window.tiles = []
      for (var i = 0; i <= 63; i++) {
        var item = []
        for (var j = 0; j <= 63; j++) {
          item.push(null)
        }
        window.tiles.push(item)
      }
      window.sight = []
      for (var i = 0; i <= 63; i++) {
        var item = []
        for (var j = 0; j <= 63; j++) {
          item.push(null)
        }
        window.sight.push(item)
      }
      window.mapObjects = undefined
      window.animations = []
      window.floatingText = []
      return
    }
    if (message.message === 'go_shopping') {
      modalLaunchers.goShopping()
      return
    }
    if (message.message === 'deck_contents') {
      window.deck = message.items
      window.deckCounts = message.counts
      return
    }
    if (message.message === 'bestiary_contents') {
      window.bestiary = message.items
      return
    }
    if (message.message === 'return_to_login') {
      window.location.href = '/index.html'
      return
    }
    if (updater.drawing === true) {
      return
    }
    updater.drawing = true
    message = wireProcessor.unpackMessage(message)
    graphics.drawAll(message)
    input.processKeyPresses()
    updater.drawing = false
    updater.sendSimpleMessage('drew')
    if (updater.counter >= updater.update_count_divisor) {
      updater.counter -= updater.update_count_divisor
    }
    if (updater.update_count_divisor > 0) {
      updater.counter += 1
    }
    if (updater.background_counter >= updater.background_count_divisor) {
      updater.background_counter -= updater.background_count_divisor
    }
    if (updater.background_count_divisor > 0) {
      return updater.background_counter += 1
    }
  },
  processNarrationMessage: function(message) {
    var item = {}
    item.text = message.text
    window.narration.unshift(item)
  },
  clearNarrationLog: function() {
    window.narration = []
  },
  extractCharacterData: function(message) {
    var char_split = updater.extractCharacterDataSetUpRawData(message)
    var char_color, char_eye_color, char_facing, char_gcd, char_hp, char_max_hp, char_max_mp, char_mp, char_name, char_pos_x, char_pos_y, char_slot_1, char_slot_2, char_slot_3, char_slot_4, char_slot_5, char_slot_6
    [char_pos_x,char_pos_y,char_facing,char_hp,char_max_hp,char_mp,char_max_mp,char_slot_1,char_slot_2,char_slot_3,char_slot_4,char_slot_5,char_slot_6,char_gcd,char_color,char_eye_color,char_name] = updater.extractCharacterDataIndividualVars(char_split,parseInt(message.char_id))
    message = updater.addCharacterDataToMessage(message,char_pos_x,char_pos_y,char_facing,char_hp,char_max_hp,char_mp,char_max_mp,char_slot_1,char_slot_2,char_slot_3,char_slot_4,char_slot_5,char_slot_6,char_gcd,char_color,char_eye_color,char_name)
    return [message,char_pos_x,char_pos_y,char_facing,char_hp,char_max_hp,char_mp,char_max_mp,char_slot_1,char_slot_2,char_slot_3,char_slot_4,char_slot_5,char_slot_6,char_gcd,char_color,char_eye_color,char_name]
  },
  extractCharacterDataSetUpRawData: function(message) {
    var char_split = []
    for (let char of message.chars)
        char_split.push(char.split(','))
    return char_split
  },
  extractCharacterDataIndividualVars: function(char_split, char_id) {
    var char, char_color, char_eye_color, char_facing, char_gcd, char_hp, char_max_hp, char_max_mp, char_mp, char_name, char_pos_x, char_pos_y, char_slot_1, char_slot_2, char_slot_3, char_slot_4, char_slot_5, char_slot_6
    [char_pos_x,char_pos_y,char_facing,char_hp,char_max_hp,char_mp,char_max_mp,char_slot_1,char_slot_2,char_slot_3,char_slot_4,char_slot_5,char_slot_6,char_gcd,char_color,char_eye_color,char_name] = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    for (var i=0; i<char_split.length; i++) {
      char = char_split[i]
      if (i == char_id) {
        char_pos_x.push(char[0])
        char_pos_y.push(char[1])
        char_gcd.push(char[2]);
        [char_slot_1,char_slot_2,char_slot_3,char_slot_4,char_slot_5,char_slot_6] = updater.extractCharacterDataHotbarSlots(char,char_slot_1,char_slot_2,char_slot_3,char_slot_4,char_slot_5,char_slot_6,true)
        char_hp.push(char[9])
        char_max_hp.push(char[10])
        char_facing.push(char[11])
        char_mp.push(char[12])
        char_max_mp.push(char[13])
        char_color.push(char[14])
        char_eye_color.push(char[15])
        char_name.push(char[16])
      } else {
        char_pos_x.push(char[0])
        char_pos_y.push(char[1])
        char_gcd.push(None)
        [char_slot_1,char_slot_2,char_slot_3,char_slot_4,char_slot_5,char_slot_6] = updater.extractCharacterDataHotbarSlots(char,char_slot_1,char_slot_2,char_slot_3,char_slot_4,char_slot_5,char_slot_6,false)
        char_hp.push(char[2])
        char_max_hp.push(char[3])
        char_facing.push(char[4])
        char_mp.push(None)
        char_max_mp.push(None)
        char_color.push(char[5])
        char_eye_color.push(char[6])
        char_name.push(char[7])
      }
    }
    return [char_pos_x, char_pos_y, char_facing, char_hp, char_max_hp, char_mp, char_max_mp, char_slot_1, char_slot_2, char_slot_3, char_slot_4, char_slot_5, char_slot_6, char_gcd, char_color, char_eye_color, char_name]
  },
  extractCharacterDataHotbarSlots: function(char, char_slot_1, char_slot_2, char_slot_3, char_slot_4, char_slot_5, char_slot_6, isYou) {
    if (isYou) {
      char_slot_1.push(char[3])
      char_slot_2.push(char[4])
      char_slot_3.push(char[5])
      char_slot_4.push(char[6])
      char_slot_5.push(char[7])
      char_slot_6.push(char[8])
    } else {
      char_slot_1.push(null)
      char_slot_2.push(null)
      char_slot_3.push(null)
      char_slot_4.push(null)
      char_slot_5.push(null)
      char_slot_6.push(null)
    }
    return [char_slot_1, char_slot_2, char_slot_3, char_slot_4, char_slot_5, char_slot_6]
  },
  addCharacterDataToMessage: function(message, char_pos_x, char_pos_y, char_facing, char_hp, char_max_hp, char_mp, char_max_mp, char_slot_1, char_slot_2, char_slot_3, char_slot_4, char_slot_5, char_slot_6, char_gcd, char_color, char_eye_color, char_name) {
    message.char_pos_x = char_pos_x[message.char_id]
    message.char_pos_y = char_pos_y[message.char_id]
    message.gcd = char_gcd[message.char_id]
    message.hp = char_hp[message.char_id]
    message.max_hp = char_max_hp[message.char_id]
    message.mp = char_mp[message.char_id]
    message.max_mp = char_max_mp[message.char_id]
    message.char_facing = char_facing[message.char_id]
    message.char_color = char_color[message.char_id]
    message.char_eye_color = char_eye_color[message.char_id]
    message.char_name = char_name[message.char_id]
    updater.addCharacterHotbarDataToMessage(message, char_slot_1, char_slot_2, char_slot_3, char_slot_4, char_slot_5, char_slot_6)
    return message
  },
  addCharacterHotbarDataToMessage: function(message, char_slot_1, char_slot_2, char_slot_3, char_slot_4, char_slot_5, char_slot_6) {
    message.slot1 = char_slot_1[message.char_id]
    message.slot2 = char_slot_2[message.char_id]
    message.slot3 = char_slot_3[message.char_id]
    message.slot4 = char_slot_4[message.char_id]
    message.slot5 = char_slot_5[message.char_id]
    message.slot6 = char_slot_6[message.char_id]
    return message
  },
  extractTileData: function(message) {
    if (!window.tiles) {
      window.tiles = []
    }
    if (!window.mapObjects) {
      window.mapObjects = []
    }
    if (message.tiles) {
      var i = 0
      while (i < message.tiles.length) {
        var x = message.tiles[i]
        var y = message.tiles[i + 1]
        var value = message.tiles[i + 2]
        if (!window.tiles[x]) {
          window.tiles[x] = []
        }
        if (!window.mapObjects[x]) {
          window.mapObjects[x] = []
        }
        if (window.tiles[x][y] != value) {
          window.mapObjects[x][y] = undefined
        }
        window.tiles[x][y] = value
        i += 3
      }
    }
    message.tiles = window.tiles
    if (!window.sight) {
      window.sight = []
    }
    if (message.sight) {
      var i = 0
      while (i < message.sight.length) {
        var x = message.sight[i]
        var y = message.sight[i + 1]
        var value = message.sight[i + 2]
        if (!window.sight[x]) {
          window.sight[x] = []
        }
        window.sight[x][y] = value
        i += 3
      }
    }
    return message
  },
  addToDetailedMobData: function(mobClass, name, level) {
    if (mobClass != undefined && name != undefined && level != undefined) {
      var mob = {}
      mob.mobClass = constants.mobClassDescriptions[mobClass]
      mob.name = name
      mob.level = level
      window.detailedMobData.push(mob)
    }
  }
}
