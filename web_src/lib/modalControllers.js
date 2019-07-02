import angular from 'angular'
import * as dragDropBehaviors from 'dragDropBehaviors'
import * as constants from 'cardrpgConstants'
import {updater} from 'gameComm'
import {guid} from 'utils'

angular.module('cardrpg').controller('TutorialCtrl', function($scope, $uibModalInstance) {
  $scope.ok = function() {
    $uibModalInstance.close()
  }
})

angular.module('cardrpg').controller('NarrationCtrl', function($scope, $uibModalInstance) {
  $scope.narration = window.narration
  $scope.height = window.view_y - 200
  $scope.ok = function() {
    $uibModalInstance.close()
  }
})

angular.module('cardrpg').controller('ClassSelectCtrl', function($scope, $uibModalInstance) {
  window.classSelectScope = $scope
  $scope.update = function() {
    $scope.classDescription = constants.classDescriptions[$scope.selectedClass]
  }
  $scope.selectedClass = 'Archer'
  $scope.update()
  $scope.up = function() {
    if ($scope.selectedClass === 'Archer') {
      $scope.selectedClass = 'Cleric'
    } else if ($scope.selectedClass === 'Cleric') {
      $scope.selectedClass = 'Fighter'
    } else if ($scope.selectedClass === 'Fighter') {
      $scope.selectedClass = 'Paladin'
    } else if ($scope.selectedClass === 'Paladin') {
      $scope.selectedClass = 'Balance Mage'
    } else if ($scope.selectedClass === 'Balance Mage') {
      $scope.selectedClass = 'Inferno Mage'
    } else if ($scope.selectedClass === 'Inferno Mage') {
      $scope.selectedClass = 'Archer'
    }
    $scope.update()
    if (!$scope.$$phase) {
      $scope.$apply()
    }
  }
  $scope.down = function() {
    if ($scope.selectedClass === 'Archer') {
      $scope.selectedClass = 'Inferno Mage'
    } else if ($scope.selectedClass === 'Cleric') {
      $scope.selectedClass = 'Archer'
    } else if ($scope.selectedClass === 'Fighter') {
      $scope.selectedClass = 'Cleric'
    } else if ($scope.selectedClass === 'Paladin') {
      $scope.selectedClass = 'Fighter'
    } else if ($scope.selectedClass === 'Balance Mage') {
      $scope.selectedClass = 'Paladin'
    } else if ($scope.selectedClass === 'Inferno Mage') {
      $scope.selectedClass = 'Balance Mage'
    }
    $scope.update()
    if (!$scope.$$phase) {
      $scope.$apply()
    }
  }
  $scope.processKey = function(keycode) {
    if (keycode === 87 || keycode === 38) {
      $scope.up()
    } else if (keycode === 83 || keycode === 40) {
      $scope.down()
    } else if (keycode === 13) {
      $scope.ok()
    }
  }
  return $scope.ok = function() {
    var message = {}
    message.message = 'class_selected'
    message.class_selected = $scope.selectedClass
    updater.socket.send(JSON.stringify(message))
    $uibModalInstance.close()
  }
})

angular.module('cardrpg').controller('PruneDeckCtrl', function($scope, $uibModalInstance) {
  window.pruneDeckModalScope = $scope
  $scope.numberToKeep = window.numberToKeep
  $scope.starterNumberToKeep = window.starterNumberToKeep
  $scope.deck = []
  $scope.prune = []
  $scope.numberToKeep = window.numberToKeep
  for (let entry of window.deck) {
    var item = {name: constants.cardNames[entry], number: entry, uuid: guid()}
    if (entry <= 10) {
      item.color = 'green'
    } else {
      item.color = 'blue'
    }
    $scope.prune.push(item)
  }
  $scope.ok = function() {
    message = {}
    message.message = 'prune_request'
    message.prune = []
    for (let item of $scope.prune) {
      message.prune.push(item.number)
    }
    updater.socket.send(JSON.stringify(message))
    $uibModalInstance.close()
  }
})

angular.module('cardrpg').controller('TrashWarningCtrl', function($scope, $uibModalInstance) {
  $scope.text = 'You must trash exactly ' + String(window.trashNumber) + ' cards.'
  $scope.ok = function() {
    $uibModalInstance.close()
  }
})

angular.module('cardrpg').controller('TrashCtrl', function($scope, $uibModalInstance, $uibModal) {
  window.trashModalScope = $scope
  $scope.deck = []
  $scope.trash = []
  $scope.trashNumber = window.trashNumber
  for (let entry of window.deck) {
    var item = {name: constants.cardNames[entry], number: entry, uuid: guid()}
    $scope.deck.push(item)
  }
  if ($scope.deck.length <= window.trashNumber) {
    $uibModalInstance.close()
  }
  $scope.cancel = function() {
    $uibModalInstance.close()
  }
  $scope.ok = function() {
    if ($scope.trash.length === window.trashNumber) {
      var message = {}
      message.message = 'trash_request'
      message.trash = []
      for (let item of $scope.trash) {
        message.trash.push(item.number)
      }
      updater.socket.send(JSON.stringify(message))
      $uibModalInstance.close()
    } else {
      var modalInstance = window.uibModal.open({
        ariaLabelledBy: 'trash-warning-title',
        ariaDescribedBy: 'trash-warning-body',
        templateUrl: 'trash-warning.html',
        size: 'sm',
        controller: 'TrashWarningCtrl'
      })
    }
  }
})

