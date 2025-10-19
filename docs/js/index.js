const animeListUrl = 'https://mal.secondo.aero/data/animelist.json';

// State Management
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
let currentSourceType = 'yt_url';
let wantsToAutoplay = true;

// ==================== UTILITY FUNCTIONS ====================

function createArray(n) {
    return Array.from({ length: n }, (_, i) => i);
}

function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

function scrollParentToChild(parent, child) {
    const parentRect = parent.getBoundingClientRect();
    const parentViewableArea = { height: parent.clientHeight, width: parent.clientWidth };
    const childRect = child.getBoundingClientRect();
    const isViewable = (childRect.top >= parentRect.top) &&
        (childRect.bottom <= parentRect.top + parentViewableArea.height);

    if (!isViewable) {
        const scrollTop = childRect.top - parentRect.top;
        const scrollBot = childRect.bottom - parentRect.bottom;
        parent.scrollTop += Math.abs(scrollTop) < Math.abs(scrollBot) ? scrollTop : scrollBot;
    }
}

function jumpN(m) {
    const length = animePlaylist.length;
    if (loop) {
        return ((n + m) % length + length) % length;
    }
    return Math.max(0, Math.min(length - 1, n + m));
}

// ==================== DATA MANAGEMENT ====================

async function fetchAnimeList(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
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

async function retrievePlaylist() {
    await loadAnimeList();

    animePlaylist = [];
    animePlaylistMap = [];

    animeList.anime.forEach((anime, animeIndex) => {
        // Process opening themes
        anime.opening_themes.forEach((theme, themeIndex) => {
            if (theme.at_url || theme.yt_url) {
                addToPlaylist(anime, theme, animeIndex, "opening_themes", themeIndex);
            }
        });

        // Process ending themes
        anime.ending_themes.forEach((theme, themeIndex) => {
            if (theme.at_url || theme.yt_url) {
                addToPlaylist(anime, theme, animeIndex, "ending_themes", themeIndex);
            }
        });
    });

    console.log(`Loaded ${animePlaylist.length} songs with valid URLs`);
    playlistIndeces = createArray(animePlaylist.length);
    populatePlaylistDiv();
}

function addToPlaylist(anime, theme, animeIndex, type, themeIndex) {
    animePlaylist.push({
        at_url: theme.at_url,
        yt_url: theme.yt_url,
        name: theme.name,
        artist: theme.artist,
        anime_index: animeIndex,
        type: type,
        theme_index: themeIndex,
        anime_id: anime.id
    });
    animePlaylistMap.push([animeIndex, type, themeIndex]);
}

function populatePlaylistDiv() {
    playlistDiv = document.getElementById('playlist');
    playlistDiv.innerHTML = '';

    animePlaylistMap.forEach((songMap, index) => {
        const playlistItem = createPlaylistItem(songMap, index);
        playlistDiv.appendChild(playlistItem);
    });
}

function createPlaylistItem(songMap, index) {
    const currentSongData = animePlaylist[playlistIndeces[index]];
    const anime = animeList.anime[songMap[0]];

    // Create elements
    const playlistItem = document.createElement("div");
    playlistItem.className = "playlist-item";
    playlistItem.id = index;
    playlistItem.onclick = () => goToSong(index);

    const playlistItemText = document.createElement("div");
    playlistItemText.className = "playlist-item-text";

    const playlistItemImage = document.createElement("div");
    playlistItemImage.className = "playlist-item-image";

    // Create content
    playlistItemText.appendChild(createTextElement("nameline", currentSongData.name));
    playlistItemText.appendChild(createTextElement("artistline", ` by ${currentSongData.artist}`));
    playlistItemText.appendChild(createTextElement("animeline", `【${anime.title}】`));
    playlistItemText.appendChild(createEpisodeContainer(songMap[1], currentSongData));

    playlistItemImage.appendChild(createAnimeImage(anime.picture, currentSongData.anime_id));

    // Assemble item
    playlistItem.appendChild(playlistItemImage);
    playlistItem.appendChild(playlistItemText);

    return playlistItem;
}

function createTextElement(className, text) {
    const element = document.createElement("span");
    element.className = `playlist-item-${className}`;
    element.textContent = text;
    return element;
}

function createEpisodeContainer(type, songData) {
    const container = document.createElement("div");
    container.className = "playlist-item-episode-container";

    const episodeLine = document.createElement("span");
    episodeLine.className = "playlist-item-episodeline";
    episodeLine.textContent = type.split("_")[0];

    const sourceIndicator = document.createElement("span");
    sourceIndicator.className = "playlist-item-source";
    const sources = [];
    if (songData.yt_url) sources.push('YT');
    if (songData.at_url) sources.push('AT');
    sourceIndicator.textContent = ` [${sources.join('/')}]`;

    container.appendChild(episodeLine);
    container.appendChild(sourceIndicator);
    return container;
}

function createAnimeImage(src, animeId) {
    const image = document.createElement("img");
    image.className = "playlist-item-animeimage";
    image.src = src;

    image.addEventListener('error', () => {
        console.warn('Failed to load image:', src);
        image.style.display = 'none';
    });

    image.addEventListener('load', () => {
        console.log('Successfully loaded image:', src);
    });

    const link = document.createElement("a");
    link.href = `https://myanimelist.net/anime/${animeId}`;
    link.target = "_blank";
    link.appendChild(image);

    return link;
}

// ==================== PLAYER CONTROLS ====================

function getCurrentSongURL() {
    const currentSong = animePlaylist[playlistIndeces[n]];
    return currentSong[currentSourceType] || currentSong.at_url || currentSong.yt_url;
}

function getAvailableSources() {
    const currentSong = animePlaylist[playlistIndeces[n]];
    const sources = [];
    if (currentSong.at_url) sources.push('at_url');
    if (currentSong.yt_url) sources.push('yt_url');
    return sources;
}

function loadNewSong() {
    const songUrl = getCurrentSongURL();
    console.log('Loading new song:', songUrl, 'Source:', currentSourceType);

    if (!songUrl) {
        console.log('No URL available for current source, skipping to next song');
        switchSourceOnError();
        return;
    }

    if (!player) {
        console.error('Player not initialized');
        return;
    }

    // Set the source based on URL type
    const isYouTube = songUrl.includes('youtube.com') || songUrl.includes('youtu.be');
    player.setSrc(songUrl, isYouTube ? 'video/youtube' : undefined);
    player.load();

    // Update UI
    applySongDivStyle();
    updateMediaSessionMetadata();
    updateStatusDisplay();
    updateSourceDisplay();

    // Auto-play the new song
    setTimeout(playSongAutomatic, 100);
}

function playSongAutomatic() {
    console.log('Attempting automatic playback');
    if (!player?.media) return;

    const playPromise = player.media.play();
    if (!playPromise) return;

    playPromise
        .then(() => {
            console.log('Automatic playback started successfully');
            isPlaying = true;
            updatePlayPauseButtons();
            updateMediaSessionPlaybackState('playing');
            updateStatusDisplay();
        })
        .catch(error => {
            console.warn('Automatic playback failed:', error);

            if (error.name === 'NotSupportedError' || error.name === 'NotAllowedError') {
                // Source might be unavailable, skip to next song
                console.log('Source unavailable, skipping to next song');
                switchSourceOnError();
            } else {
                document.getElementById('player-status').textContent = '⏸️ Click play to start';
                isPlaying = false;
                updatePlayPauseButtons();
                wantsToAutoplay = true;
            }
        });
}

function playSong() {
    console.log('User-initiated playback');
    if (!player) return;

    const playPromise = player.play();
    if (!playPromise) return;

    playPromise
        .then(() => {
            console.log('User playback started successfully');
            isPlaying = true;
            updatePlayPauseButtons();
            updateMediaSessionPlaybackState('playing');
            updateStatusDisplay();
            wantsToAutoplay = false;
        })
        .catch(error => {
            console.error('User playback failed:', error);
            document.getElementById('player-status').textContent = '❌ Playback error';
            isPlaying = false;
            updatePlayPauseButtons();
        });
}

function pauseSong() {
    console.log('Pausing song');
    player?.pause();
}

function updatePlayPauseButtons() {
    const playBtn = document.getElementById('play');
    const pauseBtn = document.getElementById('pause');

    playBtn.style.display = isPlaying ? 'none' : 'inline-block';
    pauseBtn.style.display = isPlaying ? 'inline-block' : 'none';
}

// ==================== NAVIGATION ====================

function goToNextSong() {
    console.log('Next song');
    navigateToSong(jumpN(1));
}

function goToPreviousSong() {
    console.log('Previous song');
    navigateToSong(jumpN(-1));
}

function goToSong(new_n) {
    console.log('Go to song:', new_n);
    navigateToSong(new_n);
}

function navigateToSong(newIndex) {
    const wasPlaying = isPlaying;
    clearSongDivStyle();
    n = newIndex;
    loadNewSong();

    if (wasPlaying) {
        wantsToAutoplay = true;
    }
}

function clearSongDivStyle() {
    songDiv?.classList.remove('active');
}

function applySongDivStyle() {
    songDiv = document.getElementById(n.toString());
    if (songDiv) {
        songDiv.classList.add('active');
        scrollParentToChild(document.getElementById("playlist"), songDiv);
    }
}

// ==================== SOURCE MANAGEMENT ====================

const SOURCE_DISPLAY_NAMES = {
    'yt_url': 'YouTube',
    'at_url': 'AnimeThemes'
};

function getCurrentSongURL() {
    const currentSong = animePlaylist[playlistIndeces[n]];
    return currentSong[currentSourceType];
}

function getAvailableSources() {
    const currentSong = animePlaylist[playlistIndeces[n]];
    const sources = [];
    if (currentSong.yt_url) sources.push('yt_url');
    if (currentSong.at_url) sources.push('at_url');
    return sources;
}

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

    // Update tooltip with next source in cycle
    const nextSourceIndex = (nextIndex + 1) % availableSources.length;
    const nextSource = availableSources[nextSourceIndex];
    const switchButton = document.getElementById('switch-source');
    switchButton.setAttribute('data-tooltip', `Switch to ${SOURCE_DISPLAY_NAMES[nextSource]}`);

    // Reload with new source
    const wasPlaying = isPlaying;
    loadNewSong();

    if (wasPlaying) {
        setTimeout(playSong, 500);
    }

    updateSourceDisplay();
}

