import * as helpers from 'dragDropHelpers'

interact('.draggable').draggable({
  inertia: true,
  autoScroll: true,
  onmove: helpers.dragMoveListener,
  onend: function(event) {
    var target
    target = event.target
    target.style.webkitTransform = target.style.transform = 'translate(0px, 0px)'
    target.setAttribute('data-x', 0)
    target.setAttribute('data-y', 0)
    target.classList.remove('can-drop')
  }
})

interact('.dropzone').dropzone({
  accept: '.draggable',
  overlap: 0.75,
  ondropactivate: function(event) {
    event.target.classList.add('drop-active')
  },
  ondropdeactivate: function(event) {
    event.target.classList.remove('drop-active')
    event.target.classList.remove('drop-target')
  },
  ondragenter: function(event) {
    var draggableElement = event.relatedTarget
    var dropzoneElement = event.target
    dropzoneElement.classList.add('drop-target')
    draggableElement.classList.add('can-drop')
  },
  ondragleave: function(event) {
    var draggableElement = event.relatedTarget
    var dropzoneElement = event.target
    dropzoneElement.classList.remove('drop-target')
    draggableElement.classList.remove('can-drop')
  },
  ondrop: function(event) {
    if (event.target.id === 'trash-drop') {
      helpers.dropToTrash(angular.element(event.relatedTarget).scope().item.uuid)
    }
    else if (event.target.id === 'deck-drop') {
      helpers.dropToDeck(angular.element(event.relatedTarget).scope().item.uuid)
    }
  }
})

interact('.prune-dropzone').dropzone({
  accept: '.draggable',
  overlap: 0.75,
  ondropactivate: function(event) {
    event.target.classList.add('drop-active')
  },
  ondropdeactivate: function(event) {
    event.target.classList.remove('drop-active')
    event.target.classList.remove('drop-target')
  },
  ondragenter: function(event) {
    var draggableElement = event.relatedTarget
    var dropzoneElement = event.target
    dropzoneElement.classList.add('drop-target')
    draggableElement.classList.add('can-drop')
  },
  ondragleave: function(event) {
    var draggableElement = event.relatedTarget
    var dropzoneElement = event.target
    dropzoneElement.classList.remove('drop-target')
    draggableElement.classList.remove('can-drop')
  },
  ondrop: function(event) {
    if (event.target.id === 'prune-drop') {
      helpers.dropToPrune(angular.element(event.relatedTarget).scope().item.uuid)
    }
    else if (event.target.id === 'prune-deck-drop') {
      helpers.dropToPruneDeck(angular.element(event.relatedTarget).scope().item.uuid)
    }
  }
})
