"""Category list pages (list-of-fruits.html …) + lists hub + how-to-play. Run once after build_v2.py."""
import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rarelysite import *  # noqa
R = json.load(open(os.path.join(ROOT, "data/rarely.json")))
TN = {10: ("Common", "#9AA0B4"), 30: ("Uncommon", "#3FCB7E"), 60: ("Rare", "#4C9BFF"), 85: ("Epic", "#B66BFF"), 100: ("Legendary", "#FFC23D")}
def tchips(items): return '<div class="w">' + "".join(f'<span style="text-transform:capitalize">{esc(a)}<i style="background:{TN[p][1]}">{p}</i></span>' for a, p in items) + "</div>"
hub = []
for key, c in R["cats"].items():
    noun = c["t"].replace("Name a ", "").replace("Name an ", "").replace(" (one word)", "")
    plural = c["slug"].replace("list-of-", "").replace("-", " ")
    items = sorted(c["a"].items(), key=lambda x: x[0])
    body = f'<h1>List of {esc(plural)}</h1><p class="lead">{len(items)} {esc(plural)}, from the ones everybody knows to the ones almost nobody thinks of. The badge is how many points each one scores in <b>Rarely</b>.</p>'
    body += f'<a class="cta" href="../">🎯 "{esc(c["t"])}" is a real prompt in <b>Rarely</b>, the daily game where rare answers win. <b>Play today →</b></a>'
    for p in (100, 85, 60, 30, 10):
        tier = [x for x in items if x[1] == p]
        if tier: body += f'<h2>{TN[p][0]} {esc(plural)} ({len(tier)})</h2>' + tchips(tier)
    body += f'<h2>All {esc(plural)} A–Z</h2><p class="muted" style="text-transform:capitalize">' + ", ".join(esc(a) for a, _ in items) + "</p>"
    others = [x for x in R["cats"].values() if x is not c][:20]
    body += "<h2>More lists</h2><div class='links'>" + "".join(f'<a href="{o["slug"]}.html">{esc(o["slug"].replace("list-of-","").replace("-"," ").capitalize())}</a>' for o in others) + '<a href="../lists.html">All lists →</a></div>'
    rare = [a for a, p in items if p == 100][:6]; common = [a for a, p in items if p == 10][:4]
    faq = [(f"What are some rare {plural}?", f"Rare {plural} include {', '.join(rare)}."), (f"What are the most common {plural}?", f"The most common are {', '.join(common)}.")]
    write(f"lists/{c['slug']}.html", page(f"lists/{c['slug']}.html", f"List of {plural.title()}: {len(items)} {plural.capitalize()} from Common to Rare | Rarely",
          f"A list of {len(items)} {plural}, sorted from common to rare. Great for trivia, quizzes, word games and Rarely.", body, faq))
    hub.append((c["slug"], plural))
body = '<h1>Lists</h1><p class="lead">Every category in Rarely, from common to rare.</p><div class="links">' + "".join(f'<a href="lists/{s}.html" style="text-transform:capitalize">{esc(p)}</a>' for s, p in sorted(hub, key=lambda x: x[1])) + "</div>"
write("lists.html", page("lists.html", "Lists: Fruits, Animals, Countries, Instruments & More | Rarely", f"{len(hub)} lists of things, from fruits and dog breeds to capital cities and gemstones, sorted from common to rare.", body))
body = """<h1>How to play</h1>
<h2>Rarely</h2><ol><li>7 prompts a day, like <i>Name a fruit</i>. 25 seconds each.</li><li>Type one answer. Rarer answers score more: 10, 30, 60, 85 or 100.</li><li>New prompts every midnight. Unlimited mode never ends.</li></ol>
<p>Example: <b>Name a fruit</b>. <i>apple</i> 10 · <i>mango</i> 30 · <i>papaya</i> 60 · <i>kumquat</i> 85 · <i>carambola</i> 100.</p>
<h2>Squarely</h2><ol><li>Guess the hidden 5-letter word in 6 tries.</li><li>Green: right letter, right spot. Gold: right letter, wrong spot.</li><li>New word every day. Unlimited gives you a fresh word straight away.</li></ol>
<a class="cta" href="./"><b>Play now →</b></a>"""
write("how-to-play.html", page("how-to-play.html", "How to Play Rarely & Squarely", "How to play Rarely (rare answers win) and Squarely (guess the 5-letter word).", body,
      [("How does Rarely scoring work?", "Each answer scores 10, 30, 60, 85 or 100 points depending on how rare it is."), ("How do you play Squarely?", "Guess the hidden 5-letter word in 6 tries. Green means right spot, gold means wrong spot.")]))
print("list pages:", len(hub))