function switchSourceOnError() {
    // Don't auto-switch sources, just go to next song
    console.log('Source unavailable, skipping to next song');
    goToNextSong();
}

function updateSourceDisplay() {
    const sourceStatus = document.getElementById('source-status');
    const currentSource = document.getElementById('current-source');
    const displayName = SOURCE_DISPLAY_NAMES[currentSourceType] || currentSourceType;

    sourceStatus && (sourceStatus.textContent = `Source: ${displayName}`);
    currentSource && (currentSource.textContent = displayName);
}

// ==================== PLAYLIST MANAGEMENT ====================

function shufflePlaylist() {
    shuffleArray(playlistIndeces);
    playlistDiv.innerHTML = "";
    populatePlaylistDiv();
    applySongDivStyle();
    updateStatusDisplay();
    loadNewSong();
}

function toggleLoop() {
    loop = !loop;
    const loopButton = document.getElementById('loop');

    if (loop) {
        loopButton.classList.add('loop-on');
        loopButton.classList.remove('loop-off');
    } else {
        loopButton.classList.add('loop-off');
        loopButton.classList.remove('loop-on');
    }

    console.log("Toggled loop:", loop);
}

// ==================== UI UPDATES ====================

function updateStatusDisplay() {
    const currentSongData = animePlaylist[playlistIndeces[n]];
    const elements = {
        'current-song-name': currentSongData.name || 'Unknown',
        'playback-status': isPlaying ? '▶️ Playing' : '⏸️ Paused',
        'player-status': wantsToAutoplay && !isPlaying ? '⏳ Loading...' : isPlaying ? '✅ Playing' : '✅ Ready',
        'current-position': `Song ${n + 1} of ${animePlaylist.length}`
    };

    Object.entries(elements).forEach(([id, text]) => {
        const element = document.getElementById(id);
        element && (element.textContent = text);
    });
}

