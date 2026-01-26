export interface AnimeTheme {
    at_url?: string;
    yt_url?: string;
    name: string;
    artist: string;
}

export interface Anime {
    id: number;
    title: string;
    picture: string;
    opening_themes: AnimeTheme[];
    ending_themes: AnimeTheme[];
}

export interface AnimeList {
    anime: Anime[];
}

export type SourceType = 'yt_url' | 'at_url';

export interface PlaylistItem {
    at_url?: string;
    yt_url?: string;
    name: string;
    artist: string;
    anime_index: number;
    type: 'opening_themes' | 'ending_themes';
    theme_index: number;
    anime_id: number;
}
