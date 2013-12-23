function getYoutubeQueryUrl(){
	var url;
	var query = $("#search-basic").val();
	if(query != ''){
		if(query.substring(0, 2) == "u:"){
			query = query.substring(2, query.length);
			url = 'https://gdata.youtube.com/feeds/api/users/'+query+'/uploads?v=2&alt=jsonc';
		}else if(query.substring(0, 2) == "f:"){
			query = query.substring(2, query.length);
			url = 'http://gdata.youtube.com/feeds/api/users/'+query+'/favorites?v=2&alt=jsonc';
		}else{
			url = 'http://gdata.youtube.com/feeds/api/videos?vq='+query+'&max-results='+$('#slider').val()+'&v=2&alt=jsonc&orderby=relevance&sortorder=descending';
		}
	}
	return url;
}

function getYoutubeResponseVideos(response){
	var videos = [];
	var entries = response.data.items || [];
	for (var i = 0; i < entries.length; i++) {
		var entry = entries[i];
		if(typeof entry.video != 'undefined'){
			entry = entry.video;
		}
		var video = {}
		video.id = entry.id;
		video.description = entry.description;
		video.title = entry.title;
		video.duration = entry.duration;
		if(typeof entry.thumbnail != 'undefined'){
			if(typeof entry.thumbnail.hqDefault != 'undefined'){
				video.thumbnail = entry.thumbnail.hqDefault;
			}else if(typeof entry.thumbnail.sqDefault != 'undefined'){
				video.thumbnail = entry.thumbnail.sqDefault;
			}
		}
		video.type = "youtube";
		video.format = $("#quality").val();
		videos.push(video);
	}
	return videos;
}