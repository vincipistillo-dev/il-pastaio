/* Service worker dell'app Il Pastaio.
 *
 * Serve a due cose: permettere a Chrome di offrire l'installazione vera
 * (senza un gestore di "fetch" il tasto Installa non compare), e far aprire
 * l'app anche senza rete.
 *
 * La strategia e "prima la rete": quando c'e linea si scarica sempre la
 * versione aggiornata, e se ne tiene una copia da parte. Solo quando la rete
 * manca si usa la copia. Cosi un aggiornamento non resta mai bloccato in
 * memoria, che e il difetto classico delle app installate.
 */
const DEPOSITO = "pastaio-v2";

self.addEventListener("install", () => self.skipWaiting());

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    for(const nome of await caches.keys()){
      if(nome !== DEPOSITO) await caches.delete(nome);   // via i depositi vecchi
    }
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", e => {
  const richiesta = e.request;
  if(richiesta.method !== "GET") return;
  if(new URL(richiesta.url).origin !== location.origin) return;  // solo i file dell'app

  e.respondWith((async () => {
    try {
      const risposta = await fetch(richiesta);
      if(risposta && risposta.ok){
        const copia = risposta.clone();
        caches.open(DEPOSITO).then(d => d.put(richiesta, copia)).catch(() => {});
      }
      return risposta;
    } catch (err) {
      const salvata = await caches.match(richiesta);
      if(salvata) return salvata;
      throw err;
    }
  })());
});
