import { playerState, SOURCE_DISPLAY_NAMES } from './const.js';
import { SourceType } from './types.js';
import { getAvailableSources } from './playlist.js';

export function initializeTooltips() {
    const tooltips = {
        'prev': 'Previous',
        'play': 'Play',
        'pause': 'Pause',
        'next': 'Next',
        'shuffle': 'Shuffle',
        'loop': playerState.loop ? 'Loop: On' : 'Loop: Off',
        'switch-source': 'Switch Source'
    };

    Object.entries(tooltips).forEach(([id, tooltip]) => {
        const button = document.getElementById(id);
        button && button.setAttribute('data-tooltip', tooltip);
    });
}

export function initializeControls() {
    const loopButton = document.getElementById('loop');
    if (loopButton instanceof HTMLButtonElement) {
        loopButton.classList.add(playerState.loop ? 'loop-on' : 'loop-off');
    }

    const switchButton = document.getElementById('switch-source');
    if (switchButton instanceof HTMLButtonElement) {
        const availableSources: SourceType[] = getAvailableSources();

        if (availableSources.length > 1) {
            const currentIndex = availableSources.indexOf(playerState.currentSourceType);
            const nextSource = availableSources[(currentIndex + 1) % availableSources.length];
            switchButton.setAttribute('data-tooltip', `Switch to ${SOURCE_DISPLAY_NAMES[nextSource]}`);
            switchButton.disabled = false;
            switchButton.style.opacity = '1';
        } else {
            switchButton.setAttribute('data-tooltip', 'Only one source available');
            switchButton.disabled = true;
            switchButton.style.opacity = '0.5';
        }
    }

    updateSourceDisplay();
}

export function updateStatusDisplay() {
    const currentSongData = playerState.animePlaylist[playerState.currentIndex];
    if (!currentSongData) return;

    const elements = {
        'current-song-name': currentSongData.name || 'Unknown',
        'playback-status': playerState.isPlaying ? '▶️ Playing' : '⏸️ Paused',
        'player-status': playerState.isPlaying ? '✅ Playing' : '✅ Ready',
        'current-position': `Song ${playerState.currentIndex + 1} of ${playerState.animePlaylist.length}`
    };

    Object.entries(elements).forEach(([id, text]) => {
        const element = document.getElementById(id);
        element && (element.textContent = text);
    });
}

export function updateSourceDisplay() {
    const currentSource = document.getElementById('current-source');
    const displayName = SOURCE_DISPLAY_NAMES[playerState.currentSourceType] || playerState.currentSourceType;
    currentSource && (currentSource.textContent = displayName);
}

// export function updatePlayPauseButtons() {
//     const playBtn = document.getElementById('play');
//     const pauseBtn = document.getElementById('pause');
//     playBtn.style.display = isPlaying ? 'none' : 'inline-block';
//     pauseBtn.style.display = isPlaying ? 'inline-block' : 'none';
// }


export function applySongDivStyle() {
    const playlistDiv = document.getElementById("playlist");
    if (!playlistDiv) return;

    const songDiv = document.getElementById(playerState.currentIndex.toString());
    if (!songDiv) return;

    songDiv.classList.add('active');

    scrollParentToChild(playlistDiv, songDiv);
}

export function clearSongDivStyle() {
    const songDiv = document.getElementById(playerState.currentIndex.toString());
    if (!songDiv) return;

    songDiv?.classList.remove('active');
}


export function scrollParentToChild(parent: HTMLElement, child: HTMLElement) {

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
