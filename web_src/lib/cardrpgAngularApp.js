import angular from 'angular'
import * as angularUiBootstrap from 'angular-ui-bootstrap';
import tinycolor from 'tinycolor2'
import * as colorPicker from 'angularjs-color-picker'

export var app = angular.module('cardrpg', ['ui.bootstrap', 'color.picker']).config([
  '$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken'
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
  }
])
