$(document).bind('pageinit', function () {
  $.mobile.defaultPageTransition = 'none';
});

$(document).delegate("#playlist", "pageinit", function() {
  initControls();
  window.setInterval(function(){
    $('#spinner').css('opacity', 1);
    YouTuPi.refreshPlaylist(loadPlayList);
  }, 5000);
});

$(document).delegate("#search", "pageinit", function() {
  initSearchControls();
  $("#search-basic").val("youtupi:home");
  $("#search-basic").trigger("change");
});

/**
* Load playlist items with play video on click event
* */
function loadPlayList(entries){
  $('#spinner').css('opacity', 0);
  updateControls(entries.length);
  var listSelect = "#playlist-list";
  $(listSelect).empty();
  for (var i = 0; i < entries.length; i++) {
    var video = new Video(entries[i]);
    if(i == 0){
      adjustCurrentPositionSlider(video.data.duration, video.data.position);
      if(isHistoryEnabled()){
        HistorySearch.saveToHistory(video.data);
      }
    }else if(i == 1){
      $(listSelect).append($('<li data-role="list-divider">Coming soon</li>'));
    }
    var theme = i == 0 ? 'b' : 'a';
    var icon = i > 0 ? 'false' : 'carat-r';
    var count = i > 0 ? ' <span class="ui-li-count">'+ i +'</span>' : '';
    var itemval = $('<li data-video-id="' + video.id() + '" data-theme="' + theme + '" data-icon="' + icon + '"><a href="#"><img src="'+ video.thumbnail() + '" /><h3>' + video.title() + '</h3>'+count+'<p>' + video.description() + '</p></a></li>');
    itemval.bind('click', {video: video.data}, playlistClickHandler(video, i));
    $(listSelect).append(itemval);
  }
  try {
    $(listSelect).listview("refresh");
  } catch(err) {}
}

function adjustCurrentPositionSlider(duration, position){
  var positionPct = (position != undefined && duration != undefined) ? 100*position/duration : 0;
  $("#position").val(positionPct);
  if(duration != undefined){
    if(duration !=  $("#position").data("duration")){
      $("#position").data("duration", duration);
    }
  }
  try {
    $("#position").slider("refresh");
  } catch(err) {}
}

function isHistoryEnabled(){
  return 'on' == $('#save-history').val();
}

function playlistClickHandler(video, position){
  if(position == 0){
    return function(event){
      $('#seek-controls').css('border-bottom', '6px solid #f37736').animate({borderWidth: 0}, 200);
    };
  }else{
    return function(event) {
      var video = event.data.video;
      var buttons = { 'Play': {
        click: function () {
          YouTuPi.playVideo(video, loadPlayList);
        },
        close: true
      }, 'Play Next': {
        click: function () {
          YouTuPi.playVideoNext(video, loadPlayList);
        },
        close: true
      }, 'Skip': {
        click: function () {
          YouTuPi.deleteVideo(video, loadPlayList);
        },
        close: true
      }};
      for(operationKey in event.data.video.operations){
        var operation = event.data.video.operations[operationKey];
        var buttonClick = function(e, video, operation){
          showNotification("Operation requested");
          YouTuPi.videoOperation(video, operation).done(function(){
            showNotification(operation.successMessage);
          });
        }
        buttons[operation.text] = {
          click: buttonClick,
          args: new Array(video, operation),
          close: true
        };
      }
      $(document).simpledialog2({
        mode: 'button',
        headerText: event.data.video.title,
        headerClose: true,
        buttons : buttons
      });
    };
  }
}

function showNotification(message){
  $("<div class='ui-loader ui-overlay-shadow ui-body-e ui-corner-all'><h2>"+message+"</h2></div>").css({ "display": "block", "opacity": 0.8, "top": 60, "left":"50\%", "transform":"translateX(-50\%)", "z-index":"499", "padding": "0.3em 1em", "position":"fixed" })
  .appendTo( $.mobile.pageContainer )
  .delay( 1500 )
  .fadeOut( 400, function(){
    $(this).remove();
  });
}

function initControls(){
  $(".active-on-playing").each(function() {
    var btn = $(this);
    var action = btn.data("player-action");
    $(this).bind("click", function(event, ui) {
      btn.addClass("ui-disabled");
      YouTuPi.controlServer(action).always(function() {
    		btn.removeClass("ui-disabled");
    	});
  	});
  });
  $("#playlist-list").sortable({
		delay: 250
	});
  initReorderControl();
  $("#position").bind("slidestop", function(event, ui){
		var seconds = $("#position").data("duration") * $("#position").val() / 100;
    if(!isNaN(seconds)){
      YouTuPi.jumpToPosition(seconds, function(){
        showNotification("Changed video time");
      });
    }
	});
}

function initReorderControl(){
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
      YouTuPi.changePlaylistPosition(draggedVideoId, draggedPosition, loadPlayList);
		}
	});
}

function updateControls(playListLength){
	if(playListLength == 0){
		$("#playlist-empty").show();
		$("#playlist-playing").hide();
    $(".active-on-playing").addClass("ui-disabled");
	}else{
		$("#playlist-empty").hide();
		$("#playlist-playing").show();
    $(".active-on-playing").removeClass("ui-disabled");
		if(playListLength <= 1){
      $("#reorder-control").hide();
			$("#next-button").addClass("ui-disabled");
		}else{
      $("#reorder-control").show();
    }
	}
}

