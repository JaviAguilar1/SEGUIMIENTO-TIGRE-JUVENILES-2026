// Tigre Juveniles — Service Worker v3
// Estrategia: Network First para HTML, Cache First para assets estáticos

const CACHE_NAME = 'tigre-juveniles-v3';
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
  if (url.includes('firebaseio.com') ||
      url.includes('googleapis.com') ||
      url.includes('gstatic.com') ||
      url.includes('fonts.google') ||
      url.includes('jsdelivr.net') ||
      url.includes('firebaseapp.com')) {
    return; // dejar pasar sin interceptar
  }

  // index.html — SIEMPRE desde la red (nunca desde caché)
  // Así los cambios se ven inmediatamente en todos los dispositivos
  if (url.endsWith('/') || url.includes('index.html') || 
      url.includes('SEGUIMIENTO-TIGRE-JUVENILES-2026') && !url.includes('.')) {
    e.respondWith(
      fetch(e.request)
        .catch(() => caches.match('./index.html'))
    );
    return;
  }

  // Íconos y manifest — Cache First (no cambian)
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
