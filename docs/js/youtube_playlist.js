let playlist = [];
let currentTrackIndex = 0;
let shuffle = false;
let repeat = false;

document.addEventListener('DOMContentLoaded', () => {
    fetch('../data/animelist.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log('JSON data loaded successfully:', data); // Check if JSON is loaded
            buildPlaylist(data);
            loadTrack(0);
        })
        .catch(error => console.error('Error loading JSON:', error));
});

function buildPlaylist(data) {
    const playlistElement = document.getElementById('playlist');
    data.anime.forEach(anime => {
        anime.opening_themes.concat(anime.ending_themes).forEach(song => {
            playlist.push(song);
            const li = document.createElement('li');
            li.className = 'playlist-item';
            li.textContent = `${song.name} by ${song.artist}`;
            li.onclick = () => loadTrack(playlist.indexOf(song));
            playlistElement.appendChild(li);
        });
    });
    console.log('Playlist built:', playlist); // Check if playlist is built correctly
}

function loadTrack(index) {
    if (index >= 0 && index < playlist.length) {
        currentTrackIndex = index;
        const track = playlist[currentTrackIndex];
        const currentTrackElement = document.getElementById('current-track');
        currentTrackElement.innerHTML = `Current Track: <a href="${track.yt_url}" target="_blank">${track.name} by ${track.artist}</a>`;
        console.log('Loaded track:', track); // Check if track is loaded correctly
    } else {
        console.error('Invalid track index:', index);
    }
}

function prevTrack() {
    if (shuffle) {
        currentTrackIndex = Math.floor(Math.random() * playlist.length);
    } else {
        currentTrackIndex = (currentTrackIndex - 1 + playlist.length) % playlist.length;
    }
    loadTrack(currentTrackIndex);
}

function nextTrack() {
    if (shuffle) {
        currentTrackIndex = Math.floor(Math.random() * playlist.length);
    } else {
        currentTrackIndex = (currentTrackIndex + 1) % playlist.length;
    }
    loadTrack(currentTrackIndex);
}

function toggleShuffle() {
    shuffle = !shuffle;
    alert(`Shuffle is now ${shuffle ? 'on' : 'off'}`);
}

function toggleRepeat() {
    repeat = !repeat;
    alert(`Repeat is now ${repeat ? 'on' : 'off'}`);
}
