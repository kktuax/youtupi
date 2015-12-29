angular.module('settings', [])

.service('settingsService', ['localStorageService', function(localStorageService) {
  return {
    reset: function() {
      localStorageService.remove('settings');
    },
    set: function(settings) {
      localStorageService.set('settings',angular.toJson(settings));
    },
    get: function() {
      var lsSettings = localStorageService.get('settings');
      if(lsSettings !== null){
        return angular.fromJson(lsSettings);
      }else{
        return {
          ip: "192.168.1.11",
          searchPlaylists: false,
          engine: "youtube",
          enableHistory: true,
          quality: "High quality",
          numberOfResults: 50
          };
        }
      }
    };
}]);
