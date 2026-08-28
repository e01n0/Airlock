/* Airlock service worker — offline app shell.
   Bump CACHE when shipping changes so clients pick them up,
   and keep it in step with APP_VERSION in index.html. */
const CACHE = "airlock-v1";
const ASSETS = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icon-192.png",
  "./icon-512.png",
  "./apple-touch-icon.png"
];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    const old = keys.filter(k => k !== CACHE);
    // Carry the recorded voice clips forward before dropping old caches. They
    // are immutable content, and wiping them on upgrade would leave an offline
    // device with a silent coach until it could re-download the whole pack.
    const cur = await caches.open(CACHE);
    for (const k of old) {
      try {
        const c = await caches.open(k);
        for (const req of await c.keys()) {
          if (req.url.includes("/voice/") && !(await cur.match(req))) {
            const res = await c.match(req);
            if (res) await cur.put(req, res);
          }
        }
      } catch (e) { /* a broken old cache must not block activation */ }
    }
    await Promise.all(old.map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;

  // Network-first for page navigations so an online device always loads the
  // latest app; fall back to the cached shell when offline.
  const isDoc = req.mode === "navigate" || req.destination === "document";
  if (isDoc) {
    e.respondWith(
      fetch(req).then(res => {
        if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
        return res;
      }).catch(() => caches.match(req).then(c => c || caches.match("./index.html")))
    );
    return;
  }

  // Stale-while-revalidate for everything else: instant from cache, refresh behind.
  e.respondWith(
    caches.match(req).then(cached => {
      const network = fetch(req).then(res => {
        if (res && (res.ok || res.type === "opaque")) {
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put(req, copy));
        }
        return res;
      }).catch(() => cached);
      return cached || network;
    })
  );
});
