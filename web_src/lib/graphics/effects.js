import * as constants from 'cardrpgConstants'

export function drawEffects (message) {
  window.effects_duration = message.effects_duration
  window.effects_max_duration = message.effects_max_duration
  if (message.effects.length > 0) {
    for (var i=0; i<message.effects.length; i++) {
      drawEffect(message, i)
    }
  }
}
function drawEffect (message, i) {
  var color = constants.debuffColors[message.effects[i]]
  var clipped_rect = new fabric.Rect({
    left: window.view_x - window.tileSize - (i * window.tileSize),
    top: window.view_y - 84 - 86 - 86 - window.tileSize,
    width: window.tileSize,
    height: window.tileSize,
    stroke: 'white',
    fill: color,
    strokeWidth: 2
  })
  window.i = i
  clipped_rect.clipTo = function(ctx) {
    ctx.moveTo(0, 0)
    ctx.arc(0, 0, window.tileSize, 0 - Math.PI / 2, (Math.PI * 2 * window.effects_duration[window.i] / window.effects_max_duration[window.i]) - Math.PI / 2)
  }
  window.canvas.add(clipped_rect)
  window.canvas.add(new fabric.Text(String(Math.round(message.effects_duration[i] / 60)), {
    left: window.view_x - (i * window.tileSize) + (window.tileSize / 2),
    top: window.view_y - 84 - 86 - 86 - window.tileSize + (window.tileSize / 2),
    fill: 'white',
    fontSize: 15,
    originX: 'center',
    originY: 'center',
    selectable: false
  }))
}
