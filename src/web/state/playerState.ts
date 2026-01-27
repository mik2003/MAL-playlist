import type { AnimeList } from '../types/anime.js';

export interface PlaylistSong {
    at_url?: string;
    yt_url?: string;
    name: string;
    artist: string;
    anime_index: number;
    type: 'opening_themes' | 'ending_themes';
    theme_index: number;
    anime_id: number;
}

export type SourceType = 'yt_url' | 'at_url';

export const playerState = {
    player: null as MediaElementPlayer | null,
    animeList: null as AnimeList | null,
    animePlaylist: [] as PlaylistSong[],
    animePlaylistMap: [] as [number, 'opening_themes' | 'ending_themes', number][],
    playlistIndeces: [] as number[],
    currentIndex: 0,
    isPlaying: false,
    loop: false,
    currentSourceType: 'yt_url' as SourceType
};
