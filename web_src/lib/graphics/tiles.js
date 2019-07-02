export function drawTiles (message) {
  window.elementsDrawn = {}
  window.elementsDrawn.wall = false
  window.elementsDrawn.door = false
  window.elementsDrawn.trappedDoor = false
  window.elementsDrawn.chest = false
  window.elementsDrawn.trappedChest = false
  window.elementsDrawn.stairsDown = false
  window.elementsDrawn.stairsUp = false
  window.elementsDrawn.fire = false
  window.elementsDrawn.acid = false
  window.elementsDrawn.statue = false
  window.elementsDrawn.fountain = false
  window.elementsDrawn.trap = false
  window.elementsDrawn.projectile = false
  window.elementsDrawn.shop = false
  window.elementsDrawn.mobs = []

  for (var x=0; x<message.tiles.length; x++) {
    if (message.tiles[x]) {
      for (var y=0; y<message.tiles[x].length; y++) {
        if (tileDrawTable[message.tiles[x][y]]!=undefined && message.tiles[x][y]!='C' && message.tiles[x][y]!='H' && message.tiles[x][y]!='E' && message.tiles[x][y]!='D' && message.tiles[x][y]!='O' && message.tiles[x][y]!='R') {
          var x_pos = ((x*window.tileSize)-parseInt(message.char_pos_x)+(window.view_x/2))
          var y_pos = ((y*window.tileSize)-parseInt(message.char_pos_y)+(window.view_y/2))
          if (x_pos > -window.tileSize && x_pos < window.view_x) {
            if (y_pos > -window.tileSize && y_pos < window.view_y) {
              tileDrawTable[message.tiles[x][y]](message,x,y)
            }
          }
        }
      }
    }
  }
}

function drawFloor (message, x, y) {
  if (window.floorImageLoaded && window.sight[x][y]) {
    window.preRenderCanvas.add(new fabric.Image(window.floorImage, {
      left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2),
      top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2),
      selectable: false
    }))
  } else if (window.hiddenFloorImageLoaded) {
    window.preRenderCanvas.add(new fabric.Image(window.hiddenFloorImage, {
      left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2),
      top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2),
      selectable: false
    }))
  }
}

function drawWall (message, x, y) {
  window.preRenderCanvas.add(new fabric.Rect({
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2),
    height: window.tileSize,
    width: window.tileSize,
    stroke: 'gray',
    fill: 'gray',
    strokeWidth: 2,
    selectable: false
  }))
  window.elementsDrawn.wall = true
}

function drawOutOfSightWall (message, x, y) {
  window.preRenderCanvas.add(new fabric.Rect({
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2),
    height: window.tileSize,
    width: window.tileSize,
    stroke: '#444444',
    fill: '#444444',
    strokeWidth: 2,
    selectable: false
  }))
  window.elementsDrawn.wall = true
}

function drawDoor (message, x, y) {
  if (window.sight[x][y]) {
    var brown = 'brown'
    var yellow = 'yellow'
  } else {
    var brown = '#412E1D'
    var yellow = '#888800'
  }
  window.canvas.add(new fabric.Rect({
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2),
    height: window.tileSize,
    width: window.tileSize,
    stroke: brown,
    fill: brown,
    strokeWidth: 2,
    selectable: false
  }))
  window.canvas.add(new fabric.Circle({
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2) + (window.tileSize / 4),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2) + (window.tileSize / 4),
    radius: window.tileSize / 4,
    stroke: yellow,
    fill: yellow,
    strokeWidth: 2,
    selectable: false
  }))
  window.elementsDrawn.door = true
}

function drawTrappedDoor (message, x, y) {
  if (window.sight[x][y]) {
    var brown = 'brown'
    var yellow = 'yellow'
  } else {
    var brown = '#412E1D'
    var yellow = '#888800'
  }
  window.canvas.add(new fabric.Rect({
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2),
    height: window.tileSize,
    width: window.tileSize,
    stroke: brown,
    fill: brown,
    strokeWidth: 2,
    selectable: false
  }))
  window.canvas.add(new fabric.Circle({
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2) + (window.tileSize / 4),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2) + (window.tileSize / 4),
    radius: window.tileSize / 4,
    stroke: yellow,
    fill: yellow,
    strokeWidth: 2,
    selectable: false
  }))
  window.canvas.add(new fabric.Text('T', {
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2) + (window.tileSize / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2) + (window.tileSize / 2),
    originX: 'center',
    originY: 'center',
    fill: 'black',
    fontSize: 16,
    selectable: false
  }))
  window.elementsDrawn.trappedDoor = true
}

