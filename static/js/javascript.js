function callUrl(url)
{
    var xmlHttp = null;
    xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", url, false );
    xmlHttp.send( null );
}
function changeVolume(vol)
{
    var url = "http://$config.server:$config.port/system/players/$config.player/application/setVolume?level=";
    callUrl(url.concat(vol));
}
function playback(command)
{
    var url = "http://$config.server:$config.port/system/players/$config.player/playback/";
    callUrl(url.concat(command));
}
function playMedia(key)
{
    var url = "http://$config.server:$config.port/system/players/$config.player/application/playMedia?key=" + key + "&path=http://$config.server:$config.port" + key;
    callUrl(url);
}
function init() {
    shortcut.add("space",function() {
        playback('play');
    });
    shortcut.add("x",function() {
        playback('stop');
    });
    shortcut.add("right",function() {
        playback('stepForward');
    });
    shortcut.add("left",function() {
        playback('stepBack');
    });
}
window.onload=init;
