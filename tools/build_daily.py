"""Nightly robot: answer pages for Rarely and Squarely up to today (Sydney), hubs, sitemap, robots.txt."""
import sys, os, glob, json, datetime, re; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rarelysite import *  # noqa
W, _ = load()
R = json.load(open(os.path.join(ROOT, "data/rarely.json"))); S = json.load(open(os.path.join(ROOT, "data/squarely.json")))
start = datetime.date.fromisoformat(R["start"]); today = sydney_today()
last = min((today - start).days, len(R["days"]) - 1)
TN = {10: "#9AA0B4", 30: "#3FCB7E", 60: "#4C9BFF", 85: "#B66BFF", 100: "#FFC23D"}
def wpts(p): return 100 if p >= 85 else 85 if p >= 60 else 60 if p >= 35 else 30 if p >= 15 else 10
def answers(pr):
    if pr["type"] == "cat":
        return [(a, p) for a, p in R["cats"][pr["cat"]]["a"].items() if "start" not in pr or a[0] == pr["start"]]
    if pr["type"] == "word":
        return [(w, wpts(W[w])) for w in W if fits(pr["rule"], w)]
    from collections import Counter
    bc = Counter(pr["base"]); return [(w, wpts(W[w])) for w in W if len(w) >= 4 and w != pr["base"] and not (Counter(w) - bc)]
def tchips(items): return '<div class="w">' + "".join(f'<span style="text-transform:capitalize">{esc(a)}<i style="background:{TN[p]}">{p}</i></span>' for a, p in items) + "</div>"
made = []
for d in range(last + 1):
    date = start + datetime.timedelta(days=d); nice = f"{date.day} {date.strftime('%B %Y')}"; path = f"answers/{date.isoformat()}.html"
    body = f'<h1>Rarely #{d+1} answers ({nice})</h1><p class="lead">Spoilers! The rarest answers for every prompt, plus today\'s Squarely word at the bottom.</p><a class="cta" href="../rarely.html">Not played yet? <b>Play first →</b></a>'
    faq = []
    for n, i in enumerate(R["days"][d], 1):
        pr = R["prompts"][i]; al = sorted(answers(pr), key=lambda x: (-x[1], x[0]))
        rare, easy = al[:12], sorted(al, key=lambda x: (x[1], x[0]))[:6]
        link = f'<p><a href="../lists/{R["cats"][pr["cat"]]["slug"]}.html">Full list →</a></p>' if pr["type"] == "cat" else ""
        body += f'<div class="pr"><h3>{n}. {esc(pr["t"])}</h3><b>Rarest answers</b>{tchips(rare)}<details><summary>Easy answers</summary>{tchips(easy)}</details>{link}</div>'
        faq.append((f"Best answer for '{pr['t']}' in Rarely #{d+1}?", f"Top answers: {', '.join(a for a, _ in rare[:5])}."))
    sq = S["answers"][d] if d < len(S["answers"]) else None
    if sq: body += f'<div class="pr"><h3>Squarely #{d+1} word</h3><details><summary>Reveal the word</summary><p style="font-size:28px;letter-spacing:.15em;font-weight:800">{sq.upper()}</p></details></div>'
    nav = ([f'<a href="{(date - datetime.timedelta(days=1)).isoformat()}.html">← #{d}</a>'] if d else []) + ['<a href="../answers.html">All answers</a>'] + ([f'<a href="{(date + datetime.timedelta(days=1)).isoformat()}.html">#{d+2} →</a>'] if d < last else [])
    body += "<div class='links' style='margin-top:20px'>" + "".join(nav) + "</div>"
    write(path, page(path, f"Rarely #{d+1} Answers Today ({nice}) + Squarely Word", f"Rarely #{d+1} answers for {nice}: the rarest answers for all 7 prompts, plus the Squarely word of the day.", body, faq))
    made.append((d, date, path))
body = '<h1>Answers</h1><p class="lead">Rarely answers and the Squarely word for every day. Spoilers!</p><div class="links">' + "".join(f'<a href="{p}">#{d+1} · {dt.day} {dt.strftime("%b %Y")}</a>' for d, dt, p in reversed(made)) + "</div>"
write("answers.html", page("answers.html", "Rarely Answers Today + Squarely Word of the Day", "Today's Rarely answers and Squarely word, plus every past day.", body))
body = '<h1>Squarely past answers</h1><p class="lead">Every previous Squarely word. Today\'s word is hidden until you tap it.</p>'
for d, dt, p in reversed(made):
    w = S["answers"][d]
    body += f'<div class="pr"><h3>#{d+1} · {dt.day} {dt.strftime("%B %Y")}</h3>' + (f'<details><summary>Reveal</summary><b style="letter-spacing:.15em">{w.upper()}</b></details>' if d == last else f'<b style="letter-spacing:.15em">{w.upper()}</b>') + "</div>"
write("squarely-answers.html", page("squarely-answers.html", "Squarely Answer Today + All Past Words", "Today's Squarely answer (hidden until you tap) and every past Squarely word.", body))
urls = ["", "rarely.html", "squarely.html", "quickly.html", "how-to-play.html", "lists.html", "word-lists.html", "answers.html", "squarely-answers.html", "privacy.html"] + [p for _, _, p in made] \
     + sorted("lists/" + os.path.basename(f) for f in glob.glob(os.path.join(ROOT, "lists/*.html"))) + sorted("words/" + os.path.basename(f) for f in glob.glob(os.path.join(ROOT, "words/*.html")))
open(os.path.join(ROOT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{BASE}{u}</loc><lastmod>{today.isoformat()}</lastmod></url>\n" for u in urls) + "</urlset>\n")
open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
json.dump([BASE + p for _, _, p in made[-2:]] + [BASE, BASE + "answers.html", BASE + "squarely-answers.html", BASE + "sitemap.xml"], open(os.path.join(ROOT, "tools/.new_urls.json"), "w"))
print("answer pages:", len(made), "| sitemap:", len(urls))
