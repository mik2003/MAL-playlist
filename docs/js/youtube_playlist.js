var animeList;
var animePlaylist;
var playlistIndeces;
var animePlaylistMap;
var songDiv;
var playlistDiv;
var i, j, k, n = 0;
var player;
var loop = true;

// Function to create an array with n integers
function createArray(n) {
    let array = [];
    for (let i = 0; i < n; i++) {
        array.push(i);
    }
    return array;
}

// Function to shuffle an array randomly
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]]; // Swap elements
    }
    return array;
}

function populatePlaylistDiv() {
    playlistDiv = document.getElementById('playlist');

    var playlistItem;
    var currentSongMap;
    var currentSong;
    for (i = 0; i < animePlaylistMap.length; i++) {
        playlistItem = document.createElement("div");
        playlistItem.setAttribute("class", "playlist-item");
        playlistItem.setAttribute("id", i)
        currentSongMap = animePlaylistMap[playlistIndeces[i]];
        currentSong = animeList.anime[currentSongMap[0]][currentSongMap[1]][currentSongMap[2]];
        playlistItem.innerText = currentSong.text;
        playlistItem.setAttribute('onclick', 'goToSong(' + i + ')');

        playlistDiv.appendChild(playlistItem);
    }
}

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
    animePlaylistMap = [];

    for (i = 0; i < animeList.anime.length; i++) {
        for (j = 0; j < animeList.anime[i].opening_themes.length; j++) {
            animePlaylist.push(animeList.anime[i].opening_themes[j].yt_url.slice(32, 43));
            animePlaylistMap.push([i, "opening_themes", j]);
        }
        for (k = 0; k < animeList.anime[i].ending_themes.length; k++) {
            animePlaylist.push(animeList.anime[i].ending_themes[k].yt_url.slice(32, 43));
            animePlaylistMap.push([i, "ending_themes", k]);
        }
    }

    i = 0; j = 0; k = 0;

    console.log(animePlaylist);
    console.log(animePlaylistMap);

    playlistIndeces = createArray(animePlaylist.length);

    populatePlaylistDiv();
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
        videoId: getCurrentSongId(),
        playerVars: {
            'autoplay': 1,
            'controls': 0,
        },
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange,
            'onError': onPlayerError,
        }
    });
}

// 4. The API will call this function when the video player is ready.
function onPlayerReady(event) {
    initializeMediaSession();
    applySongDivStyle();
    updateMediaSession();
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

function onPlayerError(event) {
    if (event.data == 2) {
        console.log('onError 2: Invalid video ID')
    } else if (event.data == 5) {
        console.log('onError 5: HTML5 error')
    } else if (event.data == 100) {
        console.log('onError 100: Video not found')
    } else if (event.data == 101) {
        console.log('onError 101: Video cannot be embedded')
    } else if (event.data == 150) {
        console.log('onError 150: Video cannot be embedded')
    } else {
        console.log('onError: Unknown error')
    }
    goToNextSong();
}

function stopVideo() {
    player.stopVideo();
}

function initializeMediaSession() {
    if ('mediaSession' in navigator) {
        navigator.mediaSession.setActionHandler('play', () => {
            playSong();
        });
        navigator.mediaSession.setActionHandler('pause', () => {
            pauseSong();
        });
        navigator.mediaSession.setActionHandler('seekbackward', (details) => {
            let newTime = Math.max(player.getCurrentTime() - (details.seekOffset || 10), 0);
            player.seekTo(newTime, true);
        });
        navigator.mediaSession.setActionHandler('seekforward', (details) => {
            let newTime = Math.min(player.getCurrentTime() + (details.seekOffset || 10), player.getDuration());
            player.seekTo(newTime, true);
        });
        navigator.mediaSession.setActionHandler('previoustrack', () => {
            goToPreviousSong();
        });
        navigator.mediaSession.setActionHandler('nexttrack', () => {
            goToNextSong();
        });
    }
}

function updateMediaSession() {
    var currentSongMap = animePlaylistMap[n];
    var currentSong = animeList.anime[currentSongMap[0]][currentSongMap[1]][currentSongMap[2]];

    if ("mediaSession" in navigator) {
        navigator.mediaSession.metadata = new MediaMetadata({
            title: currentSong.name,
            artist: currentSong.artist,
        });
    }
}

function clearSongDivStyle() {
    songDiv = document.getElementById(n);
    songDiv.style.color = "#FFFFFF";
}

function applySongDivStyle() {
    songDiv = document.getElementById(n);
    songDiv.style.color = "#0000FF";
    songDiv.scrollIntoView();
}

function goToNextSong() {
    clearSongDivStyle();
    n = jumpN(1);
    applySongDivStyle();
    player.loadVideoById(getCurrentSongId());
    updateMediaSession();

    console.log('next ' + n);
}

function goToPreviousSong() {
    clearSongDivStyle();
    n = jumpN(-1);
    applySongDivStyle();
    player.loadVideoById(getCurrentSongId());
    updateMediaSession();

    console.log('prev ' + n);
}

function goToSong(new_n) {
    clearSongDivStyle();
    n = new_n;
    applySongDivStyle();
    player.loadVideoById(getCurrentSongId());
    updateMediaSession();

    console.log('song ' + n);
}

function pauseSong() {
    player.pauseVideo();
}

function playSong() {
    player.playVideo();
}

function jumpN(m) {
    const length = animePlaylist.length;
    if (loop) {
        return ((n + m) % length + length) % length;
    } else {
        if (m > 0) {
            return Math.min(length - 1, n + m)
        } else if (m < 0) {
            return Math.max(0, n + m)
        }
    }
}

function getCurrentSongId() {
    return animePlaylist[playlistIndeces[n]]
}

function shufflePlaylist() {
    shuffleArray(playlistIndeces);
    playlistDiv = document.getElementById("playlist");
    playlistDiv.innerHTML = "";
    populatePlaylistDiv();
    applySongDivStyle();
    player.loadVideoById(getCurrentSongId());
    updateMediaSession();
}

function toggleLoop() {
    if (loop) {
        loop = false;
    } else {
        loop = true;
    }

    console.log("Toggled loop: " + loop);
}

initializePlayer();

// Previous video button
document.getElementById('prev').addEventListener('click', goToPreviousSong);

// Next video button
document.getElementById('next').addEventListener('click', goToNextSong);

// Pause button
document.getElementById('pause').addEventListener('click', pauseSong);

// Play button
document.getElementById('play').addEventListener('click', playSong);

// Shuffle button
document.getElementById('shuffle').addEventListener('click', shufflePlaylist);

// Loop button
document.getElementById('loop').addEventListener('click', toggleLoop);