// ==================== MEDIA SESSION ====================

function initializeIndependentMediaSession() {
    if (!('mediaSession' in navigator)) {
        console.log('Media Session API not supported');
        return;
    }

    console.log('Initializing independent media session...');

    try {
        // Clear existing handlers
        ['play', 'pause', 'previoustrack', 'nexttrack', 'seekbackward', 'seekforward'].forEach(action => {
            try { navigator.mediaSession.setActionHandler(action, null); } catch (e) { }
        });

        // Set custom handlers
        const handlers = {
            play: () => { console.log('🎵 Media session: PLAY'); playSong(); },
            pause: () => { console.log('⏸️ Media session: PAUSE'); pauseSong(); },
            previoustrack: () => { console.log('⏮️ Media session: PREVIOUS'); goToPreviousSong(); },
            nexttrack: () => { console.log('⏭️ Media session: NEXT'); goToNextSong(); },
            seekbackward: (details) => handleSeek(-(details.seekOffset || 10)),
            seekforward: (details) => handleSeek(details.seekOffset || 10)
        };

        Object.entries(handlers).forEach(([action, handler]) => {
            navigator.mediaSession.setActionHandler(action, handler);
        });

        updateMediaSessionMetadata();
        console.log('✅ Independent media session initialized');
    } catch (error) {
        console.error('❌ Error setting media session:', error);
    }
}

