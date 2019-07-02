export function drawProjectiles (message) {
  for (let proj of message.projectiles) {
    var proj_split = proj.split(',')
    var proj_x = parseInt(proj_split[0])
    var proj_y = parseInt(proj_split[1])
    var proj_color = proj_split[2].replace(/\0/g, '')
    window.canvas.add(new fabric.Circle({
      left: proj_x - parseInt(message.char_pos_x) + (window.view_x / 2),
      top: proj_y - parseInt(message.char_pos_y) + (window.view_y / 2),
      radius: 6,
      stroke: proj_color,
      fill: proj_color,
      originX: 'center',
      originY: 'center',
      strokeWidth: 2,
      selectable: false
    }))
  }
}
