var server = window.location.protocol + "//" + window.location.host;

$(document).bind('pageinit', function () {
    $.mobile.defaultPageTransition = 'none';
});

function fillVideoList(entries, listSelect, clickEvent){
	$(listSelect).empty();
	for (var i = 0; i < entries.length; i++) {
		var video = entries[i];
		thumbnail = "images/video.png";
		if(video.thumbnail != undefined){
			thumbnail = video.thumbnail;
		}
		var itemval = $('<li><a href="#"><img src="'+ thumbnail + '" /><h3>' + video.title + '</h3><p>'+video.description + '</p></a></li>');
		itemval.bind('click', {video: video}, clickEvent);
		$(listSelect).append(itemval);
	}
	$(listSelect).listview("refresh");
}

function loadPlayList(entries){
	fillVideoList(entries, "#playlist-list", function(event) {
		var url = server + "/control/play";
		var data = $.toJSON(event.data.video);
		$.post(url, data, loadPlayList, "json");
	});
}

function playerAction(paction){
	$.getJSON(
		server + "/control/" + paction, loadPlayList
	);
}
function loadVideo(video){
	tabPlaylist();
	$("#spinner").show();
	var url = server + "/playlist";
	var data = $.toJSON(video);
	$.post(url, data, function(entries){
		$("#spinner").hide();
		loadPlayList(entries);
	}, "json");
}
function tabPlaylist(){
	$(".link-playlist").first().trigger('click');
}

$(document).delegate("#youtube", "pageinit", function() {
	$("#search-basic").bind("change", function(event, ui) {
		$('#results').empty();
		$("#results").listview("refresh");
		var query = $("#search-basic").val();
		if(query != ''){
			var url;
			if(query.substring(0, 2) == "u:"){
				query = query.substring(2, query.length);
				url = 'https://gdata.youtube.com/feeds/api/users/'+query+'/uploads?v=2&alt=jsonc';
			}else if(query.substring(0, 2) == "f:"){
				query = query.substring(2, query.length);
				url = 'http://gdata.youtube.com/feeds/api/users/'+query+'/favorites?v=2&alt=jsonc';
			}else{
				url = 'http://gdata.youtube.com/feeds/api/videos?vq='+query+'&max-results='+$('#slider').val()+'&v=2&alt=jsonc&orderby=relevance&sortorder=descending';
			}
			$.getJSON(url, function(response){
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
					video.thumbnail = "images/video.png";
					if(typeof entry.thumbnail != 'undefined'){
						if(typeof entry.thumbnail.hqDefault != 'undefined'){
							video.thumbnail = entry.thumbnail.hqDefault;
						}else if(typeof entry.thumbnail.sqDefault != 'undefined'){
							video.thumbnail = entry.thumbnail.sqDefault;
						}
					}
					video.type = "youtube";
					video.format = $("#quality").val();
					var itemval = $('<li><a href="#"><img src="'+ video.thumbnail + '" /><h3>' + video.title + ' (' + Math.round(video.duration/60) + ':' + video.duration % 60 + ')' + '</h3><p>'+video.description + '</p></a></li>');
					itemval.bind('click', {video: video}, function(event) {
						loadVideo(event.data.video);
					});
					$("#results").append(itemval);
				}
				$("#results").listview("refresh");
			});
		}
	});
});

$(document).delegate("#files", "pageinit", function() {
	$.getJSON(
		server + "/local", function(entries){
			fillVideoList(entries, "#filelist", function(event) {
				loadVideo(event.data.video);
			});
		}
	);
});

$(document).delegate("#playlist", "pageinit", function() {
	window.setInterval(function(){
		$.getJSON(
			server + "/playlist", loadPlayList
		);
	}, 3000);
});
