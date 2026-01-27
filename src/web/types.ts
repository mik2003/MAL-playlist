import { SOURCE_DISPLAY_NAMES } from "./const";

export interface Theme {
    name: string;
    artist: string;
    yt_url?: string;
    at_url?: string;
}

export interface Anime {
    id: number;
    title: string;
    picture: string;
    opening_themes: Theme[];
    ending_themes: Theme[];
}

export interface AnimeList {
    anime: Anime[];
}

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


export type SourceType = keyof typeof SOURCE_DISPLAY_NAMES;

export type HandlerMap = {
    play: () => void;
    pause: () => void;
    previoustrack: () => void;
    nexttrack: () => void;
    seekbackward: (details: MediaSessionActionDetails) => void;
    seekforward: (details: MediaSessionActionDetails) => void;
};

