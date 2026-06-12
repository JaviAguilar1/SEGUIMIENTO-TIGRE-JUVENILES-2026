// Tigre Juveniles — Service Worker v4 (Optimizado para GitHub Pages)
// Estrategia: Network First para HTML, Cache First para assets estáticos

const CACHE_NAME = 'tigre-juveniles-v4';
const STATIC_ASSETS = [
  './icon-192.png',
  './icon-512.png',
  './manifest.json',
];

// Instalación — solo cachea íconos y manifest, NO el index.html
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(c => c.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activación — limpia caches viejos
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

// Fetch — estrategia según tipo de recurso
self.addEventListener('fetch', e => {
  const url = e.request.url;

  // Firebase, Google APIs, CDNs — siempre red directa, sin interceptar
  if (url.includes('firebaseio.com')) return;
  if (url.includes('googleapis.com')) return;
  if (url.includes('gstatic.com')) return;
  if (url.includes('fonts.google')) return;
  if (url.includes('jsdelivr.net')) return;
  if (url.includes('firebaseapp.com')) return;

  // index.html / Rutas de navegación — Network First
  if (url.endsWith('/') || url.includes('index.html') || !url.split('/').pop().includes('.')) {
    e.respondWith(
      fetch(e.request)
        .catch(() => {
          return caches.match('./index.html') || caches.match('index.html');
        })
    );
    return;
  }

  // Íconos y manifest — Cache First
  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;
      return fetch(e.request).then(response => {
        if (response && response.status === 200) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(c => c.put(e.request, copy));
        }
        return response;
      });
    })
  );
});
