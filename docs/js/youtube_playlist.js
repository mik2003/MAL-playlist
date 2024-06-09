async function fetchAnimeList(animeListUrl) {
    let response = await fetch(animeListUrl);
    let data = await response.json()
    return data
}


// 4. The API will call this function when the video player is ready.
function onPlayerReady(event) {
    event.target.playVideo();
}

// 5. The API calls this function when the player's state changes.
//    The function indicates that when playing a video (state=1),
//    the player should play for six seconds and then stop.
var done = false;
function onPlayerStateChange(event) {
    if (event.data == YT.PlayerState.ENDED) {
        goToNextSong();
    }
}

function stopVideo() {
    player.stopVideo();
}

function goToNextSong() {
    player.loadVideoById(getNextSongID());
}


// Next video button
document.getElementById('next').addEventListener('click', goToNextSong);

navigator.mediaSession.setActionHandler('nexttrack', () => {
    console.log("mediaSession nexttrack");
    goToNextSong();
});

var animeList;

async function loadAnimeList() {

    animeList = await fetchAnimeList('https://mik2003.github.io/MAL-playlist/data/animelist.json')
    console.log(animeList)

}

loadAnimeList();


var i = 0;
var j = 0;
var k = 0;

function getNextSongID() {
    console.log([i, j, k])
    if (i < animeList.anime.length) {
        if (j < animeList.anime[i].opening_themes.length) {
            j += 1;
            console.log(animeList.anime[i].opening_themes[j - 1].yt_url);
            return animeList.anime[i].opening_themes[j - 1].yt_url.slice(32, 43)
        }
        else if (k < animeList.anime[i].ending_themes.length) {
            k += 1;
            console.log(animeList.anime[i].ending_themes[j - 1].yt_url);
            return animeList.anime[i].ending_themes[k - 1].yt_url.slice(32, 43)
        } else {
            i += 1;
            j = 0;
            k = 0;
            return getNextSongID();
        }
    } else {
        // Finished playlist
        i = 0;
        j = 0;
        k = 0;
        return getNextSongID();
    }
}

// 2. This code loads the IFrame Player API code asynchronously.
var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

// 3. This function creates an <iframe> (and YouTube player)
//    after the API code downloads.
var player;
function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
        height: '390',
        width: '640',
        videoId: getNextSongID(),
        playerVars: {
            'autoplay': 1,
        },
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
        }
    });
}
