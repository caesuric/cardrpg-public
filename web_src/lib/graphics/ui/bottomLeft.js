import * as constants from 'cardrpgConstants'

export function drawHpAndMp (message) {
  window.canvas.add(new fabric.Rect({
    left: 0,
    top: window.view_y - 172,
    height: 86,
    width: (window.view_x - 1020) / 2,
    stroke: 'white',
    fill: 'black',
    strokeWidth: 1,
    selectable: false
  }))
  window.canvas.add(new fabric.Rect({
    left: 0,
    top: window.view_y - 172,
    height: 86,
    width: (window.view_x - 1020) / 2 * message.hp / message.max_hp,
    stroke: 'red',
    fill: 'red',
    strokeWidth: 1,
    selectable: false
  }))
  window.canvas.add(new fabric.Text("HP: " + String(message.hp) + "/" + String(message.max_hp), {
    left: 2,
    top: window.view_y - 172 + 2,
    fontSize: 15,
    fill: 'white',
    selectable: false
  }))
  window.canvas.add(new fabric.Rect({
    left: 0,
    top: window.view_y - 86,
    height: 86,
    width: (window.view_x - 1020) / 2,
    stroke: 'white',
    fill: 'black',
    strokeWidth: 1,
    selectable: false
  }))
  window.canvas.add(new fabric.Rect({
    left: 0,
    top: window.view_y - 86,
    height: 86,
    width: (window.view_x - 1020) / 2 * message.mp / message.max_mp,
    stroke: 'blue',
    fill: 'blue',
    strokeWidth: 1,
    selectable: false
  }))
  window.canvas.add(new fabric.Text("MP: " + String(message.mp) + "/" + String(message.max_mp), {
    left: 2,
    top: window.view_y - 86 + 2,
    fontSize: 15,
    fill: 'white',
    selectable: false
  }))
  window.canvas.add(new fabric.Rect({
    left: 0,
    top: window.view_y - 256,
    height: 84,
    width: (window.view_x - 1020) / 2,
    stroke: 'white',
    fill: 'black',
    strokeWidth: 1,
    selectable: false
  }))
  if (message.target === null) {
    return
  }
  window.canvas.add(new fabric.Rect({
    left: 0,
    top: window.view_y - 256,
    height: 84,
    width: (window.view_x - 1020) / 2 * message.target_hp / message.target_max_hp,
    stroke: 'red',
    fill: 'red',
    strokeWidth: 1,
    selectable: false
  }))
  var text = "Level " + message.target_level + " "
  if (constants.mobClassDescriptions[parseInt(message.target_class)]) {
    text = text + constants.mobClassDescriptions[parseInt(message.target_class)] + ' '
  }
  text = text + message.target_name
  if (message.target_level !== -1) {
    window.canvas.add(new fabric.Text(text, {
      left: 2,
      top: window.view_y - 256 + 2,
      fontSize: 15,
      fill: 'white',
      selectable: false
    }))
  }
}
