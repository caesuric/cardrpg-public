export function initPruneDeckMenu(message) {
  window.pruning = true
  window.pruningDeck = true
  window.numberToKeep = message.number_to_keep
  window.starterNumberToKeep = message.starter_number_to_keep
  window.deck = message.deck
  var modalInstance = window.uibModal.open({
    ariaLabelledBy: 'prune-deck-title',
    ariaDescribedBy: 'prune-deck-body',
    templateUrl: 'prune-deck.html',
    size: 'lg',
    controller: 'PruneDeckCtrl',
    windowClass: 'xl-modal',
    backdrop: 'static',
    keyboard: 'false'
  }).closed.then(function() {
    window.pruningDeck = false
  })
}

export function showLog(options) {
  var modalInstance = window.uibModal.open({
    ariaLabelledBy: 'narration-title',
    ariaDescribedBy: 'narration-body',
    templateUrl: 'narration.html',
    size: 'lg',
    controller: 'NarrationCtrl',
    windowClass: 'xl-modal'
  })
}

export function showDeck(options) {
  var modalInstance = window.uibModal.open({
    ariaLabelledBy: 'deck-title',
    ariaDescribedBy: 'deck-body',
    templateUrl: 'deck.html',
    size: 'lg',
    controller: 'DeckCtrl',
    windowClass: 'xl-modal'
  })
}

export function showBestiary(options) {
  var modalInstance = window.uibModal.open({
    ariaLabelledBy: 'bestiary-title',
    ariaDescribedBy: 'bestiary-body',
    templateUrl: 'bestiary.html',
    size: 'lg',
    controller: 'BestiaryCtrl',
    windowClass: 'xl-modal'
  })
}

export function onBuyClick(options) {
  var modalInstance = window.uibModal.open({
    ariaLabelledBy: 'loot-title',
    ariaDescribedBy: 'loot-body',
    templateUrl: 'loot.html',
    size: 'lg',
    controller: 'LootCtrl',
    windowClass: 'xl-modal'
  })
}

export function initTrash(message) {
  window.trashNumber = message.number
  window.deck = message.deck
  var modalInstance = window.uibModal.open({
    ariaLabelledBy: 'trash-title',
    ariaDescribedBy: 'trash-body',
    templateUrl: 'trash.html',
    size: 'lg',
    controller: 'TrashCtrl',
    windowClass: 'xl-modal',
    backdrop: 'static',
    keyboard: 'false'
  })
}
export function goShopping() {
  var modalInstance = window.uibModal.open({
    ariaLabelledBy: 'shop-title',
    ariaDescribedBy: 'shop-body',
    templateUrl: 'shop.html',
    size: 'lg',
    controller: 'ShopCtrl',
    windowClass: 'xl-modal'
  })
}
