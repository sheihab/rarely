"""Builds Rarely v2 ('Name a…' prompts) and Squarely data.
Outputs data/rarely.json and data/squarely.json. Needs data/words.json (from build_data.py)."""
import json, os, re, random, datetime, unicodedata, sys
import wordfreq
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from categories import CATS
from spellchecker import SpellChecker
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
W = {}
for p, ws in json.load(open(os.path.join(ROOT, "data/words.json"))).items():
    for w in ws.split(): W[w] = int(p)
old = json.load(open(os.path.join(ROOT, "data/puzzles.json")))   # letter-pattern rules from v1

def norm(s):
    s = unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()
    s = s.replace("&", " and ").replace("'", "").replace("-", " ")
    s = re.sub(r"[^a-z0-9 ]", " ", s); s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"^the ", "", s)
TIERS = [(0.12, 10), (0.35, 30), (0.65, 60), (0.90, 85), (1.01, 100)]
def tierpts(frac): return next(p for f, p in TIERS if frac < f)

cats = {}
for key, (prompt, slug, raw) in CATS.items():
    items = sorted({norm(x) for x in raw.split(",") if norm(x)})
    def zf(a):  # phrases: take the rarest word, minus a bit (two-word names are rarer than their parts)
        parts = a.split()
        return wordfreq.zipf_frequency(a, "en") if len(parts) == 1 else min(wordfreq.zipf_frequency(p, "en") for p in parts) - 1.5
    z = {a: zf(a) for a in items}
    order = sorted(items, key=lambda a: (-z[a], a))
    n = len(order)
    pts = {a: tierpts(i / max(1, n - 1)) for i, a in enumerate(order)}
    cats[key] = {"t": prompt, "slug": slug, "a": pts}
print("categories:", len(cats), "answers:", sum(len(c["a"]) for c in cats.values()))

prompts = []
for key, c in cats.items():
    prompts.append({"type": "cat", "cat": key, "t": c["t"]})
    if len(c["a"]) >= 70:   # letter variants for big categories
        first = {}
        for a in c["a"]: first.setdefault(a[0], []).append(a)
        for L, lst in sorted(first.items()):
            if len(lst) >= 8 and L.isalpha():
                prompts.append({"type": "cat", "cat": key, "start": L, "t": f'{c["t"]} starting with {L.upper()}'})
n_cat = len(prompts)
# word prompts from v1 letter rules (rewritten in 'Name a…' style)
for i, r in enumerate(old["rules"]):
    if r["kind"] in ("start", "end", "has", "startend", "special"):
        txt = re.sub("<.*?>", "", r["text"])
        t = "Name a word that " + txt[0].lower() + txt[1:] if r["kind"] != "special" else "Name a word that " + {
            "2double":"has two different double letters","novowel":"has no A, E, I, O or U","allvowels":"contains all five vowels",
            "threevowelsrow":"has 3 vowels in a row","4consonants":"has 4 consonants in a row","onevowel7":"has 7+ letters and only one kind of vowel",
            "zandq":"contains Z and E but no A","kx":"contains K and ends with Y","doubleo_end":"ends with a double letter",
            "samestartend":"starts and ends with the same letter (5+ letters)","alternating":"alternates consonant and vowel (6+ letters)"}[r["arg"]]
        t = t.replace("that starts with", "starting with").replace("that ends with", "ending in").replace("that contains", "containing")
        prompts.append({"type": "word", "rule": r, "t": t})
n_word = len(prompts) - n_cat
# anagram prompts: common 7-9 letter words with plenty of sub-words
from collections import Counter
def subwords(base):
    bc = Counter(base)
    return [w for w in W if 4 <= len(w) < len(base) + 1 and w != base and not (Counter(w) - bc)]
bases = [w for w in W if 7 <= len(w) <= 9 and W[w] <= 25 and len(set(w)) >= 6]
random.Random(7).shuffle(bases)
ana = 0
for b in bases:
    if ana >= 160: break
    sw = subwords(b)
    if 25 <= len(sw) <= 400:
        prompts.append({"type": "ana", "base": b, "t": f"Name a 4+ letter word using only the letters in {b.upper()}"}); ana += 1
print("prompts:", len(prompts), "(cat", n_cat, "word", n_word, "anagram", ana, ")")

# daily schedule: 5 category prompts (5 different categories) + 1 word + 1 anagram
rng = random.Random(20261124)
cat_idx = [i for i, p in enumerate(prompts) if p["type"] == "cat"]
word_idx = [i for i, p in enumerate(prompts) if p["type"] == "word"]
ana_idx = [i for i, p in enumerate(prompts) if p["type"] == "ana"]
recent, days = [], []
for d in range(800):
    day, used = [], set()
    keys = list(cats); rng.shuffle(keys)
    for k in keys:
        if len(day) == 5: break
        opts = [i for i in cat_idx if prompts[i]["cat"] == k and i not in recent]
        if not opts: continue
        base = [i for i in opts if "start" not in prompts[i]]
        var = [i for i in opts if "start" in prompts[i]]
        pick = rng.choice(base) if base and (not var or rng.random() < 0.6) else rng.choice(var)
        day.append(pick)
    day.insert(2, rng.choice([i for i in word_idx if i not in recent] or word_idx))
    day.insert(5, rng.choice([i for i in ana_idx if i not in recent] or ana_idx))
    days.append(day); recent = (recent + day)[-300:]
json.dump({"start": "2026-11-24", "cats": cats, "prompts": prompts, "days": days},
          open(os.path.join(ROOT, "data/rarely.json"), "w"), separators=(",", ":"))

# ---------------- Squarely
sp = {w for w in SpellChecker(language="en").word_frequency.keys() if re.fullmatch("[a-z]{5}", w)}
valid = sorted({w for w in W if len(w) == 5} | {w for w in sp if wordfreq.zipf_frequency(w, "en") >= 1.5})
from english_words import get_english_words_set
classic = get_english_words_set(["web2"], lower=True, alpha=True) & get_english_words_set(["gcide"], lower=True, alpha=True)
web2raw = get_english_words_set(["web2"], lower=False, alpha=True)
capital_only = {w.lower() for w in web2raw if w[0].isupper()} - {w for w in web2raw if w.islower()}
ans = [w for w in W if len(w) == 5 and w in classic and w not in capital_only and wordfreq.zipf_frequency(w, "en") >= 3.4 and not (w.endswith("s") and not w.endswith("ss"))
       and not w.endswith("ed") and len(set(w)) >= 3]
NAMES = set("maria peter james david sarah linda susan karen laura emily jason kevin brian simon diana helen julia jenny harry donna sally nancy betty clive royce allen ellen frank henry jimmy johnny kelly larry marie mason nigel oscar paula ralph roger sandy sonia steve tracy wendy willy julie annie billy bobby carol cindy danny debra derek doris irene janet jesse jerry joyce keith lucas marco moses norma pedro perry rocky ronny ryder tommy vince".split())
ans = sorted(set(ans) - NAMES); random.Random(424242).shuffle(ans)
json.dump({"start": "2026-11-24", "answers": ans, "valid": " ".join(valid)}, open(os.path.join(ROOT, "data/squarely.json"), "w"), separators=(",", ":"))
for f in ("rarely.json", "squarely.json"): print(f, os.path.getsize(os.path.join(ROOT, "data", f)) // 1024, "KB")
print("squarely answers:", len(ans), "valid:", len(valid))
