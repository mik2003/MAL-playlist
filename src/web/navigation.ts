import { playerState } from './const.js';
import { updateMediaSessionMetadata } from './mediaSession.js';
import { loadNewSong } from './playerControls.js';
import { applySongDivStyle, clearSongDivStyle, updateSourceDisplay, updateStatusDisplay } from './ui.js';


/**
 * Move forward/backward in the playlist, respecting loop
 */
function jumpN(offset: number): number {
    const length = playerState.animePlaylist.length;
    if (playerState.loop) {
        // wrap around
        return ((playerState.currentIndex + offset) % length + length) % length;
    }
    // clamp
    return Math.max(0, Math.min(length - 1, playerState.currentIndex + offset));
}

/**
 * Navigate to a specific song index
 */
export function navigateToSong(newIndex: number) {
    clearSongDivStyle();
    playerState.currentIndex = newIndex;
    loadNewSong();
    applySongDivStyle();
    updateMediaSessionMetadata();
    updateStatusDisplay();
    updateSourceDisplay();
}

/**
 * Go to next song
 */
export function goToNextSong() {
    console.log('Next song');
    navigateToSong(jumpN(1));
}

/**
 * Go to previous song
 */
export function goToPreviousSong() {
    console.log('Previous song');
    navigateToSong(jumpN(-1));
}

/**
 * Jump directly to a song by display index
 */
export function goToSong(index: number) {
    console.log('Go to song:', index);
    navigateToSong(index);
}
