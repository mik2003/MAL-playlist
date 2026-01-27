export const SOURCE_DISPLAY_NAMES = {
    yt_url: 'YouTube',
    at_url: 'AnimeThemes'
} as const;

type SourceType = keyof typeof SOURCE_DISPLAY_NAMES;
