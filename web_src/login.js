import angular from 'angular'
import $ from 'jquery'

import app from 'cardrpgAngularApp'
import errorCtrl from 'errorModal'
import {updater} from 'loginComm'
import loginCtrl from 'loginCtrl'
import classDescriptions from 'constants'

require('../node_modules/angularjs-color-picker/dist/angularjs-color-picker.min.css')
require('../node_modules/bootstrap/dist/css/bootstrap.min.css')
require('../node_modules/font-awesome/css/font-awesome.css')
require('cardrpg.css')

$(document).ready(function() {
  updater.start()
})
