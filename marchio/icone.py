# -*- coding: utf-8 -*-
"""Icone dell'app: il marchio intero, verde su bianco, disegnato dal PDF originale.

Si usa il marchio completo e non il solo stemma: nel disegno originale il
rombo e chiuso in basso dalla scritta, quindi preso da solo appare tagliato.

Due varianti, perche Android le usa in modo diverso:
- "any": il marchio grande, per le schermate dove l'icona si vede per intero;
- "maskable": il marchio dentro la zona sicura (un cerchio largo l'80%),
  perche il telefono ritaglia l'icona a cerchio o a quadrato arrotondato.
"""
import os
import numpy as np
import pymupdf
from PIL import Image

QUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(QUI)
VERDE = (20, 122, 75)                            # il verde dell'app
BIANCO = (255, 255, 255)
MARCHIO = pymupdf.Rect(355, 280, 636, 479)       # rombo, pastaio, scritta, filetti

pagina = pymupdf.open(os.path.join(QUI, 'Il Pastaio-5.pdf'))[0]
pix = pagina.get_pixmap(clip=MARCHIO, dpi=900, colorspace=pymupdf.csGRAY)
chiaro = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).astype(np.float32)
# inchiostro scuro su carta chiara; la camicia bianca resta fuori e quindi bianca
masc = Image.fromarray((np.clip((235 - chiaro) / (235 - 150), 0, 1) * 255).astype(np.uint8), 'L')
masc = masc.crop(masc.getbbox())
print('marchio reso dal PDF:', masc.size)


def icona(lato, quota):
    """Tela bianca, marchio verde centrato: largo `quota` del lato."""
    tela = Image.new('RGB', (lato, lato), BIANCO)
    largh = round(lato * quota)
    alt = round(largh * masc.height / masc.width)
    m = masc.resize((largh, alt), Image.LANCZOS)
    tela.paste(Image.new('RGB', m.size, VERDE), ((lato - largh) // 2, (lato - alt) // 2), m)
    return tela


# nella zona sicura il marchio deve stare tutto dentro un cerchio di diametro 80%:
# con queste proporzioni la larghezza massima e circa il 65% del lato
# I browser tengono in memoria le icone per indirizzo, e molto a lungo: se il
# disegno cambia, il nome del file deve cambiare con lui, altrimenti telefoni e
# segnalibri continuano a mostrare quella vecchia. Da qui il numero nel nome.
V = 2
USCITE = [
    (f'logo-v{V}-192.png', 192, 0.84), (f'logo-v{V}-512.png', 512, 0.84),
    (f'logo-v{V}-maskable-192.png', 192, 0.62), (f'logo-v{V}-maskable-512.png', 512, 0.62),
    (f'logo-v{V}-apple-180.png', 180, 0.82),     # iOS arrotonda gli angoli ma non ritaglia
]
for nome, lato, quota in USCITE:
    p = os.path.join(BASE, nome)
    icona(lato, quota).save(p, optimize=True)
    print(f'{nome:26s} {os.path.getsize(p):6d} byte')

# verifica: il marchio nella variante mascherabile sta dentro il cerchio sicuro?
largh = 0.62; alt = largh * masc.height / masc.width
semidiag = ((largh / 2) ** 2 + (alt / 2) ** 2) ** 0.5
print(f'zona sicura: angolo del marchio a {semidiag:.3f} dal centro, limite 0.400 ->',
      'dentro' if semidiag <= 0.40 else 'FUORI')
