// Service Worker — Tigre Juveniles
// Cachea el shell de la app para uso offline.
// Datos dinámicos (Firebase, tablas.json) van siempre a la red.

const CACHE = 'tigre-juveniles-v2';

// Shell de la app: se precachea en la instalación.
const APP_SHELL = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js',
  'https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js',
  'https://www.gstatic.com/firebasejs/9.23.0/firebase-database-compat.js',
  'https://www.gstatic.com/firebasejs/9.23.0/firebase-auth-compat.js'
];

// Instalación: precachea el shell. addAll falla si un recurso no responde,
// así que los CDN se cachean uno por uno para no romper la instalación si
// alguno no está disponible en ese momento.
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE).then(async cache => {
      await Promise.allSettled(APP_SHELL.map(url => cache.add(url)));
    }).then(() => self.skipWaiting())
  );
});

// Activación: borra caches viejos de versiones anteriores.
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Datos dinámicos: siempre a la red (nunca servir versión cacheada vieja).
  // Firebase Realtime DB, Google APIs de auth y la tabla LPF.
  const isDynamic =
    url.hostname.includes('firebaseio.com') ||
    url.hostname.includes('firebase') ||
    url.hostname.includes('googleapis.com') ||
    url.hostname.includes('google.com') ||
    url.pathname.includes('tablas.json');

  if (isDynamic) {
    event.respondWith(fetch(req).catch(() => caches.match(req)));
    return;
  }

  // Navegaciones (el documento HTML principal): red primero, para que el
  // usuario siempre vea la versión nueva. Si no hay conexión, se usa el
  // caché como respaldo. cache:'no-store' es necesario además del fetch-
  // primero: sin esto, el fetch podía volver a resolverse desde el caché
  // HTTP normal del navegador (GitHub Pages manda Cache-Control con unos
  // minutos de validez) y un F5 común seguía mostrando la versión vieja
  // -- solo un hard refresh (Ctrl+Shift+R) lo salteaba.
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req, {cache: 'no-store'}).then(res => {
        if (res && res.status === 200) {
          const copy = res.clone();
          caches.open(CACHE).then(cache => cache.put(req, copy));
        }
        return res;
      }).catch(() => caches.match(req).then(cached => cached || caches.match('./index.html')))
    );
    return;
  }

  // Resto (shell y assets): cache primero, y si no está, red — y se guarda.
  event.respondWith(
    caches.match(req).then(cached => {
      if (cached) return cached;
      return fetch(req).then(res => {
        if (res && res.status === 200 && (res.type === 'basic' || res.type === 'cors')) {
          const copy = res.clone();
          caches.open(CACHE).then(cache => cache.put(req, copy));
        }
        return res;
      }).catch(() => {
        // Sin red y sin cache: para navegaciones, devolver la app.
        if (req.mode === 'navigate') return caches.match('./index.html');
      });
    })
  );
});
