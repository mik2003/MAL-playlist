var animeList;
var animePlaylist;
var playlistIndeces;
var animePlaylistMap;
var songDiv;
var playlistDiv;
var i, j, k, n = 0;
var player;
var loop = true;
var isPlaying = false;
var shouldAutoplay = false;

// Add this debug function
function checkMediaSession() {
    console.log('=== Media Session Debug ===');
    console.log('Media Session supported:', 'mediaSession' in navigator);
    if ('mediaSession' in navigator) {
        console.log('Current metadata:', navigator.mediaSession.metadata);
        console.log('Playback state:', navigator.mediaSession.playbackState);

        // Check which handlers are set
        const actions = ['play', 'pause', 'previoustrack', 'nexttrack'];
        actions.forEach(action => {
            try {
                navigator.mediaSession.setActionHandler(action, () => { });
                console.log(`${action} handler: CAN be set`);
                navigator.mediaSession.setActionHandler(action, null);
            } catch (e) {
                console.log(`${action} handler: CANNOT be set - ${e.message}`);
            }
        });
    }
}

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
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

function scrollParentToChild(parent, child) {
    var parentRect = parent.getBoundingClientRect();
    var parentViewableArea = {
        height: parent.clientHeight,
        width: parent.clientWidth
    };
    var childRect = child.getBoundingClientRect();
    var isViewable = (childRect.top >= parentRect.top) && (childRect.bottom <= parentRect.top + parentViewableArea.height);

    if (!isViewable) {
        const scrollTop = childRect.top - parentRect.top;
        const scrollBot = childRect.bottom - parentRect.bottom;
        if (Math.abs(scrollTop) < Math.abs(scrollBot)) {
            parent.scrollTop += scrollTop;
        } else {
            parent.scrollTop += scrollBot;
        }
    }
}

function populatePlaylistDiv() {
    playlistDiv = document.getElementById('playlist');
    playlistDiv.innerHTML = '';

    for (i = 0; i < animePlaylistMap.length; i++) {
        let playlistItem = document.createElement("div");
        playlistItem.setAttribute("class", "playlist-item");
        playlistItem.setAttribute("id", i);
        let playlistItemText = document.createElement("div");
        playlistItemText.setAttribute("class", "playlist-item-text");
        let playlistItemImage = document.createElement("div");
        playlistItemImage.setAttribute("class", "playlist-item-image");

        let currentSongMap = animePlaylistMap[playlistIndeces[i]];
        let currentSong = animeList.anime[currentSongMap[0]][currentSongMap[1]][currentSongMap[2]];

        let animeImage = document.createElement("img");
        animeImage.setAttribute("class", "playlist-item-animeimage");
        animeImage.setAttribute("src", animeList.anime[currentSongMap[0]].picture);

        let nameLine = document.createElement("span");
        nameLine.setAttribute("class", "playlist-item-nameline");
        nameLine.innerText = `${currentSong.name}`;
        playlistItemText.appendChild(nameLine);

        let artistLine = document.createElement("span");
        artistLine.setAttribute("class", "playlist-item-artistline");
        artistLine.innerText = ` by ${currentSong.artist}`;
        playlistItemText.appendChild(artistLine);

        let animeLine = document.createElement("span");
        animeLine.setAttribute("class", "playlist-item-animeline");
        animeLine.innerText = `\n【${animeList.anime[currentSongMap[0]].title}】`;
        playlistItemText.appendChild(animeLine);

        let episodeLine = document.createElement("span");
        episodeLine.setAttribute("class", "playlist-item-episodeline");
        episodeLine.innerText = ` ${currentSongMap[1].split("_")[0]}${currentSong.index !== null ? ` #${currentSong.index}` : ''}${currentSong.episode !== null ? ` (${currentSong.episode})` : ''}`;
        playlistItemText.appendChild(episodeLine);

        let animeLink = document.createElement("a");
        animeLink.setAttribute("href", `https://myanimelist.net/anime/${currentSong.anime_id}`);
        animeLink.setAttribute("target", "_blank");
        animeLink.appendChild(animeImage);
        playlistItemImage.appendChild(animeLink);

        playlistItem.setAttribute('onclick', 'goToSong(' + i + ')');
        playlistItem.appendChild(playlistItemImage);
        playlistItem.appendChild(playlistItemText);
        playlistDiv.appendChild(playlistItem);
    }
}

async function fetchAnimeList(animeListUrl) {
    let response = await fetch(animeListUrl);
    let data = await response.json()
    return data
}

async function loadAnimeList() {
    animeList = await fetchAnimeList('https://mal.secondo.aero/data/animelist.json');
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
    playlistIndeces = createArray(animePlaylist.length);
    populatePlaylistDiv();
}

