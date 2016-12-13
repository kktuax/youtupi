
var Search = {
  server: '',
  engine: '',
  query: '',
  format: '',
  results: [],
  count: 50,
  pageNumber: 1,
  nextPageAvailable: false,
  search: function(callback){
    this.fetchResults(function(s){
      s.processResults();
      if(callback !== undefined){
        callback(s);
      }
    });
  },
  fetchResults: function(callback){
    var search = this;
    search.results = [];
    var url = this.url();
    if(url === undefined){
      callback(search);
      return;
    }
    $.getJSON(url, { 'search': this.query, 'count': this.count, 'format': this.format, 'pageNumber': this.pageNumber }, function(response){
      search.results = search.results.concat(response);
      callback(search);
    });
  },
  url: function(){
    return this.server + "/" + this.engine + "-search";
  },
  processResults: function(){
    var start = this.count * (this.pageNumber - 1);
    if(this.results.length > (start + this.count)){
      this.nextPageAvailable = true;
    }
    this.results = this.results.slice(start, start + this.count);
  },
  incrementPageNumber: function(callback){
    this.pageNumber = this.pageNumber + 1;
    this.search(callback);
  }
};

var HistorySearch = Object.create(Search);
HistorySearch.fetchResults = function(callback){
  var search = this;
  search.results = [];
  if(supports_html5_storage()){
    var history = localStorage.getObj("history");
    if(history != undefined){
      search.results = $.map(Object.keys(history), function(value, index) {
        return history[value];
      }).sort(function (a, b) {
        return b.lastPlayed > a.lastPlayed;
      });
    }
  }
  callback(search);
};
HistorySearch.clearHistory = function (){
  if(supports_html5_storage()){
    localStorage.setObj("history", {});
  }
};
HistorySearch.maxHistoryElements = 50;
HistorySearch.saveVideoToHistory = function(video){
  if(!supports_html5_storage()){
    return;
  }
  var history = localStorage.getObj("history");
  if(history == undefined){
    history = {};
  }
  if(video.id in Object.keys(history)){
    var existingVideo = history[video.id];
    existingVideo.lastPlayed = new Date();
  }else{
    video.lastPlayed = new Date();
    history[video.id] = video;
  }
  if(Object.keys(history).length > HistorySearch.maxHistoryElements){
    var lastVideo = $.map(Object.keys(history), function(value, index) {
      return history[value];
    }).sort(function (a, b) {
      return b.lastPlayed < a.lastPlayed;
    })[0];
    delete history[lastVideo.id];
  }
  localStorage.setObj("history", history);
};

var LocalDirSearch = Object.create(Search);
LocalDirSearch.engine = 'local-dir';
LocalDirSearch.url = function(){
  return this.server + "/local-browse";
};

var YoutubeSearch = Object.create(Search);
YoutubeSearch.engine = 'youtube';
YoutubeSearch.url = function(){
	if(this.query == ''){
		return undefined;
	}
	var url = 'https://www.googleapis.com/youtube/v3/';
	var key = '&key=AIzaSyAdAR3PofKiUSGFsfQ03FBEpVkVa1WA0J4';
	var maxResults = '&maxResults='+this.count;
	if(this.pageNumber > 1){
		maxResults += "&pageToken=" + this.pageToken;
	}
	var listLookup = 'list:';
	var listsLookup = 'lists:';
	if(this.query.indexOf(listLookup) > -1){
		var lid = this.query.split(listLookup);
		url += 'playlistItems?part=snippet&playlistId='+lid[1]+'&type=video' + maxResults + key;
	} else if(this.query.indexOf(listsLookup) > -1){
		var lid = this.query.split(listsLookup);
		url += 'search?order=relevance&part=snippet&q='+lid[1]+'&type=playlist' + maxResults + key;
	} else {
		url += 'search?order=relevance&part=snippet&q='+this.query+'&type=video' + maxResults + key;
	}
	return url;
};
YoutubeSearch.processResults = function(){};
YoutubeSearch.fetchResults = function(callback){
  var search = this;
  search.results = [];
  var url = this.url();
  if(url == undefined){
    callback(search);
    return;
  }
  $.getJSON(url, undefined, function(response){
    search.pageToken = undefined;
    if(response.nextPageToken != undefined){
      search.nextPageAvailable = true;
      search.pageToken = response.nextPageToken;
    }
    var entries = response.items || [];
    for (var i = 0; i < entries.length; i++) {
      var entry = entries[i];
      var video = search.createPlaylist(entry);
      if(video === null){
        video = search.createVideo(entry);
      }
      search.results.push(video);
    }
    callback(search);
  });
};
YoutubeSearch.createPlaylist = function(entry){
	if(typeof entry.id != 'undefined'){
		if(entry.id.kind != 'youtube#playlist'){
			return null;
		}
	}else{
		return null;
	}
	var video = {};
	video.id = "list:" + entry.id.playlistId;
	video.title = entry.snippet.title;
	video.description = entry.snippet.description;
	video.thumbnail = this.thumbnailFromSnippet(entry.snippet);
	video.type = "search";
	video.operations = [];
	return video;
};
YoutubeSearch.thumbnailFromSnippet = function(snippet){
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
YoutubeSearch.createVideo = function(entry){
	if(typeof entry.video != 'undefined'){
		entry = entry.video;
	}
	var video = {};
	if(typeof entry.id.videoId != 'undefined'){
		video.id = entry.id.videoId;
	} else {
		video.id = entry.snippet.resourceId.videoId;
	}
	video.description = entry.snippet.description;
	video.title = entry.snippet.title;
	video.duration = entry.duration;
	video.thumbnail = this.thumbnailFromSnippet(entry.snippet);
	video.type = "youtube";
	video.operations = [ {'name': 'download', 'text': 'Download', 'successMessage': 'Video downloaded'} ];
	return video;
};

var availableSearchEngines = [YoutubeSearch, LocalDirSearch, Search];

function createSearch(query, selectedEngine, count, format){
  var searchPrototype;
  if(query == 'youtupi:history'){
    searchPrototype = HistorySearch;
  }else{
    for (var i = 0; i < availableSearchEngines.length; i++) {
      searchPrototype = availableSearchEngines[i];
      if(searchPrototype.engine == selectedEngine){
        break;
      }
    }
  }
  var search = Object.create(searchPrototype);
  search.server = server;
  search.engine = selectedEngine;
  search.count = count;
  search.format = format;
  search.query = query;
  return search;
}
