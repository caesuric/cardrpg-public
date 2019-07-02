import * as constants from 'cardrpgConstants'

export function drawVisualKey (char_pos_x, char_pos_y) {
  var text
  if (window.elementsDrawn == undefined) {
    return
  }
  var x = window.view_x - 256 - 100
  var y = 0
  if (window.elementsDrawn.mobs.indexOf('Animated Statue') !== -1) {
    window.elementsDrawn.statue = true
  }
  if (window.elementsDrawn.mobs.indexOf('Mimic') !== -1) {
    window.elementsDrawn.statue = true
  }
  if (window.elementsDrawn.trappedDoor) {
    window.elementsDrawn.door = true
    window.elementsDrawn.trap = true
  }
  if (window.elementsDrawn.trappedChest) {
    window.elementsDrawn.chest = true
    window.elementsDrawn.trap = true
  }
  if (window.elementsDrawn.wall) {
    window.canvas.add(new fabric.Rect({
      left: x,
      top: 200 + (y * window.tileSize),
      height: window.tileSize,
      width: window.tileSize,
      stroke: 'gray',
      fill: 'gray',
      strokeWidth: 2,
      selectable: false
    }))
    text = ' = ' + constants.hoverDescriptions['W']
    window.canvas.add(new fabric.Text(text, {
      left: x + window.tileSize,
      top: 200 + (y * window.tileSize) + (window.tileSize / 2),
      originY: 'center',
      width: 256 - window.tileSize,
      height: window.tileSize,
      fontSize: 16,
      fill: 'white',
      strokeWidth: 2,
      selectable: false
    }))
    y += 1
  }
  if (window.elementsDrawn.door) {
    window.canvas.add(new fabric.Rect({
      left: x,
      top: 200 + (y * window.tileSize),
      height: window.tileSize,
      width: window.tileSize,
      stroke: 'brown',
      fill: 'brown',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Circle({
      left: x + (window.tileSize / 4),
      top: 200 + (y * window.tileSize) + (window.tileSize / 4),
      radius: window.tileSize / 4,
      stroke: 'yellow',
      fill: 'yellow',
      strokeWidth: 2,
      selectable: false
    }))
    text = ' = ' + constants.hoverDescriptions['D']
    window.canvas.add(new fabric.Text(text, {
      left: x + window.tileSize,
      top: 200 + (y * window.tileSize) + (window.tileSize / 2),
      originY: 'center',
      width: 256 - window.tileSize,
      height: window.tileSize,
      fontSize: 16,
      fill: 'white',
      strokeWidth: 2,
      selectable: false
    }))
    y += 1
  }
  if (window.elementsDrawn.chest) {
    window.canvas.add(new fabric.Rect({
      left: x,
      top: 200 + (y * window.tileSize),
      height: window.tileSize,
      width: window.tileSize,
      stroke: 'yellow',
      fill: 'brown',
      strokeWidth: 2,
      selectable: false
    }))
    text = ' = ' + constants.hoverDescriptions['C']
    window.canvas.add(new fabric.Text(text, {
      left: x + window.tileSize,
      top: 200 + (y * window.tileSize) + (window.tileSize / 2),
      originY: 'center',
      width: 256 - window.tileSize,
      height: window.tileSize,
      fontSize: 16,
      fill: 'white',
      strokeWidth: 2,
      selectable: false
    }))
    y += 1
  }
  if (window.elementsDrawn.stairsDown) {
    window.canvas.add(new fabric.Rect({
      left: x,
      top: 200 + (y * window.tileSize),
      height: window.tileSize,
      width: window.tileSize,
      stroke: 'white',
      fill: 'black',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Text('>', {
      left: x + (window.tileSize / 2),
      top: 200 + (y * window.tileSize) + (window.tileSize / 2),
      originX: 'center',
      originY: 'center',
      fill: 'white',
      fontSize: 16,
      selectable: false
    }))
    text = ' = ' + constants.hoverDescriptions['>']
    window.canvas.add(new fabric.Text(text, {
      left: x + window.tileSize,
      top: 200 + (y * window.tileSize) + (window.tileSize / 2),
      originY: 'center',
      width: 256 - window.tileSize,
      height: window.tileSize,
      fontSize: 16,
      fill: 'white',
      strokeWidth: 2,
      selectable: false
    }))
    y += 1
  }
  if (window.elementsDrawn.stairsUp) {
    window.canvas.add(new fabric.Rect({
      left: x,
      top: 200 + (y * window.tileSize),
      height: window.tileSize,
      width: window.tileSize,
      stroke: 'white',
      fill: 'black',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Text('<', {
      left: x + (window.tileSize / 2),
      top: 200 + (y * window.tileSize) + (window.tileSize / 2),
      originX: 'center',
      originY: 'center',
      fill: 'white',
      fontSize: 16,
      selectable: false
    }))
    text = ' = ' + constants.hoverDescriptions['<']
    window.canvas.add(new fabric.Text(text, {
      left: x + window.tileSize,
      top: 200 + (y * window.tileSize) + (window.tileSize / 2),
      originY: 'center',
      width: 256 - window.tileSize,
      height: window.tileSize,
      fontSize: 16,
      fill: 'white',
      strokeWidth: 2,
      selectable: false
    }))
    y += 1
  }
  if (window.elementsDrawn.fire) {
    window.canvas.add(new fabric.Rect({
      left: x,
      top: 200 + (y * window.tileSize),
      height: window.tileSize,
      width: window.tileSize,
      stroke: 'red',
      fill: 'red',
      strokeWidth: 2,
      selectable: false
    }))
    text = ' = ' + constants.hoverDescriptions['f']
    window.canvas.add(new fabric.Text(text, {
      left: x + window.tileSize,
      top: 200 + (y * window.tileSize) + (window.tileSize / 2),
      originY: 'center',
      width: 256 - window.tileSize,
      height: window.tileSize,
      fontSize: 16,
      fill: 'white',
      strokeWidth: 2,
      selectable: false
    }))
    y += 1
  }
  if (window.elementsDrawn.acid) {
    window.canvas.add(new fabric.Rect({
      left: x,
      top: 200 + (y * window.tileSize),
      height: window.tileSize,
      width: window.tileSize,
      stroke: 'green',
      fill: 'green',
      strokeWidth: 2,
      selectable: false
    }))
    text = ' = ' + constants.hoverDescriptions['a']
    window.canvas.add(new fabric.Text(text, {
      left: x + window.tileSize,
      top: 200 + (y * window.tileSize) + (window.tileSize / 2),
      originY: 'center',
      width: 256 - window.tileSize,
      height: window.tileSize,
      fontSize: 16,
      fill: 'white',
      strokeWidth: 2,
      selectable: false
    }))
    y += 1
  }
  if (window.elementsDrawn.statue) {
    window.canvas.add(new fabric.Rect({
      left: x,
      top: 200 + (y * window.tileSize),
      height: window.tileSize,
      width: window.tileSize,
      stroke: 'gray',
      fill: 'gray',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Circle({
      left: x,
      top: 200 + (y * window.tileSize) + window.tileSize - (window.tileSize * 0.1875),
      radius: window.tileSize * 0.09375,
      stroke: 'yellow',
      fill: 'yellow',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Circle({
      left: x + window.tileSize - (window.tileSize * 0.1875),
      top: 200 + (y * window.tileSize) + window.tileSize - (window.tileSize * 0.1875),
      radius: window.tileSize * 0.09375,
      stroke: 'yellow',
      fill: 'yellow',
      strokeWidth: 2,
      selectable: false
    }))
    text = ' = ' + constants.hoverDescriptions['@']
    window.canvas.add(new fabric.Text(text, {
      left: x + window.tileSize,
      top: 200 + (y * window.tileSize) + (window.tileSize / 2),
      originY: 'center',
      width: 256 - window.tileSize,
      height: window.tileSize,
      fontSize: 16,
      fill: 'white',
      strokeWidth: 2,
      selectable: false
    }))
    y += 1
  }
  if (window.elementsDrawn.fountain) {
    window.canvas.add(new fabric.Rect({
      left: x,
      top: 200 + (y * window.tileSize),
      height: window.tileSize,
      width: window.tileSize,
      stroke: 'gray',
      fill: 'gray',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Circle({
      left: x,
      top: 200 + (y * window.tileSize),
      radius: window.tileSize / 2,
      stroke: 'blue',
      fill: 'blue',
      strokeWidth: 2,
      selectable: false
    }))
    text = ' = ' + constants.hoverDescriptions['F']
    window.canvas.add(new fabric.Text(text, {
      left: x + window.tileSize,
      top: 200 + (y * window.tileSize) + (window.tileSize / 2),
      originY: 'center',
      width: 256 - window.tileSize,
      height: window.tileSize,
      fontSize: 16,
      fill: 'white',
      strokeWidth: 2,
      selectable: false
    }))
    y += 1
  }
  if (window.elementsDrawn.shop) {
    window.canvas.add(new fabric.Text('$', {
      left: x + (window.tileSize / 2),
      top: 200 + (y * window.tileSize) + (window.tileSize / 2),
      originX: 'center',
      originY: 'center',
      fontSize: 24,
      fill: 'green',
      selectable: false
    }))
    text = ' = ' + constants.hoverDescriptions['P']
    window.canvas.add(new fabric.Text(text, {
      left: x + window.tileSize,
      top: 200 + (y * window.tileSize) + (window.tileSize / 2),
      originY: 'center',
      width: 256 - window.tileSize,
      height: window.tileSize,
      fontSize: 16,
      fill: 'white',
      strokeWidth: 2,
      selectable: false
    }))
    y += 1
  }
  if (window.elementsDrawn.trap) {
    window.canvas.add(new fabric.Text('T', {
      left: x + (window.tileSize / 2),
      top: 200 + (y * window.tileSize) + (window.tileSize / 2),
      originX: 'center',
      originY: 'center',
      fill: 'white',
      fontSize: 16,
      selectable: false
    }))
    text = ' = ' + constants.hoverDescriptions['T']
    window.canvas.add(new fabric.Text(text, {
      left: x + window.tileSize,
      top: 200 + (y * window.tileSize) + (window.tileSize / 2),
      originY: 'center',
      width: 256 - window.tileSize,
      height: window.tileSize,
      fontSize: 16,
      fill: 'white',
      strokeWidth: 2,
      selectable: false
    }))
    y += 1
  }
  if (window.elementsDrawn.projectile) {
    window.canvas.add(new fabric.Circle({
      left: x + (window.tileSize / 2),
      top: 200 + (y * window.tileSize) + (window.tileSize / 2),
      radius: 6,
      stroke: 'white',
      fill: 'white',
      originX: 'center',
      originY: 'center',
      strokeWidth: 2,
      selectable: false
    }))
    text = ' = A projectile.'
    window.canvas.add(new fabric.Text(text, {
      left: x + window.tileSize,
      top: 200 + (y * window.tileSize) + (window.tileSize / 2),
      originY: 'center',
      width: 256 - window.tileSize,
      height: window.tileSize,
      fontSize: 16,
      fill: 'white',
      strokeWidth: 2,
      selectable: false
    }))
    y += 1
  }
}
export function drawDetailedMobData () {
  var color, eye_color, text
  var y = 0
  var x = window.view_x - 256 - 100
  var bottom = window.view_y - 364
  if (window.detailedMobData.length > 0) {
    for (let mob of window.detailedMobData) {
      if (mob) {
        if (mob.name == 'Animated Statue' || mob.name == 'Phantom Fungus' || mob.name == 'Mimic') {
          continue
        }
        color = constants.mobColors[mob.name]
        eye_color = determineEyeColorForKey(mob.name)
        window.canvas.add(new fabric.Rect({
          left: x,
          top: bottom - (y * (window.tileSize * 2)),
          height: window.tileSize,
          width: window.tileSize,
          stroke: color,
          fill: color,
          strokeWidth: 2,
          selectable: false
        }))
        window.canvas.add(new fabric.Circle({
          left: x,
          top: bottom - (y * (window.tileSize * 2)),
          radius: window.tileSize * 0.09375,
          stroke: eye_color,
          fill: eye_color,
          strokeWidth: 2,
          selectable: false
        }))
        window.canvas.add(new fabric.Circle({
          left: x + window.tileSize - (window.tileSize * 0.1875),
          top: bottom - (y * (window.tileSize * 2)),
          radius: window.tileSize * 0.09375,
          stroke: eye_color,
          fill: eye_color,
          strokeWidth: 2,
          selectable: false
        }))
        text = ' = Level ' + mob.level + ' ' + mob.mobClass + ' ' + mob.name + '\n     ' + constants.mobDetails[mob.name]
        window.canvas.add(new fabric.Text(text, {
          left: x + window.tileSize,
          top: bottom - (y * (window.tileSize * 2)) + (window.tileSize / 2),
          originY: 'center',
          width: 256 - window.tileSize,
          height: window.tileSize,
          fontSize: 16,
          fill: 'white',
          strokeWidth: 2,
          selectable: false
        }))
      }
    }
  }
}
export function drawHoverDescription (message, mob_pos_x, mob_pos_y, char_pos_x, char_pos_y, mob_class, mob_name) {
  if (window.mouseOverType == 1) {
    window.canvas.add(new fabric.Rect({
      left: (window.view_x / 2) - window.tileSize,
      top: (window.view_y / 2) - window.tileSize,
      width: window.tileSize * 3,
      height: window.tileSize * 3,
      stroke: 'white',
      fill: 'transparent',
      strokeWidth: 2,
      selectable: false
    }))
  }
  if (window.mapMouseOver !== '') {
    var text = constants.hoverDescriptions[window.mapMouseOver]
    if (text == undefined) {
      text = ''
    }
    text = addMobandCharHoverData(mob_pos_x, mob_pos_y, char_pos_x, char_pos_y, text, mob_class, mob_name)
    if (text == '' || text == 'Floor.') {
      return
    }
    window.canvas.add(new fabric.Rect({
      left: window.view_x - 256,
      top: 200,
      width: 256,
      height: window.tileSize * 2,
      stroke: 'black',
      fill: 'black',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Text(text, {
      left: window.view_x - 256,
      top: 200,
      width: 256,
      height: window.tileSize * 2,
      fontSize: 16,
      fill: 'white',
      strokeWidth: 2,
      selectable: false
    }))
  }
}
export function addMobandCharHoverData (mob_pos_x, mob_pos_y, char_pos_x, char_pos_y, text, mob_class, mob_name) {
  for (var i=0; i<mob_pos_x.length; i++) {
    if (window.mapMouseOverX > mob_pos_x[i] && window.mapMouseOverX < mob_pos_x[i] + window.tileSize && window.mapMouseOverY > mob_pos_y[i] && window.mapMouseOverY < mob_pos_y[i] + window.tileSize) {
      text = text + '\n' + constants.mobClassDescriptions[mob_class[i]]
      text = text + ' ' + mob_name[i]
    }
  }
  for (var i=0; i<char_pos_x.length; i++) {
    if (window.mapMouseOverX > parseInt(char_pos_x[i]) && window.mapMouseOverX < parseInt(char_pos_x[i]) + window.tileSize && window.mapMouseOverY > parseInt(char_pos_y[i]) && window.mapMouseOverY < parseInt(char_pos_y[i]) + window.tileSize) {
      text = text + '\nA character'
    }
  }
  return text
}
export function drawMouseHoverGuide () {
  var range = constants.cardRange[mouseOverType]
  var type = constants.cardRangeType[mouseOverType]
  if (!range) {
    return
  }
  if (!type) {
    type = 'line'
  }
  if (type === 'line' || type === 'aoe2' || type === 'aoe4') {
    window.canvas.add(new fabric.Rect({
      left: window.view_x / 2,
      top: (window.view_y / 2) - (range * window.tileSize),
      width: 1,
      height: range * window.tileSize,
      stroke: 'white',
      fill: 'transparent',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Rect({
      left: window.view_x / 2,
      top: (window.view_y / 2) - (range * window.tileSize),
      width: window.tileSize,
      height: 1,
      stroke: 'white',
      fill: 'transparent',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Rect({
      left: (window.view_x / 2) + window.tileSize,
      top: (window.view_y / 2) - (range * window.tileSize),
      width: 1,
      height: range * window.tileSize,
      stroke: 'white',
      fill: 'transparent',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Rect({
      left: window.view_x / 2,
      top: (window.view_y / 2) + window.tileSize,
      width: 1,
      height: range * window.tileSize,
      stroke: 'white',
      fill: 'transparent',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Rect({
      left: window.view_x / 2,
      top: (window.view_y / 2) + window.tileSize + (range * window.tileSize),
      width: window.tileSize,
      height: 1,
      stroke: 'white',
      fill: 'transparent',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Rect({
      left: (window.view_x / 2) + window.tileSize,
      top: (window.view_y / 2) + window.tileSize,
      width: 1,
      height: range * window.tileSize,
      stroke: 'white',
      fill: 'transparent',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Rect({
      top: window.view_y / 2,
      left: (window.view_x / 2) - (range * window.tileSize),
      height: 1,
      width: range * window.tileSize,
      stroke: 'white',
      fill: 'transparent',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Rect({
      top: window.view_y / 2,
      left: (window.view_x / 2) - (range * window.tileSize),
      height: window.tileSize,
      width: 1,
      stroke: 'white',
      fill: 'transparent',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Rect({
      top: (window.view_y / 2) + window.tileSize,
      left: (window.view_x / 2) - (range * window.tileSize),
      height: 1,
      width: range * window.tileSize,
      stroke: 'white',
      fill: 'transparent',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Rect({
      top: window.view_y / 2,
      left: (window.view_x / 2) + window.tileSize,
      height: 1,
      width: range * window.tileSize,
      stroke: 'white',
      fill: 'transparent',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Rect({
      top: window.view_y / 2,
      left: (window.view_x / 2) + window.tileSize + (range * window.tileSize),
      height: window.tileSize,
      width: 1,
      stroke: 'white',
      fill: 'transparent',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Rect({
      top: (window.view_y / 2) + window.tileSize,
      left: (window.view_x / 2) + window.tileSize,
      height: 1,
      width: range * window.tileSize,
      stroke: 'white',
      fill: 'transparent',
      strokeWidth: 2,
      selectable: false
    }))
  } else if (type === 'radius') {
    window.canvas.add(new fabric.Rect({
      left: window.view_x / 2,
      top: window.view_y / 2,
      originX: 'center',
      originY: 'center',
      width: radius * (window.tileSize * 2),
      height: radius * (window.tileSize * 2),
      stroke: 'white',
      fill: 'transparent',
      strokeWidth: 2,
      selectable: false
    }))
  }
  if (type === 'aoe2' || type === 'aoe4') {
    if (type === 'aoe2') {
      var radius = window.tileSize * 4
    } else {
      var radius = window.tileSize * 8
    }
    window.canvas.add(new fabric.Rect({
      left: (window.view_x / 2) - (range * window.tileSize) + (window.tileSize / 2),
      top: (window.view_y / 2) + (window.tileSize / 2),
      originX: 'center',
      originY: 'center',
      width: radius,
      height: radius,
      stroke: 'white',
      fill: 'transparent',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Rect({
      left: (window.view_x / 2) + (range * window.tileSize) + (window.tileSize / 2),
      top: (window.view_y / 2) + (window.tileSize / 2),
      originX: 'center',
      originY: 'center',
      width: radius,
      height: radius,
      stroke: 'white',
      fill: 'transparent',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Rect({
      left: (window.view_x / 2) + (window.tileSize / 2),
      top: (window.view_y / 2) - (range * window.tileSize) + (window.tileSize / 2),
      originX: 'center',
      originY: 'center',
      width: radius,
      height: radius,
      stroke: 'white',
      fill: 'transparent',
      strokeWidth: 2,
      selectable: false
    }))
    window.canvas.add(new fabric.Rect({
      left: (window.view_x / 2) + (window.tileSize / 2),
      top: (window.view_y / 2) + (range * window.tileSize) + (window.tileSize / 2),
      originX: 'center',
      originY: 'center',
      width: radius,
      height: radius,
      stroke: 'white',
      fill: 'transparent',
      strokeWidth: 2,
      selectable: false
    }))
  }
}

function determineEyeColorForKey (mob_name) {
  if (constants.mobEyeColors[mob_name] == undefined) {
    return 'yellow'
  } else {
    return constants.mobEyeColors[mob_name]
  }
}
