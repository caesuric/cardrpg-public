export var errorCtrl = angular.module('cardrpg').controller('errorCtrl', function($scope, $uibModalInstance) {
  $scope.errorMessage = window.errorMessage
  return $scope.ok = function() {
    return $uibModalInstance.close()
  }
})
