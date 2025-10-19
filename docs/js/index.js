const animeListUrl = 'http://127.0.0.1:5500/docs/data/animelist.json';
let player;
let animeList;
let animePlaylist = [];
let animePlaylistMap = [];
let playlistIndeces = [];
let playlistDiv;
let songDiv;
let n = 0;
let isPlaying = false;
let loop = false;
let currentSourceType = 'at_url';

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
        document.getElementById('player-status').textContent = '❌ Failed to load playlist';
        throw error;
    }
}

async function loadAnimeList() {
    animeList = await fetchAnimeList(animeListUrl);
    console.log('Anime list loaded:', animeList);
}

// Modify your data structure to store both URLs
async function retrievePlaylist() {
    await loadAnimeList();

    animePlaylist = [];
    animePlaylistMap = [];

    for (let i = 0; i < animeList.anime.length; i++) {
        // Process opening themes
        for (let j = 0; j < animeList.anime[i].opening_themes.length; j++) {
            const theme = animeList.anime[i].opening_themes[j];
            if (theme.at_url || theme.yt_url) {
                animePlaylist.push({
                    at_url: theme.at_url,
                    yt_url: theme.yt_url,
                    name: theme.name,
                    artist: theme.artist,
                    anime_index: i,
                    type: "opening_themes",
                    theme_index: j,
                    anime_id: animeList.anime[i].id
                });
                animePlaylistMap.push([i, "opening_themes", j]);
            }
        }

        // Process ending themes
        for (let k = 0; k < animeList.anime[i].ending_themes.length; k++) {
            const theme = animeList.anime[i].ending_themes[k];
            if (theme.at_url || theme.yt_url) {
                animePlaylist.push({
                    at_url: theme.at_url,
                    yt_url: theme.yt_url,
                    name: theme.name,
                    artist: theme.artist,
                    anime_index: i,
                    type: "ending_themes",
                    theme_index: k,
                    anime_id: animeList.anime[i].id
                });
                animePlaylistMap.push([i, "ending_themes", k]);
            }
        }
    }

    console.log(`Loaded ${animePlaylist.length} songs with valid URLs`);
    playlistIndeces = createArray(animePlaylist.length);
    populatePlaylistDiv();
}

function populatePlaylistDiv() {
    playlistDiv = document.getElementById('playlist');
    playlistDiv.innerHTML = '';

    for (let i = 0; i < animePlaylistMap.length; i++) {
        let playlistItem = document.createElement("div");
        playlistItem.setAttribute("class", "playlist-item");
        playlistItem.setAttribute("id", i);

        let playlistItemText = document.createElement("div");
        playlistItemText.setAttribute("class", "playlist-item-text");

        let playlistItemImage = document.createElement("div");
        playlistItemImage.setAttribute("class", "playlist-item-image");

        let currentSongMap = animePlaylistMap[playlistIndeces[i]];
        let currentSongData = animePlaylist[playlistIndeces[i]];

        let animeImage = document.createElement("img");
        animeImage.setAttribute("class", "playlist-item-animeimage");
        animeImage.setAttribute("src", animeList.anime[currentSongMap[0]].picture);

        // Name line
        let nameLine = document.createElement("span");
        nameLine.setAttribute("class", "playlist-item-nameline");
        nameLine.innerText = `${currentSongData.name}`;
        playlistItemText.appendChild(nameLine);

        // Artist line
        let artistLine = document.createElement("span");
        artistLine.setAttribute("class", "playlist-item-artistline");
        artistLine.innerText = ` by ${currentSongData.artist}`;
        playlistItemText.appendChild(artistLine);

        // Anime line
        let animeLine = document.createElement("span");
        animeLine.setAttribute("class", "playlist-item-animeline");
        animeLine.innerText = `【${animeList.anime[currentSongMap[0]].title}】`;
        playlistItemText.appendChild(animeLine);

        // Episode line with source indicator - NOW COMBINED
        let episodeContainer = document.createElement("div");
        episodeContainer.setAttribute("class", "playlist-item-episode-container");

        let episodeLine = document.createElement("span");
        episodeLine.setAttribute("class", "playlist-item-episodeline");
        episodeLine.innerText = `${currentSongMap[1].split("_")[0]}`;
        episodeContainer.appendChild(episodeLine);

        // Add source indicator right after episode
        let sourceIndicator = document.createElement("span");
        sourceIndicator.setAttribute("class", "playlist-item-source");
        const sources = [];
        if (currentSongData.at_url) sources.push('AT');
        if (currentSongData.yt_url) sources.push('YT');
        sourceIndicator.innerText = ` [${sources.join('/')}]`;
        episodeContainer.appendChild(sourceIndicator);

        playlistItemText.appendChild(episodeContainer);

        let animeLink = document.createElement("a");
        animeLink.setAttribute("href", `https://myanimelist.net/anime/${currentSongData.anime_id}`);
        animeLink.setAttribute("target", "_blank");
        animeLink.appendChild(animeImage);
        playlistItemImage.appendChild(animeLink);

        playlistItem.setAttribute('onclick', 'goToSong(' + i + ')');
        playlistItem.appendChild(playlistItemImage);
        playlistItem.appendChild(playlistItemText);
        playlistDiv.appendChild(playlistItem);

        animeImage.addEventListener('error', function () {
            console.warn('Failed to load image:', this.src);
            this.style.display = 'none';
        });

        animeImage.addEventListener('load', function () {
            console.log('Successfully loaded image:', this.src);
        });
    }
}

