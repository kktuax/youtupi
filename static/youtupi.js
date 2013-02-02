function loadPlayList(entries){
	$("#playlist").empty();
	for (var i = 0; i < entries.length; i++) {
		var video = entries[i];
		var itemval = $('<li><a href="#"><img src="'+ video.thumbnail + '" /><h3>' + video.title + '</h3><p>'+video.description + '</p></a></li>');
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
	$("#search-basic").bind("change", function(event, ui) {
		$('#results').empty();
		$("#results").listview("refresh");
		if($("#search-basic").val() != ''){
			var url = 'http://gdata.youtube.com/feeds/api/' + 
				'videos?vq='+$("#search-basic").val()+'&max-results=15&v=2&alt=jsonc&orderby=relevance&sortorder=descending';
			$.getJSON(url, function(response){
				var entries = response.data.items || [];
				for (var i = 0; i < entries.length; i++) {
					var entry = entries[i];
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