var search = null;

function initSearchControls(){
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
		HistorySearch.clearHistory();
    SearchHistorySearch.clearHistory();
	});
  $("#search-basic").bind("change", function(event, params) {
    $('#results').empty();
    $("#results").listview("refresh");
    var query = $("#search-basic").val().trim();
    var selectedEngine = $("#engine").val();
    var count = $("#slider").val();
    var format = $("#quality").val();
    search = createSearch(query, selectedEngine, count, format, isHistoryEnabled());
    $("#spinner-search").show();
    search.search(function(s){
      fillResults(s.results, "#results");
      updateSearchControls(s);
    });
    $("#spinner-search").hide();
  });
  initSearchPageControls();
  initAddAllControls();
  $("#engine").bind("change", function(event, ui) {
    $("#search-basic").trigger("change");
  });
  initVolumeControl();
}

function initAddAllControls(){
  $("#add-all-button").bind("click", function(event, ui) {
    loadVideos(search.results, false);
  });
  $("#add-all-random-button").bind("click", function(event, ui) {
    loadVideos(search.results, true);
  });
}

function loadVideos(ivideos, random){
  tabPlaylist();
  $("#spinner").css('opacity', 1);
  YouTuPi.addVideos(ivideos, random, loadPlayList).fail(function() {
    showNotification("Error loading videos");
  }).always(function() {
    $("#spinner").css('opacity', 0);
  });
}

function loadVideo(video){
  $("#spinner").css('opacity', 1);
  YouTuPi.addVideo(video, loadPlayList).done(function(){
    showNotification("Video queued");
  }).fail(function() {
    showNotification("Error loading video");
  }).always(function() {
    $("#spinner").css('opacity', 0);
  });
}

function tabPlaylist(){
  $(".link-playlist").first().trigger('click');
}

function initSearchPageControls(){
  $("#prev-page-button").bind("click", function(event, ui) {
    $('#results').empty();
    $("#results").listview("refresh");
    search.decrementPageNumber(function(s){
      fillResults(s.results, "#results");
      updateSearchControls(s);
    });
  });
  $("#next-page-button").bind("click", function(event, ui) {
    $('#results').empty();
    $("#results").listview("refresh");
    search.incrementPageNumber(function(s){
      fillResults(s.results, "#results");
      updateSearchControls(s);
    });
  });
}

function updateSearchControls(search){
  var videos = $.grep(search.results, function(v){
    return v.type != 'search';
  });
  updateButtonState("#add-all-button", videos.length > 0);
  updateButtonState("#add-all-random-button", videos.length > 0);
  updateButtonState("#next-page-button", search.nextPageAvailable);
  updateButtonState("#prev-page-button", search.prevPageAvailable);
}

function updateButtonState(selector, enabled){
  if(enabled){
		$(selector).removeClass("ui-disabled");
	}else{
		$(selector).addClass("ui-disabled");
	}
}

function initVolumeControl(){
  $("#volume").bind("change", function(event, ui) {
    YouTuPi.setServerParam('volume', $("#volume").val(), function(){
      showNotification("Updated volume")
    });
  });
  if(addLocalStorageFor("#volume", "volume")){
    $("#volume").slider("refresh");
  }
}

/**
* Refresh listview with array of videos
* @param {entries} array of videos
* @param {listSelect} selector of listview to update
* */
function fillResults(entries, listSelect){
  $(listSelect).empty();
  for (var i = 0; i < entries.length; i++) {
    var video = new Video(entries[i]);
    $(listSelect).append(createResultItem(video, 'a', 'carat-r'));
  }
  if(entries.length == 0){
    var itemval = $('<li data-role="list-divider">No results found</li>');
    $(listSelect).append(itemval);
    var otherVideos = [{
      'id' : 'youtupi:home',
      'title' : 'Home',
      'description' : 'Back to home',
      'type' : 'search',
    }];
    for (var i = 0; i < otherVideos.length; i++) {
      var video = new Video(otherVideos[i]);
      $(listSelect).append(createResultItem(video, 'a', 'carat-r'));
    }
  }
  try {
    $(listSelect).listview("refresh");
  } catch(err) {}
}

function createResultItem(video, theme, icon){
  var itemval = $('<li data-video-id="' + video.id() + '" data-theme="' + theme + '" data-icon="' + icon + '"><a href="#"><img src="'+ video.thumbnail() + '" /><h3>' + video.title() + '</h3><p>' + video.description() + '</p></a></li>');
  itemval.bind('click', {video: video.data}, function(event){
    if(event.data.video.type == "search") {
      var engine = event.data.video.engine;
      var selectedEngine = $("#engine").val();
      if(engine && (selectedEngine != engine)){
        $("#engine").val(engine);
        $("#engine").selectmenu("refresh");
      }
      $("#search-basic").val(event.data.video.id);
      $("#search-basic").trigger("change");
    }else{
      loadVideo(event.data.video);
    }
  });
  return itemval;
}
