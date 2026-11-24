"""Builds Rarely's word list (with rarity points), the rule pool and the daily puzzle calendar.
Run once (needs: pip install wordfreq english-words pyspellchecker better_profanity)."""
import json, os, re, random, datetime
import wordfreq
from english_words import get_english_words_set
from spellchecker import SpellChecker
from better_profanity import profanity

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(OUT, exist_ok=True)
MODERN = """selfie emoji emojis hashtag wifi quokka vlog vlogger meme memes app apps smartphone podcast influencer crypto bitcoin unfriend
binge blogger blogging texting gif gifs livestream streamer webcam username password online offline hoodie sneakers emoji latte matcha
smoothie avocado quinoa kale sriracha ramen boba kombucha croissant baguette espresso cappuccino barista tofu sushi burrito nachos
podcaster youtuber tweet tweets retweet unboxing playlist ebook earbuds airfryer vape vaping skateboard snowboard parkour zumba yoga pilates""".split()

def zipf(w): return wordfreq.zipf_frequency(w, "en")
MINZ = 1.2
def points(z):  # rarer word -> more points (1..100)
    return max(1, min(100, round(100 * ((6.6 - z) / (6.6 - MINZ)) ** 2)))

web2_raw = get_english_words_set(["web2"], lower=False, alpha=True)
lower_forms = {w for w in web2_raw if w.islower()}
proper = {w.lower() for w in web2_raw if w[0].isupper()} - lower_forms
classic = get_english_words_set(["web2"], lower=True, alpha=True) & get_english_words_set(["gcide"], lower=True, alpha=True)
sp = set(SpellChecker(language="en").word_frequency.keys())
profanity.load_censor_words()
bad = {str(w).lower() for w in profanity.CENSOR_WORDSET}
extra_bad = {"nigger","nigga","faggot","fag","retard","retarded","spic","chink","kike","tranny","dyke","coon","gook","wetback","cunt","twat","slut","whore","rape","raped","rapist","nazi"}

words = {}
cand = (set(classic) & sp) | {w for w in sp if zipf(w) >= 2.2} | set(MODERN)
for w in cand:
    if not re.fullmatch(r"[a-z]{3,12}", w): continue
    if w in proper and w not in MODERN: continue
    if not re.search("[aeiouy]", w): continue                      # abbreviations like "hts"
    if len(w) <= 3 and w not in classic and w not in MODERN: continue  # odd 3-letter forms
    if w in bad or w in extra_bad or any(b in w for b in extra_bad if len(b) >= 4): continue
    z = zipf(w)
    if z < MINZ and w not in MODERN: continue
    words[w] = points(max(z, MINZ))
print("words:", len(words))

# ---------------- rule pool
L = "abcdefghijklmnopqrstuvwxyz"
rules = []
def add(kind, arg, text, test):
    ans = [w for w in words if test(w)]
    if 40 <= len(ans) <= 4000 and sum(1 for w in ans if words[w] >= 60) >= 6 and sum(1 for w in ans if words[w] <= 20) >= 3:
        rules.append(dict(id=f"{kind}-{arg}", kind=kind, arg=arg, text=text, n=len(ans)))
starts2 = ["qu","ph","kn","gn","wr","sc","sh","th","ch","bl","br","cl","cr","dr","fl","fr","gl","gr","pl","pr","sk","sl","sm","sn","sp","st","sw","tr","tw","wh","oc","un","ex","im","em","al","ab","ad","ap","ar","ob","om","ov","ul","up","ze","zi","yo","ja","jo","ju","ki","ka","va","vi","vo","ga","go","gu","hy","py","sy","ty"]
starts3 = ["scr","spl","str","thr","squ","shr","chr","sph","psy","pho","gno","kni","wre","tra","pre","pro","con","dis","mis","sub","sup","ant","mon","hyp","per","pal","mar","car","bar","cor"]
ends = ["ight","ough","tion","ness","ment","ful","less","ism","ist","ous","ive","able","ible","ery","ory","ary","ock","ack","ick","uck","ump","ink","ank","unk","ench","inch","atch","itch","udge","idge","ze","zz","ox","ax","ix","ex","oo","oon","oom","ool","ula","ola","ina","ino","ano","ato","eau","que","ette","ism","cy","sy","dy","ky","py","wy","zy","ia","ar","or","ian","ese"]
contains = ["oo","ee","zz","ll","ss","ff","pp","rr","tt","x","z","q","j","kn","gh","ph","wh","ae","oe","ui","ua","ya","yo","au","ou","ie","ei","ck","sch","tch","dge","mb","mn","bt","ps","rh","yr","yg","oy","aw","ew","ow","ax","ox","ix","az","oz","iz","eo","io","ia"]
for s in starts2 + starts3: add("start", s, f"Starts with <b>{s.upper()}</b>", lambda w,s=s: w.startswith(s))
for e in ends: add("end", e, f"Ends with <b>{e.upper()}</b>", lambda w,e=e: w.endswith(e) and w != e)
for c in contains: add("has", c, f"Contains <b>{c.upper()}</b>", lambda w,c=c: c in w)
for a in L:
    for n in (4,5,6,7):
        add("lenstart", f"{n}{a}", f"<b>{n} letters</b>, starts with <b>{a.upper()}</b>", lambda w,a=a,n=n: len(w)==n and w[0]==a)
