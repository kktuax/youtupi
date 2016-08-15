var server = window.location.protocol + "//" + window.location.host;

$(document).bind('pageinit', function () {
    $.mobile.defaultPageTransition = 'none';
});

/**
 * Refresh listview with array of videos
 * @param {entries} array of videos
 * @param {listSelect} selector of listview to update
 * @param {function} event on video click, by default adds to playlist
 * */
function fillVideoList(entries, listSelect, clickEvent){
	if(typeof clickEvent === 'undefined') {
		clickEvent = function(event){
			loadVideo(event.data.video);
		};
	}
	$(listSelect).empty();
	for (var i = 0; i < entries.length; i++) {
		var video = entries[i];
		if((i == 0) && (listSelect == "#playlist-list")){
			adjustCurrentPositionSlider(video.duration, video.position);
		}
		thumbnail = "images/video.png";
		if(video.thumbnail != undefined){
			thumbnail = video.thumbnail;
		}
		var	duration = getDurationString(video.duration);
		if(duration){
			duration = " [" + duration + "]";
		}
		var itemval = $('<li data-video-id="' + video.id + '"><a href="#"><img src="'+ thumbnail + '" /><h3>' + video.title + duration + '</h3><p>' + video.description + '</p></a></li>');
		itemval.bind('click', {video: video}, clickEvent);
		$(listSelect).append(itemval);
	}
	$(listSelect).listview("refresh");
}

function adjustCurrentPositionSlider(duration, position){
	var positionPct = (position != undefined && duration != undefined) ? 100*position/duration : 0;
	$("#position").val(positionPct);
	if(duration != undefined){
		if(duration !=  $("#position").data("duration")){
			$("#position").data("duration", duration);
		}
	}
	$("#position").slider("refresh");
}

function getDurationString(time){
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
}

/**
 * Load playlist items with play video on click event
 * */
function loadPlayList(entries){
	updateControls(entries.length);
	fillVideoList(entries, "#playlist-list", function(event) {
		var data = $.toJSON(event.data.video);
		var playBtn = {
			click: function () {
				var url = server + "/control/play";
				$.post(url, data, loadPlayList, "json");
			},
			close: true
		};
		var playNextBtn = {
			click: function () {
				var url = server + "/control/playNext";
				$.post(url, data, loadPlayList, "json");
			},
			close: true
		};
		var deleteBtn = {
			click: function () {
				var url = server + "/playlist";
				$.ajax({url: url, type: 'DELETE', data: data, dataType: 'json', success: loadPlayList});
			},
			close: true
		};
		var buttons = { 'Play': playBtn, 'Play Next': playNextBtn, 'Skip': deleteBtn };
		for(operationKey in event.data.video.operations){
			var operation = event.data.video.operations[operationKey];
			var type = event.data.video.type;
			var buttonClick = function(e, type, operation, data){
				var successFunction = function(){
					showNotification(operation.successMessage);
				}
				var url = server + "/" + type + "-" + operation.name;
				$.post(url, data).done(successFunction, "json");
			}
			buttons[operation.text] = {
				click: buttonClick,
				args: new Array(type, operation, data),
				close: true
			};
		}
		$(document).simpledialog2({
			mode: 'button',
			headerText: event.data.video.title,
			headerClose: true,
			buttons : buttons
		});
	});
}

function updateControls(playListLength){
	if(playListLength == 0){
		$("#playlist-empty").show();
		$("#playlist-playing").hide();
		$("#next-button").addClass("ui-disabled");
		$("#pause-button").addClass("ui-disabled");
		$("#stop-button").addClass("ui-disabled");
		$("#player-button").addClass("ui-disabled");
	}else{
		$("#playlist-empty").hide();
		$("#playlist-playing").show();
		if(playListLength > 1){
			$("#next-button").removeClass("ui-disabled");
		}
		$("#pause-button").removeClass("ui-disabled");
		$("#player-button").removeClass("ui-disabled");
		$("#stop-button").removeClass("ui-disabled");
	}
}

function updateSearchControls(results, nextPageAvailable){
  resultsLength = results.length
  $("#add-all-button").unbind("click");
	if(resultsLength == 0){
		$("#results-empty").show();
		$("#add-all-button").addClass("ui-disabled");
		$("#add-all-random-button").addClass("ui-disabled");
	}else{
    $("#add-all-button").bind("click", function(event, ui) {
      loadVideos(results);
    });
		$("#results-empty").hide();
		$("#add-all-button").removeClass("ui-disabled");
		$("#add-all-random-button").removeClass("ui-disabled");
	}
	if(nextPageAvailable){
		$("#next-page-button").removeClass("ui-disabled");
	}else{
		$("#next-page-button").addClass("ui-disabled");
	}
}

