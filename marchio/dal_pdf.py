# -*- coding: utf-8 -*-
"""Estrae dal PDF di Illustrator i pezzi del marchio come SVG vettoriale.

Il PDF e il disegno di stampa del sacchetto: oltre al marchio contiene la
riga dei soci, gli indirizzi, la fascia col claim e le linee di piega.
Qui si seleziona ogni pezzo per posizione e lo si converte in tracciati SVG,
senza passare da immagini: sono le curve originali del grafico.

Il risultato usa currentColor, cosi prende il colore del testo e regge i due
temi. I bianchi dentro il marchio (la camicia sopra la giacca) diventano fori
ritagliati con una maschera, rispettando l'ordine di disegno originale.
"""
import pymupdf

PDF = 'Il Pastaio-5.pdf'
BIANCO = (1.0, 1.0, 1.0)
PEZZI = {
    'marchio': (355, 280, 636, 479),   # rombo, pastaio, IL PASTAIO, filetti, Pastificio Artigianale
    'soci':    (400, 481, 590, 502),   # di Pistillo F. & Tesse L.
    'claim':   (325, 695, 668, 766),   # La nobile arte di fare la pasta: la f e la p scendono in basso
}


def colore(d):
    c = d.get('fill') if 'f' in d['type'] else d.get('color')
    return tuple(round(x, 3) for x in c) if c else None


def dati(d, dx, dy, dec=2):
    """Un tracciato di PyMuPDF in dati di percorso SVG, spostato di (dx, dy)."""
    r = lambda v: f'{round(v, dec):g}'
    pt = lambda p: f'{r(p.x - dx)} {r(p.y - dy)}'
    out, cur = [], None
    for it in d['items']:
        op = it[0]
        if op in ('l', 'c'):
            a = it[1]
            if cur is None or abs(cur.x - a.x) > 1e-3 or abs(cur.y - a.y) > 1e-3:
                out.append('M' + pt(a))
            if op == 'l':
                out.append('L' + pt(it[2])); cur = it[2]
            else:
                out.append('C' + pt(it[2]) + ' ' + pt(it[3]) + ' ' + pt(it[4])); cur = it[4]
        elif op == 're':
            q = it[1]
            out.append(f'M{r(q.x0-dx)} {r(q.y0-dy)}H{r(q.x1-dx)}V{r(q.y1-dy)}H{r(q.x0-dx)}Z'); cur = None
        elif op == 'qu':
            q = it[1]
            out.append('M' + pt(q.ul) + 'L' + pt(q.ur) + 'L' + pt(q.lr) + 'L' + pt(q.ll) + 'Z'); cur = None
    if d.get('closePath'):
        out.append('Z')
    return ''.join(out)


def seleziona(disegni, riquadro):
    x0, y0, x1, y1 = riquadro
    return [d for d in disegni
            if d['rect'].x0 >= x0 - 1 and d['rect'].x1 <= x1 + 1
            and d['rect'].y0 >= y0 - 1 and d['rect'].y1 <= y1 + 1]


def ingombro(scelti, margine):
    """Il riquadro esatto, contando anche lo spessore dei tratti."""
    def lati(d):
        w = (d.get('width') or 0) / 2 if 's' in d['type'] else 0
        r = d['rect']
        return r.x0 - w, r.y0 - w, r.x1 + w, r.y1 + w
    L = [lati(d) for d in scelti]
    return (min(l[0] for l in L) - margine, min(l[1] for l in L) - margine,
            max(l[2] for l in L) + margine, max(l[3] for l in L) + margine)


def elemento(d, dx, dy, pieno, vuoto, bianco_pieno):
    """Un tracciato come elemento SVG. Nella maschera il pieno e bianco e il foro nero."""
    bianco = colore(d) == BIANCO and not bianco_pieno
    tinta = vuoto if bianco else pieno
    dd = dati(d, dx, dy)
    if 's' in d['type'] and 'f' not in d['type']:
        return (f'<path d="{dd}" fill="none" stroke="{tinta}" '
                f'stroke-width="{d.get("width", 1):.3f}" stroke-linecap="butt" stroke-linejoin="miter"/>')
    regola = 'evenodd' if d.get('even_odd') else 'nonzero'
    return f'<path fill-rule="{regola}" fill="{tinta}" d="{dd}"/>'


