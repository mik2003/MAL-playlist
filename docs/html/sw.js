const CACHE_NAME = 'anime-playlist-v1';
const urlsToCache = [
    './youtube_playlist.html',
    '../css/youtube_playlist.css',
    '../js/youtube_playlist.js',
    './manifest.json'
];

self.addEventListener('install', function (event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function (cache) {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', function (event) {
    event.respondWith(
        caches.match(event.request)
            .then(function (response) {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            })
    );
});