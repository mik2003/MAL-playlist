type HandlerMap = {
    play: () => void;
    pause: () => void;
    previoustrack: () => void;
    nexttrack: () => void;
    seekbackward: (details: MediaSessionActionDetails) => void;
    seekforward: (details: MediaSessionActionDetails) => void;
};