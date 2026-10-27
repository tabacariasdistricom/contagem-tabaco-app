// Funciona sem rede: guarda a app e o catálogo. Mudar VERSAO quando se publica uma versão nova.
const VERSAO = "tab-v17";
const FICHEIROS = ["./", "./index.html", "./intermec.html", "./manifest-intermec.webmanifest", "./zxing.min.js", "./manifest.webmanifest", "./icon.svg", "./icon-192.png", "./icon-512.png", "./icon-maskable-512.png", "./artigos.json"];
self.addEventListener("install", e => e.waitUntil(caches.open(VERSAO).then(c => c.addAll(FICHEIROS)).then(() => self.skipWaiting())));
self.addEventListener("activate", e => e.waitUntil(
  caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSAO).map(k => caches.delete(k)))).then(() => self.clients.claim())));
// rede primeiro (catálogo atualizado), cópia guardada sem rede
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  const rede = fetch(e.request).then(r => { const c = r.clone(); caches.open(VERSAO).then(ca => ca.put(e.request, c)); return r; });
  e.respondWith(rede.catch(() => caches.match(e.request, { ignoreSearch: true })));
});
