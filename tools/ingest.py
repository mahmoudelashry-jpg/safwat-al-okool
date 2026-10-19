#!/usr/bin/env python3
"""Import one character folder into the site.

Usage: python3 tools/ingest.py <source_folder> [slug]

Source folder holds:
  - one .docx card: paragraph 1 = kicker, 2 = title, 3+ = intro
  - images named "NN <LANG>- caption.jpg"  (LANG: Gr, En, Ar, La, De, Fr ...)
Writes <slug>/img/NN-<lang>.jpg and upserts the entry in characters.json.
"""
import json, os, re, shutil, sys, zipfile, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_RE = re.compile(r"^(\d+)\s*([A-Za-z]{2,3})\s*-\s*(.+?)\.(jpe?g|png|webp)$", re.I)
# original-language codes sort before translations
# "إكسينوفان الكولوفوني وحجة التنزيه" -> name / "حجة التنزيه"
SPLIT_RE = re.compile(r"^(.+?)\s+و((?:حجة|برهان|دليل)\b.*)$")
ORDER = {"gr": 0, "la": 0, "ar": 0, "he": 0, "de": 1, "fr": 1, "en": 2}


def docx_paragraphs(path):
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
    m = re.match(r"^\d+\s+(.*)$", folder)
    name_en = m.group(1) if m else folder
    slug = sys.argv[2] if len(sys.argv) > 2 else slugify(folder)

    files = os.listdir(src)
    docx = [f for f in files if f.lower().endswith(".docx") and not f.startswith("~$")]
    if len(docx) != 1:
        sys.exit(f"{folder}: expected one .docx, found {docx}")
    paras = docx_paragraphs(os.path.join(src, docx[0]))
    if len(paras) < 2:
        sys.exit(f"{folder}: card has fewer than 2 lines")

    sections = {}
    skipped = []
    for f in files:
        mm = IMG_RE.match(f)
        if not mm:
            if not f.lower().endswith(".docx"):
                skipped.append(f)
            continue
        n, lang, cap = int(mm.group(1)), mm.group(2).lower(), mm.group(3).strip()
        sections.setdefault(n, {"n": n, "caption": cap, "images": []})
        sections[n]["images"].append({"lang": lang, "src": f})
    if not sections:
        sys.exit(f"{folder}: no images matched")

    dest = os.path.join(ROOT, slug, "img")
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    out_sections = []
    for n in sorted(sections):
        s = sections[n]
        s["images"].sort(key=lambda i: (ORDER.get(i["lang"], 1), i["lang"]))
        imgs = []
        for im in s["images"]:
            ext = os.path.splitext(im["src"])[1].lower().replace(".jpeg", ".jpg")
            fn = f"{n:02d}-{im['lang']}{ext}"
            shutil.copyfile(os.path.join(src, im["src"]), os.path.join(dest, fn))
            imgs.append({"lang": im["lang"], "file": fn})
        out_sections.append({"n": n, "caption": s["caption"], "images": imgs})

    title = paras[1]
    sp = SPLIT_RE.match(title)
    name_ar, argument = (sp.group(1).strip(), sp.group(2).strip()) if sp else (title, "")
    if not sp:
        print(f"  ! {folder}: could not split title into name + argument: {title}")
    entry = {
        "slug": slug,
        "name": name_en,
        "name_ar": name_ar,
        "argument": argument,
        "kicker": paras[0],
        "title": title,
        "intro": paras[2:],
        "sections": out_sections,
    }
    jp = os.path.join(ROOT, "characters.json")
    chars = json.load(open(jp, encoding="utf-8")) if os.path.exists(jp) else []
    chars = [c for c in chars if c["slug"] != slug] + [entry]
    chars.sort(key=lambda c: int(c["slug"].split("-")[0]))
    json.dump(chars, open(jp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"{slug}: {len(out_sections)} sections, {sum(len(s['images']) for s in out_sections)} images"
          + (f", skipped {skipped}" if skipped else ""))


if __name__ == "__main__":
    main()
