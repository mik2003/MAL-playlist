var animeList;
var currentPlaylist = [];
var currentSongIndex = 0;
var loop = true;
var isPlaying = false;

// DOM Elements
let spotifyEmbed;
let playlistDiv;

async function initializePlayer() {
    console.log('Initializing Spotify playlist player...');

    // Load the anime list data
    await loadAnimeList();

    // Initialize DOM elements
    spotifyEmbed = document.getElementById('spotify-embed');
    playlistDiv = document.getElementById('playlist');

    // Populate the playlist
    populatePlaylist();

    // Set up event listeners
    setupEventListeners();

    // Load first song
    if (currentPlaylist.length > 0) {
        loadSong(0);
    }

    console.log('Spotify player initialized successfully');
}

async function loadAnimeList() {
    try {
        // Load Spotify songs data
        const songsResponse = await fetch('https://mal.secondo.aero/data/songs_spotify.json');
        const songsData = await songsResponse.json();
        console.log('Spotify songs data loaded:', songsData);

        // Load full anime list data to get titles and pictures
        const animeListResponse = await fetch('https://mal.secondo.aero/data/animelist.json');
        const fullAnimeList = await animeListResponse.json();
        console.log('Full anime list loaded:', fullAnimeList);

        // Build the playlist using both data sources
        buildPlaylistFromSongsData(songsData, fullAnimeList);
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

function buildPlaylistFromSongsData(songsData, fullAnimeList) {
    currentPlaylist = [];

    // Convert the songs object to an array
    const songsArray = Object.values(songsData);

    // Create a map for quick anime lookup by ID
    const animeMap = {};
    fullAnimeList.anime.forEach(anime => {
        animeMap[anime.id] = anime;
    });

    for (const song of songsArray) {
        if (song.spotify_uri && song.spotify_uri.trim() !== '') {
            // Find the anime in the full anime list
            const anime = animeMap[song.anime_id];

            if (anime) {
                // Determine type from the song text
                let type = song.text.toLowerCase().includes('ending') ? 'ending' : 'opening';

                currentPlaylist.push({
                    type: type,
                    anime: {
                        id: song.anime_id,
                        title: anime.title,
                        picture: anime.picture
                    },
                    theme: song,
                    spotifyUri: song.spotify_uri
                });
            } else {
                console.warn(`Anime with ID ${song.anime_id} not found in full anime list`);
            }
        }
    }

    console.log(`Built playlist with ${currentPlaylist.length} Spotify songs`);

    // Debug: show first few entries
    if (currentPlaylist.length > 0) {
        console.log('First playlist entry:', currentPlaylist[0]);
    }
}

function buildPlaylistFromAnimeList() {
    currentPlaylist = [];

    if (!animeList || !animeList.anime) {
        console.error('Invalid anime list structure');
        return;
    }

    for (const anime of animeList.anime) {
        // Add opening themes
        if (anime.opening_themes) {
            for (const theme of anime.opening_themes) {
                if (theme.spotify_uri) {
                    currentPlaylist.push({
                        type: 'opening',
                        anime: anime,
                        theme: theme,
                        spotifyUri: theme.spotify_uri
                    });
                }
            }
        }

        // Add ending themes
        if (anime.ending_themes) {
            for (const theme of anime.ending_themes) {
                if (theme.spotify_uri) {
                    currentPlaylist.push({
                        type: 'ending',
                        anime: anime,
                        theme: theme,
                        spotifyUri: theme.spotify_uri
                    });
                }
            }
        }
    }

    console.log(`Built playlist with ${currentPlaylist.length} Spotify songs`);
}

function populatePlaylist() {
    playlistDiv.innerHTML = '';

    if (currentPlaylist.length === 0) {
        playlistDiv.innerHTML = '<div class="playlist-item" style="text-align: center; padding: 20px;">No Spotify songs found in playlist</div>';
        return;
    }

    currentPlaylist.forEach((song, index) => {
        const playlistItem = createPlaylistItem(song, index);
        playlistDiv.appendChild(playlistItem);
    });
}

function createPlaylistItem(song, index) {
    const playlistItem = document.createElement("div");
    playlistItem.className = "playlist-item";
    playlistItem.id = `song-${index}`;

    const playlistItemImage = document.createElement("div");
    playlistItemImage.className = "playlist-item-image";

    const animeImage = document.createElement("img");
    animeImage.className = "playlist-item-animeimage";
    animeImage.src = song.anime.picture;
    animeImage.alt = song.anime.title;

    const animeLink = document.createElement("a");
    animeLink.href = `https://myanimelist.net/anime/${song.anime.id}`;
    animeLink.target = "_blank";
    animeLink.appendChild(animeImage);
    playlistItemImage.appendChild(animeLink);

    const playlistItemText = document.createElement("div");
    playlistItemText.className = "playlist-item-text";

    const nameLine = document.createElement("span");
    nameLine.className = "playlist-item-nameline";
    nameLine.textContent = song.theme.name || 'Unknown Song';

    const artistLine = document.createElement("span");
    artistLine.className = "playlist-item-artistline";
    artistLine.textContent = `by ${song.theme.artist || 'Unknown Artist'}`;

    const animeLine = document.createElement("span");
    animeLine.className = "playlist-item-animeline";
    animeLine.textContent = `【${song.anime.title}】`;

    const episodeLine = document.createElement("span");
    episodeLine.className = "playlist-item-episodeline";
    episodeLine.textContent = `${song.type === 'opening' ? 'OP' : 'ED'}${song.theme.index ? ` #${song.theme.index}` : ''}${song.theme.episode ? ` (${song.theme.episode})` : ''}`;

    playlistItemText.appendChild(nameLine);
    playlistItemText.appendChild(artistLine);
    playlistItemText.appendChild(animeLine);
    playlistItemText.appendChild(episodeLine);

    playlistItem.appendChild(playlistItemImage);
    playlistItem.appendChild(playlistItemText);

    // Click handler
    playlistItem.addEventListener('click', () => {
        loadSong(index);
    });

    return playlistItem;
}

function loadSong(index) {
    if (index < 0 || index >= currentPlaylist.length) {
        console.error('Invalid song index:', index);
        return;
    }

    currentSongIndex = index;
    const song = currentPlaylist[index];

    console.log('Loading song:', song.theme.name);

    // Update Spotify embed
    const spotifyUri = song.spotifyUri;
    if (spotifyUri) {
        // Extract track ID from spotify:track:xxx format
        const trackId = spotifyUri.replace('spotify:track:', '');
        const embedUrl = `https://open.spotify.com/embed/track/${trackId}`;

        spotifyEmbed.src = embedUrl;
        console.log('Set Spotify embed URL:', embedUrl);
    }

    // Update UI
    updateActiveSong();
    updateStatusDisplay(song);

    // Scroll to active song
    scrollToActiveSong();
}

function updateActiveSong() {
    // Remove active class from all items
    document.querySelectorAll('.playlist-item').forEach(item => {
        item.classList.remove('active');
    });

    // Add active class to current song
    const activeItem = document.getElementById(`song-${currentSongIndex}`);
    if (activeItem) {
        activeItem.classList.add('active');
    }
}

function updateStatusDisplay(song) {
    document.getElementById('current-song-name').textContent = song.theme.name || 'Unknown';
    document.getElementById('current-anime').textContent = song.anime.title;
    document.getElementById('current-position').textContent = `Song ${currentSongIndex + 1} of ${currentPlaylist.length}`;
}

function scrollToActiveSong() {
    const activeItem = document.getElementById(`song-${currentSongIndex}`);
    if (activeItem && playlistDiv) {
        activeItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function nextSong() {
    let newIndex;
    if (loop) {
        newIndex = (currentSongIndex + 1) % currentPlaylist.length;
    } else {
        newIndex = Math.min(currentSongIndex + 1, currentPlaylist.length - 1);
    }

    if (newIndex !== currentSongIndex) {
        loadSong(newIndex);
    }
}

function previousSong() {
    let newIndex;
    if (loop) {
        newIndex = (currentSongIndex - 1 + currentPlaylist.length) % currentPlaylist.length;
    } else {
        newIndex = Math.max(currentSongIndex - 1, 0);
    }

    if (newIndex !== currentSongIndex) {
        loadSong(newIndex);
    }
}

function shufflePlaylist() {
    // Fisher-Yates shuffle
    for (let i = currentPlaylist.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [currentPlaylist[i], currentPlaylist[j]] = [currentPlaylist[j], currentPlaylist[i]];
    }

    // Re-populate playlist and reset to first song
    populatePlaylist();
    loadSong(0);
}

function toggleLoop() {
    loop = !loop;
    const loopStatus = document.getElementById('loop-status');
    loopStatus.textContent = `Loop: ${loop ? 'On' : 'Off'}`;
    console.log("Toggled loop: " + loop);
}

function setupEventListeners() {
    document.getElementById('prev').addEventListener('click', previousSong);
    document.getElementById('next').addEventListener('click', nextSong);
    document.getElementById('shuffle').addEventListener('click', shufflePlaylist);
    document.getElementById('loop').addEventListener('click', toggleLoop);

    // Listen for messages from Spotify embed (if needed)
    window.addEventListener('message', (event) => {
        // You can handle messages from Spotify embed here if needed
        console.log('Message from Spotify:', event);
    });
}

// Auto-advance when song ends (Spotify embed doesn't provide events, so we'll use a timer)
function startPlaybackMonitor() {
    // Since Spotify embed doesn't expose playback events easily,
    // we'll rely on manual next/prev controls
    console.log('Spotify playback monitor started - use manual controls for navigation');
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', initializePlayer);