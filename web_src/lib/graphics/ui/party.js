import {updater} from 'gameComm'

export function drawPartyBar (message, char_hp, char_max_hp, char_name) {
  if (char_hp.length < 2) {
    return
  }
  for (var i=0; i<char_hp.length; i++) {
    drawPartyMember(i, message, char_hp, char_max_hp, char_name)
  }
  updater.drops_length = message.drops.length
}
export function drawPartyMember (i, message, char_hp, char_max_hp, char_name) {
  var color
  if (parseInt(message.friendly_target) === i) {
    color = 'blue'
  } else if (parseInt(message.char_id) === i) {
    color = 'yellow'
  } else {
    color = 'white'
  }
  window.canvas.add(new fabric.Rect({
    left: 0,
    top: window.view_y - 256 - (window.tileSize * 2) - (window.tileSize * i),
    width: 170,
    height: window.tileSize,
    stroke: color,
    strokeWidth: 2,
    selectable: false
  }))
  window.canvas.add(new fabric.Rect({
    left: 2,
    top: window.view_y - 256 - (window.tileSize * 2) - (window.tileSize * i) + 2,
    width: (170 * char_hp[i] / char_max_hp[i]) - 4,
    height: window.tileSize - 4,
    stroke: 'red',
    fill: 'red',
    strokeWidth: 2,
    selectable: false
  }))
  window.canvas.add(new fabric.Text(char_name[i], {
    left: 2,
    top: window.view_y - 256 - (window.tileSize * 2) - (window.tileSize * i) + 2,
    fontSize: 16,
    fill: 'white',
    selectable: false
  }))
}