function handleSeek(offset) {
    if (!player?.media) return;

    const newTime = player.media.currentTime + offset;
    player.media.currentTime = Math.max(0, Math.min(player.media.duration, newTime));
    console.log(`⏩ Media session: SEEK ${offset > 0 ? 'FORWARD' : 'BACKWARD'}`);
}

function updateMediaSessionMetadata() {
    if (!('mediaSession' in navigator)) return;

    const currentSongData = animePlaylist[playlistIndeces[n]];

    try {
        navigator.mediaSession.metadata = new MediaMetadata({
            title: currentSongData.name || 'Unknown Title',
            artist: currentSongData.artist || 'Unknown Artist',
            album: animeList.anime[currentSongData.anime_index].title || 'Anime Themes',
            artwork: [{
                src: animeList.anime[currentSongData.anime_index].picture || '',
                sizes: '225x225',
                type: 'image/jpeg'
            }]
        });
        console.log('Media session metadata updated:', currentSongData.name);
    } catch (error) {
        console.error('Error updating media session metadata:', error);
    }
}

function updateMediaSessionPlaybackState(state) {
    if ('mediaSession' in navigator) {
        navigator.mediaSession.playbackState = state;
    }
}

// ==================== PLAYER INITIALIZATION ====================

function handleAutoplayPolicies() {
    const tryAutoplay = () => {
        if (wantsToAutoplay && !isPlaying) playSongAutomatic();
    };

    document.addEventListener('click', tryAutoplay, { once: true });
    document.addEventListener('touchstart', tryAutoplay, { once: true });
}

