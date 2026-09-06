# -*- coding: utf-8 -*-
"""Ricava contorni vettoriali puliti dalla maschera del marchio."""
import numpy as np
from PIL import Image, ImageFilter

def tura_buchi(bin_, area_max):
    """Chiude i micro-buchi lasciati dalla grana della stampa dentro i pieni.
    I vuoti veri del disegno (occhiello della O, camicia, interno del rombo)
    sono molto piu grandi e restano."""
    from collections import deque
    H, W = bin_.shape
    fuori = np.zeros_like(bin_)
    coda = deque()
    for x in range(W):
        for y in (0, H-1):
            if not bin_[y, x] and not fuori[y, x]: fuori[y, x] = True; coda.append((y, x))
    for y in range(H):
        for x in (0, W-1):
            if not bin_[y, x] and not fuori[y, x]: fuori[y, x] = True; coda.append((y, x))
    while coda:                                    # lo sfondo vero, quello che tocca il bordo
        y, x = coda.popleft()
        for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny, nx = y+dy, x+dx
            if 0 <= ny < H and 0 <= nx < W and not bin_[ny, nx] and not fuori[ny, nx]:
                fuori[ny, nx] = True; coda.append((ny, nx))
    visto = fuori | bin_
    turati = 0
    for y0 in range(H):
        for x0 in range(W):
            if visto[y0, x0]: continue
            gruppo = []; coda = deque([(y0, x0)]); visto[y0, x0] = True
            while coda:
                y, x = coda.popleft(); gruppo.append((y, x))
                for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny, nx = y+dy, x+dx
                    if 0 <= ny < H and 0 <= nx < W and not visto[ny, nx] and not bin_[ny, nx]:
                        visto[ny, nx] = True; coda.append((ny, nx))
            if len(gruppo) <= area_max:
                turati += 1
                for y, x in gruppo: bin_[y, x] = True
    return bin_, turati

def campo(mask_png, scala=3, sfoca=1.4, area_max=420, soglia=100, zone=()):
    """Alza la risoluzione, tura i micro-buchi e smussa i denti della stampa.
    `zone` permette una soglia piu bassa dove serve: i segni del viso sono
    tratti sottilissimi, con la soglia generale se ne salva solo il cuore."""
    a = Image.open(mask_png).split()[3]
    a = a.resize((a.width*scala, a.height*scala), Image.LANCZOS)
    arr = np.asarray(a, dtype=np.float32)
    limite = np.full(arr.shape, float(soglia), dtype=np.float32)
    for x0, y0, x1, y1, s_ in zone:
        limite[int(y0*scala):int(y1*scala), int(x0*scala):int(x1*scala)] = s_
    bin_ = arr > limite
    bin_, turati = tura_buchi(bin_.copy(), area_max)
    campo.turati = turati
    pieno = Image.fromarray((bin_*255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(sfoca))
    return np.asarray(pieno, dtype=np.float32)/255.0, scala

def marching_squares(f, livello=0.5):
    """Contorni al mezzo tono, con interpolazione: bordi a precisione sub-pixel."""
    H, W = f.shape
    segmenti = []
    def interp(p, q, vp, vq):
        t = (livello - vp) / (vq - vp) if vq != vp else 0.5
        return (p[0] + (q[0]-p[0])*t, p[1] + (q[1]-p[1])*t)
    for y in range(H-1):
        riga0, riga1 = f[y], f[y+1]
        for x in range(W-1):
            a, b, c, d = riga0[x], riga0[x+1], riga1[x+1], riga1[x]
            caso = (a>livello)*8 + (b>livello)*4 + (c>livello)*2 + (d>livello)*1
            if caso in (0, 15): continue
            A = interp((x,y),   (x+1,y),   a, b)   # alto
            B = interp((x+1,y), (x+1,y+1), b, c)   # destra
            C = interp((x+1,y+1),(x,y+1),  c, d)   # basso
            D = interp((x,y+1), (x,y),     d, a)   # sinistra
            tab = {1:[(C,D)], 2:[(B,C)], 3:[(B,D)], 4:[(A,B)], 5:[(A,D),(B,C)],
                   6:[(A,C)], 7:[(A,D)], 8:[(D,A)], 9:[(C,A)], 10:[(D,C),(A,B)],
                   11:[(B,A)], 12:[(D,B)], 13:[(C,B)], 14:[(C,D)]}
            segmenti.extend(tab[caso])
    return segmenti

def in_anelli(segmenti, tol=3, minimo=8):
    """Incolla i segmenti in anelli chiusi, senza fidarsi del loro verso:
    nelle celle ambigue marching squares li orienta in modo incoerente."""
    chiave = lambda p: (round(p[0], tol), round(p[1], tol))
    incidenti = {}
    for i, (a, b) in enumerate(segmenti):
        incidenti.setdefault(chiave(a), []).append((i, b))
        incidenti.setdefault(chiave(b), []).append((i, a))
    consumato = [False]*len(segmenti)

    def prossimo(nodo):
        for j, (i, altro) in enumerate(incidenti.get(nodo, [])):
            if not consumato[i]:
                return i, altro
        return None, None

    anelli = []
    for i0, (a0, b0) in enumerate(segmenti):
        if consumato[i0]: continue
        consumato[i0] = True
        anello = [a0, b0]
        cur = chiave(b0)
        partenza = chiave(a0)
        while cur != partenza:
            i, altro = prossimo(cur)
            if i is None: break
            consumato[i] = True
            anello.append(altro)
            cur = chiave(altro)
        if cur == partenza and len(anello) >= minimo:
            anelli.append(anello)
    return anelli

def douglas_peucker(punti, eps):
    if len(punti) < 3: return punti
    inizio, fine = punti[0], punti[-1]
    dx, dy = fine[0]-inizio[0], fine[1]-inizio[1]
    lung = (dx*dx + dy*dy) ** 0.5
    peggiore, indice = 0.0, 0
    for i in range(1, len(punti)-1):
        p = punti[i]
        d = (abs(dy*p[0] - dx*p[1] + fine[0]*inizio[1] - fine[1]*inizio[0]) / lung) if lung else \
            (((p[0]-inizio[0])**2 + (p[1]-inizio[1])**2) ** 0.5)
        if d > peggiore: peggiore, indice = d, i
    if peggiore <= eps: return [inizio, fine]
    return douglas_peucker(punti[:indice+1], eps)[:-1] + douglas_peucker(punti[indice:], eps)

def in_path(anello, scala, eps, decimali=1):
    """Spezzata retta: i tratti lunghi diventano rette e i vertici restano vivi.
    Con le curve il rombo si arrotonderebbe in una goccia."""
    pts = douglas_peucker([(p[0]/scala, p[1]/scala) for p in anello], eps)
    if len(pts) > 2 and pts[0] == pts[-1]: pts = pts[:-1]
    if len(pts) < 3: return ''
    r = lambda v: f'{round(v, decimali):g}'
    d = [f'M{r(pts[0][0])} {r(pts[0][1])}']
    d += [f'L{r(x)} {r(y)}' for x, y in pts[1:]]
    d.append('Z')
    return ''.join(d)
