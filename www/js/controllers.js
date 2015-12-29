angular.module('starter.controllers', [])

.controller('DashCtrl', function($scope) {})

.controller('SearchCtrl', function($scope, settingsService, youtubeService) {
  // With the new view caching in Ionic, Controllers are only called
  // when they are recreated or on app start, instead of every page change.
  // To listen for when this page is active (for example, to refresh data),
  // listen for the $ionicView.enter event:
  //
  //$scope.$on('$ionicView.enter', function(e) {
  //});
  $scope.settings = settingsService.get();
  $scope.videos = [];
  $scope.search = function(query) {
    if($scope.settings.engine == "youtube"){
      youtubeService.search(query, $scope.settings.numberOfResults, 1, function(videos){
        $scope.videos = [];
        $scope.videos = $scope.videos.concat(videos);
      });
    }
  };

  $scope.duration = function getDurationString(time){
  	if(time == undefined) return "";
  	var duration = "";
  	var hours = Math.floor(time / 3600);
  	if(hours > 0) duration = duration + hours + ":";
  	time = time - hours * 3600;
  	var minutes = Math.floor(time / 60);
  	duration = duration + (((minutes < 10) && (hours > 0)) ? ("0" + minutes) : minutes);
  	var seconds = time - minutes * 60;
  	duration = duration + ((seconds < 10) ? (":0" + seconds) : (":" + seconds));
  	return duration;
  };

})

.controller('ChatDetailCtrl', function($scope, $stateParams, Chats) {
  $scope.chat = Chats.get($stateParams.chatId);
})

.controller('SettingsCtrl', function($scope, settingsService) {
  $scope.reset = function() {
    settingsService.reset();
    $scope.settings = settingsService.get();
  };
  $scope.$watch('settings', function(value){
    settingsService.set(value);
  }, true);
  $scope.settings = settingsService.get();
});
