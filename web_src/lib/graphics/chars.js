export function drawCharacters (message, char_pos_x, char_pos_y, char_facing, char_hp, char_max_hp, char_slot_1, char_slot_2, char_slot_3, char_slot_4, char_slot_5, char_slot_6, char_gcd, char_color, char_eye_color) {
  for (var i=0; i<char_pos_x.length; i++) {
    var x, y
    [x,y] = getCharacterDisplayCoordinates(char_pos_x, char_pos_y, message, i)
    window.canvas.add(new fabric.Rect({
      left: x,
      top: y,
      height: window.tileSize,
      width: window.tileSize,
      stroke: char_color[i],
      fill: char_color[i],
      strokeWidth: 2,
      selectable: false
    }))
    if (char_facing[i] !== void 0) {
      drawCharEyes[char_facing[i]](x, y, char_eye_color[i])
    }
    if (parseInt(message.friendly_target) === i && parseInt(message.friendly_target) !== parseInt(message.char_id)) {
      window.canvas.add(new fabric.Rect({
        left: x,
        top: y,
        height: window.tileSize,
        width: window.tileSize,
        stroke: 'red',
        fill: 'transparent',
        strokeWidth: 2,
        selectable: false
      }))
    }
  }
}
function drawCharEyesUp (x, y, color) {
  window.canvas.add(new fabric.Circle({
    left: x,
    top: y,
    radius: window.tileSize * 0.09375,
    stroke: color,
    fill: color,
    strokeWidth: 2,
    selectable: false
  }))
  window.canvas.add(new fabric.Circle({
    left: x + window.tileSize - (window.tileSize * 0.1875),
    top: y,
    radius: window.tileSize * 0.09375,
    stroke: color,
    fill: color,
    strokeWidth: 2,
    selectable: false
  }))
}
function drawCharEyesRight (x, y, color) {
  window.canvas.add(new fabric.Circle({
    left: x + window.tileSize - (window.tileSize * 0.1875),
    top: y + window.tileSize - (window.tileSize * 0.1875),
    radius: window.tileSize * 0.09375,
    stroke: color,
    fill: color,
    strokeWidth: 2,
    selectable: false
  }))
  window.canvas.add(new fabric.Circle({
    left: x + window.tileSize - (window.tileSize * 0.1875),
    top: y,
    radius: window.tileSize * 0.09375,
    stroke: color,
    fill: color,
    strokeWidth: 2,
    selectable: false
  }))
}
function drawCharEyesDown (x, y, color) {
  window.canvas.add(new fabric.Circle({
    left: x,
    top: y + window.tileSize - (window.tileSize * 0.1875),
    radius: window.tileSize * 0.09375,
    stroke: color,
    fill: color,
    strokeWidth: 2,
    selectable: false
  }))
  window.canvas.add(new fabric.Circle({
    left: x + window.tileSize - (window.tileSize * 0.1875),
    top: y + window.tileSize - (window.tileSize * 0.1875),
    radius: window.tileSize * 0.09375,
    stroke: color,
    fill: color,
    strokeWidth: 2,
    selectable: false
  }))
}
function drawCharEyesLeft (x, y, color) {
  window.canvas.add(new fabric.Circle({
    left: x,
    top: y,
    radius: window.tileSize * 0.09375,
    stroke: color,
    fill: color,
    strokeWidth: 2,
    selectable: false
  }))
  window.canvas.add(new fabric.Circle({
    left: x,
    top: y + window.tileSize - (window.tileSize * 0.1875),
    radius: window.tileSize * 0.09375,
    stroke: color,
    fill: color,
    strokeWidth: 2,
    selectable: false
  }))
}
function getCharacterDisplayCoordinates (char_pos_x, char_pos_y, message, i) {
  var x, y
  [x,y] = [parseInt(char_pos_x[i]) - message.char_pos_x + (window.view_x / 2), parseInt(char_pos_y[i]) - message.char_pos_y + (window.view_y / 2)]
  if (x < 0) {
    x = -(window.tileSize / 2)
  }
  if (y < 0) {
    y = -(window.tileSize / 2)
  }
  if (x > window.view_x) {
    x = window.view_x - (window.tileSize / 2)
  }
  if (y > window.view_y) {
    y = window.view_y - (window.tileSize / 2)
  }
  return [x, y]
}

var drawCharEyes = {
  '0': drawCharEyesUp,
  '1': drawCharEyesRight,
  '2': drawCharEyesDown,
  '3': drawCharEyesLeft
}
