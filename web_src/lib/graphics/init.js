export function init() {
  initMainCanvas()
  initPreRenderCanvas()
  initMiniMapCanvas()
  loadCardImages()
  loadHotbarImages()
  loadFloorImage()
}

function initMainCanvas() {
  var main_canvas_container = document.getElementById('main_canvas_container')
  main_canvas_container.style.width = window.view_x
  main_canvas_container.style.height = window.view_y
  window.canvas = new fabric.Canvas('main_canvas', {
    width: window.view_x,
    height: window.view_y
  })
  window.canvas.backgroundColor = "black"
  window.canvas.selection = false
  window.canvas.stateful = false
  window.canvas.renderOnAddRemove = false
  window.canvas.skipTargetFind = true
  window.canvas.renderAll()
}

function initPreRenderCanvas() {
  window.rawPreRenderCanvas = document.createElement('canvas')
  window.rawPreRenderCanvas.width = window.view_x
  window.rawPreRenderCanvas.height = window.view_y
  window.preRenderCanvas = new fabric.Canvas(window.rawPreRenderCanvas, {
    width: window.view_x,
    height: window.view_y
  })
  window.preRenderCanvas.backgroundColor = "black"
  window.preRenderCanvas.selection = false
  window.preRenderCanvas.stateful = false
  window.preRenderCanvas.renderOnAddRemove = false
  window.preRenderCanvas.skipTargetFind = true
}

function initMiniMapCanvas() {
  window.rawMiniMapCanvas = document.createElement('canvas')
  window.rawMiniMapCanvas.width = window.view_x
  window.rawMiniMapCanvas.height = window.view_y
  window.miniMapCanvas = new fabric.Canvas(window.rawMiniMapCanvas, {
    width: window.view_x,
    height: window.view_y
  })
  window.miniMapCanvas.backgroundColor = "transparent"
  window.miniMapCanvas.selection = false
  window.miniMapCanvas.stateful = false
  window.miniMapCanvas.renderOnAddRemove = false
  window.miniMapCanvas.skipTargetFind = true
}

function loadCardImages() {
  window.cardLoadCount = 0
  window.cardImgs = []
  var results = []
  for (var i = 0; i <= 56; i++) {
    window.cardImgs[i] = new Image
    window.cardImgs[i].onload = function() {
      window.cardLoadCount++
    }
    window.cardImgs[i].src = 'assets/images/' + String(i) + '.jpg'
  }
}

function loadHotbarImages() {
  window.hotbarLoadCount = 0
  window.hotbarImgs = []
  for (var i = 0; i <= 56; i++) {
    window.hotbarImgs[i] = new Image
    window.hotbarImgs[i].onload = function() {
      window.hotbarLoadCount++
    }
    window.hotbarImgs[i].src = 'assets/images/' + String(i) + '_small.jpg'
  }
}

function loadFloorImage() {
  window.floorImageLoaded = false
  window.floorImage = new Image
  window.floorImage.src = 'assets/images/floor.jpg'
  window.floorImage.onload = function() {
    window.floorImageLoaded = true
  }
  window.hiddenFloorImageLoaded = false
  window.hiddenFloorImage = new Image
  window.hiddenFloorImage.src = 'assets/images/hiddenFloor.jpg'
  window.hiddenFloorImage.onload = function() {
    window.hiddenFloorImageLoaded = true
  }
}
