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
		var itemval = $('<li><a href="#"><img src="'+ thumbnail + '" /><h3>' + video.title + duration + '</h3><p>' + video.description + '</p></a></li>');
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
	}, "json").fail(function() {
		$("#spinner").hide(); 
		showNotification("Error loading video"); 
	});
}

function tabPlaylist(){
	$(".link-playlist").first().trigger('click');
}

function supports_html5_storage() {
	try {
		return 'localStorage' in window && window['localStorage'] !== null;
	} catch (e) {
		return false;
	}
}

function addLocalStorageFor(select, key){
	if(supports_html5_storage()){
		var oldValue = localStorage.getItem(key);
		if(oldValue){
			$(select).val(oldValue);
		}
		$(select).bind("change", function(event, ui) {
			localStorage.setItem(key, $(select).val());
		});
		return true;
	}else{
		return false;
	}
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
	$("#search-basic").bind("change", function(event, ui) {
		$('#results').empty();
		$("#results").listview("refresh");
		var url = getSearchUrl();
		if(url !== undefined){
			$("#spinner-search").show();
			$.getJSON(url, getSearchData(), function(response){
				fillVideoList(processSearchResponse(response), "#results");
			}).always(function() {
				$("#spinner-search").hide();
			});
		}
	});
	$("#engine").bind("change", function(event, ui) {
		$("#search-basic").trigger("change");
	});
});

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
