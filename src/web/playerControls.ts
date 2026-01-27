import { goToNextSong, goToPreviousSong } from './navigation.js';
import { filterPlaylist, getAvailableSources, getCurrentSongURL, populatePlaylistDiv } from './playlist.js';
import { applySongDivStyle, updateSourceDisplay, updateStatusDisplay } from './ui.js';
import { initializeIndependentMediaSession, updateMediaSessionMetadata, updateMediaSessionPlaybackState } from './mediaSession.js';
import { retrievePlaylist } from './data.js';
import { initializeTooltips, initializeControls } from './ui.js';
import { playerState, SOURCE_DISPLAY_NAMES } from './const.js';
import { shuffleArray } from './utils.js';
import { SourceType } from './types.js';


export function loadNewSong() {
    const songUrl = getCurrentSongURL();
    console.log('Loading new song:', songUrl, 'Source:', playerState.currentSourceType);

    if (!songUrl) {
        console.log('No URL available for current source, skipping to next song');
        if (playerState.animePlaylist && playerState.animePlaylist.length > 0) {
            goToNextSong();
        }
        return;
    }

    const player = playerState.player;

    if (!player) {
        console.error('Player not initialized');
        return;
    }

    const isYouTube = songUrl.includes('youtube.com') || songUrl.includes('youtu.be');

    // Clear previous source and stop
    player.pause();
    player.setSrc('');

    // Let MediaElement.js handle the source detection
    console.log('Setting source for MediaElement.js');
    player.setSrc(songUrl);

    player.load();

    // Use MediaElement.js events to detect when it's ready to play
    const onCanPlay = () => {
        console.log('MediaElement.js: Can play event received');
        player.media.removeEventListener('canplay', onCanPlay);
        player.media.removeEventListener('loadeddata', onLoadedData);
        playSong();
    };

    const onLoadedData = () => {
        console.log('MediaElement.js: Loaded data event received');
        player.media.removeEventListener('canplay', onCanPlay);
        player.media.removeEventListener('loadeddata', onLoadedData);
        playSong();
    };

    // For YouTube, also listen for the YouTube-specific ready event
    if (isYouTube) {
        const onYouTubeReady = () => {
            console.log('YouTube player ready');
            player.media.removeEventListener('canplay', onCanPlay);
            player.media.removeEventListener('loadeddata', onLoadedData);
            // Small delay for YouTube iframe to initialize
            setTimeout(playSong, 500);
        };
        player.media.addEventListener('canplay', onYouTubeReady);
    } else {
        player.media.addEventListener('canplay', onCanPlay);
        player.media.addEventListener('loadeddata', onLoadedData);
    }

    // Fallback: if no events fire within 5 seconds, try to play anyway
    setTimeout(() => {
        player.media.removeEventListener('canplay', onCanPlay);
        player.media.removeEventListener('loadeddata', onLoadedData);
        console.log('Fallback: attempting playback after timeout');
        playSong();
    }, 5000);
}

export function playSong() {
    console.log('Attempting playback');
    if (!playerState.player) return;

    const playPromise = playerState.player.play();
    if (!playPromise) return;

    playPromise
        .then(() => {
            console.log('Playback started successfully');
            playerState.isPlaying = true;
            updatePlayPauseButtons();
            updateMediaSessionPlaybackState('playing');
            updateStatusDisplay();
        })
        .catch(error => {
            console.warn('Playback failed:', error);

            if (error.name === 'NotAllowedError') {
                console.log('Autoplay blocked by browser policy');
                const statusElement = document.getElementById('player-status');
                if (statusElement) {
                    statusElement.textContent = '⏸️ Click play to start';
                }
                playerState.isPlaying = false;
                updatePlayPauseButtons();
            } else if (error.name === 'NotSupportedError' || error.message.includes('decoders')) {
                console.log('Format not supported, this might be a YouTube iframe issue - skipping to next song');
                goToNextSong();
            } else {
                console.log('Playback error, skipping to next song');
                goToNextSong();
            }
        });
}

export function pauseSong() {
    console.log('Pausing song');
    playerState.player?.pause();
    playerState.isPlaying = false;
    updatePlayPauseButtons();
    updateMediaSessionPlaybackState('paused');
    updateStatusDisplay();
}

export function updatePlayPauseButtons() {
    const playBtn = document.getElementById('play');
    const pauseBtn = document.getElementById('pause');
    if (!(playBtn && pauseBtn)) return;

    playBtn.style.display = playerState.isPlaying ? 'none' : 'inline-block';
    pauseBtn.style.display = playerState.isPlaying ? 'inline-block' : 'none';
}

export function switchSource() {
    const availableSources: SourceType[] = getAvailableSources();

    if (availableSources.length < 2) {
        console.log('Only one source available for this song');
        return;
    }

    const currentIndex = availableSources.indexOf(playerState.currentSourceType);
    const nextIndex = (currentIndex + 1) % availableSources.length;
    playerState.currentSourceType = availableSources[nextIndex];

    console.log(`User switched source to: ${playerState.currentSourceType}`);

    // Update tooltip
    const nextSourceIndex = (nextIndex + 1) % availableSources.length;
    const nextSource = availableSources[nextSourceIndex];
    const switchButton = document.getElementById('switch-source');
    if (switchButton) {
        switchButton.setAttribute('data-tooltip', `Switch to ${SOURCE_DISPLAY_NAMES[nextSource]}`);
    }

    // Reload with new source
    const wasPlaying = playerState.isPlaying;
    loadNewSong();

    if (wasPlaying) {
        setTimeout(playSong, 500);
    }

    updateSourceDisplay();
}