function drawChest (message, x, y) {
  if (window.sight[x][y]) {
    var brown = 'brown'
    var yellow = 'yellow'
  } else {
    var brown = '#412E1D'
    var yellow = '#888800'
  }
  window.canvas.add(new fabric.Rect({
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2),
    height: window.tileSize - 1,
    width: window.tileSize - 1,
    stroke: yellow,
    fill: brown,
    strokeWidth: 2,
    selectable: false
  }))
  window.elementsDrawn.chest = true
}

function drawTrappedChest (message, x, y) {
  if (window.sight[x][y]) {
    var brown = 'brown'
    var yellow = 'yellow'
  } else {
    var brown = '#412E1D'
    var yellow = '#888800'
  }
  window.canvas.add(new fabric.Rect({
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2),
    height: window.tileSize,
    width: window.tileSize,
    stroke: yellow,
    fill: brown,
    strokeWidth: 2,
    selectable: false
  }))
  window.canvas.add(new fabric.Text('T', {
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2) + (window.tileSize / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2) + (window.tileSize / 2),
    originX: 'center',
    originY: 'center',
    fill: 'white',
    fontSize: 16,
    selectable: false
  }))
  window.elementsDrawn.trappedChest = true
}

function drawStairsDown (message, x, y) {
  window.preRenderCanvas.add(new fabric.Rect({
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2),
    height: window.tileSize - 1,
    width: window.tileSize - 1,
    stroke: 'white',
    fill: 'black',
    strokeWidth: 2,
    selectable: false
  }))
  window.preRenderCanvas.add(new fabric.Text('>', {
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2) + (window.tileSize / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2) + (window.tileSize / 2),
    originX: 'center',
    originY: 'center',
    fill: 'white',
    fontSize: 16,
    selectable: false
  }))
  window.elementsDrawn.stairsDown = true
}

function drawStairsUp (message, x, y) {
  window.preRenderCanvas.add(new fabric.Rect({
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2),
    height: window.tileSize - 1,
    width: window.tileSize - 1,
    stroke: 'white',
    fill: 'black',
    strokeWidth: 2,
    selectable: false
  }))
  window.preRenderCanvas.add(new fabric.Text('<', {
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2) + (window.tileSize / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2) + (window.tileSize / 2),
    originX: 'center',
    originY: 'center',
    fill: 'white',
    fontSize: 16,
    selectable: false
  }))
  window.elementsDrawn.stairsUp = true
}

function drawFire (message, x, y) {
  window.preRenderCanvas.add(new fabric.Rect({
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2),
    height: window.tileSize,
    width: window.tileSize,
    stroke: 'red',
    fill: 'red',
    strokeWidth: 2,
    selectable: false
  }))
  window.elementsDrawn.fire = true
}

function drawAcid (message, x, y) {
  window.preRenderCanvas.add(new fabric.Rect({
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2),
    height: window.tileSize,
    width: window.tileSize,
    stroke: 'green',
    fill: 'green',
    strokeWidth: 2,
    selectable: false
  }))
  window.elementsDrawn.acid = true
}

function drawStatue (message, x, y) {
  if (window.sight[x][y]) {
    var gray = 'gray'
  } else {
    var gray = 'darkgray'
  }
  window.preRenderCanvas.add(new fabric.Rect({
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2),
    height: window.tileSize,
    width: window.tileSize,
    stroke: gray,
    fill: gray,
    strokeWidth: 2,
    selectable: false
  }))
  window.preRenderCanvas.add(new fabric.Circle({
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2) + window.tileSize - (window.tileSize * 0.1875),
    radius: window.tileSize * 0.09375,
    stroke: 'yellow',
    fill: 'yellow',
    strokeWidth: 2,
    selectable: false
  }))
  window.preRenderCanvas.add(new fabric.Circle({
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2) + window.tileSize - (window.tileSize * 0.1875),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2) + window.tileSize - (window.tileSize * 0.1875),
    radius: window.tileSize * 0.09375,
    stroke: 'yellow',
    fill: 'yellow',
    strokeWidth: 2,
    selectable: false
  }))
  window.elementsDrawn.statue = true
}

