"""Shared helpers for Rarely's static pages."""
import json, os, re, html, datetime
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BASE = "https://sheihab.github.io/rarely/"
esc = html.escape

def load():
    W = {}
    for p, ws in json.load(open(os.path.join(ROOT, "data/words.json"))).items():
        for w in ws.split(): W[w] = int(p)
    P = json.load(open(os.path.join(ROOT, "data/puzzles.json")))
    return W, P

def fits(rule, w):
    k, a = rule["kind"], rule["arg"]
    if k == "start": return w.startswith(a)
    if k == "end": return w.endswith(a) and w != a
    if k == "has": return a in w
    if k == "lenstart": return len(w) == int(a[:-1]) and w[0] == a[-1]
    if k == "long": return len(w) >= int(a[:-1]) and w[0] == a[-1]
    if k == "startend": return w[0] == a[0] and w[-1] == a[1]
    v = "aeiou"
    return {
        "2double": lambda: len(set(re.findall(r"(.)\1", w))) >= 2,
        "novowel": lambda: not re.search("[aeiou]", w),
        "allvowels": lambda: all(c in w for c in v),
        "threevowelsrow": lambda: re.search("[aeiou]{3}", w) is not None,
        "4consonants": lambda: re.search("[^aeiouy]{4}", w) is not None,
        "onevowel7": lambda: len(w) >= 7 and len(set(re.findall("[aeiou]", w))) == 1,
        "zandq": lambda: "z" in w and "e" in w and "a" not in w,
        "kx": lambda: "k" in w and w.endswith("y"),
        "doubleo_end": lambda: len(w) > 3 and w[-1] == w[-2],
        "samestartend": lambda: len(w) >= 5 and w[0] == w[-1],
        "alternating": lambda: len(w) >= 6 and all((c in v) != (w[i+1] in v) for i, c in enumerate(w[:-1])),
    }.get(a, lambda: False)()

SPECIAL = {
    "2double": ("words-with-two-double-letters", "Words With Two Double Letters", "words with two different double letters, like balloon or bookkeeper"),
    "novowel": ("words-with-no-vowels", "Words With No Vowels", "words with no A, E, I, O or U"),
    "allvowels": ("words-with-all-five-vowels", "Words With All Five Vowels", "words that contain A, E, I, O and U"),
    "threevowelsrow": ("words-with-three-vowels-in-a-row", "Words With Three Vowels in a Row", "words with three vowels in a row"),
    "4consonants": ("words-with-four-consonants-in-a-row", "Words With Four Consonants in a Row", "words with four consonants in a row"),
    "onevowel7": ("long-words-with-one-vowel", "Long Words With Only One Vowel", "words of 7+ letters that use only one kind of vowel"),
    "zandq": ("words-with-z-and-e-but-no-a", "Words With Z and E but No A", "words containing Z and E but no A"),
    "kx": ("words-with-k-ending-in-y", "Words With K That End in Y", "words that contain K and end in Y"),
    "doubleo_end": ("words-ending-in-double-letters", "Words Ending in Double Letters", "words that end with a double letter"),
    "samestartend": ("words-that-start-and-end-with-the-same-letter", "Words That Start and End With the Same Letter", "words that start and end with the same letter"),
    "alternating": ("words-with-alternating-consonants-and-vowels", "Words That Alternate Consonants and Vowels", "words of 6+ letters that alternate consonant, vowel, consonant (like potato)"),
}
def page_info(rule):
    """slug, title, short description for a rule's word-list page"""
    k, a = rule["kind"], rule["arg"]; U = a.upper()
    if k == "start": return f"words-that-start-with-{a}", f"Words That Start With {U}", f"words that start with {U}"
    if k == "end": return f"words-that-end-with-{a}", f"Words That End With {U}", f"words that end with {U}"
    if k == "has": return f"words-containing-{a}", f"Words Containing {U}", f"words containing {U}"
    if k == "lenstart": n, c = a[:-1], a[-1].upper(); return f"{n}-letter-words-starting-with-{a[-1]}", f"{n} Letter Words Starting With {c}", f"{n}-letter words starting with {c}"
    if k == "long": n, c = a[:-1], a[-1].upper(); return f"long-words-starting-with-{a[-1]}-{n}-plus-letters", f"Long Words Starting With {c} ({n}+ Letters)", f"words of {n} or more letters starting with {c}"
    if k == "startend": return f"words-that-start-with-{a[0]}-and-end-with-{a[1]}", f"Words That Start With {a[0].upper()} and End With {a[1].upper()}", f"words that start with {a[0].upper()} and end with {a[1].upper()}"
    return SPECIAL[a]

