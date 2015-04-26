function getYoutubeQueryUrl(){
	var url;
	var query = $("#search-basic").val().trim();
	if(query != ''){
		url = 'https://www.googleapis.com/youtube/v3/search?order=relevance&part=snippet&q='+query+'&type=video&maxResults='+$('#slider').val()+'&key=AIzaSyAdAR3PofKiUSGFsfQ03FBEpVkVa1WA0J4';
	}
	return url;
}

function getYoutubeResponseVideos(response){
	var videos = [];
	var entries = response.items || [];
	for (var i = 0; i < entries.length; i++) {
		var entry = entries[i];
		if(typeof entry.video != 'undefined'){
			entry = entry.video;
		}
		var video = {}
		video.id = entry.id.videoId;
		video.description = entry.snippet.description;
		video.title = entry.snippet.title;
		video.duration = entry.duration;
		if(typeof entry.snippet.thumbnails != 'undefined'){
			if(typeof entry.snippet.thumbnails.high != 'undefined'){
				video.thumbnail = entry.snippet.thumbnails.high.url;
			}else if(typeof entry.snippet.thumbnails.medium != 'undefined'){
				video.thumbnail = entry.snippet.thumbnails.medium.url;
			}else{
				video.thumbnail = entry.snippet.thumbnails.default.url;
			}
		}
		video.type = "youtube";
		video.operations = [ {'name': 'download', 'text': 'Download', 'successMessage': 'Video downloaded'} ];
		video.format = $("#quality").val();
		videos.push(video);
	}
	return videos;
}
