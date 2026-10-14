const CACHE = 'asf-swr-v1';
const OFFLINE = '/offline.html';

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll([OFFLINE, '/'])));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const cached = await cache.match(req);
    const network = fetch(req).then((res) => {
      if (res.ok && new URL(req.url).origin === self.location.origin) {
        cache.put(req, res.clone());
      }
      return res;
    }).catch(() => null);
    return cached || (await network) || (await cache.match(OFFLINE));
  })());
});
