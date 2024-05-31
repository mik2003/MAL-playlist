// List of anime from JSON data
let animeList;

let currentIndex = 0;
let isLooping = false;

// Shuffle function
function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}

// Load the JSON data
fetch('../data/animelist.json')
    .then(response => response.json())
    .then(data => {
        animeList = data.anime;
        initPlayer();
    })
    .catch(error => console.error('Error loading JSON:', error));

// Initialize YouTube player
let player;
function initPlayer() {
    player = new YT.Player('player', {
        height: '315',
        width: '560',
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
    currentIndex = (currentIndex + 1) % animeList.length;
    const videoId = extractVideoId(animeList[currentIndex].yt_url);
    player.loadVideoById(videoId);
    updateVideoList();
}

// Play the previous video
function prevVideo() {
    currentIndex = (currentIndex - 1 + animeList.length) % animeList.length;
    const videoId = extractVideoId(animeList[currentIndex].yt_url);
    player.loadVideoById(videoId);
    updateVideoList();
}

// Shuffle the playlist
document.getElementById('shuffleBtn').addEventListener('click', () => {
    shuffle(animeList);
    currentIndex = 0;
    const videoId = extractVideoId(animeList[currentIndex].yt_url);
    player.loadVideoById(videoId);
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
    for (let i = 0; i < animeList.length; i++) {
        const li = document.createElement('li');
        if (i === currentIndex) {
            li.innerHTML = `<strong>Current: ${animeList[i].title}</strong>`;
        } else if (i === (currentIndex + 1) % animeList.length) {
            li.innerHTML = `Next: ${animeList[i].title}`;
        } else {
            li.innerHTML = animeList[i].title;
        }
        videoList.appendChild(li);
    }
}

// Extract video ID from YouTube URL
function extractVideoId(url) {
    const urlObj = new URL(url);
    let videoId = urlObj.searchParams.get('v');
    if (!videoId) {
        const pathSegments = urlObj.pathname.split('/');
        videoId = pathSegments[pathSegments.length - 1];
    }
    return videoId;
}
