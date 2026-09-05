-- Il Pastaio — struttura del database condiviso
-- Da incollare UNA SOLA VOLTA nell'SQL Editor del progetto Supabase.
-- Poi: Authentication → Users → Add user, per ogni persona che deve entrare.

create table if not exists public.articoli (
  id             text primary key,
  nome           text not null,
  categoria      text,
  quantita       numeric default 0,
  unita          text,
  scorta_minima  numeric default 0,
  posizione      text,
  scadenza       text,
  note           text,
  updated_at     timestamptz default now()
);

create table if not exists public.attivita (
  id          text primary key,
  nome        text not null,
  tipo        text,
  telefono    text,
  indirizzo   text,
  note        text,
  updated_at  timestamptz default now()
);

create table if not exists public.ordini (
  id             text primary key,
  data           text,
  attivita_id    text,
  attivita_nome  text,
  ora            text,
  stato          text default 'Da preparare',
  note           text,
  righe          jsonb default '[]'::jsonb,
  scaricato      boolean default false,
  updated_at     timestamptz default now()
);

create table if not exists public.conferme (
  id          text primary key,   -- una riga per punto vendita al giorno
  sede        text not null,
  data        text not null,
  quando      timestamptz default now(),
  autore      text,               -- dispositivo che ha inviato il resoconto
  articoli    integer default 0,
  updated_at  timestamptz default now()
);

create index if not exists ordini_data_idx on public.ordini (data);
create index if not exists ordini_attivita_idx on public.ordini (attivita_id);

-- Sicurezza: solo chi ha effettuato l'accesso legge e scrive.
alter table public.articoli enable row level security;
alter table public.attivita enable row level security;
alter table public.ordini   enable row level security;
alter table public.conferme enable row level security;

drop policy if exists "accesso interno articoli" on public.articoli;
drop policy if exists "accesso interno attivita" on public.attivita;
drop policy if exists "accesso interno ordini"   on public.ordini;
drop policy if exists "accesso interno conferme" on public.conferme;

create policy "accesso interno articoli" on public.articoli
  for all to authenticated using (true) with check (true);
create policy "accesso interno attivita" on public.attivita
  for all to authenticated using (true) with check (true);
create policy "accesso interno ordini" on public.ordini
  for all to authenticated using (true) with check (true);
create policy "accesso interno conferme" on public.conferme
  for all to authenticated using (true) with check (true);

-- Aggiornamenti in tempo reale sugli altri dispositivi.
alter publication supabase_realtime add table public.articoli;
alter publication supabase_realtime add table public.attivita;
alter publication supabase_realtime add table public.ordini;
alter publication supabase_realtime add table public.conferme;
