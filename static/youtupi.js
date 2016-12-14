var YouTuPi = {};
YouTuPi.server = window.location.protocol + "//" + window.location.host;
YouTuPi.refreshPlaylist = function(success){
  var url = this.server + "/playlist";
  return $.getJSON(url, success);
};
YouTuPi.playVideo = function(video, success){
  var url = this.server + "/control/play";
  return $.post(url, $.toJSON(video), success, "json");
};
YouTuPi.playVideoNext = function(video, success){
  var url = this.server + "/control/playNext";
  return $.post(url, $.toJSON(video), success, "json");
};
YouTuPi.deleteVideo = function(video, success){
  var url = this.server + "/playlist";
  return $.ajax({url: url, type: 'DELETE', data: $.toJSON(video), dataType: 'json', success: success});
};
YouTuPi.jumpToPosition = function(seconds, success){
  var data = $.toJSON({seconds : seconds});
  var url = this.server + "/control/position";
  return $.post(url, data, success);
};
YouTuPi.changePlaylistPosition = function(videoId, newPosition, success){
  if(newPosition > 0){
    var data = $.toJSON({id : videoId, order: newPosition + 1});
    var url = this.server + "/control/order";
    return $.post(url, data, success, "json");
  }else if(newPosition == 0){
    var url = this.server + "/control/play";
    return $.post(url, $.toJSON({id : videoId}), success, "json");
  }else{
    return $.Deferred().resolve().promise();
  }
};
YouTuPi.controlServer = function(action, success){
  var url = this.server + "/control/" + action;
  return $.get(url, {}, success);
};
YouTuPi.setServerParam = function(param, value, success){
  var jsonobj = {};
  jsonobj[param] = value;
  var url = this.server + "/control/" + param;
  return $.post(url, $.toJSON(jsonobj), success);
};
YouTuPi.addVideo = function(video, success){
  var url = this.server + "/playlist";
  var data = $.toJSON(video);
  return $.post(url, data, success, "json");
};
YouTuPi.addVideos = function(ivideos, random, success){
  var url = this.server + "/playlist";
  var videos = random ? YouTuPi._shuffle(ivideos) : ivideos;
  videos = $.grep(videos, function(v){
    return v.type != 'search';
  });
  return $.post(url, $.toJSON(videos), success, "json");
};
YouTuPi._shuffle = function(array) {
  var currentIndex = array.length, temporaryValue, randomIndex;
  while (0 !== currentIndex) {
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex -= 1;
    temporaryValue = array[currentIndex];
    array[currentIndex] = array[randomIndex];
    array[randomIndex] = temporaryValue;
  }
  return array;
};
YouTuPi.videoOperation = function(video, operation, success){
  var type = video.type;
  var url = this.server + "/" + type + "-" + operation.name;
  return $.post(url, $.toJSON(video), success);
};

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

};
