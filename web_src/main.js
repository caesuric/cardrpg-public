import $ from 'jquery'

import app from 'cardrpgAngularApp'
import * as angularObjects from 'angularObjects'
import {init} from 'init'
import {updater} from 'gameComm'
import * as narrationLog from 'narrationLog'
import * as graphics from 'graphics'
import * as input from 'input'
import * as audio from 'audio'

require('../node_modules/bootstrap/dist/css/bootstrap.min.css')
require('../node_modules/font-awesome/css/font-awesome.min.css')
require('cardrpg.css')

$(document).ready(function() {
  init()
  narrationLog.init()
  graphics.init()
  input.init()
  audio.init()
  updater.start()
})
