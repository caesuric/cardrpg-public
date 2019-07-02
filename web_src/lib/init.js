export function init() {
  window.miniMapOn = false
  window.selectingClass = false
  window.pruningDeck = false
  window.view_x = $(window).width()
  window.view_y = $(window).height()
  window.tileSize = 64
  initTileGlobal()
  initSightGlobal()
}

function initTileGlobal() {
  window.tiles = []
  for (var i = 0; i <= 63; i++) {
    var item = []
    for (var j = 0; j <= 63; j++) {
      item.push(null)
    }
    window.tiles.push(item)
  }
}
function initSightGlobal() {
  window.sight = []
  for (var i = 0; i<= 63; i++) {
    var item = []
    for (var j=0; j<=63; j++) {
      item.push(null)
    }
    window.sight.push(item)
  }
}
