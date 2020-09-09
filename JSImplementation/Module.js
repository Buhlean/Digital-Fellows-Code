
var loadedAPI = false;
var loadedPlayer = false;
var startedPlaying = false;
var video_id = "";

function playPlayer() {
  player.play();
}
function pausePlayer() {
  player.pause();
}
function stopPlayer() {
  player.stop();
}
function seekToPlayer(seconds) {
  player.seekTo(seconds);
}

function create_and_change_player(id) {
  loadedPlayer = false;
  startedPlaying = false;
  if (typeof(id) === 'string') {
    console.log("type correct");
    video_id = id;
    if (!(loadedAPI)) {
      console.log("branch one");
      var tag = document.createElement('script');
        tag.src = "https://www.youtube.com/iframe_api";
      var firstScriptTag = document.getElementById('player');
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
    }
    else {
      console.log("branch two");
      create_player();
    }
  }
  else {
    console.log("type wrong");
  }
}
var player;
var playerState;
function onYouTubeIframeAPIReady() {
  loadedAPI = true;
  create_player();
}
function create_player() {
  player = new YT.Player('player',
    { height: '270'
    , width: '480'
    , videoId: video_id
//    , playerVars: { origin: 'https://liascript.github.io/' }
    , events:
      { 'onReady': onPlayerReady
      , 'onStateChange': onPlayerStateChange
      }
  });
}
function onPlayerReady(event) {
  event.target.setVolume(10);
  loadedPlayer = true;
}
function onPlayerStateChange(e) {
  if(e.DATA === -1) {
     startedPlaying = false;
  }
  else {
    startedPlaying = true;
  }
}
