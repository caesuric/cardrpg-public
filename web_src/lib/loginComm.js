export var updater = {
  socket: null,
  start: function() {
    var url
    url = 'ws://' + location.host + '/loginsocket'
    updater.socket = new WebSocket(url)
    updater.socket.onmessage = function(event) {
      updater.processMessage(JSON.parse(event.data))
    }
    updater.socket.onopen = updater.initialize
    updater.socket.onclose = updater.close
    updater.loot_update = true
    window.updater = this
  },
  initialize: function() {
    console.log('connected')
  },
  close: function() {
    console.log('CONNECTION CLOSED')
    setTimeout((function() {
      var url
      url = 'ws://' + location.host + '/loginsocket'
      updater.socket = new WebSocket(url)
      updater.socket.onmessage = function(event) {
        return updater.processMessage(JSON.parse(event.data))
      }
      updater.socket.onopen = updater.initialize
      updater.socket.onclose = updater.close
    }), 0.5 * 1000)
  },
  processMessage: function(message) {
    console.log(message)
    if (messageLookup[message.message]!=undefined) {
      messageLookup[message.message](message)
    }
  }
}

var messageLookup = {
  'error': function(message) {
    window.errorMessage = message.error
    var modalInstance = window.uibModal.open({
      ariaLabelledBy: 'error-title',
      ariaDescribedBy: 'error-body',
      templateUrl: 'error.html',
      size: 'sm',
      controller: 'errorCtrl'
    })
  },
  'character_select': function(message) {
    window.scope.mode = 'character'
    window.scope.characters = message.characters
    if (!window.scope.$$phase) {
      window.scope.$apply()
    }
  },
  'game_select': function(message) {
    window.scope.mode = 'game'
    window.scope.runningGames = message.running_games
    window.scope.savedGames = message.saved_games
    if (!window.scope.$$phase) {
      window.scope.$apply()
    }
  },
  'enter_game': function(message) {
    localStorage.setItem('cardrpg_game', window.game_uuid)
    localStorage.setItem('cardrpg_character', window.character_uuid)
    window.location.href = '/game.html'
  }
}
