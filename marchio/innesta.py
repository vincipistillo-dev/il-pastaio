# -*- coding: utf-8 -*-
"""Porta nell'app il marchio originale del PDF.

Si puo rilanciare quante volte serve: se il grafico manda una versione nuova
del PDF, basta sostituire il file e lanciare `python innesta.py`.
"""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import pymupdf
from dal_pdf import estrai, seleziona, ingombro, PEZZI

INDEX = os.path.join('..', 'index.html')
pezzi = estrai()
m, soci, claim, scritta = (pezzi[k] for k in ('marchio', 'soci', 'claim', 'scritta'))

# lo stemma per la barra in alto: il rombo col pastaio, fino alle ali del filetto
d = pymupdf.open('Il Pastaio-5.pdf')[0].get_drawings()
bx0, by0, _, _ = ingombro(seleziona(d, PEZZI['marchio']), 1.5)
S = (405, 285.5, 590, 413)                        # in punti sulla pagina
stemma_vb = f'{S[0]-bx0:.2f} {S[1]-by0:.2f} {S[2]-S[0]:.2f} {S[3]-S[1]:.2f}'
vb = lambda p: f'0 0 {p["larg"]:.2f} {p["alt"]:.2f}'

sprite = ('<!-- Marchio originale, dal file di Illustrator del grafico: curve vere, non ricostruite.\n'
          '     Generato da marchio/innesta.py: per aggiornarlo si rilancia quello, non si tocca qui. -->\n'
          '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">\n'
          f'  <defs>{m["defs"]}{soci["defs"]}{claim["defs"]}{scritta["defs"]}</defs>\n'
          f'  {m["corpo"]}\n  {soci["corpo"]}\n  {claim["corpo"]}\n  {scritta["corpo"]}\n'
          '</svg>\n\n')

s = io.open(INDEX, encoding='utf-8').read()

# 1) lo sprite, qualunque versione ci fosse prima
inizio = re.search(r'<!-- Marchio (originale|ricavato)', s).start()
fine = s.index('<div class="splash"', inizio)
s = s[:inizio] + sprite + s[fine:]

# 2) proporzioni aggiornate ovunque il marchio sia richiamato
for cls, v in (('marchio-completo', vb(m)), ('accesso-marchio', vb(m)), ('soci', vb(soci)),
               ('claim', vb(claim)), ('marchio-stemma', stemma_vb), ('brand-scritta', vb(scritta))):
    s = re.sub(rf'(<svg class="{cls}" viewBox=")[^"]*(")', rf'\g<1>{v}\g<2>', s)

# 3) barra in alto: "IL PASTAIO" con le lettere vere al posto del Bodoni
vecchio = '<div class="brand-name">IL PASTAIO</div>'
if vecchio in s:
    s = s.replace(vecchio, f'<svg class="brand-scritta" viewBox="{vb(scritta)}" role="img" '
                           f'aria-label="Il Pastaio"><use href="#scritta"/></svg>', 1)

# 4) misure della scritta nella barra
if '.brand-scritta{' not in s:
    s = s.replace('.brand-txt{min-width:0}',
                  '.brand-txt{min-width:0}\n'
                  '/* le lettere vere del marchio: altezza fissa, larghezza dalle proporzioni */\n'
                  '.brand-scritta{display:block;height:17px;width:auto;aspect-ratio:263.02/35.89;color:var(--head-ink);overflow:hidden}', 1)
    s = s.replace('  .brand-name{font-size:23px}', '  .brand-scritta{height:21px}', 1)

io.open(INDEX, 'w', encoding='utf-8').write(s)
print('viewBox stemma :', stemma_vb)
print('scritta        :', f'{scritta["larg"]:.1f} x {scritta["alt"]:.1f} pt')
print('index.html     :', round(os.path.getsize(INDEX) / 1024), 'KB')