function playerAction(paction){
	$.getJSON(
		server + "/control/" + paction, loadPlayList
	);
}

function loadVideos(videos){
	tabPlaylist();
	$("#spinner").show();
  for (var i = 0; i < videos.length; i++) {
    video = videos[i];
    if(video.type == "youtube"){
      video.format = $("#quality").val();
    }
  }
  var url = server + "/playlist";
	$.post(url, $.toJSON(videos), function(entries){
		loadPlayList(entries);
	}, "json").fail(function() {
		showNotification("Error loading videos");
  }).done(function() {
    if('on' == $('#save-history').val()){
      for (var i = 0; i < videos.length; i++) {
        video = videos[i];
        saveVideoToHistory(video);
      }
		}
	}).always(function() {
		$("#spinner").hide();
	});
}

function loadVideo(video){
	if(video.type == "youtube:playlist"){
		$("#search-basic").val("list:" + video.id);
		$("#search-basic").trigger("change");
	}else{
		tabPlaylist();
		$("#spinner").show();
		if(video.type == "youtube"){
			video.format = $("#quality").val();
		}
		var url = server + "/playlist";
		var data = $.toJSON(video);
		$.post(url, data, function(entries){
			loadPlayList(entries);
		}, "json").fail(function() {
			showNotification("Error loading video");
    }).done(function() {
      if('on' == $('#save-history').val()){
				saveVideoToHistory(video);
			}
		}).always(function() {
			$("#spinner").hide();
		});
	}
}

function saveVideoToHistory(video){
	if(!supports_html5_storage()){
		return;
	}
	var history = localStorage.getObj("history");
	if(history == undefined){
		history = {};
	}
	if(video.id in history){
		var existingVideo = history[video.id];
		existingVideo.playedTimes += 1;
		existingVideo.lastPlayed = new Date();
	}else{
		video.playedTimes = 1;
		video.lastPlayed = new Date();
		history[video.id] = video;
	}
	var numberOfElements = Object.keys(history).length;
	if(numberOfElements > $('#slider').val()){
		var deleteKey;
		var lastPlayed;
		var playedTimes;
		for (var vid in history) {
			if (history.hasOwnProperty(vid)) {
				var evideo = history[vid];
				if(deleteKey == undefined){
					deleteKey = vid;
					lastPlayed = evideo.lastPlayed;
					playedTimes = evideo.playedTimes;
				}else{
					if((playedTimes > evideo.playedTimes) || ((playedTimes == evideo.playedTimes) && (lastPlayed > evideo.lastPlayed))){
						deleteKey = vid;
						lastPlayed = evideo.lastPlayed;
						playedTimes = evideo.playedTimes;
					}
				}
			}
		}
		if(deleteKey != undefined){
			delete history[deleteKey];
		}
	}
	localStorage.setObj("history", history);
}

function tabPlaylist(){
	$(".link-playlist").first().trigger('click');
}

function showNotification(message){
	$("<div class='ui-loader ui-overlay-shadow ui-body-e ui-corner-all'><h1>"+message+"</h1></div>").css({ "display": "block", "opacity": 0.96, "top": $(window).scrollTop() + 100 })
	.appendTo( $.mobile.pageContainer )
	.delay( 1500 )
	.fadeOut( 400, function(){
		$(this).remove();
	});
}

