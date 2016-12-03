var server = window.location.protocol + "//" + window.location.host;
var oldvolumesliderposition = 0;

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
      if(event.data.video.type == "local-dir") {
        $("#search-basic").val(event.data.video.id);
        $("#search-basic").trigger("change");
      } else {
        loadVideo(event.data.video);
      }
    };
  }

  $(listSelect).empty();
  for (var i = 0; i < entries.length; i++) {
    var video = entries[i];
    if(i == 0){
      adjustCurrentPositionSlider(video.duration, video.position);
    }
    thumbnail = "images/video.png";
    if(video.type == "local-dir") {
      thumbnail = "images/folder_open.png";
      if(video.title == "..") {
        thumbnail = "images/folder.png";
      }
    }
    if(video.thumbnail != undefined){
      thumbnail = video.thumbnail;
    }
    var	duration = getDurationString(video.duration);
    if(duration){
      duration = " [" + duration + "]";
    }
    if(video.title == undefined) {
      video.title = "Loading data for " + video.id;
      video.description = "";
    }
    var itemval = $('<li data-video-id="' + video.id + '"><a href="#"><img src="'+ thumbnail + '" /><h3>' + video.title + duration + '</h3><p>' + video.description + '</p></a></li>');
    itemval.bind('click', {video: video}, clickEvent);
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
  $('#spinner').css('opacity', 0);
  updateControls(entries.length);
  var playlist_entry_handler = function(event) {
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
  };
  fillVideoList(entries, "#playlist-list", playlist_entry_handler);
}

function jumpToPosition(seconds){
  var data = $.toJSON({seconds : seconds});
  var url = server + "/control/position";
  $.post(url, data, loadPlayList, "json");
}

function changePlaylistPosition(videoId, newPosition){
  if(newPosition > 0){
    var data = $.toJSON({id : videoId, order: newPosition + 1});
    var url = server + "/control/order";
    $.post(url, data, loadPlayList, "json");
  }else if(newPosition == 0){
    var url = server + "/control/play";
    $.post(url, $.toJSON({id : videoId}), loadPlayList, "json");
  }
}

function setServerParam(param, value){
  var jsonobj = {};
  jsonobj[param] = value;
  $.post(
    server + "/control/" + param, $.toJSON(jsonobj), function(){}, "json"
  );
}

function loadVideos(videos){
  tabPlaylist();
  $("#spinner").css('opacity', 1);
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
    $("#spinner").css('opacity', 0);
  });
}

function loadVideo(video){
  if(video.type == "youtube:playlist"){
    $("#search-basic").val("list:" + video.id);
    $("#search-basic").trigger("change");
  }else{
    $("#spinner").css('opacity', 1);
    if(video.type == "youtube"){
      video.format = $("#quality").val();
    }
    var url = server + "/playlist";
    var data = $.toJSON(video);
    $.post(url, data, function(entries){
      loadPlayList(entries);
      showNotification("Video queued");
    }, "json").fail(function() {
      showNotification("Error loading video");
    }).done(function() {
      if('on' == $('#save-history').val()){
        saveVideoToHistory(video);
      }
    }).always(function() {
      $("#spinner").css('opacity', 0);
    });
  }
}

function getVideosFromHistory(){
  if(!supports_html5_storage()){
    return [];
  }
  var history = localStorage.getObj("history");
  if(history != undefined){
    fillVideoList($.map(history, function(value, index) {
      return [value];
    }).sort(function (a, b) {
      return b.playedTimes - a.playedTimes;
    }), "#results");
    return Object.keys(history).map(function(k){return history[k]});
  }else{
    return [];
  }
}

function clearHistory(){
  if(supports_html5_storage()){
    localStorage.setObj("history", {});
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
  $("<div class='ui-loader ui-overlay-shadow ui-body-e ui-corner-all'><h2>"+message+"</h2></div>").css({ "display": "block", "opacity": 0.8, "top": 60, "left":"50\%", "transform":"translateX(-50\%)", "z-index":"499", "padding": "0.3em 1em", "position":"fixed" })
  .appendTo( $.mobile.pageContainer )
  .delay( 1500 )
  .fadeOut( 400, function(){
    $(this).remove();
  });
}

$(document).delegate("#search", "pageinit", function() {
  initSearchControls();
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
      updateSearchControls(getVideosFromHistory(), false);
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
    if( $("#engine").val() == "local-dir") {
      $("#search-basic").val("/");
    }
    $("#search-basic").trigger("change");
  });
  if( $("#engine").val() == "local-dir") {
    $("#search-basic").val("/");
  } else {
    $("#search-basic").val("youtupi:history");
  }
  $("#search-basic").trigger("change");
  $("#volume").bind("change", function(event, ui) {
    var newposition = $("#volume").val();
    if( oldvolumesliderposition != newposition ) {
      setServerParam('volume', newposition);
      oldvolumesliderposition = newposition;
    }
  });
  if(addLocalStorageFor("#volume", "volume")){
    $("#volume").slider("refresh");
  }
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
  }else
  if(engine == "local-dir"){
    return server + "/local-browse";
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
  initControls();
  window.setInterval(function(){
    $('#spinner').css('opacity', 1);
    $.getJSON(
      server + "/playlist", loadPlayList
    );
  }, 5000);
});