def pezzo_svg(disegni, riquadro, id_, bianco_pieno=False, margine=1.5):
    scelti = seleziona(disegni, riquadro)
    bx0, by0, bx1, by1 = ingombro(scelti, margine)
    L, A = bx1 - bx0, by1 - by0
    ha_fori = any(colore(d) == BIANCO for d in scelti) and not bianco_pieno
    if not ha_fori:
        corpo = ''.join(elemento(d, bx0, by0, 'currentColor', 'currentColor', bianco_pieno) for d in scelti)
        return {'id': id_, 'larg': L, 'alt': A, 'n': len(scelti), 'defs': '',
                'corpo': f'<g id="{id_}">{corpo}</g>'}
    # l'ordine di disegno resta quello originale: cio che sta sopra al bianco ricompare
    dentro = ''.join(elemento(d, bx0, by0, '#fff', '#000', bianco_pieno) for d in scelti)
    m = f'{id_}-fori'
    defs = (f'<mask id="{m}" maskUnits="userSpaceOnUse" x="0" y="0" width="{L:.2f}" height="{A:.2f}">'
            f'{dentro}</mask>')
    corpo = f'<g id="{id_}"><rect width="{L:.2f}" height="{A:.2f}" fill="currentColor" mask="url(#{m})"/></g>'
    return {'id': id_, 'larg': L, 'alt': A, 'n': len(scelti), 'defs': defs, 'corpo': corpo}


def scritta_svg(disegni, id_='scritta', margine=1.0):
    """IL PASTAIO da solo, per la barra in alto.

    Fra la A e la S il grafico lascia uno stacco largo (7,7 punti contro i 2-3
    delle altre coppie): nel marchio completo ci scende la punta della giacca.
    Presa da sola la scritta si leggerebbe "PA STAIO", quindi qui le lettere
    dalla S in poi vengono accostate di 5 punti. Le forme restano quelle originali.
    """
    lettere = [d for d in disegni if 'f' in d['type']
               and 412 <= d['rect'].y0 and d['rect'].y1 <= 460
               and 355 <= d['rect'].x0 and d['rect'].x1 <= 636]
    ACCOSTA, DA_X = 5.0, 486
    bx0, by0, bx1, by1 = ingombro(lettere, margine)
    corpo = ''
    for d in lettere:
        dx = bx0 + (ACCOSTA if d['rect'].x0 >= DA_X else 0)
        corpo += elemento(d, dx, by0, 'currentColor', 'currentColor', False)
    L, A = (bx1 - bx0) - ACCOSTA, by1 - by0
    return {'id': id_, 'larg': L, 'alt': A, 'n': len(lettere), 'defs': '',
            'corpo': f'<g id="{id_}">{corpo}</g>'}


def estrai():
    doc = pymupdf.open(PDF)
    disegni = doc[0].get_drawings()
    return {
        'marchio': pezzo_svg(disegni, PEZZI['marchio'], 'marchio'),
        'soci':    pezzo_svg(disegni, PEZZI['soci'], 'soci'),
        'claim':   pezzo_svg(disegni, PEZZI['claim'], 'claim', bianco_pieno=True),
        'scritta': scritta_svg(disegni),
    }


if __name__ == '__main__':
    for nome, p in estrai().items():
        print(f'{nome:8s}: {p["n"]:3d} tracciati  {p["larg"]:.1f} x {p["alt"]:.1f} pt  '
              f'maschera={"si" if p["defs"] else "no"}  '
              f'{(len(p["defs"]) + len(p["corpo"])) / 1024:.1f} KB')