function initializeControls() {
    const loopButton = document.getElementById('loop');
    loopButton.classList.add(loop ? 'loop-on' : 'loop-off');

    const switchButton = document.getElementById('switch-source');
    const availableSources = getAvailableSources();

    if (availableSources.length > 1) {
        const currentIndex = availableSources.indexOf(currentSourceType);
        const nextSource = availableSources[(currentIndex + 1) % availableSources.length];
        const nextDisplayName = SOURCE_DISPLAY_NAMES[nextSource] || nextSource;
        switchButton.setAttribute('data-tooltip', `Switch to ${nextDisplayName}`);
        switchButton.disabled = false;
        switchButton.style.opacity = '1';
    } else {
        switchButton.setAttribute('data-tooltip', 'Only one source available');
        switchButton.disabled = true;
        switchButton.style.opacity = '0.5';
    }

    updateSourceDisplay();
}

async function initializePlayer() {
    player = new MediaElementPlayer('mediaelement-player', {
        features: ['playpause', 'current', 'progress', 'duration', 'volume', 'fullscreen'],
        stretching: 'auto',
        youtube: { cc_load_policy: 1, iv_load_policy: 3, modestbranding: 1, rel: 0 },

        success: function (media) {
            console.log('MediaElement.js player initialized successfully');

            const eventHandlers = {
                play: () => handlePlayerEvent('Play', true),
                pause: () => handlePlayerEvent('Pause', false),
                ended: handlePlaybackEnded,
                error: (e) => {
                    console.error('MediaElement.js error:', e);
                    document.getElementById('player-status').textContent = '❌ Error loading video';

                    // On error, skip to next song instead of switching source
                    setTimeout(() => {
                        switchSourceOnError();
                    }, 1000);
                },
                loadeddata: () => {
                    console.log('MediaElement.js: Video loaded successfully');
                    document.getElementById('player-status').textContent = '✅ Ready';
                    if (wantsToAutoplay) setTimeout(playSongAutomatic, 200);
                },
                canplay: () => {
                    if (wantsToAutoplay && !isPlaying) setTimeout(playSongAutomatic, 300);
                }
            };

            Object.entries(eventHandlers).forEach(([event, handler]) => {
                media.addEventListener(event, handler);
            });
        },

        error: (error) => {
            console.error('MediaElement.js initialization error:', error);
        }
    });

    await retrievePlaylist();
    initializeIndependentMediaSession();

    // Register service worker
    if ('serviceWorker' in navigator) {
        try {
            await navigator.serviceWorker.register('sw.js');
            console.log('Service Worker registered successfully');
        } catch (error) {
            console.warn('Service Worker registration failed:', error);
        }
    }

    initializeControls();
    applySongDivStyle();
    updateMediaSessionMetadata();
    updateStatusDisplay();

    wantsToAutoplay = true;
    isPlaying = false;
    updatePlayPauseButtons();
    updateMediaSessionPlaybackState('paused');
    handleAutoplayPolicies();

    console.log('Player ready - attempting autoplay...');
}

function handlePlayerEvent(eventName, playing) {
    console.log(`MediaElement.js: ${eventName} event`);
    isPlaying = playing;
    updatePlayPauseButtons();
    updateMediaSessionPlaybackState(playing ? 'playing' : 'paused');
    updateStatusDisplay();
}

function handlePlaybackEnded() {
    console.log('MediaElement.js: Ended event');
    if (loop || n < animePlaylist.length - 1) {
        setTimeout(goToNextSong, 500);
    } else {
        isPlaying = false;
        updatePlayPauseButtons();
        updateMediaSessionPlaybackState('none');
        updateStatusDisplay();
        wantsToAutoplay = false;
    }
}

// ==================== INITIALIZATION ====================

// Add CSS for source indicator
const style = document.createElement('style');
style.textContent = `.playlist-item-source { margin-left: 5px; font-style: italic; }`;
document.head.appendChild(style);

// Event listeners
const controlHandlers = {
    'prev': goToPreviousSong,
    'next': goToNextSong,
    'pause': pauseSong,
    'play': playSong,
    'shuffle': shufflePlaylist,
    'loop': toggleLoop,
    'switch-source': switchSource
};

Object.entries(controlHandlers).forEach(([id, handler]) => {
    document.getElementById(id)?.addEventListener('click', handler);
});

// Initialize the app
initializePlayer();