angular.module('cardrpg').controller('ShopCtrl', function($scope, $uibModalInstance) {
  $scope.click = function(num) {
    var message = {}
    message.message = 'shop_click'
    message.num = num
    updater.socket.send(JSON.stringify(message))
    $scope.update()
  }
  $scope.allowMerge = function(num) {
    n = window.chains.indexOf(num + 'x')
    if (n === -1) {
      return false
    }
    if (parseInt(window.chains.slice(n+2, n+4)) < 4) {
      return false
    }
    return true
  }
  $scope.merge = function(num) {
    var message = {}
    message.message = 'merge_chains'
    message.num = num
    updater.socket.send(JSON.stringify(message))
    $scope.updateLoot()
  }
  $scope.getHighestCoin = function() {
    var highest = 0
    for (var i = 1; i <= 8; i++) {
      var n = window.chains.indexOf(i + 'x')
      if (n !== -1) {
        highest = i
      }
    }
    return highest
  }
  $scope.getColor = function(num) {
    if (num <= $scope.highestCoin) {
      return 'black'
    }
    return 'red'
  }
  $scope.getUnlockPointColor = function() {
    if ($scope.unlockPoints >= 1) {
      return 'black'
    }
    return 'red'
  }
  $scope.update = function() {
    setTimeout((function() {
      $scope.highestCoin = $scope.getHighestCoin()
      $scope.chains = window.chains
      $scope.unlockPoints = window.unlock_points
      if (!$scope.$$phase) {
        $scope.$apply()
      }
    }), 50)
  }
  $scope.ok = function() {
    $uibModalInstance.close()
  }
  $scope.update()
})

angular.module('cardrpg').controller('LootCtrl', function($scope, $uibModalInstance) {
  $scope.click = function(num, e) {
    var message = {}
    message.message = 'loot_click'
    message.num = num
    message.ctrl_click = e.ctrlKey
    updater.socket.send(JSON.stringify(message))
    $scope.updateLoot()
  }
  $scope.allowMerge = function(num) {
    var n = window.chains.indexOf(num + 'x')
    if (n === -1) {
      return false
    }
    var startPoint = n + 2
    var endPoint = n + 4
    if (parseInt(window.chains.slice(startPoint, endPoint)) < 4) {
      return false
    }
    return true
  }
  $scope.merge = function(num) {
    var message = {}
    message.message = 'merge_chains'
    message.num = num
    updater.socket.send(JSON.stringify(message))
    $scope.updateLoot()
  }
  $scope.getHighestCoin = function() {
    var highest = 0
    for (var i=1; i <= 8; i++) {
      var n = window.chains.indexOf(i + 'x')
      if (n !== -1) {
        highest = i
      }
    }
    return highest
  }
  $scope.updateLoot = function() {
    setTimeout((function() {
      $scope.drops = []
      var highestCoin = $scope.getHighestCoin()
      for (var i=0; i<window.drops.length; i++) {
        var drop = {}
        drop.stack = window.drop_depth[i]
        drop.cost = constants.cardXpTable[window.drops[i]]
        drop.texts = constants.cardText[window.drops[i]].split('\n')
        drop.img = 'assets/images/' + window.drops[i] + '.jpg'
        drop.fontSize = constants.fontSize[window.drops[i]]
        if (window.drop_unlocked[i] && drop.cost <= highestCoin) {
          drop.color = 'black'
        } else if (window.drop_unlocked[i]) {
          drop.color = 'gray'
        } else if (!window.drop_unlocked[i] && drop.cost <= highestCoin) {
          drop.color = 'red'
        } else {
          drop.color = '#AA4444'
        }
        $scope.drops.push(drop)
      }
      $scope.chains = window.chains
      $scope.unlockPoints = window.unlock_points
      if (!$scope.$$phase) {
        $scope.$apply()
      }
    }), 50)
  }
  $scope.ok = function() {
    $uibModalInstance.close()
  }
  $scope.updateLoot()
})

angular.module('cardrpg').controller('DeckCtrl', function($scope, $uibModalInstance) {
  $scope.update = function() {
    return setTimeout((function() {
      $scope.deck = []
      for (var i=0; i<window.deck.length; i++) {
        var item = {}
        item.texts = constants.cardText[window.deck[i]].split('\n')
        item.count = window.deckCounts[i]
        item.img = 'assets/images/' + window.deck[i] + '.jpg'
        item.fontSize = constants.fontSize[window.deck[i]]
        item.color = constants.backgroundColors[window.deck[i]]
        item.textColor = constants.textColors[window.deck[i]]
        $scope.deck.push(item)
      }
      if (!$scope.$$phase) {
        $scope.$apply()
      }
    }), 50)
  }
  $scope.ok = function() {
    $uibModalInstance.close()
  }
  window.deck = []
  window.deckCounts = []
  var message = {}
  message.message = 'request_deck'
  updater.socket.send(JSON.stringify(message))
  $scope.update()
})

angular.module('cardrpg').controller('BestiaryCtrl', function($scope, $uibModalInstance) {
  $scope.update = function() {
    setTimeout((function() {
      $scope.constants.mobColors = constants.mobColors
      $scope.mobClassDescriptions = constants.mobClassDescriptions2
      $scope.bestiary = window.bestiary
      for (let item of $scope.bestiary) {
        item.eyeColor = constants.mobEyeColors[item.name]
        if (!item.eyeColor) {
          item.eyeColor = 'yellow'
        }
        item.details = constants.mobDetails[item.name]
      }
      if (!$scope.$$phase) {
        $scope.$apply()
      }
    }), 50)
  }
  $scope.ok = function() {
    $uibModalInstance.close()
  }
  window.bestiary = []
  var message = {}
  message.message = 'request_bestiary'
  updater.socket.send(JSON.stringify(message))
  $scope.update()
})
