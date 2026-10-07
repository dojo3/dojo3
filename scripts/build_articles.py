"""Build sound-site reading pages from the preserved Kirsten Antony archive."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://soundhealingcolorado.com/'
ARCHIVE = 'https://coloradofootcarenurse.com/'
ARTICLES = json.loads((ROOT / 'data/articles.json').read_text())
def esc(s): return html.escape(str(s), quote=True)
def page(title, description, path, body, article=None):
    prefix = '../' if path.startswith('articles/') else ''
    canonical = ARCHIVE + path if article else BASE + path
    schema = {'@context':'https://schema.org','@type':'Article' if article else 'CollectionPage','name':title,'url':canonical,'author':{'@type':'Person','name':'Kirsten Antony','honorificSuffix':'RN','url':ARCHIVE+'about.html'}}
    if article:
        schema.update(headline=article['title'],datePublished=article['date'],articleSection=article['category'],mainEntityOfPage=canonical)
    else:
        schema['mainEntity']={'@type':'ItemList','numberOfItems':len(ARTICLES),'itemListElement':[{'@type':'ListItem','position':i+1,'name':a['title'],'url':BASE+'articles/'+a['slug']+'.html'} for i,a in enumerate(ARTICLES)]}
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Colorado Sound Healing</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{canonical}"><meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><meta name="author" content="Kirsten Antony, RN"><link rel="icon" href="{prefix}assets/img/favi.png"><link rel="stylesheet" href="{prefix}assets/css/articles.css"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False).replace('</','<\\/')}</script></head><body><a class="skip" href="#main">Skip to article content</a><header><a class="brand" href="{prefix}index.html">Colorado Sound Healing</a><nav aria-label="Main navigation"><a href="{prefix}articles.html">Articles</a><a href="{prefix}index.html#services">Sessions</a><a class="call" href="tel:+13036688992">Call Kirsten</a></nav></header><main id="main">{body}</main><footer><p>Colorado Sound Healing · Kirsten Antony, RN</p><a href="{ARCHIVE}articles.html">Explore Kirsten’s complete 42-article collection →</a><p><a href="tel:+13036688992">(303) 668-8992</a> · <a href="{prefix}index.html#contact">Contact Kirsten</a></p></footer></body></html>'''

cards = ''.join(f'<a class="card" href="articles/{a["slug"]}.html"><span>{esc(a["category"])} · {a["date"][:4]}</span><h2>{esc(a["title"])}</h2><p>{esc(a["excerpt"])}</p><strong>Read the full article →</strong></a>' for a in ARTICLES)
body = f'''<section class="intro"><p class="eyebrow">Kirsten’s writing</p><h1>Sound, stillness &amp; the healing arts.</h1><p>Five complete articles by Kirsten Antony, RN, originally published in Prime Time News and preserved here for reading, reflection and enjoyment.</p><a href="{ARCHIVE}articles.html">Browse all 42 of Kirsten’s articles →</a></section><section class="cards" aria-label="Article collection">{cards}</section>'''
(ROOT/'articles.html').write_text(page('Sound Healing & Wellness Articles by Kirsten Antony, RN','Read Kirsten Antony’s full articles on sound healing, vocal toning, color therapy and energy medicine, preserved from Prime Time News.','articles.html',body))
(ROOT/'articles').mkdir(exist_ok=True)
for a in ARTICLES:
    path = 'articles/'+a['slug']+'.html'
    body = f'''<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../index.html">Home</a> / <a href="../articles.html">Articles</a></nav><section class="intro"><p class="eyebrow">{esc(a['category'])}</p><h1>{esc(a['title'])}</h1><p class="byline">By Kirsten Antony, RN · <time datetime="{a['date']}">{a['date']}</time> · {a['minutes']} min read</p><p class="publication">Originally published in Prime Time News · Preserved from the original publication</p></section><article class="prose">{a['body_html']}</article><aside class="note"><p>Preserved as originally published, with formatting adapted for reading. These historical articles reflect their original publication dates.</p><p>Educational content does not replace individual medical advice, diagnosis or treatment.</p><a href="{ARCHIVE+path}">View this article in Kirsten’s complete archive →</a></aside><div class="reader-end"><a href="../articles.html">← More articles</a></div>'''
    (ROOT/path).write_text(page(a['title'],a['excerpt'],path,body,a))

home = ROOT/'index.html'
s = home.read_text()
for a in ARTICLES:
    s = re.sub(r'href="https?://(?:www\.)?myprimetimenews\.com/'+re.escape(a['slug'])+r'/[^\"]*" target="_blank"', 'href="articles/'+a['slug']+'.html"',s)
s = re.sub(r'href="https?://(?:www\.)?myprimetimenews\.com/category/kirsten-antony/[^\"]*" target="_blank"','href="'+ARCHIVE+'articles.html"',s)
s = s.replace('Explore our collection of informative and engaging articles','Read Kirsten’s complete articles, preserved from Prime Time News. <a href="articles.html">Browse the sound healing collection →</a>')
# Remove an accidentally nested second document head while retaining the original assets.
nested_start = s.find('<!DOCTYPE html>', s.find('<!DOCTYPE html>') + 1)
if nested_start != -1:
    nested_end = s.find('</head>', nested_start)
    s = s[:nested_start] + s[nested_end:]
s = s.replace('<meta content="" name="description">','<meta name="description" content="Sound healing with Kirsten Antony, RN, in Littleton and the Denver metro. Explore private sessions, group sound baths and her preserved wellness articles."><link rel="canonical" href="'+BASE+'">')
home.write_text(s)
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'+BASE+'</loc></url><url><loc>'+BASE+'articles.html</loc></url></urlset>\n')
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE+'sitemap.xml\n')
print('Built five full article pages and repaired six homepage links.')
