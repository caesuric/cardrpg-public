import {Base64Binary} from 'base64-binary'
import {jspack} from 'jspack'
import * as utils from 'utils'

export function unpackMessage(message) {
  var binary = Base64Binary.decode(message.u)
  var initialFormat = '!15shiihhfiiLhL15scch8s30shc'
  var mainData = jspack.Unpack(initialFormat, binary, 0)
  var message = {}
  var length = jspack.Unpack('!I', binary, jspack.CalcLength(initialFormat))
  var projectiles = []
  var offset = jspack.CalcLength(initialFormat) + jspack.CalcLength('I')
  if (length > 0) {
    for (var i = 0; i<length; i++) {
      projectiles[i] = jspack.Unpack('!II7s', binary, offset)
      projectiles[i] = projectiles[i].join(',')
      offset += jspack.CalcLength('II7s')
    }
  }
  message.projectiles = projectiles
  length = jspack.Unpack('!I', binary, offset)[0]
  var monsters = []
  offset += jspack.CalcLength('I')
  if (length > 0) {
    for (var i = 0; i<length; i++) {
      monsters[i] = jspack.Unpack('!IIHh15sH', binary, offset)
      monsters[i] = monsters[i].join(',')
      offset += jspack.CalcLength('IIHh15sH')
    }
  }
  message.monsters = monsters
  length = jspack.Unpack('!I', binary, offset)[0]
  var tiles = []
  offset += jspack.CalcLength('I')
  if (length > 0) {
    for (var i=0; i<length; i++) {
      var items = jspack.Unpack('!IIc', binary, offset)
      for (let item of items) {
        tiles.push(item)
      }
      offset += jspack.CalcLength('IIc')
    }
  }
  message.tiles = tiles
  length = jspack.Unpack('!I', binary, offset)[0]
  var sight = []
  offset += jspack.CalcLength('I')
  if (length > 0) {
    for (var i=0; i<length; i++) {
      var items = jspack.Unpack('!IIc', binary, offset)
      for (let item of items) {
        if (item === 'T') {
          sight.push(true)
        } else if (item === 'F') {
          sight.push(false)
        } else {
          sight.push(item)
        }
      }
      offset += jspack.CalcLength('IIc')
    }
  }
  message.sight = sight
  length = jspack.Unpack('!I', binary, offset)[0]
  var effects = []
  offset += jspack.CalcLength('I')
  if (length > 0) {
    for (var i=0; i<length; i++) {
      effects[i] = jspack.Unpack('!H', binary, offset)
      offset += jspack.CalcLength('H')
    }
  }
  message.effects = effects
  length = jspack.Unpack('!I', binary, offset)[0]
  var effects_duration = []
  offset += jspack.CalcLength('I')
  if (length > 0) {
    for (var i=0; i<length; i++) {
      effects_duration[i] = jspack.Unpack('!I', binary, offset)
      offset += jspack.CalcLength('I')
    }
  }
  message.effects_duration = effects_duration
  length = jspack.Unpack('!I', binary, offset)[0]
  var effects_max_duration = []
  offset += jspack.CalcLength('I')
  if (length > 0) {
    for (var i=0; i<length; i++) {
      effects_max_duration[i] = jspack.Unpack('!I', binary, offset)
      offset += jspack.CalcLength('I')
    }
  }
  message.effects_max_duration = effects_max_duration
  var temp = jspack.Unpack('!I', binary, offset)
  if (temp) {
    length = temp[0]
  }
  var sounds = []
  offset += jspack.CalcLength('I')
  if (length > 0) {
    for (var i=0; i<length; i++) {
      var placeholder = jspack.Unpack('15s', binary, offset)
      if (placeholder) {
        sounds[i] = placeholder[0]
      }
      offset += jspack.CalcLength('15s')
    }
  }
  message.sounds = sounds
  length = jspack.Unpack('!I', binary, offset)[0]
  var animations = []
  offset += jspack.CalcLength('I')
  if (length > 0) {
    for (var i=0; i<length; i++) {
      animations[i] = jspack.Unpack('!IIII7s', binary, offset)
      animations[i] = animations[i].join(',')
      offset += jspack.CalcLength('!IIII7s')
    }
  }
  message.animations = animations
  length = jspack.Unpack('!I', binary, offset)[0]
  var floating_text = []
  offset += jspack.CalcLength('I')
  if (length > 0) {
    for (var i=0; i<length; i++) {
      floating_text[i] = jspack.Unpack('!II15s7s', binary, offset)
      floating_text[i] = floating_text[i].join(',')
      offset += jspack.CalcLength('!II15s7s')
    }
  }
  message.floating_text = floating_text
  length = jspack.Unpack('!I', binary, offset)[0]
  var chars = []
  offset += jspack.CalcLength('I')
  if (length > 0) {
    for (var i=0; i<length; i++) {
      var flags = jspack.Unpack('cc', binary, offset)
      offset += jspack.CalcLength('cc')
      var char_format
      if (flags[0] === 'F' && flags[1] === 'F') {
        char_format = '!IIHIIIIIIIIHII'
      } else if (flags[0] === 'F' && flags[1] === 'T') {
        char_format = '!IIHIIIIIIIIHII7s7s15s'
      } else if (flags[0] === 'T' && flags[1] === 'F') {
        char_format = '!IIIIH'
      } else if (flags[0] === 'T' && flags[1] === 'T') {
        char_format = '!IIIIH7s7s15s'
      } else {
        break
      }
      chars[i] = jspack.Unpack(char_format, binary, offset)
      chars[i] = chars[i].join(',')
      offset += jspack.CalcLength(char_format)
    }
  }
  message.chars = chars
  var drops_added = jspack.Unpack('c', binary, offset)[0]
  if (drops_added === 'T') {
    message.drops_added = true
  } else {
    message.drops_added = false
  }
  offset += jspack.CalcLength('c')
  if (drops_added === 'T') {
    length = jspack.Unpack('!I', binary, offset)[0]
    var drops = []
    offset += jspack.CalcLength('I')
    if (length > 0) {
      for (var i=0; i<length; i++) {
        drops[i] = jspack.Unpack('!I', binary, offset)[0]
        offset += jspack.CalcLength('!I')
      }
    }
    message.drops = drops
    length = jspack.Unpack('!I', binary, offset)[0]
    var drop_depth = []
    offset += jspack.CalcLength('I')
    if (length > 0) {
      for (var i=0; i<length; i++) {
        drop_depth[i] = jspack.Unpack('!I', binary, offset)[0]
        offset += jspack.CalcLength('!I')
      }
    }
    message.drop_depth = drop_depth
    length = jspack.Unpack('!I', binary, offset)[0]
    var drop_unlocked = []
    offset += jspack.CalcLength('I')
    if (length > 0) {
      for (var i=0; i<length; i++) {
        var value = jspack.Unpack('c', binary, offset)[0]
        if (value === 'T') {
          drop_unlocked[i] = true
        } else {
          drop_unlocked[i] = false
        }
        offset += jspack.CalcLength('c')
      }
    }
    message.drop_unlocked = drop_unlocked
  }
  message.message = 'update'
  message.target = mainData[0]
  message.friendly_target = mainData[1]
  message.target_hp = mainData[2]
  message.target_max_hp = mainData[3]
  message.char_id = mainData[4]
  message.unlock_points = mainData[5]
  message.unlock_progress = mainData[6]
  message.target_class = mainData[7]
  message.target_level = mainData[8]
  message.total_xp = mainData[9]
  message.level = mainData[10]
  message.next_level_xp = mainData[11]
  message.target_name = utils.stripOutZeros(mainData[12])
  if (mainData[13] === 'T') {
    message.paralyzed = true
  } else {
    message.paralyzed = false
  }
  if (mainData[14] === 'T') {
    message.won = true
  } else {
    message.won = false
  }
  message.current_chain = mainData[15]
  message.chain_timer = parseFloat(mainData[16])
  message.chains = utils.stripOutZeros(mainData[17])
  message.floor = mainData[18]
  if (mainData[19] === 'T') {
    message.update_background = true
  } else {
    message.update_background = false
  }
  return message
}