for a in "bcdfghklmnprstw":
    for b in "aeiouy":
        add("startend", f"{a}{b}", f"Starts with <b>{a.upper()}</b>, ends with <b>{b.upper()}</b>", lambda w,a=a,b=b: w[0]==a and w[-1]==b)
for n in (8,9,10):
    for a in "abcdeimprst":
        add("long", f"{n}{a}", f"<b>{n}+ letters</b>, starts with <b>{a.upper()}</b>", lambda w,a=a,n=n: len(w)>=n and w[0]==a)
add("special","2double","Has <b>two different double letters</b> (like baLLOOn)", lambda w: len(set(re.findall(r"(.)\1", w)))>=2)
add("special","novowel","No <b>A, E, I, O or U</b> at all", lambda w: not re.search("[aeiou]", w))
add("special","allvowels","Contains <b>all five vowels</b>", lambda w: all(v in w for v in "aeiou"))
add("special","threevowelsrow","Has <b>3 vowels in a row</b>", lambda w: re.search("[aeiou]{3}", w) is not None)
add("special","4consonants","Has <b>4 consonants in a row</b>", lambda w: re.search("[^aeiouy]{4}", w) is not None)
add("special","onevowel7","<b>7+ letters</b> with only <b>one vowel</b> type", lambda w: len(w)>=7 and len(set(re.findall("[aeiou]", w)))==1)
add("special","zandq","Contains both <b>Z</b> and <b>E</b>, no <b>A</b>", lambda w: "z" in w and "e" in w and "a" not in w)
add("special","kx","Contains <b>K</b> and ends with <b>Y</b>", lambda w: "k" in w and w.endswith("y"))
add("special","doubleo_end","Ends with a <b>double letter</b>", lambda w: len(w)>3 and w[-1]==w[-2])
add("special","samestartend","<b>Starts and ends</b> with the same letter", lambda w: len(w)>=5 and w[0]==w[-1])
add("special","alternating","Letters alternate <b>consonant-vowel</b> (like PoTaTo), 6+ letters", lambda w: len(w)>=6 and all((c in "aeiou")!=(w[i+1] in "aeiou") for i,c in enumerate(w[:-1])))
print("rules:", len(rules))

# ---------------- daily calendar: 7 rules a day, mixed kinds, easy -> hard, no repeats within 60 days
rng = random.Random(20261124)
START = datetime.date(2026, 11, 24)
by_kind = {}
for i,r in enumerate(rules): by_kind.setdefault(r["kind"], []).append(i)
def key(r):  # first letter a prompt revolves around, to keep each day varied
    letters = re.sub(r"[^a-z]", "", r["arg"]) if r["kind"] != "special" else r["arg"]
    return letters[:1] if r["kind"] in ("start","lenstart","startend","long") else r["kind"] + r["arg"]
recent = []; days = []
for d in range(800):
    picked = []
    kinds = ["start","end","has","lenstart","startend","long","special"]
    rng.shuffle(kinds)
    for k in kinds:
        used = {key(rules[j]) for j in picked}
        opts = [i for i in by_kind.get(k, []) if i not in recent and i not in picked and key(rules[i]) not in used] or [i for i in by_kind.get(k, []) if key(rules[i]) not in used] or by_kind.get(k, [])
        if opts: picked.append(rng.choice(opts))
    while len(picked) < 7:
        i = rng.randrange(len(rules))
        if i not in picked: picked.append(i)
    picked = sorted(picked[:7], key=lambda i: -rules[i]["n"])   # most answers first (easiest)
    days.append(picked)
    recent = (recent + picked)[-420:]
json.dump({"start": START.isoformat(), "rules": rules, "days": days}, open(os.path.join(OUT, "puzzles.json"), "w"), separators=(",",":"))
buckets = {}
for w,p in words.items(): buckets.setdefault(p, []).append(w)
json.dump({str(p): " ".join(sorted(ws)) for p,ws in sorted(buckets.items())}, open(os.path.join(OUT, "words.json"), "w"), separators=(",",":"))
print("sizes:", os.path.getsize(os.path.join(OUT,"words.json"))//1024, "KB words;", os.path.getsize(os.path.join(OUT,"puzzles.json"))//1024, "KB puzzles")
