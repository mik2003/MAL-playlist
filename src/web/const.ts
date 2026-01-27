import { AnimeList, PlaylistSong, SourceType } from "./types";

export const SOURCE_DISPLAY_NAMES = {
    yt_url: 'YouTube',
    at_url: 'AnimeThemes'
} as const;

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
