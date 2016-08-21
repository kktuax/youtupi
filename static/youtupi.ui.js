function initControls(){
  $(".active-on-playing").each(function() {
    var action = $(this).data("player-action");
    $(this).bind("click", function(event, ui) {
  		playerAction(action);
  	});
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
			$("#next-button").addClass("ui-disabled");
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
		clearHistory();
	});
  $("#add-all-random-button").bind("click", function(event, ui) {
		for (var $x=$("#results").children(), i=$x.length-1, j, temp; i>=0; i--) {
			j=Math.floor(Math.random()*(i+1)), temp=$x[i], $x[i]=$x[j], $x[j]=temp;
		}
		$x.each(function(i, el) {
			$(el).trigger('click');
		});
	});
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