// Initialize MediaElement.js player
async function initializePlayer() {
    // Initialize MediaElement.js player
    player = new MediaElementPlayer('mediaelement-player', {
        features: ['playpause', 'current', 'progress', 'duration', 'volume', 'fullscreen'],
        stretching: 'auto',

        // YouTube support
        youtube: {
            cc_load_policy: 1,
            iv_load_policy: 3,
            modestbranding: 1,
            rel: 0
        },

        success: function (media, element, instance) {
            console.log('MediaElement.js player initialized successfully');

            // Add event listeners
            media.addEventListener('play', () => {
                console.log('MediaElement.js: Play event');
                isPlaying = true;
                updatePlayPauseButtons();
                updateMediaSessionPlaybackState('playing');
                updateStatusDisplay();
            });

            media.addEventListener('pause', () => {
                console.log('MediaElement.js: Pause event');
                isPlaying = false;
                updatePlayPauseButtons();
                updateMediaSessionPlaybackState('paused');
                updateStatusDisplay();
            });

            media.addEventListener('ended', () => {
                console.log('MediaElement.js: Ended event');
                if (loop || n < animePlaylist.length - 1) {
                    goToNextSong();
                }
            });

            media.addEventListener('error', (e) => {
                console.error('MediaElement.js error:', e);
                document.getElementById('player-status').textContent = '❌ Error loading video';
                switchSourceOnError();
            });

            media.addEventListener('loadeddata', () => {
                console.log('MediaElement.js: Video loaded successfully');
                document.getElementById('player-status').textContent = '✅ Ready';
            });
        },

        error: function (error) {
            console.error('MediaElement.js initialization error:', error);
        }
    });

    await retrievePlaylist();
    initializeIndependentMediaSession();

    // Register service worker
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
            if (player && player.media) {
                const newTime = Math.max(player.media.currentTime - (details.seekOffset || 10), 0);
                player.media.currentTime = newTime;
            }
        });

        navigator.mediaSession.setActionHandler('seekforward', (details) => {
            console.log('⏩ Independent Media session: SEEK FORWARD');
            if (player && player.media) {
                const newTime = Math.min(player.media.currentTime + (details.seekOffset || 10), player.media.duration);
                player.media.currentTime = newTime;
            }
        });

        updateMediaSessionMetadata();
        console.log('✅ Independent media session initialized');
    } catch (error) {
        console.error('❌ Error setting independent media session:', error);
    }
}

