import { highlightMatch } from './utils.js';
import { playerState, PlaylistSong, SourceType } from '../state/playerState.js';
import { goToSong } from './navigation.js';

export function populatePlaylistDiv() {
    const playlistDiv = document.getElementById('playlist');
    if (!playlistDiv) return;
    playlistDiv.innerHTML = '';

    // Create playlist items in shuffled order
    playerState.playlistIndeces.forEach((shuffledIndex, displayIndex) => {
        const playlistItem = createPlaylistItem(shuffledIndex, displayIndex);
        playlistDiv.appendChild(playlistItem);
    });

    // Add search
    filterPlaylist();
}

export function createPlaylistItem(shuffledIndex: number, displayIndex: number): HTMLDivElement {
    const currentSongData: PlaylistSong | undefined = playerState.animePlaylist[shuffledIndex];
    if (!currentSongData || !playerState.animeList) {
        throw new Error(`Invalid song data at index ${shuffledIndex}`);
    }

    const anime = playerState.animeList.anime[currentSongData.anime_index];

    const playlistItem = document.createElement("div");
    playlistItem.className = "playlist-item";
    playlistItem.id = displayIndex.toString();
    playlistItem.onclick = () => goToSong(displayIndex);

    const playlistItemText = document.createElement("div");
    playlistItemText.className = "playlist-item-text";

    const playlistItemImage = document.createElement("div");
    playlistItemImage.className = "playlist-item-image";

    // Create content
    playlistItemText.appendChild(createTextElement("nameline", currentSongData.name));
    playlistItemText.appendChild(createTextElement("artistline", ` by ${currentSongData.artist}`));
    playlistItemText.appendChild(createTextElement("animeline", `【${anime.title}】`));
    playlistItemText.appendChild(createEpisodeContainer(currentSongData.type, currentSongData));

    playlistItemImage.appendChild(createAnimeImage(anime.picture, currentSongData.anime_id));

    playlistItem.appendChild(playlistItemImage);
    playlistItem.appendChild(playlistItemText);

    return playlistItem;
}

export function createTextElement(className: string, text: string): HTMLElement {
    const el = document.createElement('span');
    el.className = `playlist-item-${className}`;
    el.textContent = text;
    return el;
}

export function createEpisodeContainer(type: 'opening_themes' | 'ending_themes', songData: typeof playerState.animePlaylist[0]): HTMLElement {
    const container = document.createElement("div");
    container.className = "playlist-item-episode-container";

    const episodeLine = document.createElement("span");
    episodeLine.className = "playlist-item-episodeline";
    episodeLine.textContent = type.split("_")[0];

    const sourceIndicator = document.createElement("span");
    sourceIndicator.className = "playlist-item-source";
    const sources = [];
    if (songData.yt_url) sources.push('YouTube');
    if (songData.at_url) sources.push('AnimeThemes');
    sourceIndicator.textContent = ` [${sources.join('/')}]`;

    container.appendChild(episodeLine);
    container.appendChild(sourceIndicator);
    return container;
}

export function createAnimeImage(src: string, animeId: number): HTMLElement {
    const image = document.createElement("img");
    image.className = "playlist-item-animeimage";
    image.src = src;

    image.addEventListener('error', () => {
        console.warn('Failed to load image:', src);
        image.style.display = 'none';
    });

    const link = document.createElement("a");
    link.href = `https://myanimelist.net/anime/${animeId}`;
    link.target = "_blank";
    link.appendChild(image);

    return link;
}

export function filterPlaylist() {
    const queryElement = document.getElementById('playlist-search-input')
    if (!(queryElement instanceof HTMLInputElement)) return;
    const query = queryElement.value.toLowerCase();

    const filterElement = document.getElementById('playlist-search-filter');
    if (!(filterElement instanceof HTMLSelectElement)) return;
    const filter = filterElement.value;

    const items = document.querySelectorAll('.playlist-item');

    items.forEach(item => {
        const htmlItem = item as HTMLElement;

        const fields = {
            nameline: htmlItem.querySelector('.playlist-item-nameline'),
            artistline: htmlItem.querySelector('.playlist-item-artistline'),
            animeline: htmlItem.querySelector('.playlist-item-animeline')
        };

        let match = false;

        Object.entries(fields).forEach(([key, el]) => {
            if (!el) return;

            const original = el.textContent;
            const text = original.toLowerCase();

            // Reset previous highlights
            el.innerHTML = original;

            if (
                (filter === 'all' || filter === key) &&
                query &&
                text.includes(query)
            ) {
                match = true;
                el.innerHTML = highlightMatch(original, query);
            }
        });

        htmlItem.style.display = match || !query ? '' : 'none';
    });
}

export function getCurrentSongURL() {
    const currentSong = playerState.animePlaylist[playerState.playlistIndeces[playerState.currentIndex]];
    if (!currentSong) return;

    return currentSong[playerState.currentSourceType];
}

export function getAvailableSources(): SourceType[] {
    const currentSong = playerState.animePlaylist[playerState.playlistIndeces[playerState.currentIndex]];
    const sources: SourceType[] = [];
    if (currentSong.yt_url) sources.push('yt_url');
    if (currentSong.at_url) sources.push('at_url');
    return sources;
}