async function initializePlayer() {
    await retrievePlaylist();

    // Initialize our independent media session FIRST
    initializeIndependentMediaSession();

    // Register service worker
    if ('serviceWorker' in navigator) {
        try {
            await navigator.serviceWorker.register('sw.js');
            console.log('Service Worker registered');
        } catch (error) {
            console.log('Service Worker registration failed:', error);
        }
    }

    // Load YouTube IFrame API
    var tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
    var firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
}

// Create our own independent media session
function initializeIndependentMediaSession() {
    if (!('mediaSession' in navigator)) {
        console.log('Media Session API not supported');
        return;
    }

    console.log('Initializing independent media session...');

    // Set up our media session completely independently
    try {
        // Clear any existing handlers
        const actions = ['play', 'pause', 'previoustrack', 'nexttrack', 'seekbackward', 'seekforward'];
        actions.forEach(action => {
            try {
                navigator.mediaSession.setActionHandler(action, null);
            } catch (e) { }
        });

        // Set our custom handlers
        navigator.mediaSession.setActionHandler('play', () => {
            console.log('🎵 Independent Media session: PLAY');
            playSong();
        });

        navigator.mediaSession.setActionHandler('pause', () => {
            console.log('⏸️ Independent Media session: PAUSE');
            pauseSong();
        });

        navigator.mediaSession.setActionHandler('previoustrack', () => {
            console.log('⏮️ Independent Media session: PREVIOUS');
            goToPreviousSong();
        });

        navigator.mediaSession.setActionHandler('nexttrack', () => {
            console.log('⏭️ Independent Media session: NEXT');
            goToNextSong();
        });

        navigator.mediaSession.setActionHandler('seekbackward', (details) => {
            console.log('⏪ Independent Media session: SEEK BACKWARD');
            if (player && player.getCurrentTime) {
                const newTime = Math.max(player.getCurrentTime() - (details.seekOffset || 10), 0);
                player.seekTo(newTime, true);
            }
        });

        navigator.mediaSession.setActionHandler('seekforward', (details) => {
            console.log('⏩ Independent Media session: SEEK FORWARD');
            if (player && player.getCurrentTime) {
                const newTime = Math.min(player.getCurrentTime() + (details.seekOffset || 10), player.getDuration());
                player.seekTo(newTime, true);
            }
        });

        // Set initial metadata
        updateMediaSessionMetadata();

        console.log('✅ Independent media session initialized');
    } catch (error) {
        console.error('❌ Error setting independent media session:', error);
    }
}

// YouTube Player setup with youtube-nocookie.com
function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
        height: '390',
        width: '640',
        videoId: getCurrentSongId(),
        host: 'https://www.youtube-nocookie.com',
        playerVars: {
            'playsinline': 1,
            'enablejsapi': 1,
            'origin': window.location.origin,
            'autoplay': 0, // CHANGE: 0 instead of 1 (start paused)
            'controls': 0,
            'modestbranding': 1,
            'rel': 0,
            'showinfo': 0,
            'iv_load_policy': 3,
            'fs': 0,
            'disablekb': 1
        },
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange,
            'onError': onPlayerError,
        }
    });
}

function onPlayerReady(event) {
    console.log('YouTube player ready (no-cookie version)');
    applySongDivStyle();
    updateMediaSessionMetadata();
    updateStatusDisplay();

    isPlaying = false;
    updatePlayPauseButtons();
    updateMediaSessionPlaybackState('paused');
    console.log('Player ready and paused - click play to start');

    setTimeout(checkMediaSession, 2000);
}

function onPlayerStateChange(event) {
    console.log('Player state:', event.data);
    switch (event.data) {
        case YT.PlayerState.PLAYING:
            isPlaying = true;
            updatePlayPauseButtons();
            updateMediaSessionPlaybackState('playing');
            updateStatusDisplay();
            break;
        case YT.PlayerState.PAUSED:
            isPlaying = false;
            updatePlayPauseButtons();
            updateMediaSessionPlaybackState('paused');
            updateStatusDisplay();
            break;
        case YT.PlayerState.ENDED:
            isPlaying = false;
            updatePlayPauseButtons();
            updateMediaSessionPlaybackState('none');
            updateStatusDisplay();
            goToNextSong();
            break;
    }
}

function onPlayerError(event) {
    console.log('Player error:', event.data);
    goToNextSong();
}

function updateMediaSessionMetadata() {
    if (!('mediaSession' in navigator)) return;

    const currentSongMap = animePlaylistMap[playlistIndeces[n]];
    const currentSong = animeList.anime[currentSongMap[0]][currentSongMap[1]][currentSongMap[2]];

    try {
        const metadata = new MediaMetadata({
            title: currentSong.name || 'Unknown Title',
            artist: currentSong.artist || 'Unknown Artist',
            album: animeList.anime[currentSongMap[0]].title || 'Anime Themes',
            artwork: [
                {
                    src: animeList.anime[currentSongMap[0]].picture || '',
                    sizes: '225x225',
                    type: 'image/jpeg'
                }
            ]
        });

        navigator.mediaSession.metadata = metadata;
        console.log('Independent media session metadata updated:', currentSong.name);
    } catch (error) {
        console.error('Error updating media session metadata:', error);
    }
}

