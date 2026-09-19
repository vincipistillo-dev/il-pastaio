# -*- coding: utf-8 -*-
"""Icone dell'app, disegnate direttamente dal PDF originale del grafico.

Il rombo col pastaio viene reso dal vettoriale ad alta risoluzione e usato
come maschera: stemma bianco su fondo verde, con la camicia che resta verde
come nel disegno originale.
"""
import os
import numpy as np
import pymupdf
from PIL import Image

QUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(QUI)
VERDE = (20, 122, 75)
STEMMA = pymupdf.Rect(405, 285.5, 590, 404)   # il rombo, sopra le ali dei filetti

pagina = pymupdf.open(os.path.join(QUI, 'Il Pastaio-5.pdf'))[0]
pix = pagina.get_pixmap(clip=STEMMA, dpi=900, colorspace=pymupdf.csGRAY)
chiaro = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).astype(np.float32)
# l'inchiostro e scuro sulla carta chiara: la maschera e il suo inverso
inchiostro = np.clip((235 - chiaro) / (235 - 150), 0, 1)
masc = Image.fromarray((inchiostro * 255).astype(np.uint8), 'L')
bb = masc.getbbox()
masc = masc.crop(bb)
print('stemma reso dal PDF:', masc.size)


def icona(lato, quota):
    """Quadrato verde pieno, stemma bianco al centro dentro la zona che Android non ritaglia."""
    tela = Image.new('RGB', (lato, lato), VERDE)
    largh = int(lato * quota)
    alt = int(round(largh * masc.height / masc.width))
    m = masc.resize((largh, alt), Image.LANCZOS)
    tela.paste(Image.new('RGB', m.size, (255, 255, 255)), ((lato - largh) // 2, (lato - alt) // 2), m)
    return tela


for lato in (192, 512):
    p = os.path.join(BASE, f'icona-{lato}.png')
    icona(lato, 0.62).save(p, optimize=True)
    print(f'icona-{lato}.png', os.path.getsize(p), 'byte')

p = os.path.join(BASE, 'apple-touch-icon.png')
icona(180, 0.72).save(p, optimize=True)     # iOS non ritaglia: puo stare piu largo
print('apple-touch-icon.png', os.path.getsize(p), 'byte')
