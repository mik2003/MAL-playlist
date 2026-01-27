import { playerState } from '../state/playerState.js';
import { playSong, pauseSong } from './playerControls.js';
import { goToPreviousSong, goToNextSong } from './navigation.js';

export function initializeIndependentMediaSession() {
    if (!('mediaSession' in navigator)) return;

    console.log('Initializing independent media session...');

    try {
        // Clear existing handlers
        // ['play', 'pause', 'previoustrack', 'nexttrack', 'seekbackward', 'seekforward'].forEach(action => {
        //     try { navigator.mediaSession.setActionHandler(action, null); } catch (e) { }
        // });

        // Set custom handlers
        const handlers: HandlerMap = {
            play: () => { console.log('🎵 Media session: PLAY'); playSong(); },
            pause: () => { console.log('⏸️ Media session: PAUSE'); pauseSong(); },
            previoustrack: () => { console.log('⏮️ Media session: PREVIOUS'); goToPreviousSong(); },
            nexttrack: () => { console.log('⏭️ Media session: NEXT'); goToNextSong(); },
            seekbackward: (details: MediaSessionActionDetails) => handleSeek(-(details.seekOffset || 10)),
            seekforward: (details: MediaSessionActionDetails) => handleSeek(details.seekOffset || 10)
        };

        (Object.keys(handlers) as (keyof HandlerMap)[]).forEach(action => {
            navigator.mediaSession.setActionHandler(action, handlers[action] as any);
        });

        updateMediaSessionMetadata();
        console.log('✅ Independent media session initialized');
    } catch (error) {
        console.error('❌ Error setting media session:', error);
    }
}

export function handleSeek(offset: number) {
    if (!playerState.player?.media) return;

    const newTime = playerState.player.media.currentTime + offset;
    playerState.player.media.currentTime = Math.max(0, Math.min(playerState.player.media.duration, newTime));
    console.log(`⏩ Media session: SEEK ${offset > 0 ? 'FORWARD' : 'BACKWARD'}`);
}

export function updateMediaSessionMetadata() {
    if (!('mediaSession' in navigator)) return;

    const currentSongData = playerState.animePlaylist[playerState.playlistIndeces[playerState.currentIndex]];

    try {
        const animeList = playerState.animeList;
        if (!animeList) throw "Anime list is null";
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
        console.log('Media session metadata updated');
    } catch (error) {
        console.error('Error updating media session metadata:', error);
    }
}

export function updateMediaSessionPlaybackState(state: 'none' | 'paused' | 'playing') {
    if ('mediaSession' in navigator) {
        navigator.mediaSession.playbackState = state;
    }
}
