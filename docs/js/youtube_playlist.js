var animeList;
var animePlaylist;
var i, j, k;

var player;

async function fetchAnimeList(animeListUrl) {
    let response = await fetch(animeListUrl);
    let data = await response.json()
    return data
}

async function loadAnimeList() {

    animeList = await fetchAnimeList('https://mik2003.github.io/MAL-playlist/data/animelist.json');
    console.log(animeList);

}


async function retrievePlaylist() {
    await loadAnimeList();

    animePlaylist = [];

    for (i = 0; i < animeList.anime.length; i++) {
        for (j = 0; j < animeList.anime[i].opening_themes.length; j++) {
            animePlaylist[animePlaylist.length] = animeList.anime[i].opening_themes[j].yt_url.slice(32, 43)
        }
        for (k = 0; k < animeList.anime[i].ending_themes.length; k++) {
            animePlaylist[animePlaylist.length] = animeList.anime[i].ending_themes[k].yt_url.slice(32, 43)
        }
    }

    i = 0; j = 0; k = 0;

    console.log(animePlaylist);
}

async function initializePlayer() {
    await retrievePlaylist();

    // 2. This code loads the IFrame Player API code asynchronously.
    var tag = document.createElement('script');

    tag.src = "https://www.youtube.com/iframe_api";
    var firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
}

// 3. This function creates an <iframe> (and YouTube player)
//    after the API code downloads.
function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
        height: '390',
        width: '640',
        videoId: getNextSongID(),
        playerVars: {
            'autoplay': 1,
            // 'listType': 'playlist',
        },
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
        }
    });
}

// 4. The API will call this function when the video player is ready.
function onPlayerReady(event) {
    player.cuePlaylist(animePlaylist.slice(0, 10));
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
    // player.loadVideoById(getNextSongID());
    console.log('next');
    player.nextVideo();
}

function goToPreviousSong() {
    player.previousVideo();
}


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

initializePlayer();

// Previous video button
document.getElementById('prev').addEventListener('click', goToPreviousSong)

// Next video button
document.getElementById('next').addEventListener('click', goToNextSong);

// var audio = document.createElement('audio');

// navigator.mediaSession.setActionHandler('nexttrack', () => {
//     console.log("mediaSession nexttrack");
//     goToNextSong();
// });
