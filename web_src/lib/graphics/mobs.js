import * as constants from 'cardrpgConstants'

export function drawMobs (message) {
  window.detailedMobData = []
  var mob_split, mob_pos_x, mob_pos_y, mob_facing, mob_class, mob_name, mob_level
  [mob_split, mob_pos_x, mob_pos_y, mob_facing, mob_class, mob_name, mob_level] = extractMobData(message)
  if (window.elementsDrawn == undefined) {
    return [mob_pos_x, mob_pos_y, mob_class, mob_name]
  }
  for (var i=0; i<mob_split.length; i++) {
    if (mob_name[i] === 'Mimic') {
      var brown = 'brown'
      var yellow = 'yellow'
      window.canvas.add(new fabric.Rect({
        left: mob_pos_x[i] - parseInt(message.char_pos_x) + (window.view_x / 2),
        top: mob_pos_y[i] - parseInt(message.char_pos_y) + (window.view_y / 2),
        height: window.tileSize - 1,
        width: window.tileSize - 1,
        stroke: yellow,
        fill: brown,
        strokeWidth: 2,
        selectable: false
      }))
      window.elementsDrawn.chest = true
      continue
    }
    var color = constants.mobColors[mob_name[i]]
    var eye_color = determineEyeColor(mob_name, i)
    window.canvas.add(new fabric.Rect({
      left: mob_pos_x[i] - parseInt(message.char_pos_x) + (window.view_x / 2),
      top: mob_pos_y[i] - parseInt(message.char_pos_y) + (window.view_y / 2),
      height: window.tileSize,
      width: window.tileSize,
      stroke: color,
      fill: color,
      strokeWidth: 2,
      selectable: false
    }))
    if (mobDrawEyes[mob_facing[i]] != undefined) {
      mobDrawEyes[mob_facing[i]](mob_pos_x, mob_pos_y, eye_color, i, message)
    }
    if (window.elementsDrawn.mobs.indexOf(mob_name[i]) === -1) {
      window.elementsDrawn.mobs.push(mob_name[i])
    }
    updater.addToDetailedMobData(mob_class[i], mob_name[i], mob_level[i])
  }
  return [mob_pos_x, mob_pos_y, mob_class, mob_name]
}

function extractMobData(message) {
  var mob_split, mob_pos_x, mob_pos_y, mob_facing, mob_class, mob_name, mob_level
  [mob_split,mob_pos_x,mob_pos_y,mob_facing,mob_class,mob_name,mob_level] = [[],[],[],[],[],[],[]]
  for (let mob of message.monsters) {
    mob_split.push(mob.split(','))
  }
  for (let mob of mob_split) {
    mob_pos_x.push(parseInt(mob[0]))
    mob_pos_y.push(parseInt(mob[1]))
    mob_facing.push(parseInt(mob[2]))
    mob_class.push(parseInt(mob[3]))
    mob_name.push(mob[4].replace(/\0/g, ''))
    mob_level.push(mob[5])
  }
  return [mob_split, mob_pos_x, mob_pos_y, mob_facing, mob_class, mob_name, mob_level]
}

function mobDrawEyesUp (mob_pos_x, mob_pos_y, eye_color, i, message) {
  window.canvas.add(new fabric.Circle({
    left: mob_pos_x[i] - parseInt(message.char_pos_x) + (window.view_x / 2),
    top: mob_pos_y[i] - parseInt(message.char_pos_y) + (window.view_y / 2),
    radius: window.tileSize * 0.09375,
    stroke: eye_color,
    fill: eye_color,
    strokeWidth: 2,
    selectable: false
  }))
  window.canvas.add(new fabric.Circle({
    left: mob_pos_x[i] - parseInt(message.char_pos_x) + (window.view_x / 2) + window.tileSize - (window.tileSize * 0.1875),
    top: mob_pos_y[i] - parseInt(message.char_pos_y) + (window.view_y / 2),
    radius: window.tileSize * 0.09375,
    stroke: eye_color,
    fill: eye_color,
    strokeWidth: 2,
    selectable: false
  }))
}
function mobDrawEyesRight (mob_pos_x, mob_pos_y, eye_color, i, message) {
  window.canvas.add(new fabric.Circle({
    left: mob_pos_x[i] - parseInt(message.char_pos_x) + (window.view_x / 2) + window.tileSize - (window.tileSize * 0.1875),
    top: mob_pos_y[i] - parseInt(message.char_pos_y) + (window.view_y / 2) + window.tileSize - (window.tileSize * 0.1875),
    radius: window.tileSize * 0.09375,
    stroke: eye_color,
    fill: eye_color,
    strokeWidth: 2,
    selectable: false
  }))
  window.canvas.add(new fabric.Circle({
    left: mob_pos_x[i] - parseInt(message.char_pos_x) + (window.view_x / 2) + window.tileSize - (window.tileSize * 0.1875),
    top: mob_pos_y[i] - parseInt(message.char_pos_y) + (window.view_y / 2),
    radius: window.tileSize * 0.09375,
    stroke: eye_color,
    fill: eye_color,
    strokeWidth: 2,
    selectable: false
  }))
}
function mobDrawEyesDown (mob_pos_x, mob_pos_y, eye_color, i, message) {
  window.canvas.add(new fabric.Circle({
    left: mob_pos_x[i] - parseInt(message.char_pos_x) + (window.view_x / 2),
    top: mob_pos_y[i] - parseInt(message.char_pos_y) + (window.view_y / 2) + window.tileSize - (window.tileSize * 0.1875),
    radius: window.tileSize * 0.09375,
    stroke: eye_color,
    fill: eye_color,
    strokeWidth: 2,
    selectable: false
  }))
  window.canvas.add(new fabric.Circle({
    left: mob_pos_x[i] - parseInt(message.char_pos_x) + (window.view_x / 2) + window.tileSize - (window.tileSize * 0.1875),
    top: mob_pos_y[i] - parseInt(message.char_pos_y) + (window.view_y / 2) + window.tileSize - (window.tileSize * 0.1875),
    radius: window.tileSize * 0.09375,
    stroke: eye_color,
    fill: eye_color,
    strokeWidth: 2,
    selectable: false
  }))
}
function mobDrawEyesLeft (mob_pos_x, mob_pos_y, eye_color, i, message) {
  window.canvas.add(new fabric.Circle({
    left: mob_pos_x[i] - parseInt(message.char_pos_x) + (window.view_x / 2),
    top: mob_pos_y[i] - parseInt(message.char_pos_y) + (window.view_y / 2),
    radius: window.tileSize * 0.09375,
    stroke: eye_color,
    fill: eye_color,
    strokeWidth: 2,
    selectable: false
  }))
  window.canvas.add(new fabric.Circle({
    left: mob_pos_x[i] - parseInt(message.char_pos_x) + (window.view_x / 2),
    top: mob_pos_y[i] - parseInt(message.char_pos_y) + (window.view_y / 2) + window.tileSize - (window.tileSize * 0.1875),
    radius: window.tileSize * 0.09375,
    stroke: eye_color,
    fill: eye_color,
    strokeWidth: 2,
    selectable: false
  }))
}

function determineEyeColor (mob_name, i) {
  if (constants.mobEyeColors[mob_name[i]] == undefined) {
    return 'yellow'
  } else {
    return constants.mobEyeColors[mob_name[i]]
  }
}

var mobDrawEyes = {
  0: mobDrawEyesUp,
  1: mobDrawEyesRight,
  2: mobDrawEyesDown,
  3: mobDrawEyesLeft
}
