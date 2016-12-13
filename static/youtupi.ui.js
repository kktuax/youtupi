function initControls(){
  $(".active-on-playing").each(function() {
    var btn = $(this);
    var action = btn.data("player-action");
    $(this).bind("click", function(event, ui) {
      btn.addClass("ui-disabled");
      $.getJSON(
        server + "/control/" + action, loadPlayList
      ).always(function() {
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
    jumpToPosition(seconds);
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
      changePlaylistPosition(draggedVideoId, draggedPosition);
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
	});
}

function updateSearchControls(search){
  if(search.results.length == 0){
		$("#results-empty").show();
	}else{
    $("#results-empty").hide();
	}
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