export function shufflePlaylist() {
    shuffleArray(playerState.playlistIndeces);
    playerState.currentIndex = 0;


    const playlistDiv = document.getElementById('playlist');
    if (!playlistDiv) return;
    playlistDiv.innerHTML = "";

    populatePlaylistDiv();
    applySongDivStyle();
    updateStatusDisplay();
    loadNewSong();
}

export function toggleLoop() {
    playerState.loop = !playerState.loop;
    const loopButton = document.getElementById('loop');
    if (!loopButton) {
        console.log("Loop button not found");
        return;
    }

    if (playerState.loop) {
        loopButton.classList.add('loop-on');
        loopButton.classList.remove('loop-off');
        loopButton.setAttribute('data-tooltip', 'Loop: On');
    } else {
        loopButton.classList.add('loop-off');
        loopButton.classList.remove('loop-on');
        loopButton.setAttribute('data-tooltip', 'Loop: Off');
    }

    console.log("Toggled loop:", playerState.loop);
}

export async function initializePlayer() {
    // First load the playlist data
    await retrievePlaylist();

    // Handle playlist search
    document.getElementById('playlist-search-input')
        ?.addEventListener('input', filterPlaylist);

    document.getElementById('playlist-search-filter')
        ?.addEventListener('change', filterPlaylist);

    document.addEventListener('keydown', (e) => {
        if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey) {
            const active = document.activeElement;
            if (active instanceof HTMLElement) {
                const isTyping =
                    active.tagName === 'INPUT' ||
                    active.tagName === 'TEXTAREA' ||
                    active.isContentEditable;

                if (!isTyping) {
                    e.preventDefault();
                    document.getElementById('playlist-search-input')?.focus();
                }
            }
        }
    });

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

    document.getElementById('playlist-search-input')
        ?.addEventListener('focus', (e: FocusEvent) => {
            const target = e.target as HTMLInputElement | null;
            target?.select();
        });

    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
            const input = document.getElementById('playlist-search-input');
            if (input instanceof HTMLInputElement && document.activeElement === input) {
                input.value = '';
                filterPlaylist();
                input.blur();
            }
        }
    });

    // Then initialize the player
    playerState.player = new MediaElementPlayer('mediaelement-player', {
        features: ['playpause', 'current', 'progress', 'duration', 'volume', 'fullscreen'],
        stretching: 'auto',
        youtube: {
            cc_load_policy: 1,
            iv_load_policy: 3,
            modestbranding: 1,
            rel: 0,
            autoplay: 1
        },
        success: function (
            media: HTMLMediaElement,   // the <video> or <audio> element
            node: HTMLElement,          // the wrapper element
            instance: MediaElementPlayer // the MediaElementPlayer instance
        ) {
            console.log('MediaElement.js player initialized successfully');

            // Set up event handlers
            media.addEventListener('play', () => {
                console.log('MediaElement.js: Play event');
                playerState.isPlaying = true;
                updatePlayPauseButtons();
                updateMediaSessionPlaybackState('playing');
                updateStatusDisplay();
            });

            media.addEventListener('pause', () => {
                console.log('MediaElement.js: Pause event');
                playerState.isPlaying = false;
                updatePlayPauseButtons();
                updateMediaSessionPlaybackState('paused');
                updateStatusDisplay();
            });

            media.addEventListener('ended', () => {
                console.log('MediaElement.js: Ended event');
                if (playerState.loop || playerState.currentIndex < playerState.animePlaylist.length - 1) {
                    setTimeout(goToNextSong, 500);
                } else {
                    playerState.isPlaying = false;
                    updatePlayPauseButtons();
                    updateMediaSessionPlaybackState('none');
                    updateStatusDisplay();
                }
            });

            media.addEventListener('error', (e) => {
                console.error('MediaElement.js error:', e, media.error);
                const statusElement = document.getElementById('player-status');
                if (statusElement) {
                    statusElement.textContent = '❌ Error loading video';
                }
                setTimeout(goToNextSong, 1000);
            });

            media.addEventListener('loadeddata', () => {
                console.log('MediaElement.js: Video loaded successfully');
                const statusElement = document.getElementById('player-status');
                if (statusElement) {
                    statusElement.textContent = '✅ Ready';
                }
            });

            media.addEventListener('canplay', () => {
                console.log('MediaElement.js: Can play event');
            });

            // Now load the first song - use setTimeout to ensure player assignment is complete
            setTimeout(() => {
                console.log('Loading first song after player initialization');
                loadNewSong();
            }, 0);
        },
        error: (error: Error) => {
            console.error('MediaElement.js initialization error:', error);
        }
    });

    // These should happen AFTER player is assigned
    initializeIndependentMediaSession();
    initializeTooltips();
    initializeControls();
    updateMediaSessionMetadata();
    updateStatusDisplay();

    // Register service worker (can happen anytime)
    if ('serviceWorker' in navigator) {
        try {
            await navigator.serviceWorker.register('sw.js');
            console.log('Service Worker registered successfully');
        } catch (error) {
            console.warn('Service Worker registration failed:', error);
        }
    }

    console.log('Player initialization complete');
}
