angular.module('starter.controllers', [])

.controller('DashCtrl', function($scope) {})

.controller('ChatsCtrl', function($scope, Chats) {
  // With the new view caching in Ionic, Controllers are only called
  // when they are recreated or on app start, instead of every page change.
  // To listen for when this page is active (for example, to refresh data),
  // listen for the $ionicView.enter event:
  //
  //$scope.$on('$ionicView.enter', function(e) {
  //});

  $scope.chats = Chats.all();
  $scope.remove = function(chat) {
    Chats.remove(chat);
  };
})

.controller('ChatDetailCtrl', function($scope, $stateParams, Chats) {
  $scope.chat = Chats.get($stateParams.chatId);
})

.controller('SettingsCtrl', function($scope, localStorageService) {
  $scope.reset = function() {
    localStorageService.remove('settings');
    $scope.assign();
  };

  $scope.assign = function() {
    var lsSettings = localStorageService.get('settings');
    if(lsSettings !== null){
      $scope.settings = angular.fromJson(lsSettings);
    }else{
      $scope.settings = {
        ip: "192.168.1.11",
        searchPlaylists: false,
        engine: "youtube",
        enableHistory: true,
        quality: "High quality",
        numberOfResults: 50
      };
    }
  };

  $scope.$watch('settings', function(value){
    localStorageService.set('settings',angular.toJson(value));
  }, true);
  $scope.assign();
});