function drawFountain (message, x, y) {
  if (window.sight[x][y]) {
    var gray = 'gray'
    var blue = 'blue'
  } else {
    var gray = 'darkgray'
    var blue = 'darkblue'
  }
  window.preRenderCanvas.add(new fabric.Rect({
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2),
    height: window.tileSize,
    width: window.tileSize,
    stroke: gray,
    fill: gray,
    strokeWidth: 2,
    selectable: false
  }))
  window.preRenderCanvas.add(new fabric.Circle({
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2),
    radius: window.tileSize / 2,
    stroke: blue,
    fill: blue,
    strokeWidth: 2,
    selectable: false
  }))
  window.elementsDrawn.fountain = true
}

function drawTrap (message, x, y) {
  window.preRenderCanvas.add(new fabric.Text('T', {
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2) + (window.tileSize / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2) + (window.tileSize / 2),
    originX: 'center',
    originY: 'center',
    fill: 'white',
    fontSize: 16,
    selectable: false
  }))
  window.elementsDrawn.trap = true
}

function drawShop (message, x, y) {
  if (window.sight[x][y]) {
    var green = 'green'
  } else {
    var green = 'darkgreen'
  }
  window.preRenderCanvas.add(new fabric.Text('$', {
    left: (x * window.tileSize) - parseInt(message.char_pos_x) + (window.view_x / 2) + (window.tileSize / 2),
    top: (y * window.tileSize) - parseInt(message.char_pos_y) + (window.view_y / 2) + (window.tileSize / 2),
    originX: 'center',
    originY: 'center',
    fontSize: 24,
    fill: green,
    selectable: false
  }))
  window.elementsDrawn.shop = true
}

function drawMiniFloor (message, x, y, size) {
  return [
    new fabric.Rect({
      left: x,
      top: y,
      height: size,
      width: size,
      opacity: 1,
      stroke: '#444444',
      fill: '#444444',
      strokeWidth: 0,
      selectable: false
    })
  ]
}

function drawMiniWall (message, x, y, size) {
  return [
    new fabric.Rect({
      left: x,
      top: y,
      height: size,
      width: size,
      opacity: 1,
      stroke: 'gray',
      fill: 'gray',
      strokeWidth: 0,
      selectable: false
    })
  ]
}

function drawMiniDoor (message, x, y, size) {
  return [
    new fabric.Rect({
      left: x,
      top: y,
      height: size,
      width: size,
      opacity: 1,
      stroke: 'brown',
      fill: 'brown',
      strokeWidth: 1,
      selectable: false
    }), new fabric.Circle({
      left: x + Math.floor(size / 4),
      top: y + Math.floor(size / 4),
      opacity: 1,
      radius: Math.floor(size / 4),
      stroke: 'yellow',
      fill: 'yellow',
      strokeWidth: 1,
      selectable: false
    })
  ]
}

function drawMiniChest (message, x, y, size) {
  return [
    new fabric.Rect({
      left: x,
      top: y,
      height: size,
      width: size,
      opacity: 1,
      stroke: 'yellow',
      fill: 'brown',
      strokeWidth: 1,
      selectable: false
    })
  ]
}

function drawMiniStairsDown (message, x, y, size) {
  return [
    new fabric.Rect({
      left: x,
      top: y,
      height: size,
      width: size,
      opacity: 1,
      stroke: 'white',
      fill: 'black',
      strokeWidth: 1,
      selectable: false
    }), new fabric.Text('>', {
      left: x,
      top: y,
      opacity: 1,
      originX: 'center',
      originY: 'center',
      fill: 'white',
      fontSize: Math.floor(size / 2),
      selectable: false
    })
  ]
}

