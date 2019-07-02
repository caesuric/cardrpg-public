import * as modalLaunchers from 'modalLaunchers'
import {updater} from 'gameComm'

export function init() {
  initResizeHook()
  initMouseOverVariables()
  initInputHooks()
  resetKeypresses()
}

function initResizeHook() {
  $(window).resize(function() {
    window.view_x = $(window).width()
    window.view_y = $(window).height()
    var main_canvas_container = document.getElementById('main_canvas_container')
    main_canvas_container.style.width = window.view_x
    main_canvas_container.style.height = window.view_y
    window.canvas.setWidth(window.view_x)
    window.canvas.setHeight(window.view_y)
    window.preRenderCanvas.setWidth(window.view_x)
    window.preRenderCanvas.setHeight(window.view_y)
    return window.mapObjects = []
  })
}

function initMouseOverVariables() {
  window.mouseOverType = -1
}

function initInputHooks() {
  $(document).keydown(function(options) {
    onKeyDown(options)
  })
  $(document).keyup(function(options) {
    onKeyUp(options)
  })
  window.canvas.on('mouse:up', function(options) {
    onMouseClick(options)
  })
  window.canvas.on('mouse:move', function(options) {
    onMouseMove(options)
  })
}

export var keypresses = {
    up: false,
    down: false,
    left: false,
    right: false
}

export function resetKeypresses() {
    keypresses.hb1 = false
    keypresses.hb2 = false
    keypresses.hb3 = false
    keypresses.hb4 = false
    keypresses.hb5 = false
    keypresses.hb6 = false
    keypresses.upstairs = false
    keypresses.downstairs = false
    keypresses.q_press = false
    keypresses.m_press = false
    keypresses.b_press = false
    keypresses.tab_press = false
}

function onKeyDown(options) {
  if (options.which === 78) {
    modalLaunchers.showBestiary()
  }
  else if (options.which === 90) {
    window.miniMapOn = !window.miniMapOn
  }
  else if (window.selectingClass) {
    window.classSelectScope.processKey(options.which)
  }
  else if (keyCodes[options.which] !== void 0) {
    keyCodes[options.which](options)
  }
}

function onTabPress(options) {
  options.preventDefault()
  keypresses.tab_press = true
}

function onUpPress(options) {
  keypresses.up = true
}

function onDownPress(options) {
  keypresses.down = true
}

function onLeftPress(options) {
  keypresses.left = true
}

function onRightPress(options) {
  keypresses.right = true
}

function on1Press(options) {
  keypresses.hb1 = true
}

function on2Press(options) {
  keypresses.hb2 = true
}

function on3Press(options) {
  keypresses.hb3 = true
}

function on4Press(options) {
  keypresses.hb4 = true
}

function on5Press(options) {
  keypresses.hb5 = true
}

function on6Press(options) {
  keypresses.hb6 = true
}

function onUpstairsPress(options) {
  keypresses.upstairs = true
}

function onDownstairsPress(options) {
  keypresses.downstairs = true
}

function onQPress(options) {
  keypresses.q_press = true
}

function onMPress(options) {
  keypresses.m_press = true
}

function onBPress(options) {
  keypresses.b_press = true
}

function onKeyUp(options) {
  if (options.which === 87 || options.which === 38) {
    keypresses.up = false
  }
  else if (options.which === 83 || options.which === 40) {
    keypresses.down = false
  }
  else if (options.which === 65 || options.which === 37) {
    keypresses.left = false
  }
  else if (options.which === 68 || options.which === 39) {
    keypresses.right = false
  }
}

function onMouseMove(options) {
  var x = options.e.layerX
  var y = options.e.layerY
  if (x >= (window.view_x / 2) - 510 && x <= (window.view_x / 2) - 510 + (170 * 6) && y >= (window.view_y - 256)) {
    var left = (window.view_x / 2) - 510
    var x_in = x - left
    x_in = Math.floor(x_in / 170)
    window.mouseOverType = window.hand[x_in]
  } else {
    window.mouseOverType = -1
  }
}

function onMouseClick(options) {
  var x = options.e.layerX
  var y = options.e.layerY
  if (x >= (((window.view_x - 1020) / 2) + 1020) && x <= ((((window.view_x - 1020) / 2) + 1020) + (window.view_x - 1020) / 6) && y >= window.view_y - 84 && y <= window.view_y) {
    modalLaunchers.onBuyClick()
  } else if (x >= window.view_x - ((window.view_x - 1020) / 6) && x <= window.view_x && y >= window.view_y - 84 && y <= window.view_y) {
    modalLaunchers.showLog()
  } else if (x >= ((window.view_x - 1020) / 2) + 1020 && x <= window.view_x && y >= window.view_y - 84 && y <= window.view_y) {
    modalLaunchers.showDeck()
  }
}

export function processKeyPresses() {
  if (keypresses.up === true) {
    updater.sendSimpleMessage('push_up')
  }
  if (keypresses.down === true) {
    updater.sendSimpleMessage('push_down')
  }
  if (keypresses.left === true) {
    updater.sendSimpleMessage('push_left')
  }
  if (keypresses.right === true) {
    updater.sendSimpleMessage('push_right')
  }
  if (keypresses.hb1 === true) {
    updater.sendSimpleMessage('push_1')
  }
  if (keypresses.hb2 === true) {
    updater.sendSimpleMessage('push_2')
  }
  if (keypresses.hb3 === true) {
    updater.sendSimpleMessage('push_3')
  }
  if (keypresses.hb4 === true) {
    updater.sendSimpleMessage('push_4')
  }
  if (keypresses.hb5 === true) {
    updater.sendSimpleMessage('push_5')
  }
  if (keypresses.hb6 === true) {
    updater.sendSimpleMessage('push_6')
  }
  if (keypresses.upstairs === true) {
    updater.sendSimpleMessage('push_upstairs')
  }
  if (keypresses.downstairs === true) {
    updater.sendSimpleMessage('push_downstairs')
  }
  if (keypresses.q_press === true) {
    updater.sendSimpleMessage('push_q')
  }
  if (keypresses.m_press === true) {
    updater.sendSimpleMessage('push_m')
  }
  if (keypresses.b_press === true) {
    updater.sendSimpleMessage('push_b')
  }
  if (keypresses.tab_press === true) {
    updater.sendSimpleMessage('push_tab')
  }
  resetKeypresses()
}

var keyCodes = {
  9: onTabPress,
  87: onUpPress,
  38: onUpPress,
  83: onDownPress,
  40: onDownPress,
  65: onLeftPress,
  37: onLeftPress,
  68: onRightPress,
  39: onRightPress,
  49: on1Press,
  50: on2Press,
  51: on3Press,
  52: on4Press,
  53: on5Press,
  54: on6Press,
  188: onUpstairsPress,
  190: onDownstairsPress,
  66: onBPress,
  77: onMPress,
  81: onQPress
}
