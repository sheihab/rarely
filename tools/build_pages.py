"""Builds the static SEO pages: one word-list page per prompt type, word-list hub, how-to-play, privacy.
Run: python3 tools/build_pages.py"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rarelysite import *  # noqa
import collections

W, P = load()
rules = P["rules"]
KIND_TITLE = {"start":"Words that start with…","end":"Words that end with…","has":"Words containing…","lenstart":"Words by length and first letter",
              "long":"Long words by first letter","startend":"Words by first and last letter","special":"Tricky word lists"}
pages = []
for r in rules:
    slug, title, short = page_info(r)
    ans = sorted([w for w in W if fits(r, w)])
    rare = sorted(ans, key=lambda w: (-W[w], w))[:15]
    common = sorted(ans, key=lambda w: (W[w], w))[:15]
    bylen = collections.defaultdict(list)
    for w in ans: bylen[len(w)].append(w)
    body = f'<h1>{esc(title)}</h1><p class="lead">We found <b>{len(ans):,}</b> {esc(short)}. The number next to each word is its <b>Rarely score</b>: the rarer the word, the higher the score.</p>'
    body += f'<a class="cta" href="../">🎯 This is a real prompt in <b>Rarely</b>, the daily word game where rare answers win. <b>Play today\'s puzzle →</b></a>'
    body += f'<h2>Rarest {esc(short)}</h2><p class="muted">Use these to impress in word games.</p>{chips(rare, W)}'
    body += f'<h2>Most common {esc(short)}</h2>{chips(common, W)}'
    body += f'<h2>All {esc(short)}, by length</h2>'
    for n in sorted(bylen):
        lst = bylen[n]; show = lst[:150]
        body += f'<h3>{n}-letter words ({len(lst)})</h3>' + chips(show, W)
        if len(lst) > 150: body += f'<p class="muted">…and {len(lst)-150} more.</p>'
    same = [x for x in rules if x["kind"] == r["kind"] and x is not r][:18]
    body += "<h2>More word lists</h2><div class='links'>" + "".join(f'<a href="{page_info(x)[0]}.html">{esc(page_info(x)[1])}</a>' for x in same) + '<a href="../word-lists.html">All word lists →</a></div>'
    faq = [(f"How many {short} are there?", f"Our list has {len(ans):,} {short}, from common words like {', '.join(common[:3])} to rare ones like {', '.join(rare[:3])}."),
           (f"What are some rare {short}?", f"Some of the rarest are {', '.join(rare[:8])}.")]
    desc = f"{len(ans):,} {short}, sorted by length, with the rarest and most common highlighted. Great for Scrabble, Wordle, crosswords and Rarely."
    write(f"words/{slug}.html", page(f"words/{slug}.html", f"{title} ({len(ans):,} Words) | Rarely", desc, body, faq))
    pages.append((r["kind"], slug, title, len(ans)))

# hub
body = '<h1>Word lists</h1><p class="lead">Every list below is a real prompt type in Rarely. Browse them for ideas, or for Scrabble, Wordle and crossword help.</p>'
for k, t in KIND_TITLE.items():
    items = [p for p in pages if p[0] == k]
    if not items: continue
    body += f"<h2>{t}</h2><div class='links'>" + "".join(f'<a href="words/{s}.html">{esc(ti)}</a>' for _, s, ti, _ in sorted(items, key=lambda x: x[2])) + "</div>"
write("word-lists.html", page("word-lists.html", "Word Lists: Words by Letters, Length and Pattern | Rarely",
      f"{len(pages)} word lists: words that start with, end with or contain any letters, words by length, words with no vowels and more.", body))

# how to play
body = """<h1>How to play Rarely</h1><p class="lead">Rarely is a free daily word game. The twist: <b>the rarer your word, the more points you score.</b></p>
<h2>The rules</h2><ol><li>Every day there are <b>7 prompts</b>, the same for everyone, like <i>"Starts with QU"</i> or <i>"Contains Z"</i>.</li>
<li>For each prompt, type <b>one real English word</b> that fits.</li><li>Your word scores <b>1–100 points</b> depending on how rare it is in everyday English.</li>
<li>Add up all 7 for your daily score, out of 700.</li><li>A new puzzle arrives at midnight. Come back daily to build your streak.</li></ol>
<h2>Rarity tiers</h2><div class="w"><span>Common <i style="background:#9AA0B4">1–14</i></span><span>Uncommon <i style="background:#3FCB7E">15–34</i></span><span>Rare <i style="background:#4C9BFF">35–59</i></span><span>Epic <i style="background:#B66BFF">60–84</i></span><span>Legendary <i style="background:#FFC23D">85–100</i></span></div>
<h2>Example</h2><p>Prompt: <b>Starts with QU</b>. """ + " ".join(f"<i>{w}</i> scores {W[w]} ({tier(W[w])[1].lower()})." for w in ["quiet","quota","quiver","quiddity"]) + """</p>
<h2>Tips for high scores</h2><ul><li>Think of science, nature and old-fashioned words: animals, plants, minerals, instruments.</li><li>Longer words are often rarer, but not always.</li><li>Skip a prompt if you're stuck (0 points) rather than burning time.</li><li>After each answer we show the rarest possible word, so you learn as you play.</li></ul>
<h2>Other modes</h2><p><b>Unlimited</b> gives you endless random rounds. The <b>Archive</b> lets you play every past daily puzzle.</p>
<a class="cta" href="./"><b>Play today's puzzle →</b></a>"""
write("how-to-play.html", page("how-to-play.html", "How to Play Rarely: Rules, Scoring & Tips", "How Rarely works: 7 daily word prompts, rarer words score more, up to 700 points a day. Rules, rarity tiers and tips.", body,
      [("How does Rarely scoring work?", "Each answer scores 1 to 100 points based on how rare the word is in everyday English. Common words score low, rare words score high."),
       ("When does a new Rarely puzzle come out?", "Every day at midnight, your local time.")]))

# privacy
body = """<h1>Privacy</h1><p>Rarely needs no account. Your scores, streak and progress are stored only in your own browser.</p>
<p>We may show ads from Google AdSense to keep the game free. Google and its partners may use cookies to show ads based on your visits to this and other sites. You can turn off personalised ads at <a href="https://adssettings.google.com">Google Ads Settings</a>, and see <a href="https://policies.google.com/technologies/ads">how Google uses data</a>.</p>
<p>Word frequency data comes from the open-source <i>wordfreq</i> project.</p>"""
write("privacy.html", page("privacy.html", "Privacy | Rarely", "Rarely privacy policy: no account, data stays on your device.", body))
print("word-list pages:", len(pages))