function updateMediaSessionMetadata() {
    if (!('mediaSession' in navigator)) return;

    const currentSongData = animePlaylist[playlistIndeces[n]];

    try {
        const metadata = new MediaMetadata({
            title: currentSongData.name || 'Unknown Title',
            artist: currentSongData.artist || 'Unknown Artist',
            album: animeList.anime[currentSongData.anime_index].title || 'Anime Themes',
            artwork: [
                {
                    src: animeList.anime[currentSongData.anime_index].picture || '',
                    sizes: '225x225',
                    type: 'image/jpeg'
                }
            ]
        });

        navigator.mediaSession.metadata = metadata;
        console.log('Independent media session metadata updated:', currentSongData.name);
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
    const currentSongData = animePlaylist[playlistIndeces[n]];

    if (document.getElementById('current-song-name')) {
        document.getElementById('current-song-name').textContent = currentSongData.name || 'Unknown';
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

// Get current song URL based on source type
function getCurrentSongURL() {
    const currentSong = animePlaylist[playlistIndeces[n]];
    return currentSong[currentSourceType] || currentSong.at_url || currentSong.yt_url;
}

// Get available sources for current song
function getAvailableSources() {
    const currentSong = animePlaylist[playlistIndeces[n]];
    const sources = [];

    if (currentSong.at_url) sources.push('at_url');
    if (currentSong.yt_url) sources.push('yt_url');

    return sources;
}

// Switch between at_url and yt_url
function switchSource() {
    const availableSources = getAvailableSources();

    if (availableSources.length < 2) {
        console.log('Only one source available for this song');
        return;
    }

    // Cycle to next available source
    const currentIndex = availableSources.indexOf(currentSourceType);
    const nextIndex = (currentIndex + 1) % availableSources.length;
    currentSourceType = availableSources[nextIndex];

    console.log(`Switched source to: ${currentSourceType}`);

    // Reload the current song with new source
    const wasPlaying = isPlaying;
    loadNewSong();

    // Restore play state if it was playing
    if (wasPlaying) {
        setTimeout(() => {
            playSong();
        }, 500);
    }

    updateSourceDisplay();
}

// Switch source automatically on error
function switchSourceOnError() {
    const availableSources = getAvailableSources();

    if (availableSources.length > 1) {
        console.log('Auto-switching source due to error...');
        switchSource();
    }
}

// Update source display
function updateSourceDisplay() {
    const sourceStatus = document.getElementById('source-status');
    const currentSource = document.getElementById('current-source');

    if (sourceStatus) {
        sourceStatus.textContent = `Source: ${currentSourceType}`;
    }
    if (currentSource) {
        currentSource.textContent = currentSourceType;
    }
}

// Modified loadNewSong function
function loadNewSong() {
    const songUrl = getCurrentSongURL();
    console.log('Loading new song:', songUrl, 'Source:', currentSourceType);

    if (songUrl && player) {
        // Set the source based on URL type
        if (songUrl.includes('youtube.com') || songUrl.includes('youtu.be')) {
            player.setSrc(songUrl, 'video/youtube');
        } else {
            player.setSrc(songUrl);
        }

        player.load();

        // Update UI
        applySongDivStyle();
        updateMediaSessionMetadata();
        updateStatusDisplay();
        updateSourceDisplay();

        // Auto-play if was playing before
        if (isPlaying) {
            setTimeout(() => {
                playSong();
            }, 500);
        }
    } else {
        console.error('Invalid song URL or player not initialized:', songUrl);
    }
}

// Playback control functions
function playSong() {
    console.log('Attempting to play song');
    if (player) {
        player.play();
    }
}

function pauseSong() {
    console.log('Pausing song');
    if (player) {
        player.pause();
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

function clearSongDivStyle() {
    if (songDiv) {
        songDiv.classList.remove('active');
    }
}

function applySongDivStyle() {
    songDiv = document.getElementById(n);
    if (songDiv) {
        songDiv.classList.add('active');
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
document.getElementById('switch-source').addEventListener('click', switchSource);

// Add CSS for source indicator
const style = document.createElement('style');
style.textContent = `
    .playlist-item-source {
        margin-left: 5px;
        font-style: italic;
    }
`;
document.head.appendChild(style);