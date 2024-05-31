const playlist = [
    {
        title: "Rouge no Dengon (Message of Rouge)",
        yt_id: "UJwtKY_iWkM"
    },
    {
        title: "Soaring",
        yt_id: "gCVoKhGgShc"
    },
    // Add more playlist items here
];

let currentIndex = 0;

const youtubePlayer = document.getElementById("youtube-player");
const playlistItemsContainer = document.getElementById("playlist-items");

function loadVideo(index) {
    const currentItem = playlist[index];
    youtubePlayer.contentWindow.postMessage('{"event":"command","func":"' + 'loadVideoByUrl' + '","args":["https://www.youtube.com/embed/' + currentItem.yt_id + '?autoplay=1&enablejsapi=1","0","normal"]}', '*');
}

function loadPlaylistItems() {
    playlistItemsContainer.innerHTML = "";
    playlist.forEach((item, index) => {
        const listItem = document.createElement("li");
        listItem.textContent = item.title;
        listItem.addEventListener("click", () => {
            currentIndex = index;
            loadVideo(currentIndex);
        });
        playlistItemsContainer.appendChild(listItem);
    });
}

function playNext() {
    currentIndex = (currentIndex + 1) % playlist.length;
    loadVideo(currentIndex);
}

function playPrevious() {
    currentIndex = (currentIndex - 1 + playlist.length) % playlist.length;
    loadVideo(currentIndex);
}

document.getElementById("next-btn").addEventListener("click", playNext);
document.getElementById("prev-btn").addEventListener("click", playPrevious);

loadVideo(currentIndex);
loadPlaylistItems();
