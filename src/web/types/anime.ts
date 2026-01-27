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
