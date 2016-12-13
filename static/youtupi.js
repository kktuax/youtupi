var server = window.location.protocol + "//" + window.location.host;

$(document).bind('pageinit', function () {
  $.mobile.defaultPageTransition = 'none';
});

function Video(data){

  this.data = data;

  this.id = function(){
    return this.data.id;
  };

  this.title = function(){
    var title = this.data.title;
    if(title == undefined) {
      title = "Loading data for " + this.data.id;
    }
    var	duration = this.getDurationString();
    if(duration){
      return title + " [" + duration + "]";
    }else{
      return title;
    }
  };

  this.getDurationString = function(){
    var time = this.data.duration;
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
  };

  this.description = function(){
    return (this.data.description != undefined) ? this.data.description : "";
  };

  this.thumbnail = function (){
    var thumbnail = "images/video.png";
    if(this.data.type == "search") {
      thumbnail = "images/folder_open.png";
      if(this.data.title == "..") {
        thumbnail = "images/folder.png";
      }
    }
    if(this.data.thumbnail != undefined){
      thumbnail = this.data.thumbnail;
    }
    return thumbnail;
  };

}

/**
* Refresh listview with array of videos
* @param {entries} array of videos
* @param {listSelect} selector of listview to update
* @param {function} event on video click
* */
function fillPlayList(entries, listSelect, clickEvent){
  $(listSelect).empty();
  for (var i = 0; i < entries.length; i++) {
    var video = new Video(entries[i]);
    var videoEvent = clickEvent;
    if(i == 0){
      adjustCurrentPositionSlider(video.duration, video.position);
      if('on' == $('#save-history').val()){
        HistorySearch.saveVideoToHistory(video.data);
      }
      videoEvent = function(){
        $('#seek-controls').css('border-bottom', '6px solid #f37736').animate({borderWidth: 0}, 200);
      };
    }else if(i == 1){
      $(listSelect).append($('<li data-role="list-divider">Coming soon</li>'));
    }
    var theme = i == 0 ? 'b' : 'a';
    var icon = i > 0 ? 'false' : 'carat-r';
    var count = i > 0 ? ' <span class="ui-li-count">'+ i +'</span>' : '';
    var itemval = $('<li data-video-id="' + video.id() + '" data-theme="' + theme + '" data-icon="' + icon + '"><a href="#"><img src="'+ video.thumbnail() + '" /><h3>' + video.title() + '</h3>'+count+'<p>' + video.description() + '</p></a></li>');
    itemval.bind('click', {video: video.data}, videoEvent);
    $(listSelect).append(itemval);
  }
  try {
    $(listSelect).listview("refresh");
  } catch(err) {}
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
    var theme = 'a';
    var icon = 'carat-r';
    var itemval = $('<li data-video-id="' + video.id() + '" data-theme="' + theme + '" data-icon="' + icon + '"><a href="#"><img src="'+ video.thumbnail() + '" /><h3>' + video.title() + '</h3><p>' + video.description() + '</p></a></li>');
    itemval.bind('click', {video: video.data}, function(event){
      if(event.data.video.type == "search") {
        $("#search-basic").val(event.data.video.id);
        $("#search-basic").trigger("change");
      }else{
        loadVideo(event.data.video);
      }
    });
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
  fillPlayList(entries, "#playlist-list", playlist_entry_handler);
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
  var url = server + "/playlist";
  $.post(url, $.toJSON(videos), function(entries){
    loadPlayList(entries);
  }, "json").fail(function() {
    showNotification("Error loading videos");
  }).always(function() {
    $("#spinner").css('opacity', 0);
  });
}

function loadVideo(video){
  $("#spinner").css('opacity', 1);
  var url = server + "/playlist";
  var data = $.toJSON(video);
  $.post(url, data, function(entries){
    loadPlayList(entries);
    showNotification("Video queued");
  }, "json").fail(function() {
    showNotification("Error loading video");
  }).always(function() {
    $("#spinner").css('opacity', 0);
  });
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

var search = null;

$(document).delegate("#search", "pageinit", function() {
  initSearchControls();
  $("#search-basic").bind("change", function(event, params) {
    $('#results').empty();
    $("#results").listview("refresh");
    var query = $("#search-basic").val().trim();
    var selectedEngine = $("#engine").val();
    var count = $("#slider").val();
    var format = $("#quality").val();
    search = createSearch(query, selectedEngine, count, format);
    $("#spinner-search").show();
    search.search(function(s){
      fillResults(s.results, "#results");
      updateSearchControls(s);
    });
    $("#spinner-search").hide();
  });
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
  $("#engine").bind("change", function(event, ui) {
    $("#search-basic").val("");
    $("#search-basic").trigger("change");
  });
  $("#volume").bind("change", function(event, ui) {
    setServerParam('volume', $("#volume").val());
  });
  if(addLocalStorageFor("#volume", "volume")){
    $("#volume").slider("refresh");
  }
  $("#search-basic").trigger("change");
});

$(document).delegate("#playlist", "pageinit", function() {
  initControls();
  window.setInterval(function(){
    $('#spinner').css('opacity', 1);
    $.getJSON(
      server + "/playlist", loadPlayList
    );
  }, 5000);
});
