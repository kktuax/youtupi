function loadPlayList(entries){
	$("#playlist").empty();
	for (var i = 0; i < entries.length; i++) {
		var video = entries[i];
		var itemval = $('<li><a href="#"><img src="'+ video.thumbnail + '" /><h3>' + video.title + '</h3><p>'+video.description + '</p></a></li>');
		itemval.bind('click', {video: video}, function(event) {
			var server = $("#server").val();
			var url = server + "/control/play";
			var data = $.toJSON(event.data.video);
			$.post(url, data, loadPlayList, "json");
		});
		$("#playlist").append(itemval);
	}
	$("#playlist").listview("refresh");
}
function playerAction(paction){
	var server = $("#server").val();
	$.getJSON(
		server + "/control/"+paction, loadPlayList
	);
}
function loadVideo(video){
	$('#search').trigger('collapse');
	$("#spinner").show();
	video.type = "youtube";
	video.format = $("#quality").val();
	var server = $("#server").val();
	var url = server + "/playlist";
	var data = $.toJSON(video);
	$.post(url, data, function(entries){
		$("#spinner").hide();
		loadPlayList(entries);
	}, "json");
}
$(document).ready(function() {
	$("#server").val(window.location.protocol + "//" + window.location.host);
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
				url = 'http://gdata.youtube.com/feeds/api/videos?vq='+query+'&max-results=15&v=2&alt=jsonc&orderby=relevance&sortorder=descending';
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
					video.thumbnail = entry.thumbnail.sqDefault;
					var itemval = $('<li><a href="#"><img src="'+ video.thumbnail + '" /><h3>' + video.title + '</h3><p>'+video.description + '</p></a></li>');
					itemval.bind('click', {video: video}, function(event) {
						loadVideo(event.data.video);
					});
					$("#results").append(itemval);
				}
				$("#results").listview("refresh");
			});
		}
	});
	window.setInterval(function(){
		var server = $("#server").val();
		$.getJSON(
			server + "/playlist", loadPlayList
		);
	}, 3000);
});