$(document).delegate("#search", "pageinit", function() {
	if(addLocalStorageFor("#engine", "engine")){
		$("#engine").selectmenu("refresh");
	}
	if(addLocalStorageFor("#quality", "quality")){
		$("#quality").selectmenu("refresh");
	}
	if(addLocalStorageFor("#slider", "slider")){
		$("#slider" ).slider("refresh");
	}
	if(addLocalStorageFor("#save-history", "save-history")){
		$("#save-history" ).slider("refresh");
	}
	$("#clear-history-button").bind("click", function(event, ui) {
		if(supports_html5_storage()){
			localStorage.setObj("history", {});
		}
	});
  $("#add-all-random-button").bind("click", function(event, ui) {
		for (var $x=$("#results").children(), i=$x.length-1, j, temp; i>=0; i--) {
			j=Math.floor(Math.random()*(i+1)), temp=$x[i], $x[i]=$x[j], $x[j]=temp;
		}
		$x.each(function(i, el) {
			$(el).trigger('click');
		});
	});
	$("#search-basic").bind("change", function(event, params) {
		$('#results').empty();
		$("#results").listview("refresh");
		var resetPage = true;
		if(params != undefined){
			if(params.incrementingingPage != undefined){
				if(params.incrementingingPage){
					resetPage = !params.incrementingingPage;
				}
			}
		}
		if(resetPage){
			resetPageNumber();
		}
		if('youtupi:history' == $("#search-basic").val().trim()){
			if(supports_html5_storage()){
				var history = localStorage.getObj("history");
				if(history != undefined){
					fillVideoList($.map(history, function(value, index) {
						return [value];
					}).sort(function (a, b) {
						return b.playedTimes - a.playedTimes;
					}), "#results");
          var videos = Object.keys(history).map(function(k){return history[k]});
					updateSearchControls(videos, false);
				}else{
					updateSearchControls([], false);
				}
			}
		}else{
			var url = getSearchUrl();
			if(url !== undefined){
				$("#spinner-search").show();
				$.getJSON(url, getSearchData(), function(response){
					var pResponse = processSearchResponse(response);
					fillVideoList(pResponse, "#results");
					updateSearchControls(pResponse, isNextPageAvailable(response));
				}).always(function() {
					$("#spinner-search").hide();
				});
			}else{
				updateSearchControls([], false);
			}
		}
	});
	$("#next-page-button").bind("click", function(event, ui) {
		incrementPageNumber();
		$("#search-basic").trigger("change", {
			"incrementingingPage" : true
		});
	});
	$("#engine").bind("change", function(event, ui) {
		$("#search-basic").trigger("change");
	});
	$("#search-basic").val("youtupi:history");
	$("#search-basic").trigger("change");
});

function resetPageNumber(){
	$("#pageNumber").val("1");
}

function incrementPageNumber(){
	var el = $("#pageNumber");
	var pageNumber = parseInt(el.val());
	pageNumber = pageNumber + 1;
	el.val(pageNumber.toString());
}

function getSearchData(){
	var engine = $("#engine").val();
	if(engine != "youtube"){
		return { 'search': $("#search-basic").val(), 'count': $("#slider").val() }
	}else{
		return undefined;
	}
}

function getSearchUrl(){
	var engine = $("#engine").val();
	if(engine == "youtube"){
		return getYoutubeQueryUrl();
	}else{
		return server + "/" + engine + "-search";
	}
}

function processSearchResponse(response){
	var engine = $("#engine").val();
	if(engine == "youtube"){
		return getYoutubeResponseVideos(response);
	}else{
		return response;
	}
}

function isNextPageAvailable(response){
	var engine = $("#engine").val();
	if(engine == "youtube"){
		return getYoutubeNextPage(response);
	}else{
		return false;
	}
}

$(document).delegate("#playlist", "pageinit", function() {
	$("#next-button").bind("click", function(event, ui) {
		playerAction('play');
	});
	$("#pause-button").bind("click", function(event, ui) {
		playerAction('pause');
	});
	$("#stop-button").bind("click", function(event, ui) {
		playerAction('stop');
	});
	$("#volup-button").bind("click", function(event, ui) {
		playerAction('volup');
	});
	$("#voldown-button").bind("click", function(event, ui) {
		playerAction('voldown');
	});
  $("#playlist-list").sortable();
  $('#playlist-reorder').change(function() {
    if('on' == $(this).val()){
      $("#playlist-list").sortable("enable");
    	$("#playlist-list").disableSelection();
    }else{
      $("#playlist-list").sortable('disable');
      $("#playlist-list").enableSelection();
    }
  });
  $("#playlist-reorder").trigger("change");
	$("#playlist-list").bind("sortstop", function(event, ui) {
		$('#playlist-list').listview('refresh');
		if($("#playlist-list").children().length > 1){
			var draggedVideoId = ui.item.data("video-id");
			var draggedPosition = $("#playlist-list").children().index(ui.item);
			if(draggedPosition > 0){
				var data = $.toJSON({id : draggedVideoId, order: draggedPosition + 1});
				var url = server + "/control/order";
				$.post(url, data, loadPlayList, "json");
			}else if(draggedPosition == 0){
				var url = server + "/control/play";
				$.post(url, $.toJSON({id : draggedVideoId}), loadPlayList, "json");
			}
		}
	});
	$("#position").bind("slidestop", function(event, ui){
		var seconds = $("#position").data("duration") * $("#position").val() / 100;
		var data = $.toJSON({seconds : seconds});
		var url = server + "/control/position";
		$.post(url, data, loadPlayList, "json");
	});
	window.setInterval(function(){
		$.getJSON(
			server + "/playlist", loadPlayList
		);
	}, 5000);
});
