document.addEventListener("DOMContentLoaded", function () {
    const playlist = [
        {
            id: 53424,
            name: "Rouge no Dengon (Message of Rouge)",
            artist: "Yumi Arai (Japanese version - 'Witch Express Delivery')",
            yt_url: "https://www.youtube.com/embed/UJwtKY_iWkM?autoplay=1"
        },
        {
            id: 53425,
            name: "Soaring",
            artist: "Sydney Forest (English/US Disney version - 'Kiki's Delivery Service')",
            yt_url: "https://www.youtube.com/embed/gCVoKhGgShc?autoplay=1"
        }
        // Add more playlist items here
    ];

    const playlistItems = document.getElementById("playlist-items");
    const videoPlayer = document.getElementById("youtube-video");
    const playBtn = document.getElementById("play-btn");
    const prevBtn = document.getElementById("prev-btn");
    const nextBtn = document.getElementById("next-btn");
    let currentIndex = 0;

    function loadVideo(index) {
        currentIndex = index;
        const item = playlist[index];
        videoPlayer.src = item.yt_url;
    }

    function renderPlaylist() {
        playlistItems.innerHTML = "";
        playlist.forEach((item, index) => {
            const li = document.createElement("li");
            li.textContent = `${item.name} - ${item.artist}`;
            li.addEventListener("click", () => loadVideo(index));
            playlistItems.appendChild(li);
        });
    }

    playBtn.addEventListener("click", () => {
        if (videoPlayer.paused) {
            videoPlayer.play();
            playBtn.textContent = "Pause";
        } else {
            videoPlayer.pause();
            playBtn.textContent = "Play";
        }
    });

    prevBtn.addEventListener("click", () => {
        currentIndex = (currentIndex - 1 + playlist.length) % playlist.length;
        loadVideo(currentIndex);
    });

    nextBtn.addEventListener("click", () => {
        currentIndex = (currentIndex + 1) % playlist.length;
        loadVideo(currentIndex);
    });

    renderPlaylist();
    loadVideo(currentIndex);
});
