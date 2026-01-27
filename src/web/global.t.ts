declare class MediaElementPlayer {
    constructor(element: string, options?: any);

    media: HTMLMediaElement;
    play(): Promise<void>;
    pause(): void;
    setSrc(src: string): void;
    load(): void;
    // Add more methods if you use them
}
