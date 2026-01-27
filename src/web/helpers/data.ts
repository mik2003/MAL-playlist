import type { AnimeList, Theme, Anime } from '../types/anime.js';
import { playerState } from '../state/playerState.js';
import { createArray } from './utils.js';
import { populatePlaylistDiv } from './playlist.js';

const animeListUrl = 'https://mal.secondo.aero/data/animelist.json';

export async function fetchAnimeList(url = animeListUrl): Promise<AnimeList> {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
}

export async function loadAnimeList(): Promise<void> {
    playerState.animeList = await fetchAnimeList();
    console.log('Anime list loaded');
}

export async function retrievePlaylist(): Promise<void> {
    await loadAnimeList();

    playerState.animePlaylist = [];
    playerState.animePlaylistMap = [];

    playerState.animeList!.anime.forEach((anime, animeIndex) => {
        anime.opening_themes.forEach((theme, themeIndex) => {
            if (theme.at_url || theme.yt_url) addToPlaylist(anime, theme, animeIndex, 'opening_themes', themeIndex);
        });

        anime.ending_themes.forEach((theme, themeIndex) => {
            if (theme.at_url || theme.yt_url) addToPlaylist(anime, theme, animeIndex, 'ending_themes', themeIndex);
        });
    });

    console.log(`Loaded ${playerState.animePlaylist.length} songs with valid URLs`);
    playerState.playlistIndeces = createArray(playerState.animePlaylist.length);
    populatePlaylistDiv();
}

function addToPlaylist(anime: Anime, theme: Theme, animeIndex: number, type: 'opening_themes' | 'ending_themes', themeIndex: number) {
    playerState.animePlaylist.push({
        at_url: theme.at_url,
        yt_url: theme.yt_url,
        name: theme.name,
        artist: theme.artist,
        anime_index: animeIndex,
        type,
        theme_index: themeIndex,
        anime_id: anime.id
    });

    playerState.animePlaylistMap.push([animeIndex, type, themeIndex]);
}
