# -*- coding: utf-8 -*-
"""Genera il marchio vettoriale rifinito a partire dalla maschera."""
import sys; sys.setrecursionlimit(50000); sys.path.insert(0, 'marchio')
from vettorizza import campo, marching_squares, in_anelli, douglas_peucker, in_path

W, H = 528, 350
# filetti misurati sulla stampa
FILETTI = [(13, 220.4, 516, 224.6), (7, 326.2, 100, 330.2), (424, 326.2, 521, 330.2)]
BANDA_FILETTO_ALTO = (216, 228)
BANDA_FILETTO_BASSO = (323, 333)
BANDA_TESTO_PICCOLO = 318          # sotto questa riga c'è "Pastificio Artigianale"

def bbox(anello):
    xs = [p[0] for p in anello]; ys = [p[1] for p in anello]
    return min(xs), min(ys), max(xs), max(ys)

# il viso e il papillon sono tratti sottili e chiari: li serve una soglia piu bassa
VISO = [(200, 75, 340, 190, 66)]

def costruisci(sfoca=1.5, scala=3):
    f, sc = campo('marchio/logo-completo.png', scala=scala, sfoca=sfoca, zone=VISO)
    anelli = in_anelli(marching_squares(f))
    tenuti, scartati = [], 0
    for a in anelli:
        x0, y0, x1, y1 = [v/sc for v in bbox(a)]
        larg, alt = x1-x0, y1-y0
        # via la scritta piccola: a questa risoluzione è illeggibile, la rifaccio col carattere
        if y0 > BANDA_TESTO_PICCOLO: scartati += 1; continue
        # via i filetti tracciati: al loro posto vanno rette esatte
        if larg > 60 and alt < 9 and (BANDA_FILETTO_ALTO[0] < (y0+y1)/2 < BANDA_FILETTO_ALTO[1]
                                      or BANDA_FILETTO_BASSO[0] < (y0+y1)/2 < BANDA_FILETTO_BASSO[1]):
            scartati += 1; continue
        # semplificazione su misura: molta sui tratti lunghi, poca sui dettagli del viso
        eps = min(1.5, max(0.32, 0.32 + 0.0042 * max(larg, alt)))
        tenuti.append((a, eps))
    d = ''.join(in_path(a, sc, eps) for a, eps in tenuti)
    for x0, y0, x1, y1 in FILETTI:
        d += f'M{x0} {y0}H{x1}V{y1}H{x0}Z'
    return d, len(tenuti), scartati

if __name__ == '__main__':
    d, tenuti, scartati = costruisci()
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" fill="currentColor">'
           f'<path fill-rule="evenodd" d="{d}"/>'
           f'<text x="262" y="336.5" text-anchor="middle" textLength="300" lengthAdjust="spacingAndGlyphs" '
           f'font-family="Bodoni Moda, Didot, Georgia, serif" font-size="19" font-weight="500">'
           f'Pastificio Artigianale</text></svg>')
    open('marchio/logo.svg', 'w', encoding='utf-8').write(svg)
    print(f'anelli tenuti {tenuti}, scartati {scartati} — svg {len(svg)/1024:.1f} KB')
