# Il Pastaio — Magazzino e Ordini

App per il pastificio: giacenze di magazzino e ordini divisi per data di consegna e attività richiedente.
Un solo file, nessuna installazione: `index.html`.

## Usarla subito

Apri `index.html` con un doppio click. Funziona anche dal telefono, ma i dati restano
sul dispositivo su cui la apri finché non colleghi la sincronizzazione.

## Metterla online (gratis, con GitHub Pages)

1. Crea un repository su github.com e carica `index.html`.
2. Nel repository: **Settings → Pages → Source: Deploy from a branch → main / (root)**.
3. Dopo un paio di minuti l'app è su `https://<tuo-utente>.github.io/<repository>/`.
4. Apri quell'indirizzo dal telefono e aggiungilo alla schermata Home: si comporta come un'app.

GitHub Pages ospita l'app, non i dati. Per quelli serve il passo successivo.

## Far vedere gli stessi dati a più telefoni

1. Crea un progetto gratuito su [supabase.com](https://supabase.com).
2. **SQL Editor** → incolla tutto il contenuto di `supabase/schema.sql` → Run.
3. **Authentication → Users → Add user**: crea un account (email e password) per ogni persona.
4. **Project Settings → API**: copia *Project URL* e *anon public key*.
5. Nell'app: **Impostazioni → Collega Supabase**, incolla i due valori, accedi.

Da quel momento ogni modifica compare sugli altri dispositivi in pochi secondi.
La chiave *anon* è pensata per stare dentro l'app: da sola non apre niente, perché le
tabelle sono protette e richiedono l'accesso con account.

## Cosa c'è dentro

- **Magazzino** — diviso fra i due punti vendita, Viale Alto Adige e Via Savonarola.
  Ogni riga porta il nome, la quantità con i tasti `+` / `−` e il cestino per eliminarla;
  toccando il nome si aprono gli altri dati (unità, scorta minima, posizione, scadenza).
  Una barra colorata a sinistra segnala scorta esaurita e scadenze vicine.
- **Ordini** — un calendario del mese: i pallini segnano i giorni con ordini (oro se ci sono
  ancora voci da fare, verde se è tutto completato). Toccando un giorno compaiono i suoi ordini
  e il tasto "Ordine" ne registra uno **già datato a quel giorno**: si scrivono a mano il nome del
  ristorante, i prodotti con la quantità e una nota facoltativa. La tendina del nome propone i
  quattro ristoranti serviti più di recente, quella dei prodotti quello che c'è in magazzino.
  Ogni prodotto si spunta singolarmente e l'ordine è **da preparare** finché non sono spuntati
  tutti, poi diventa **completato**. Modifica, scarico dal magazzino ed eliminazione stanno in
  tre icone piccole in fondo alla scheda.
- **Attività** — i ristoranti con il numero di ordini della settimana, dal più attivo in giù.
  Le linguette in alto tornano indietro fino a un mese; la settimana va da lunedì a domenica.
  Un nome scritto su un ordine ma non ancora in rubrica compare lo stesso, segnalato: toccandolo
  si apre la scheda già compilata per aggiungerlo.
- **Conferma situazione** — in fondo al magazzino: registra il resoconto di giornata del punto
  vendita e avvisa gli altri dispositivi. Chi invia non riceve il proprio avviso.
- **Impostazioni** — notifiche, sincronizzazione, backup su file, azzeramento.

## Limite delle notifiche

L'avviso compare in cima all'app e, se il permesso è stato concesso, anche come notifica di
sistema — **ma solo sui dispositivi che hanno l'app aperta** (anche in secondo piano). A app
chiusa non arriva niente: servirebbero un service worker e un servizio di Web Push, che Supabase
da solo non copre. Chi apre l'app più tardi trova comunque l'avviso in cima, finché non lo chiude.

## Marchio

Colori e caratteri sono ripresi dal packaging: verde del pastificio su carta bianca,
"IL PASTAIO" in Bodoni Moda, il claim *La nobile arte di fare la pasta* in Petit Formal Script.
Lo stemma nella schermata di apertura è una ricostruzione vettoriale: per sostituirlo con
l'originale basta rimpiazzare il contenuto di `<symbol id="crest">` in `index.html`.
