import * as constants from 'cardrpgConstants'
import {updater} from 'loginComm'

export var loginCtrl = angular.module('cardrpg').controller('loginCtrl', function($scope, $uibModal) {
  window.uibModal = $uibModal
  window.scope = $scope
  $scope.mode = 'login'
  $scope.classDescription = ''
  $scope.colorPickerOptions = {}
  $scope.colorPickerOptions.alpha = false
  $scope.colorPickerOptions.swatchOnly = true
  $scope.colorPickerOptions.format = 'hexString'
  $scope.updateClassDescription = function(type) {
    $scope.classDescription = constants.classDescriptions[type]
  }
  $scope.login = function() {
    var message = {}
    message.message = 'login'
    message.username = $scope.username
    message.password = $scope.password
    updater.socket.send(JSON.stringify(message))
  }
  $scope.register = function() {
    var message = {}
    message.message = 'register'
    message.username = $scope.username
    message.password = $scope.password
    updater.socket.send(JSON.stringify(message))
  }
  $scope.newCharacter = function() {
    $scope.mode = 'newCharacter'
  }
  $scope.selectClass = function(selection) {
    $scope.classSelected = selection
    $scope.characterColor = '#0000FF'
    $scope.eyeColor = '#FFFF00'
    $scope.characterName = ''
    $scope.mode = 'customizeCharacter'
  }
  $scope.finalizeCharacter = function() {
    var message = {}
    message.message = 'finalize_character'
    message.class_selected = $scope.classSelected
    message.name = $scope.characterName
    message.color = $scope.characterColor
    message.eye_color = $scope.eyeColor
    updater.socket.send(JSON.stringify(message))
  }
  $scope.cancelCharacter = function() {
    $scope.mode = 'character'
  }
  $scope.selectCharacter = function(character) {
    $scope.selectedCharacter = character
    var message = {}
    message.message = 'request_games'
    updater.socket.send(JSON.stringify(message))
  }
  $scope.newGame = function() {
    var message = {}
    message.message = 'new_game'
    message.character = $scope.selectedCharacter.uuid
    updater.socket.send(JSON.stringify(message))
  }
  $scope.loadGame = function(game) {
    var message = {}
    message.message = 'load_game'
    message.character = $scope.selectedCharacter.uuid
    message.game = game.uuid
    window.character_uuid = message.character
    window.game_uuid = message.game
    updater.socket.send(JSON.stringify(message))
  }
  $scope.joinGame = function(game) {
    var message = {}
    message.message = 'join_game'
    message.character = $scope.selectedCharacter.uuid
    message.game = game.uuid
    window.character_uuid = message.character
    window.game_uuid = message.game
    updater.socket.send(JSON.stringify(message))
  }
})