function updateMediaSessionPlaybackState(state) {
    if ('mediaSession' in navigator) {
        navigator.mediaSession.playbackState = state;
    }
}

function updateStatusDisplay() {
    const currentSongMap = animePlaylistMap[playlistIndeces[n]];
    const currentSong = animeList.anime[currentSongMap[0]][currentSongMap[1]][currentSongMap[2]];

    if (document.getElementById('current-song-name')) {
        document.getElementById('current-song-name').textContent = currentSong.name || 'Unknown';
    }
    if (document.getElementById('playback-status')) {
        document.getElementById('playback-status').textContent = isPlaying ? '▶️ Playing' : '⏸️ Paused';
    }
    if (document.getElementById('player-status')) {
        document.getElementById('player-status').textContent = '✅ Ready';
    }
    if (document.getElementById('current-position')) {
        document.getElementById('current-position').textContent = `Song ${n + 1} of ${animePlaylist.length}`;
    }
}

// Playback control functions
function playSong() {
    console.log('Playing song');
    if (player && player.playVideo) {
        player.playVideo();
        isPlaying = true;
        shouldAutoplay = true; // Add this line
        updatePlayPauseButtons();
        updateMediaSessionPlaybackState('playing');
        updateStatusDisplay();
    }
}

function pauseSong() {
    console.log('Pausing song');
    if (player && player.pauseVideo) {
        player.pauseVideo();
        isPlaying = false;
        shouldAutoplay = false; // Add this line
        updatePlayPauseButtons();
        updateMediaSessionPlaybackState('paused');
        updateStatusDisplay();
    }
}

function updatePlayPauseButtons() {
    const playBtn = document.getElementById('play');
    const pauseBtn = document.getElementById('pause');

    if (isPlaying) {
        playBtn.style.display = 'none';
        pauseBtn.style.display = 'inline-block';
    } else {
        playBtn.style.display = 'inline-block';
        pauseBtn.style.display = 'none';
    }
}

// Navigation functions
function goToNextSong() {
    console.log('Next song');
    clearSongDivStyle();
    n = jumpN(1);
    loadNewSong();
}

function goToPreviousSong() {
    console.log('Previous song');
    clearSongDivStyle();
    n = jumpN(-1);
    loadNewSong();
}

function goToSong(new_n) {
    console.log('Go to song:', new_n);
    clearSongDivStyle();
    n = new_n;
    loadNewSong();
}

function loadNewSong() {
    if (player && player.loadVideoById) {
        player.loadVideoById(getCurrentSongId());
        applySongDivStyle();
        updateMediaSessionMetadata();
        updateStatusDisplay();

        // Only auto-play if user was already playing
        if (shouldAutoplay) {
            setTimeout(() => {
                player.playVideo();
                isPlaying = true;
                updatePlayPauseButtons();
                updateMediaSessionPlaybackState('playing');
                updateStatusDisplay();
            }, 500);
        } else {
            // Keep it paused for new songs
            isPlaying = false;
            updatePlayPauseButtons();
            updateMediaSessionPlaybackState('paused');
            updateStatusDisplay();
        }
    }
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

function clearSongDivStyle() {
    if (songDiv) {
        songDiv.style.color = "#f8f9fa";
        songDiv.style.backgroundColor = "#495057";
    }
}

function applySongDivStyle() {
    songDiv = document.getElementById(n);
    if (songDiv) {
        songDiv.style.color = "#f8f9fa";
        songDiv.style.backgroundColor = "#1c7ed6";
        scrollParentToChild(document.getElementById("playlist"), songDiv);
    }
}

function shufflePlaylist() {
    shuffleArray(playlistIndeces);
    playlistDiv = document.getElementById("playlist");
    playlistDiv.innerHTML = "";
    populatePlaylistDiv();
    applySongDivStyle();
    updateStatusDisplay();
    loadNewSong();
}

function toggleLoop() {
    loop = !loop;
    const loopStatus = document.getElementById('loop-status');
    loopStatus.textContent = `Loop: ${loop ? 'On' : 'Off'}`;
    console.log("Toggled loop: " + loop);
}

// Initialize the app
initializePlayer();

// Event listeners
document.getElementById('prev').addEventListener('click', goToPreviousSong);
document.getElementById('next').addEventListener('click', goToNextSong);
document.getElementById('pause').addEventListener('click', pauseSong);
document.getElementById('play').addEventListener('click', playSong);
document.getElementById('shuffle').addEventListener('click', shufflePlaylist);
document.getElementById('loop').addEventListener('click', toggleLoop);