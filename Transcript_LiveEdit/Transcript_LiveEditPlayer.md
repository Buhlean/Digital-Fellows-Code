<!--

author:   Alexander Buhl
version:  0.0.2
language: en

script:   https://raw.githubusercontent.com/Buhlean/Digital-Fellows-Code/master/Transcript_LiveEdit/Main.js
link:     https://cdn.jsdelivr.net/chartist.js/latest/chartist.min.css

link:     https://cdnjs.cloudflare.com/ajax/libs/animate.css/3.7.0/animate.min.css

translation: Deutsch  translations/German.md
translation: Français translations/French.md
translation: Русский  translations/Russian.md

-->

### Transcript LiveEdit Test

Rendered version at:

https://liascript.github.io/course/?https://raw.githubusercontent.com/Buhlean/Digital-Fellows-Code/master/Transcript_LiveEdit/Transcript_LiveEditPlayer.md

## LiveEdit any transcript in here!
<div id="player"></div>
<div id="ElmHook"></div>
<script>
  var app = Elm.Main.init({
    node: document.getElementById('ElmHook')
  });
  var video_id;
  var tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
  var firstScriptTag = document.getElementById('player');
  app.ports.send_to_yt_API.subscribe(function(message){
    if (message.indexOf('ID:') !== -1) {
      if (message.indexOf('default') !== -1) {
        create_and_change_player('6Af6b_wyiwI'); }
      else { create_and_change_player(message.slice(3)); } }
    else if (message.indexOf('Seek:') !== -1) {
      console.log(message);
      console.log(player);
      try{
        if (playerState !== -1) {player.seekTo(parseInt(message.slice(5)),true); }
      } catch(e) {
        console.log("SeekTo Exception"+e);
      } }
    else if (message.indexOf('Play:') !== -1) {
      player.playVideo(); }
    else if (message.indexOf('Pause:') !== -1) {
      player.pauseVideo(); }
  });
  function create_and_change_player(id){
    console.log(id);
    video_id = id;
    try {
      player.destroy();
      create_player();
      console.log("reached end of try");
    } catch(e) {
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
      console.log("reached end of except");
    }
  }
  var player;
  var playerState;
  function onYouTubeIframeAPIReady() {
    create_player();
    console.log("API ready");
  }
  function create_player(){
    player = new YT.Player('player', 
      { height: '270'
      , width: '480'
      , videoId: video_id
      , playerVars: 
        { origin: 'https://liascript.github.io/'
        }
      , events: 
        { 'onReady': onPlayerReady
        , 'onStateChange': onPlayerStateChange
        }
    });
    app.ports.receive_msg_from_API.send(-1);
    console.log("ELM notified");
  }
  function onPlayerReady(e){
    console.log("PlayerReady");
  }
  function onPlayerStateChange(e){
    console.log("New State: "+e.data);
    playerState = e.data;
    if (playerState >= 0) {
      player.setVolume(10);
    }
  }
</script>
