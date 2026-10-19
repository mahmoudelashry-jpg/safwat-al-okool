#!/usr/bin/env python3
"""Make one labelled QR PNG per character. Usage: make_qr.py <out_dir> <arabic_font>"""
import json, segno, io, os, sys
from PIL import Image, ImageDraw, ImageFont
from pyzbar.pyzbar import decode
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT, FONT = sys.argv[1], sys.argv[2]
BASE = "https://mahmoudelashry-jpg.github.io/safwat-al-okool/"
ar = ImageFont.truetype(FONT, 64, layout_engine=ImageFont.Layout.RAQM)
enb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 52)
en = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 36)
os.makedirs(OUT, exist_ok=True)
bad = []
for c in json.load(open(os.path.join(ROOT, 'characters.json'), encoding='utf-8')):
    url = BASE + c['slug'] + '/'
    buf = io.BytesIO(); segno.make(url, error='h').save(buf, kind='png', scale=20, border=4)
    im = Image.open(buf).convert('RGB'); w, h = im.size
    cv = Image.new('RGB', (w, h + 230), 'white'); cv.paste(im, (0, 0)); d = ImageDraw.Draw(cv)
    if c['name_ar']:
        kw = dict(direction='rtl', language='ar'); t, f = c['name_ar'], ar
    else:
        kw = {}; t, f = c['name'], enb
    d.text(((w - d.textlength(t, font=f, **kw)) / 2, h - 10), t, fill='black', font=f, **kw)
    sub = f"{c['num']:02d} · {c['name']}"
    d.text(((w - d.textlength(sub, font=en)) / 2, h + 110), sub, fill='#555', font=en)
    fn = os.path.join(OUT, f"{c['num']:02d} {c['name']}.png"); cv.save(fn, dpi=(300, 300))
    got = decode(Image.open(fn))
    if not got or got[0].data.decode() != url: bad.append(fn)
print('made', len(os.listdir(OUT)), 'decode failures:', bad)
