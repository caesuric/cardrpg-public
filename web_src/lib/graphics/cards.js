import * as constants from 'cardrpgConstants'

export function drawCards (message) {
  window.hand = []
  window.hand[0] = message.slot1
  window.hand[1] = message.slot2
  window.hand[2] = message.slot3
  window.hand[3] = message.slot4
  window.hand[4] = message.slot5
  window.hand[5] = message.slot6
  window.canvas.add(new fabric.Rect({
    left: (window.view_x / 2) - 510,
    top: window.view_y - 256,
    width: 170 * 5,
    height: 256,
    strike: 'black,',
    fill: 'black',
    strokeWidth: 2,
    selectable: false
  }))
  var x = [message.slot1, message.slot2, message.slot3, message.slot4, message.slot5, message.slot6]
  window.slots = x
  for (var i = 0; i <= 5; i++) {
    drawCardBox(i, message, x)
    drawCardImageAndText(i, message, x)
  }
}
function drawCardBox (i, message, x) {
  var clipped_rect = new fabric.Rect({
    left: (window.view_x / 2) - 510 + (i * 170),
    top: window.view_y - 256,
    width: 170,
    height: 256,
    stroke: 'white',
    fill: constants.backgroundColors[parseInt(x[i])],
    strokeWidth: 2,
    selectable: false
  })
  clipped_rect.clipTo = function(ctx) {
    ctx.moveTo(0, 0)
    ctx.arc(0, 0, 256, 0 - Math.PI / 2, Math.PI * 2 - (Math.PI * 2 * parseInt(message.gcd) / 90) - Math.PI / 2)
  }
  window.canvas.add(clipped_rect)
}

function stripTrash (text) {
  if (!text) {
    return ''
  }
  var x = text.indexOf('Trash ')
  if (x === -1) {
    return text
  }
  return text.slice(0, x) + text.slice(x + 8)
}
function drawCardImageAndText (i, message, x) {
  window.canvas.add(new fabric.Text(String(i + 1) + ' - ' + stripTrash(constants.cardText[parseInt(x[i])]), {
    left: (window.view_x / 2) - 510 + 2 + (i * 170),
    top: window.view_y - 256 + 130,
    scaleToWidth: 166,
    height: 252,
    fill: constants.textColors[parseInt(x[i])],
    fontSize: constants.fontSize[parseInt(x[i])],
    selectable: false
  }))
  if (window.cardLoadCount === 57) {
    var clipped_image = new fabric.Image(window.cardImgs[parseInt(x[i])], {
      left: (window.view_x / 2) - 510 + (i * 170),
      top: window.view_y - 256,
      selectable: false
    })
    clipped_image.clipTo = function(ctx) {
      ctx.moveTo(0, 0)
      ctx.arc(0, 0, 256, 0 - Math.PI / 2, Math.PI * 2 - (Math.PI * 2 * parseInt(message.gcd) / 90) - Math.PI / 2)
    }
    window.canvas.add(clipped_image)
  }
}
