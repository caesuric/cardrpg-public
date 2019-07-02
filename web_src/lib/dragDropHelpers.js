export function dragMoveListener(event) {
  var target, x, y
  target = event.target
  x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx
  y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy
  target.style.webkitTransform = target.style.transform = 'translate(' + x + 'px, ' + y + 'px)'
  target.setAttribute('data-x', x)
  target.setAttribute('data-y', y)
}

export function dropToTrash(uuid) {
  for (let item of window.trashModalScope.deck) {
    if (item.uuid === uuid) {
      window.trashModalScope.deck.splice(window.trashModalScope.deck.indexOf(item), 1)
      window.trashModalScope.trash.push(item)
      if (!window.trashModalScope.$$phase) {
        window.trashModalScope.$apply()
      }
      return
    }
  }
}

export function dropToDeck(uuid) {
  for (let item of window.trashModalScope.trash) {
    if (item.uuid === uuid) {
      window.trashModalScope.trash.splice(window.trashModalScope.trash.indexOf(item), 1)
      window.trashModalScope.deck.push(item)
      if (!window.trashModalScope.$$phase) {
        window.trashModalScope.$apply()
      }
      return
    }
  }
}

export function dropToPrune (uuid) {
  for (let item of window.pruneDeckModalScope.deck) {
    if (item.uuid === uuid) {
      window.pruneDeckModalScope.deck.splice(window.pruneDeckModalScope.deck.indexOf(item), 1)
      window.pruneDeckModalScope.prune.push(item)
      if (!window.pruneDeckModalScope.$$phase) {
        window.pruneDeckModalScope.$apply()
      }
      return
    }
  }
}

export function dropToPruneDeck(uuid) {
  for (let item of window.pruneDeckModalScope.prune) {
    if (item.uuid === uuid) {
      window.pruneDeckModalScope.prune.splice(window.pruneDeckModalScope.prune.indexOf(item), 1)
      window.pruneDeckModalScope.deck.push(item)
      if (!window.pruneDeckModalScope.$$phase) {
        window.pruneDeckModalScope.$apply()
      }
      return
    }
  }
}
