export function drawFloatingText (floating_text, char_pos_x, char_pos_y) {
  if (!window.floatingText) {
    window.floatingText = []
  }
  for (let entry of floating_text) {
    var floatingText = entry.split(',')
    var item = {}
    item.x = parseInt(floatingText[0])
    item.y = parseInt(floatingText[1])
    item.text = floatingText[2].replace(/\0/g, '')
    item.color = floatingText[3].replace(/\0/g, '')
    item.ticks = 120
    item.max_ticks = 120
    item.speed = 4
    window.floatingText.push(item)
  }
  if (window.floatingText.length >= 2) {
    for (var i=0; i<window.floatingText.length-1; i++) {
      var ft1 = window.floatingText[i]
      for (var j=i+1; j<window.floatingText.length; j++) {
        var ft2 = window.floatingText[j]
        if (ft1 === ft2) {
          continue
        }
        if (Math.abs(ft1.x - ft2.x) < window.tileSize && Math.abs((ft1.y - (ft1.speed * (ft1.max_ticks - ft1.ticks))) - (ft2.y - (ft2.speed * (ft2.max_ticks - ft2.ticks)))) < window.tileSize) {
          ft2.ticks += 1
        }
      }
    }
  }
  for (let ft of window.floatingText) {
    window.canvas.add(new fabric.Text(ft.text, {
      left: ft.x - parseInt(char_pos_x) + (window.view_x / 2) + (window.tileSize / 2),
      top: ft.y - parseInt(char_pos_y) + (window.view_y / 2) - (ft.speed * (ft.max_ticks - ft.ticks)) + (window.tileSize / 2),
      fill: ft.color,
      fontSize: 20,
      selectable: false,
      opacity: Math.min(1 * (ft.ticks / ft.max_ticks), 1),
      originX: 'center',
      originY: 'center'
    }))
    ft.ticks -= 1
  }
  for (let ft of window.floatingText) {
    if (ft.ticks <= 0) {
      window.floatingText.splice(window.floatingText.indexOf(ft), 1)
      break
    }
  }
}
