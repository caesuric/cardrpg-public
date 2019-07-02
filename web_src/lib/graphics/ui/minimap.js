import * as tiles from 'graphics/tiles'

export function drawMiniMapCallback () {
  window.miniMapCanvas.clear()
  drawMap(window.minimap_message)
  window.miniMapCanvas.renderAll()
  window.miniMapImage = new fabric.Image(window.rawMiniMapCanvas, {
    left: 0,
    top: 0,
    selectable: false,
    opacity: 0.5
  })
}

function drawMap (message) {
  if (!window.mapObjects) {
    return
  }
  var left = Math.floor(window.view_x / 4)
  var width = Math.floor(window.view_x / 2)
  var top = Math.floor(window.view_y / 4)
  var height = Math.floor(window.view_y / 2)
  var tile_size = Math.floor(Math.min(width, height) / message.tiles.length)
  for (var x=0; x<message.tiles.length; x++) {
    if (message.tiles[x]) {
      for (var y=0; y<message.tiles[x].length; y++) {
        if (tiles.miniTileDrawTable[message.tiles[x][y]] !== void 0) {
          if (!window.mapObjects[x]) {
            window.mapObjects[x] = []
          }
          if (!window.mapObjects[x][y]) {
            window.mapObjects[x][y] = tiles.miniTileDrawTable[message.tiles[x][y]](message, left + (x * tile_size), top + (y * tile_size), tile_size)
          }
        }
      }
    }
  }
  for (var x=0; x<window.mapObjects.length; x++) {
    if (window.mapObjects[x]) {
      for (var y=0; y<window.mapObjects[x].length; y++) {
        if (window.mapObjects[x][y]) {
          for (let item of window.mapObjects[x][y]) {
            window.miniMapCanvas.add(item)
          }
        }
      }
    }
  }
  window.miniMapCanvas.add(new fabric.Rect({
    left: Math.floor(left + (parseInt(message.char_pos_x) / window.tileSize) * tile_size),
    top: Math.floor(top + (parseInt(message.char_pos_y) / window.tileSize) * tile_size),
    height: tile_size,
    width: tile_size,
    opacity: 0.5,
    stroke: 'blue',
    fill: 'blue',
    strokeWidth: 0,
    selectable: false
  }))
}