TIER = [(85,"Legendary","#FFC23D"),(60,"Epic","#B66BFF"),(35,"Rare","#4C9BFF"),(15,"Uncommon","#3FCB7E"),(1,"Common","#9AA0B4")]
def tier(p): return next(t for t in TIER if p >= t[0])

CSS = """*{box-sizing:border-box;min-width:0}body{margin:0;background:#14121F;color:#F4F1FF;font:17px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;overflow-x:clip}
a{color:#FFC23D}main{max-width:780px;margin:0 auto;padding:10px 18px 60px}
.top{display:flex;justify-content:space-between;align-items:center;max-width:780px;margin:0 auto;padding:14px 18px;border-bottom:1px solid #363056}
.logo{font:800 22px "Avenir Next",Futura,"Segoe UI",sans-serif;color:#F4F1FF;text-decoration:none;display:flex;gap:8px;align-items:center}
.play{background:#FFC23D;color:#1B1530;text-decoration:none;font-weight:800;border-radius:12px;padding:10px 16px;font-size:15px}
h1,h2,h3{font-family:"Avenir Next",Futura,"Segoe UI",sans-serif;line-height:1.2}h1{font-size:clamp(28px,6vw,40px);margin:20px 0 8px}h2{font-size:23px;margin:34px 0 10px}h3{font-size:18px;margin:22px 0 8px;color:#A9A3C7}
.lead{color:#A9A3C7;font-size:18px}.muted{color:#A9A3C7}
.cta{display:block;background:#1E1B2E;border:1px solid #363056;border-radius:18px;padding:18px 20px;margin:22px 0;text-decoration:none;color:#F4F1FF}
.cta b{color:#FFC23D}
.w{display:flex;flex-wrap:wrap;gap:8px}.w span{background:#1E1B2E;border:1px solid #363056;border-radius:10px;padding:5px 10px;font-size:15px}
.w span i{font-style:normal;font-size:12px;font-weight:800;color:#14121F;border-radius:999px;padding:1px 6px;margin-left:6px}
.links{display:flex;flex-wrap:wrap;gap:8px}.links a{background:#1E1B2E;border:1px solid #363056;border-radius:999px;padding:6px 12px;font-size:14px;text-decoration:none;color:#F4F1FF}
.pr{background:#1E1B2E;border:1px solid #363056;border-radius:16px;padding:16px 18px;margin:14px 0}.pr h3{margin:0 0 10px;color:#F4F1FF}.pr h3 b{color:#FFC23D}
details{margin-top:10px}summary{cursor:pointer;color:#A9A3C7}
footer{text-align:center;color:#A9A3C7;font-size:13px;padding:24px}footer a{color:#A9A3C7}"""

def page(path, title, desc, body, faq=None, extra_ld=None):
    url = BASE + path
    ld = [{"@context":"https://schema.org","@type":"WebPage","name":title.split(" | ")[0],"description":desc,"url":url}]
    if faq: ld.append({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]})
    if extra_ld: ld.append(extra_ld)
    depth = path.count("/"); up = "../" * depth
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}og-image.png"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{up}icon.svg" type="image/svg+xml"><meta name="theme-color" content="#14121F">
<script type="application/ld+json">{json.dumps(ld)}</script><style>{CSS}</style></head><body>
<div class="top"><a class="logo" href="{up}"><svg width="20" height="20" viewBox="0 0 24 24"><path d="M6 3h12l4 6-10 12L2 9z" fill="#FFC23D"/></svg>Rarely</a><a class="play" href="{up}">Play free games</a></div>
<main>{body}</main>
<footer><a href="{up}rarely.html">Rarely</a> · <a href="{up}squarely.html">Squarely</a> · <a href="{up}quickly.html">Quickly</a> · <a href="{up}lists.html">Lists</a> · <a href="{up}word-lists.html">Word lists</a> · <a href="{up}answers.html">Answers</a> · <a href="{up}privacy.html">Privacy</a></footer></body></html>"""

def write(path, content):
    full = os.path.join(ROOT, path); os.makedirs(os.path.dirname(full) or ROOT, exist_ok=True)
    open(full, "w").write(content)

def chips(words, W):
    return '<div class="w">' + "".join(f'<span>{w}<i style="background:{tier(W[w])[2]}">{W[w]}</i></span>' for w in words) + "</div>"

def sydney_today():
    return (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=11)).date()
