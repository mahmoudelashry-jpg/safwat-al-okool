#!/usr/bin/env python3
"""Import one character folder into the site.

Usage: python3 tools/ingest.py <source_folder> [slug]

Source folder holds:
  - one .docx card: paragraph 1 = kicker, 2 = "<Arabic name> و<argument>", 3+ = intro
  - images named "NN [LANG-] caption.jpg"  (LANG: Gr, En, Lat, Ger, IT ... or none)
Writes <slug>/img/NN-<lang>[-k].jpg and upserts the entry in characters.json.
Anything odd is printed as a "!" warning line.
"""
import json, os, re, shutil, sys, zipfile, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK = "حجة صفوة العقول الإنسانية"
AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
IMG_RE = re.compile(r"^(\d+)?\s*(?:([A-Za-z]{2,3})\s*-+\s*)?(.+?)\.(jpe?g|png|webp)$", re.I)
LANG_NORM = {"en": "en", "ent": "en", "gr": "gr", "lat": "la", "la": "la",
             "ger": "de", "de": "de", "it": "it", "fr": "fr"}
# obvious typos in the source folder names
NAME_FIX = {"Immanuel Kan": "Immanuel Kant", "voltaire": "Voltaire"}
# originals first, English translation last
ORDER = {"": 0, "gr": 0, "la": 0, "de": 0, "it": 0, "fr": 0, "en": 2}
# first " و" after the name starts the argument: "أفلاطون وبرهان الحركة"
# prefer the " و" that starts an argument word (so "مونتغمري وات" stays whole)
KW = r"(?:ال)?(?:حجة|حجج|برهان|براهين|دليل|دليلا|طرق|قياس|شهادة|شهادته|بطل)"
SPLIT_KW = re.compile(r"^(.+?)\s+و(" + KW + r"(?:\s.*)?)$")
SPLIT_RE = re.compile(r"^(\S+(?:\s+\S+)*?)\s+و(\S.*)$")


def docx_paragraphs(path):
    if os.path.getsize(path) == 0:
        return []
    x = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
    out = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", x, re.S):
        t = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)).strip()
        if t:
            out.append(t)
    return out


def slugify(folder):
    m = re.match(r"^(\d+)\s+(.*)$", folder)
    num, rest = (m.group(1), m.group(2)) if m else ("", folder)
    rest = unicodedata.normalize("NFKD", rest).encode("ascii", "ignore").decode()
    rest = re.sub(r"[^a-z0-9]+", "-", rest.lower()).strip("-")
    return f"{int(num):02d}-{rest}" if num else rest


def main():
    src = sys.argv[1].rstrip("/")
    folder = os.path.basename(src)
    m = re.match(r"^(\d+)\s+(.*)$", folder)
    num = int(m.group(1))
    name_en = NAME_FIX.get(m.group(2), m.group(2))
    slug = sys.argv[2] if len(sys.argv) > 2 else slugify(f"{m.group(1)} {name_en}")
    warn = []

    files = sorted(os.listdir(src))
    docx = [f for f in files if f.lower().endswith(".docx") and not f.startswith("~$")]
    paras = docx_paragraphs(os.path.join(src, docx[0])) if docx else []
    if not docx:
        warn.append("no Word card")
    elif not paras:
        warn.append("Word card is empty")

    kicker = f"{BOOK} • البطاقة {str(num).translate(AR_DIGITS)}"
    title = paras[1] if len(paras) > 1 else ""
    if paras:
        cm = re.search(r"البطاقة\s*([\d٠-٩]+)", paras[0])
        if cm and int(cm.group(1).translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))) != num:
            warn.append(f"card says «{paras[0]}» but folder is {num}")
    sp = (SPLIT_KW.match(title) or SPLIT_RE.match(title)) if title else None
    name_ar, argument = (sp.group(1).strip(), sp.group(2).strip()) if sp else (title, "")
    if title and not sp:
        warn.append(f"could not split title: {title}")

    sections, loose = {}, []
    for f in files:
        mm = IMG_RE.match(f)
        if not mm:
            continue
        n = int(mm.group(1)) if mm.group(1) else None
        raw = (mm.group(2) or "").lower()
        lang = LANG_NORM.get(raw, raw)
        cap = re.sub(r"\s+", " ", mm.group(3)).strip()
        if n is None:
            loose.append((lang, cap, f))
            continue
        sections.setdefault(n, []).append({"lang": lang, "cap": cap, "src": f})
    for lang, cap, f in loose:
        n = max(sections or {0: 0}) + 1
        sections[n] = [{"lang": lang, "cap": cap, "src": f}]
        warn.append(f"unnumbered image placed as section {n}: {f}")
    if not sections:
        sys.exit(f"{folder}: no images")

    dest = os.path.join(ROOT, slug, "img")
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    out_sections = []
    for n in sorted(sections):
        ims = sorted(sections[n], key=lambda i: (ORDER.get(i["lang"], 1), i["lang"], i["src"]))
        caps = {i["cap"] for i in ims}
        if len(caps) > 1:
            warn.append(f"section {n} has different captions: {' / '.join(sorted(caps))}")
        caption = ims[0]["cap"]
        imgs, seen = [], {}
        for im in ims:
            ext = os.path.splitext(im["src"])[1].lower().replace(".jpeg", ".jpg")
            key = im["lang"] or "x"
            seen[key] = seen.get(key, 0) + 1
            fn = f"{n:02d}-{key}{'' if seen[key] == 1 else '-' + str(seen[key])}{ext}"
            shutil.copyfile(os.path.join(src, im["src"]), os.path.join(dest, fn))
            imgs.append({"lang": im["lang"], "file": fn})
        out_sections.append({"n": n, "caption": caption, "images": imgs})

    entry = {
        "slug": slug, "num": num, "name": name_en, "name_ar": name_ar,
        "argument": argument, "kicker": kicker, "title": title,
        "intro": paras[2:], "sections": out_sections, "warnings": warn,
    }
    jp = os.path.join(ROOT, "characters.json")
    chars = json.load(open(jp, encoding="utf-8")) if os.path.exists(jp) else []
    chars = [c for c in chars if c["slug"] != slug] + [entry]
    chars.sort(key=lambda c: c["num"])
    json.dump(chars, open(jp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    nimg = sum(len(s["images"]) for s in out_sections)
    print(f"{slug}: {len(out_sections)} sections, {nimg} images")
    for w in warn:
        print(f"  ! {w}")


if __name__ == "__main__":
    main()
