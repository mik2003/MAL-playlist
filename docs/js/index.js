const animeListUrl = 'https://mal.secondo.aero/data/animelist.json';
let player;
let video;
let animeList;
let animePlaylist = [];
let animePlaylistMap = [];
let playlistIndeces = [];
let playlistDiv;
let songDiv;
let n = 0;
let isPlaying = false;
let loop = false;

async function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        try {
            // Use a more specific path if needed
            const registration = await navigator.serviceWorker.register('/sw.js');
            console.log('SW registered: ', registration);
            return registration;
        } catch (registrationError) {
            console.log('SW registration failed: ', registrationError);
            return null;
        }
    }
    console.log('Service Workers not supported');
    return null;
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

        animeImage.addEventListener('error', function () {
            console.warn('Failed to load image:', this.src);
            // Set a placeholder image or hide the image
            this.style.display = 'none';
        });

        animeImage.addEventListener('load', function () {
            console.log('Successfully loaded image:', this.src);
        });
    }
}

async function fetchAnimeList(animeListUrl) {
    try {
        let response = await fetch(animeListUrl);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        let data = await response.json();
        return data;
    } catch (error) {
        console.error('Failed to fetch anime list:', error);
        // You might want to show a user-friendly error message here
        document.getElementById('player-status').textContent = '❌ Failed to load playlist';
        throw error; // Re-throw to handle in calling function
    }
}

async function loadAnimeList() {
    animeList = await fetchAnimeList(animeListUrl);
    console.log(animeList);
}

async function retrievePlaylist() {
    await loadAnimeList();

    animePlaylist = [];
    animePlaylistMap = [];

    for (i = 0; i < animeList.anime.length; i++) {
        for (j = 0; j < animeList.anime[i].opening_themes.length; j++) {
            const at_url = animeList.anime[i].opening_themes[j].at_url;
            if (at_url) { // Only add if URL exists
                animePlaylist.push(at_url);
                animePlaylistMap.push([i, "opening_themes", j]);
            }
        }
        for (k = 0; k < animeList.anime[i].ending_themes.length; k++) {
            const at_url = animeList.anime[i].ending_themes[k].at_url;
            if (at_url) { // Only add if URL exists
                animePlaylist.push(at_url);
                animePlaylistMap.push([i, "ending_themes", k]);
            }
        }
    }

    console.log(`Loaded ${animePlaylist.length} songs with valid URLs`);
    i = 0; j = 0; k = 0;
    playlistIndeces = createArray(animePlaylist.length);
    populatePlaylistDiv();
}

async function initializePlayer() {
    player = document.getElementById('player');
    video = document.createElement('video');

    // Add essential video attributes
    video.controls = true;
    video.style.width = '100%';
    video.style.maxWidth = '800px';
    video.autoplay = true;

    // Add event listeners for the video
    video.addEventListener('play', () => {
        console.log('Video play event');
        isPlaying = true;
        updatePlayPauseButtons();
        updateMediaSessionPlaybackState('playing');
        updateStatusDisplay();
    });

    video.addEventListener('pause', () => {
        console.log('Video pause event');
        isPlaying = false;
        updatePlayPauseButtons();
        updateMediaSessionPlaybackState('paused');
        updateStatusDisplay();
    });

    video.addEventListener('ended', () => {
        console.log('Video ended event');
        if (loop || n < animePlaylist.length - 1) {
            goToNextSong();
        }
    });

    video.addEventListener('error', (e) => {
        console.error('Video error:', e);
        console.error('Video error details:', video.error);
        document.getElementById('player-status').textContent = '❌ Error loading video';
    });

    video.addEventListener('loadeddata', () => {
        console.log('Video loaded successfully');
        document.getElementById('player-status').textContent = '✅ Ready';
    });

    player.appendChild(video);

    await retrievePlaylist();
    initializeIndependentMediaSession();

    // Register service worker with better error handling
    if ('serviceWorker' in navigator) {
        try {
            const registration = await navigator.serviceWorker.register('sw.js');
            console.log('Service Worker registered successfully');
        } catch (error) {
            console.warn('Service Worker registration failed:', error);
        }
    }

    applySongDivStyle();
    updateMediaSessionMetadata();
    updateStatusDisplay();

    isPlaying = false;
    updatePlayPauseButtons();
    updateMediaSessionPlaybackState('paused');
    console.log('Player ready and paused - click play to start');
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
    console.log('Attempting to play song');
    if (video && video.src) {
        video.play().then(() => {
            console.log('Playback started successfully');
        }).catch(error => {
            console.error('Playback failed:', error);
            document.getElementById('player-status').textContent = '❌ Playback failed';
        });
    } else {
        console.error('No video source available');
        loadNewSong();
        // Try playing again after a short delay
        setTimeout(() => {
            if (video.src) {
                video.play().catch(e => console.error('Retry playback failed:', e));
            }
        }, 100);
    }
}

function pauseSong() {
    console.log('Pausing song');
    if (video) {
        video.pause();
    }
}

function loadNewSong() {
    const songUrl = getCurrentSongURL();
    console.log('Loading new song:', songUrl);

    if (songUrl && video) {
        video.src = songUrl;
        video.load(); // Important: load the new source

        // Update UI immediately
        applySongDivStyle();
        updateMediaSessionMetadata();
        updateStatusDisplay();

        // Auto-play if was playing before
        if (isPlaying) {
            setTimeout(() => {
                video.play().catch(e => {
                    console.warn('Auto-play prevented:', e);
                    isPlaying = false;
                    updatePlayPauseButtons();
                });
            }, 100);
        }
    } else {
        console.error('Invalid song URL or video element:', songUrl);
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

function getCurrentSongURL() {
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
