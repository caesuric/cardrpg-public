import angular from 'angular'
import app from 'cardrpg'
import * as modalControllers from 'modalControllers'

angular.module('cardrpg').controller('mainCtrl', function($scope, $uibModal) {
  window.uibModal = $uibModal
})
