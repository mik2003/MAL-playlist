const videos = [
    {
        title: "Rouge no Dengon (Message of Rouge)",
        id: "UJwtKY_iWkM"
    },
    {
        title: "Soaring",
        id: "gCVoKhGgShc"
    },
    // Add more playlist items here
];

let currentIndex = 0;
let isLooping = false;

// Shuffle function
function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}

// Load the YouTube IFrame API
let tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
let firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

// Create YouTube player
let player;
function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
        height: '315',
        width: '560',
        videoId: videos[currentIndex].id,
        events: {
            'onStateChange': onPlayerStateChange
        }
    });
    updateVideoList();
}

// Handle player state changes
function onPlayerStateChange(event) {
    if (event.data === YT.PlayerState.ENDED) {
        nextVideo();
    }
}

// Play the next video
function nextVideo() {
    currentIndex = (currentIndex + 1) % videos.length;
    if (currentIndex === 0 && !isLooping) {
        return;
    }
    player.loadVideoById(videos[currentIndex].id);
    updateVideoList();
}

// Play the previous video
function prevVideo() {
    currentIndex = (currentIndex - 1 + videos.length) % videos.length;
    player.loadVideoById(videos[currentIndex].id);
    updateVideoList();
}

// Shuffle the playlist
document.getElementById('shuffleBtn').addEventListener('click', () => {
    shuffle(videos);
    currentIndex = 0;
    player.loadVideoById(videos[currentIndex].id);
    updateVideoList();
});

// Toggle looping
document.getElementById('loopBtn').addEventListener('click', () => {
    isLooping = !isLooping;
    document.getElementById('loopBtn').innerText = isLooping ? "Looping: On" : "Looping: Off";
});

// Next video button
document.getElementById('nextBtn').addEventListener('click', nextVideo);

// Previous video button
document.getElementById('prevBtn').addEventListener('click', prevVideo);

// Update video list display
function updateVideoList() {
    const videoList = document.getElementById('videoList');
    videoList.innerHTML = "";
    for (let i = 0; i < videos.length; i++) {
        const li = document.createElement('li');
        if (i === currentIndex) {
            li.innerHTML = `<strong>Current: ${videos[i].title}</strong>`;
        } else if (i === (currentIndex + 1) % videos.length) {
            li.innerHTML = `Next: ${videos[i].title}`;
        } else {
            li.innerHTML = videos[i].title;
        }
        videoList.appendChild(li);
    }
}
