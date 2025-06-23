self.addEventListener('install', event => {
  event.waitUntil(
    caches.open('crm-cache-v1').then(cache => {
      return cache.addAll([
        '/',
        '/static/style.css',
        '/static/icons/icon-192x192.png',
        '/static/icons/icon-512x512.png',
        // add more static assets as needed
      ]);
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
