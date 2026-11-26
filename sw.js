const V='stgo27-c28d64c5',CORE=['./','./data.js?v=c28d64c5','./app.js?v=c28d64c5'];
self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(V).then(c=>c.addAll(CORE)).catch(()=>{}))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==V&&k!=='stgo27-tiles').map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
function race(p,ms){return new Promise((res,rej)=>{const t=setTimeout(()=>rej(new Error('t')),ms);p.then(r=>{clearTimeout(t);res(r)},e=>{clearTimeout(t);rej(e)})})}
self.addEventListener('fetch',e=>{const r=e.request;if(r.method!=='GET')return;const u=new URL(r.url);
 if(u.hostname==='tile.openstreetmap.org'){e.respondWith(caches.open('stgo27-tiles').then(c=>c.match(r)).then(h=>h||fetch(r).then(n=>{if(n.ok){const cp=n.clone();caches.open('stgo27-tiles').then(c=>c.put(r,cp))}return n})).catch(()=>fetch(r)));return}
 if(u.origin!==location.origin)return;
 const scope=new URL(self.registration.scope).pathname;
 if(r.mode==='navigate'&&(u.pathname===scope||u.pathname===scope+'index.html')){
  const net=fetch(r).then(n=>{if(n.ok&&!n.redirected){const cp=n.clone();caches.open(V).then(c=>c.put('./',cp))}return n});
  e.respondWith(caches.match('./').then(h=>h?race(net,3000).catch(()=>h):net).catch(()=>fetch(r)));return}
 if(u.search.indexOf('v=c28d64c5')>=0){e.respondWith(caches.match(r).then(h=>h||fetch(r)).catch(()=>fetch(r)))}
});