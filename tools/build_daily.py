"""Daily robot: builds the answers page for every day up to today (Sydney time), the answers hub,
sitemap.xml and robots.txt. Run by .github/workflows/daily.yml just after midnight."""
import sys, os, glob; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rarelysite import *  # noqa
import datetime, json

W, P = load()
start = datetime.date.fromisoformat(P["start"])
today = sydney_today()
last = min((today - start).days, len(P["days"]) - 1)
made = []
for d in range(0, last + 1):
    date = start + datetime.timedelta(days=d)
    path = f"answers/{date.isoformat()}.html"
    nice = f"{date.day} {date.strftime('%B %Y')}"
    body = f'<h1>Rarely #{d+1} answers: {nice}</h1><p class="lead">Spoilers ahead! The best answers for every prompt in Rarely #{d+1}, from the rarest (highest score) to the easiest.</p>'
    body += f'<a class="cta" href="../?day={d+1}">Haven\'t played yet? <b>Play Rarely #{d+1} first →</b></a>'
    faq = []
    for n, i in enumerate(P["days"][d], 1):
        r = P["rules"][i]; slug, title, short = page_info(r)
        ans = [w for w in W if fits(r, w)]
        rare = sorted(ans, key=lambda w: (-W[w], w))[:12]
        easy = sorted(ans, key=lambda w: (W[w], w))[:6]
        txt = re.sub("<.*?>", "", r["text"])
        body += f'<div class="pr"><h3>Prompt {n}: {r["text"]}</h3><p class="muted">{len(ans):,} possible answers.</p><b>Rarest answers</b>{chips(rare, W)}'
        body += f'<details><summary>Easy answers (low score)</summary>{chips(easy, W)}</details><p><a href="../words/{slug}.html">See all {esc(short)} →</a></p></div>'
        faq.append((f"What is the best answer for '{txt}' in Rarely #{d+1}?", f"The rarest answers are {', '.join(rare[:5])}. Easy answers include {', '.join(easy[:3])}."))
    nav = []
    if d > 0: nav.append(f'<a href="{(date - datetime.timedelta(days=1)).isoformat()}.html">← Rarely #{d}</a>')
    nav.append('<a href="../answers.html">All answers</a>')
    if d < last: nav.append(f'<a href="{(date + datetime.timedelta(days=1)).isoformat()}.html">Rarely #{d+2} →</a>')
    body += "<div class='links' style='margin-top:24px'>" + "".join(nav) + "</div>"
    write(path, page(path, f"Rarely #{d+1} Answers Today ({nice}) | Best Rare Words",
                     f"Rarely #{d+1} answers for {nice}: the rarest, highest-scoring words for all 7 prompts, plus easy answers.", body, faq))
    made.append((d, date, path))

body = '<h1>Rarely answers</h1><p class="lead">The rarest answers for every daily Rarely puzzle. Spoilers, so play first!</p><div class="links">'
body += "".join(f'<a href="{p}">#{d+1} · {dt.day} {dt.strftime("%b %Y")}</a>' for d, dt, p in reversed(made)) + "</div>"
write("answers.html", page("answers.html", "Rarely Answers: Today's and All Past Puzzles", "Answers for today's Rarely puzzle and every past daily puzzle: the rarest, highest-scoring words for each prompt.", body))

urls = ["", "how-to-play.html", "word-lists.html", "answers.html", "privacy.html"] + [p for _, _, p in made] + sorted("words/" + os.path.basename(f) for f in glob.glob(os.path.join(ROOT, "words/*.html")))
open(os.path.join(ROOT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{BASE}{u}</loc><lastmod>{today.isoformat()}</lastmod></url>\n" for u in urls) + "</urlset>\n")
open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
json.dump([BASE + p for _, _, p in made[-2:]] + [BASE, BASE + "answers.html", BASE + "sitemap.xml"], open(os.path.join(ROOT, "tools/.new_urls.json"), "w"))
print("answer pages:", len(made), "| sitemap urls:", len(urls))
