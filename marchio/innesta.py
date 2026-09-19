# -*- coding: utf-8 -*-
"""Sostituisce nell'app il marchio ricostruito con quello originale del PDF."""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))
import pymupdf
from dal_pdf import estrai, seleziona, ingombro, PEZZI

INDEX = os.path.join('..', 'index.html')
pezzi = estrai()
m, soci, claim = pezzi['marchio'], pezzi['soci'], pezzi['claim']

# lo stemma per la barra in alto: il rombo col pastaio, fino alle ali del filetto
d = pymupdf.open('Il Pastaio-5.pdf')[0].get_drawings()
bx0, by0, _, _ = ingombro(seleziona(d, PEZZI['marchio']), 1.5)
S = (405, 285.5, 590, 413)                        # in punti sulla pagina
stemma_vb = f'{S[0]-bx0:.2f} {S[1]-by0:.2f} {S[2]-S[0]:.2f} {S[3]-S[1]:.2f}'
print('viewBox stemma:', stemma_vb)

vb = lambda p: f'0 0 {p["larg"]:.2f} {p["alt"]:.2f}'
sprite = ('<!-- Marchio originale, dal file di Illustrator del grafico: curve vere, non ricostruite.\n'
          '     Generato da marchio/innesta.py: per aggiornarlo si rilancia quello, non si tocca qui. -->\n'
          '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">\n'
          f'  <defs>{m["defs"]}{soci["defs"]}{claim["defs"]}</defs>\n'
          f'  {m["corpo"]}\n  {soci["corpo"]}\n  {claim["corpo"]}\n'
          '</svg>\n\n')

s = io.open(INDEX, encoding='utf-8').read()

# 1) lo sprite
i = s.index('<!-- Marchio ricavato dalla stampa')
j = s.index('<div class="splash"', i)
s = s[:i] + sprite + s[j:]

# 2) apertura: marchio, riga dei soci e claim, tutti originali
vecchio = re.search(r'<svg class="marchio-completo"[^>]*>.*?</svg>\s*<p class="claim">La nobile arte di fare la pasta</p>', s, re.S).group(0)
nuovo = (f'<svg class="marchio-completo" viewBox="{vb(m)}" role="img" aria-label="Il Pastaio, pastificio artigianale"><use href="#marchio"/></svg>\n'
         f'    <svg class="soci" viewBox="{vb(soci)}" role="img" aria-label="di Pistillo F. &amp; Tesse L."><use href="#soci"/></svg>\n'
         f'    <svg class="claim" viewBox="{vb(claim)}" role="img" aria-label="La nobile arte di fare la pasta"><use href="#claim"/></svg>')
s = s.replace(vecchio, nuovo, 1)

# 3) barra in alto e schermata di accesso
s = re.sub(r'<svg class="marchio-stemma" viewBox="[^"]*"', f'<svg class="marchio-stemma" viewBox="{stemma_vb}"', s, count=1)
s = re.sub(r'<svg class="accesso-marchio" viewBox="[^"]*"', f'<svg class="accesso-marchio" viewBox="{vb(m)}"', s, count=1)

# 4) il claim ora e un disegno: misure da disegno, non da testo
s = re.sub(r'\.splash \.claim\{.*?\n\}\n',
           '.splash .soci{\n'
           '  display:block;width:min(170px,44vw);height:auto;margin-top:12px;color:var(--murgia);\n'
           '  opacity:0;animation:riseIn .8s .3s ease-out forwards;\n'
           '}\n'
           '.splash .claim{\n'
           '  display:block;width:min(300px,76vw);height:auto;margin-top:22px;color:var(--murgia);\n'
           '  opacity:0;animation:riseIn .9s .55s ease-out forwards;\n'
           '}\n', s, count=1, flags=re.S)
s = s.replace('.splash .marchio-completo,.splash .claim{animation:none;opacity:1}',
              '.splash .marchio-completo,.splash .soci,.splash .claim{animation:none;opacity:1}', 1)

# 5) il corsivo di Google non serve piu: il claim e disegnato
s = s.replace('&family=Petit+Formal+Script', '', 1)

io.open(INDEX, 'w', encoding='utf-8').write(s)
print('index.html:', round(os.path.getsize(INDEX) / 1024), 'KB')
print('riferimenti residui a Petit Formal Script:', s.count('Petit+Formal'))
