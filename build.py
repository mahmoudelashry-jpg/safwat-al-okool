#!/usr/bin/env python3
"""Builds one gallery page per character from characters.json.
Run: python3 build.py   -> writes <slug>/index.html and index.html
"""
import json, html, os

ROOT = os.path.dirname(os.path.abspath(__file__))
BOOK = "حجة صفوة العقول الإنسانية"

LANG = {
    "gr": "النص الأصلي · اليونانية",
    "la": "النص الأصلي · اللاتينية",
    "ar": "النص الأصلي · العربية",
    "he": "النص الأصلي · العبرية",
    "de": "الألمانية",
    "fr": "الفرنسية",
    "en": "الترجمة الإنجليزية",
}
AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
e = html.escape

PAGE = """<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title} — {book}</title>
<meta name="robots" content="noindex">
<meta name="theme-color" content="#14110d">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cormorant+Garamond:ital,wght@0,500;1,500&display=swap" rel="stylesheet">
<style>
:root{{--bg:#14110d;--ink:#efe6d4;--muted:#a89a80;--line:#3a3226;--gold:#c9a45c;--card:#1d1912}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:var(--bg);color:var(--ink)}}
body{{font-family:"Amiri",serif;min-height:100vh;-webkit-font-smoothing:antialiased;line-height:1.7}}
header{{text-align:center;padding:44px 20px 30px;border-bottom:1px solid var(--line);max-width:760px;margin:0 auto}}
.kicker{{font-size:15px;color:var(--gold);letter-spacing:.03em}}
.orn{{width:56px;height:1px;background:var(--gold);margin:14px auto;opacity:.7}}
h1{{font-weight:700;font-size:clamp(28px,7.5vw,44px);line-height:1.35}}
.arg{{color:var(--gold);font-size:clamp(20px,5.2vw,26px);margin-top:10px}}
.en{{font-family:"Cormorant Garamond",serif;font-style:italic;font-weight:500;font-size:clamp(18px,4.6vw,23px);color:var(--muted);margin-top:4px;direction:ltr}}
.intro{{color:#d8ccb4;font-size:clamp(16px,4.2vw,18px);margin:16px auto 0;max-width:560px}}
main{{max-width:760px;margin:0 auto;padding:10px 16px 56px}}
section{{padding:30px 0 6px;border-bottom:1px solid var(--line)}}
section:last-child{{border-bottom:0}}
h2{{display:flex;align-items:baseline;gap:12px;font-size:clamp(21px,5.4vw,27px);font-weight:700;margin-bottom:16px}}
h2 b{{color:var(--gold);font-weight:400;font-size:.85em;min-width:1.4em}}
.pair{{display:grid;gap:18px}}
@media (min-width:900px){{main{{max-width:1180px}}.pair{{grid-template-columns:1fr 1fr}}}}
figure{{cursor:zoom-in}}
figcaption{{font-size:14px;color:var(--muted);margin-bottom:7px}}
.frame{{background:var(--card);border:1px solid var(--line);border-radius:6px;overflow:hidden;aspect-ratio:1372/968}}
.frame img{{display:block;width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .4s}}
.frame img.ok{{opacity:1}}
footer{{text-align:center;color:var(--muted);font-size:13px;padding:0 16px 40px}}
#lb{{position:fixed;inset:0;background:#000;display:none;z-index:9;flex-direction:column;align-items:center;justify-content:center}}
#lb.on{{display:flex}}
#lb img{{max-width:100vw;max-height:calc(100vh - 90px);object-fit:contain;user-select:none;-webkit-user-drag:none}}
#lb button{{position:absolute;background:rgba(0,0,0,.45);color:#fff;border:0;font-size:26px;width:48px;height:48px;border-radius:50%;cursor:pointer}}
#x{{top:max(14px,env(safe-area-inset-top));left:14px}}
#nx{{left:10px;top:50%;transform:translateY(-50%)}}
#pv{{right:10px;top:50%;transform:translateY(-50%)}}
#cap{{color:#eee;font-size:17px;text-align:center;padding:12px 16px 0}}
#ct{{color:#999;font-size:14px;padding-bottom:max(10px,env(safe-area-inset-bottom))}}
@media (hover:none){{#nx,#pv{{display:none}}}}
</style>
</head>
<body>
<header>
  <div class="kicker">{kicker}</div>
  <div class="orn"></div>
  <h1>{name_ar}</h1>
  <div class="en">{name}</div>
  {argument}
  {intro}
</header>
<main>
{sections}
</main>
<footer>{book}</footer>
<div id="lb" role="dialog" aria-modal="true">
  <img id="lbi" alt="">
  <div id="cap"></div><div id="ct"></div>
  <button id="x" aria-label="إغلاق">✕</button>
  <button id="pv" aria-label="السابق">›</button>
  <button id="nx" aria-label="التالي">‹</button>
</div>
<script>
const big={big};
const lb=document.getElementById('lb'),im=document.getElementById('lbi'),cap=document.getElementById('cap'),ct=document.getElementById('ct');
let i=0;
function show(k){{i=(k+big.length)%big.length;im.src=big[i][0];cap.textContent=big[i][1];ct.textContent=(i+1)+' من '+big.length;}}
function open_(k){{show(k);lb.classList.add('on');document.body.style.overflow='hidden';}}
function close_(){{lb.classList.remove('on');document.body.style.overflow='';}}
document.querySelectorAll('figure').forEach((f,k)=>f.addEventListener('click',()=>open_(k)));
document.querySelectorAll('.frame img').forEach(m=>{{if(m.complete)m.classList.add('ok');m.addEventListener('load',()=>m.classList.add('ok'));}});
document.getElementById('x').onclick=close_;
document.getElementById('nx').onclick=e=>{{e.stopPropagation();show(i+1)}};
document.getElementById('pv').onclick=e=>{{e.stopPropagation();show(i-1)}};
lb.addEventListener('click',e=>{{if(e.target===lb)close_()}});
document.addEventListener('keydown',e=>{{if(!lb.classList.contains('on'))return;if(e.key==='Escape')close_();if(e.key==='ArrowLeft')show(i+1);if(e.key==='ArrowRight')show(i-1);}});
let sx=null;
lb.addEventListener('touchstart',e=>{{sx=e.touches[0].clientX}},{{passive:true}});
lb.addEventListener('touchend',e=>{{if(sx===null)return;const d=e.changedTouches[0].clientX-sx;if(Math.abs(d)>45)show(d>0?i+1:i-1);sx=null;}});
</script>
</body>
</html>
"""

