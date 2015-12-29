angular.module('youtube', [])

.service('youtubeService', ['$http', function($http) {

  var nextPageToken = null;

  var getYoutubeQueryUrl = function (query, pageSize, pageNumber){
  	var url = 'https://www.googleapis.com/youtube/v3/';
  	var key = '&key=AIzaSyAdAR3PofKiUSGFsfQ03FBEpVkVa1WA0J4';
    var maxResults = '&maxResults=' + pageSize;
  	if(pageNumber > 1){
  		maxResults += "&pageToken=" + nextPageToken;
  	}
  	var listLookup = 'list:';
  	var listsLookup = 'lists:';
  	if(query.indexOf(listLookup) > -1){
  		var lid = query.split(listLookup);
  		url += 'playlistItems?part=snippet&playlistId='+encodeURIComponent(lid[1])+'&type=video' + maxResults + key;
  	} else if(query.indexOf(listsLookup) > -1){
  		var lid = query.split(listsLookup);
  		url += 'search?order=relevance&part=snippet&q='+encodeURIComponent(lid[1])+'&type=playlist' + maxResults + key;
  	} else {
  		url += 'search?order=relevance&part=snippet&q='+encodeURIComponent(query)+'&type=video' + maxResults + key;
  	}
  	return url;
  };

  var getYoutubeResponseVideos = function (response){
  	var videos = [];
    response = response.data;
  	var entries = response.items || [];
  	for (var i = 0; i < entries.length; i++) {
  		var entry = entries[i];
  		var video = createYoutubePlaylist(entry);
  		if(video === null){
  			video = createYoutubeVideo(entry);
  		}
      if(video !== null){
        videos.push(video);
      }
  	}
  	return videos;
  };

  var getYoutubeNextPage = function (response){
  	if(response.nextPageToken != undefined){
      nextPageToken = response.nextPageToken;
  		return true;
  	}
  	return false;
  };

  var createYoutubePlaylist = function(entry){
  	if(typeof entry.id != 'undefined'){
  		if(entry.id.kind != 'youtube#playlist'){
  			return null;
  		}
  	}else{
  		return null;
  	}
  	var video = {}
  	video.id = entry.id.playlistId;
  	video.title = entry.snippet.title;
  	video.description = entry.snippet.description;
  	video.thumbnail = thumbnailFromYoutubeSnippet(entry.snippet);
  	video.type = "youtube:playlist";
  	video.operations = [];
  	return video;
  };

  var thumbnailFromYoutubeSnippet = function (snippet){
  	if(typeof snippet.thumbnails != 'undefined'){
  		if(typeof snippet.thumbnails.high != 'undefined'){
  			return snippet.thumbnails.high.url;
  		}else if(typeof snippet.thumbnails.medium != 'undefined'){
  			return snippet.thumbnails.medium.url;
  		}else{
  			return snippet.thumbnails.default.url;
  		}
  	}
  	return null;
  };

  var createYoutubeVideo = function(entry){
  	if(typeof entry.video != 'undefined'){
  		entry = entry.video;
  	}
  	var video = {}
  	if(typeof entry.id.videoId != 'undefined'){
  		video.id = entry.id.videoId;
    } else if(typeof entry.snippet.resourceId != 'undefined'){
      video.id = entry.snippet.resourceId.videoId;
  	} else {
      console.debug("Unkown video id");
  		return null;
  	}
  	video.description = entry.snippet.description;
  	video.title = entry.snippet.title;
  	video.duration = entry.duration;
  	video.thumbnail = thumbnailFromYoutubeSnippet(entry.snippet);
  	video.type = "youtube";
  	video.operations = [ {'name': 'download', 'text': 'Download', 'successMessage': 'Video downloaded'} ];
  	return video;
  };

  var isInt = function (value) {
    return !isNaN(value) && parseInt(Number(value)) == value && !isNaN(parseInt(value, 10));
  };

  return {
    engineName: 'youtube',
    multiPageSupport: true,
    search: function(query, maxResults, pageNumber, videosCallback) {
      if((!query) || (!isInt(maxResults)) || (!isInt(pageNumber))){
        videosCallback([]);
      }else{
        var url = getYoutubeQueryUrl(query, maxResults, pageNumber);
        $http.get(url).then(function (response) {
          getYoutubeNextPage(response);
          var videos = getYoutubeResponseVideos(response);
          videosCallback(videos);
        }, function(reason) {
          videosCallback([]);
          console.debug('Failed: ' + reason);
        });
      }
    }
  };
}]);
