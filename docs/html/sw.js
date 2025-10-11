const CACHE_NAME = 'anime-playlist-v2';

self.addEventListener('install', (event) => {
    console.log('Service Worker installing');
    // Activate immediately without waiting
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    console.log('Service Worker activating');
    // Take control of all open pages immediately
    event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
    // Simple fetch handler - you can enhance this later
    event.respondWith(fetch(event.request));
});