INDEX = """<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{book}</title><meta name="robots" content="noindex">
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap" rel="stylesheet">
<style>
body{{margin:0;background:#14110d;color:#efe6d4;font-family:"Amiri",serif}}
h1{{text-align:center;color:#c9a45c;font-size:30px;padding:48px 16px 24px;margin:0}}
ul{{list-style:none;max-width:560px;margin:0 auto;padding:0 16px 48px}}
li a{{display:block;padding:14px 4px;border-bottom:1px solid #3a3226;color:inherit;text-decoration:none;font-size:20px}}
</style></head><body><h1>{book}</h1><ul>{items}</ul></body></html>
"""


def render(c):
    big, secs, k = [], [], 0
    for s in c["sections"]:
        figs = []
        for im in s["images"]:
            label = LANG.get(im["lang"], im["lang"].upper())
            src = f"img/{im['file']}"
            figs.append(
                f'<figure><figcaption>{e(label)}</figcaption><div class="frame">'
                f'<img src="{src}" alt="{e(s["caption"])} — {e(label)}" loading="{"eager" if k < 2 else "lazy"}">'
                f"</div></figure>")
            big.append([src, f'{s["caption"]} — {label}'])
            k += 1
        num = str(s["n"]).translate(AR_DIGITS)
        secs.append(f'<section><h2><b>{num}</b>{e(s["caption"])}</h2><div class="pair">{"".join(figs)}</div></section>')
    intro = "".join(f'<p class="intro">{e(p)}</p>' for p in c.get("intro", []))
    return PAGE.format(
        book=BOOK, kicker=e(c["kicker"]), title=e(c["title"]), name=e(c["name"]),
        name_ar=e(c.get("name_ar") or c["title"]),
        argument=f'<div class="arg">{e(c["argument"])}</div>' if c.get("argument") else "",
        intro=intro, sections="\n".join(secs),
        big=json.dumps(big, ensure_ascii=False))


def main():
    chars = json.load(open(os.path.join(ROOT, "characters.json"), encoding="utf-8"))
    for c in chars:
        os.makedirs(os.path.join(ROOT, c["slug"]), exist_ok=True)
        open(os.path.join(ROOT, c["slug"], "index.html"), "w", encoding="utf-8").write(render(c))
    items = "".join(f'<li><a href="{c["slug"]}/">{e(c["title"])}</a></li>' for c in chars)
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(INDEX.format(book=BOOK, items=items))
    print("built", len(chars), "pages")


if __name__ == "__main__":
    main()