function drawMiniStairsUp (message, x, y, size) {
  return [
    new fabric.Rect({
      left: x,
      top: y,
      height: size,
      width: size,
      opacity: 1,
      stroke: 'white',
      fill: 'black',
      strokeWidth: 1,
      selectable: false
    }), new fabric.Text('<', {
      left: x,
      top: y,
      opacity: 1,
      originX: 'center',
      originY: 'center',
      fill: 'white',
      fontSize: Math.floor(size / 2),
      selectable: false
    })
  ]
}

function drawMiniFire (message, x, y, size) {
  return [
    new fabric.Rect({
      left: x,
      top: y,
      height: size,
      width: size,
      opacity: 1,
      stroke: 'red',
      fill: 'red',
      strokeWidth: 1,
      selectable: false
    })
  ]
}

function drawMiniAcid (message, x, y, size) {
  return [
    new fabric.Rect({
      left: x,
      top: y,
      height: size,
      width: size,
      opacity: 1,
      stroke: 'green',
      fill: 'green',
      strokeWidth: 1,
      selectable: false
    })
  ]
}

function drawMiniFountain (message, x, y, size) {
  return [
    new fabric.Rect({
      left: x,
      top: y,
      height: size,
      width: size,
      opacity: 1,
      stroke: 'gray',
      fill: 'gray',
      strokeWidth: 1,
      selectable: false
    }), new fabric.Circle({
      left: x,
      top: y,
      opacity: 1,
      radius: Math.floor(size / 2),
      stroke: 'blue',
      fill: 'blue',
      strokeWidth: 1,
      selectable: false
    })
  ]
}

function drawMiniShop (message, x, y, size) {
  return [
    new fabric.Text('$', {
      left: x + (window.tileSize / 2),
      top: y + (window.tileSize / 2),
      originX: 'center',
      originY: 'center',
      fontSize: 16,
      opacity: 1,
      fill: 'green',
      selectable: false
    })
  ]
}

export function drawChestsAndDoors (message) {
  if (!window.elementsDrawn) {
    window.elementsDrawn = {}
  }
  if (!window.elementsDrawn.mobs) {
    window.elementsDrawn.mobs = []
  }
  for (var x=0; x<message.tiles.length; x++) {
    if (message.tiles[x]) {
      for (var y=0; y<message.tiles[x].length; y++) {
        if (tileDrawTable[message.tiles[x][y]]!=undefined && (message.tiles[x][y]=='C' || message.tiles[x][y]=='H' || message.tiles[x][y]=='E' || message.tiles[x][y]=='D' || message.tiles[x][y]=='O' || message.tiles[x][y]=='R')) {
          var x_pos = ((x*window.tileSize)-parseInt(message.char_pos_x)+(window.view_x/2))
          var y_pos = ((y*window.tileSize)-parseInt(message.char_pos_y)+(window.view_y/2))
          if (x_pos > -window.tileSize && x_pos < window.view_x) {
            if (y_pos > -window.tileSize && y_pos < window.view_y) {
              tileDrawTable[message.tiles[x][y]](message,x,y)
            }
          }
        }
      }
    }
  }
}


var tileDrawTable = {
  'W': drawWall,
  'X': drawOutOfSightWall,
  'D': drawDoor,
  'O': drawDoor,
  'R': drawTrappedDoor,
  'C': drawChest,
  'H': drawChest,
  'E': drawTrappedChest,
  '>': drawStairsDown,
  '<': drawStairsUp,
  'f': drawFire,
  'a': drawAcid,
  '@': drawStatue,
  'F': drawFountain,
  'Q': drawFountain,
  'T': drawTrap,
  'P': drawShop,
  ' ': drawFloor
}

export var miniTileDrawTable = {
  'W': drawMiniWall,
  'X': drawMiniWall,
  'D': drawMiniDoor,
  'O': drawMiniDoor,
  'R': drawMiniDoor,
  'C': drawMiniChest,
  'H': drawMiniChest,
  'E': drawMiniChest,
  '>': drawMiniStairsDown,
  '<': drawMiniStairsUp,
  'f': drawMiniFire,
  'a': drawMiniAcid,
  'F': drawMiniFountain,
  'Q': drawMiniFountain,
  'P': drawMiniShop,
  ' ': drawMiniFloor
}
