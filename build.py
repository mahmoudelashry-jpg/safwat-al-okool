#!/usr/bin/env python3
"""Builds one gallery page per character from characters.json.
Run: python3 build.py   -> writes <slug>/index.html and index.html
"""
import json, html, os

ROOT = os.path.dirname(os.path.abspath(__file__))
BOOK = "صفوة العقول الإنسانية"

def images_of(slug):
    d = os.path.join(ROOT, slug, "img")
    return sorted(f for f in os.listdir(d) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))

PAGE = """<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="robots" content="noindex">
<meta name="theme-color" content="#14110d">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cormorant+Garamond:ital,wght@0,500;1,500&display=swap" rel="stylesheet">
<style>
:root{{--bg:#14110d;--ink:#efe6d4;--muted:#a89a80;--line:#3a3226;--gold:#c9a45c}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:var(--bg);color:var(--ink)}}
body{{font-family:"Amiri",serif;min-height:100vh;-webkit-font-smoothing:antialiased}}
header{{text-align:center;padding:48px 20px 28px;border-bottom:1px solid var(--line);max-width:760px;margin:0 auto}}
.book{{font-size:15px;letter-spacing:.08em;color:var(--gold)}}
.orn{{width:56px;height:1px;background:var(--gold);margin:14px auto;opacity:.7}}
h1{{font-family:"Amiri",serif;font-weight:700;font-size:clamp(30px,8vw,46px);line-height:1.3}}
.en{{font-family:"Cormorant Garamond",serif;font-style:italic;font-weight:500;font-size:clamp(19px,4.8vw,24px);color:var(--muted);margin-top:4px;direction:ltr}}
.count{{color:var(--muted);font-size:15px;margin-top:12px}}
main{{max-width:760px;margin:0 auto;padding:24px 16px 64px;display:grid;gap:22px}}
figure{{position:relative;background:#1d1912;border:1px solid var(--line);border-radius:6px;overflow:hidden;cursor:zoom-in;min-height:200px}}
figure img{{display:block;width:100%;height:auto;opacity:0;transition:opacity .4s}}
figure img.ok{{opacity:1}}
figure span{{position:absolute;top:10px;right:10px;background:rgba(20,17,13,.75);color:var(--gold);font-size:14px;padding:2px 10px;border-radius:20px;border:1px solid var(--line)}}
footer{{text-align:center;color:var(--muted);font-size:13px;padding:0 16px 40px}}
#lb{{position:fixed;inset:0;background:#000;display:none;z-index:9;touch-action:pan-y}}
#lb.on{{display:flex;align-items:center;justify-content:center}}
#lb img{{max-width:100vw;max-height:100vh;object-fit:contain;user-select:none;-webkit-user-drag:none}}
#lb button{{position:absolute;background:rgba(0,0,0,.45);color:#fff;border:0;font-size:26px;width:48px;height:48px;border-radius:50%;cursor:pointer}}
#x{{top:max(14px,env(safe-area-inset-top));left:14px}}
#nx{{left:10px;top:50%;transform:translateY(-50%)}}
#pv{{right:10px;top:50%;transform:translateY(-50%)}}
#ct{{position:absolute;bottom:max(16px,env(safe-area-inset-bottom));left:0;right:0;text-align:center;color:#ddd;font-size:16px}}
@media (hover:none){{#nx,#pv{{display:none}}}}
</style>
</head>
<body>
<header>
  <div class="book">{book}</div>
  <div class="orn"></div>
  <h1>{h1}</h1>
  {sub}
  <div class="count">{n} صور · اضغط على أي صورة لتكبيرها</div>
</header>
<main>
{figures}
</main>
<footer>{book}</footer>
<div id="lb" role="dialog" aria-modal="true">
  <img id="lbi" alt="">
  <button id="x" aria-label="إغلاق">✕</button>
  <button id="pv" aria-label="السابق">›</button>
  <button id="nx" aria-label="التالي">‹</button>
  <div id="ct"></div>
</div>
<script>
const big={big};
const lb=document.getElementById('lb'),im=document.getElementById('lbi'),ct=document.getElementById('ct');
let i=0;
function show(k){{i=(k+big.length)%big.length;im.src=big[i];ct.textContent=(i+1)+' من '+big.length;}}
function open_(k){{show(k);lb.classList.add('on');document.body.style.overflow='hidden';}}
function close_(){{lb.classList.remove('on');document.body.style.overflow='';}}
document.querySelectorAll('figure').forEach((f,k)=>f.addEventListener('click',()=>open_(k)));
document.querySelectorAll('figure img').forEach(m=>{{if(m.complete)m.classList.add('ok');m.addEventListener('load',()=>m.classList.add('ok'));}});
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
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cormorant+Garamond:wght@500&display=swap" rel="stylesheet">
<style>
body{{margin:0;background:#14110d;color:#efe6d4;font-family:"Amiri",serif}}
h1{{text-align:center;color:#c9a45c;font-size:30px;padding:48px 16px 24px;margin:0}}
ul{{list-style:none;max-width:560px;margin:0 auto;padding:0 16px 48px}}
li a{{display:block;padding:16px;border-bottom:1px solid #3a3226;color:inherit;text-decoration:none;font-family:"Cormorant Garamond",serif;font-size:22px;direction:ltr;text-align:left}}
</style></head><body><h1>{book}</h1><ul>{items}</ul></body></html>
"""

def main():
    chars = json.load(open(os.path.join(ROOT, "characters.json"), encoding="utf-8"))
    for c in chars:
        c["images"] = images_of(c["slug"])
        figs = "\n".join(
            f'<figure><img src="img/{f}" alt="{html.escape(c["name"])} — {k}" loading="{"eager" if k<3 else "lazy"}"><span>{k}</span></figure>'
            for k, f in enumerate(c["images"], 1))
        page = PAGE.format(
            title=html.escape(c.get("name_ar") or c["name"]) + " — " + BOOK, book=BOOK,
            h1=html.escape(c.get("name_ar") or c["name"]),
            sub=f'<div class="en">{html.escape(c["name"])}</div>' if c.get("name_ar") else "",
            n=len(c["images"]), figures=figs,
            big=json.dumps(["img/" + f for f in c["images"]]))
        os.makedirs(os.path.join(ROOT, c["slug"]), exist_ok=True)
        open(os.path.join(ROOT, c["slug"], "index.html"), "w", encoding="utf-8").write(page)
    items = "".join(f'<li><a href="{c["slug"]}/">{html.escape(c["name"])}</a></li>' for c in chars)
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(INDEX.format(book=BOOK, items=items))
    print("built", len(chars), "pages")

if __name__ == "__main__":
    main()
