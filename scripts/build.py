#!/usr/bin/env python3
"""Generate the static site from curated documentation. Python standard library only."""
from pathlib import Path
from html import escape
import re
import json

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://dernekyazilimi.github.io'
REPO = 'https://github.com/lkdtr/dernekyazilimi/blob/main/'
PAGES = [
 ('hakkinda', 'Proje hakkında', 'Ortak ihtiyaçlardan doğan özgür yazılım.', 'Projenin hikâyesi, yaklaşımı ve teknik temeli.', ['README.md', 'CLAUDE.md']),
 ('moduller', 'Modüller', 'Her ihtiyaca bir araç. Hepsi bir arada.', 'Üyelik, aidat, bağış ve gönüllülükten resmî yazışmaya uzanan modüller.', ['CLAUDE.md', 'config/modules.php']),
 ('entegrasyonlar', 'Entegrasyonlar', 'Derneğinizin araçlarıyla bağlantıda.', 'Web sitesi, ödeme, iletişim ve veri aktarımı entegrasyonları.', ['CLAUDE.md', 'INSTALLING.md']),
 ('kurulum', 'Kurulum', 'Kendi sunucunuzda, kendi derneğiniz için.', 'Gereksinimler, yerel kurulum adımları ve canlı ortam işletimi.', ['INSTALLING.md', 'CLAUDE.md', 'composer.json', 'package.json']),
 ('katki', 'Katkıda bulunun', 'Bir katkı, birçok derneğe fayda.', 'Test, dokümantasyon, topluluk ve kod katkısı için rehber.', ['CONTRIBUTING.md', 'CLAUDE.md']),
 ('lisans', 'Lisans', 'Özgür yazılımın ortak zemini.', 'Projenin GNU GPLv3 lisans belgesi ve tam metni.', ['README.md', 'LICENSE', 'LICENSE.md']),
]
NAV = [('hakkinda', 'Proje'), ('moduller', 'Modüller'), ('entegrasyonlar', 'Entegrasyonlar'), ('kurulum', 'Kurulum'), ('katki', 'Katkı')]
BRAND = '<img class="brand-svg" src="/assets/logo/logo.svg" alt="Dernek Yazılımı" width="209" height="40">'
def shell(slug, title, description, body):
    url = BASE + ('/' + slug + '/' if slug else '/')
    full_title = f'{title} — Dernek Yazılımı'
    graph = [
        {'@type': 'WebSite', '@id': BASE+'/#website', 'url': BASE+'/', 'name': 'Dernek Yazılımı', 'inLanguage': 'tr-TR'},
        {'@type': 'WebPage', '@id': url+'#webpage', 'url': url, 'name': full_title,
         'description': description, 'inLanguage': 'tr-TR', 'isPartOf': {'@id': BASE+'/#website'},
         'primaryImageOfPage': {'@type': 'ImageObject', 'url': BASE+'/assets/seo/sosyal-paylasim.png', 'width': 1200, 'height': 630}}
    ]
    if slug:
        graph[1]['breadcrumb'] = {'@id': url+'#breadcrumb'}
        graph.append({'@type': 'BreadcrumbList', '@id': url+'#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Ana sayfa', 'item': BASE+'/'},
            {'@type': 'ListItem', 'position': 2, 'name': title, 'item': url}
        ]})
    structured_data = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False).replace('<', r'\u003c')
    links = ''.join(f'<a href="/{s}/"'+(' aria-current="page"' if s == slug else '')+f'>{label}</a>' for s,label in NAV)
    return f'''<!doctype html>
<html lang="tr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#163e33"><title>{escape(title)} — Dernek Yazılımı</title>
<meta name="description" content="{escape(description, quote=True)}">
<link rel="canonical" href="{url}"><meta property="og:title" content="{escape(title, quote=True)} — Dernek Yazılımı">
<meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:type" content="website"><meta property="og:locale" content="tr_TR"><meta property="og:url" content="{url}">
<meta name="google-site-verification" content="j6_uljYlRGv56WpgYGPcqRMnV8SQH3b9RziaYasDpI0">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:site_name" content="Dernek Yazılımı">
<meta property="og:image" content="{BASE}/assets/seo/sosyal-paylasim.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Dernek Yazılımı — Birlikte daha fazlası. Üyelik, aidat, bağış ve gönüllülük.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(full_title, quote=True)}">
<meta name="twitter:description" content="{escape(description, quote=True)}">
<meta name="twitter:image" content="{BASE}/assets/seo/sosyal-paylasim.png">
<meta name="twitter:image:alt" content="Dernek Yazılımı — özgür dernek yönetim yazılımı">
<script type="application/ld+json">{structured_data}</script>
<link rel="sitemap" type="application/xml" href="/sitemap.xml">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css">
</head><body>
<a class="skip" href="#icerik">İçeriğe geç</a>
<header class="header wrap site-header"><a class="brand" href="/" aria-label="Dernek Yazılımı ana sayfa">{BRAND}</a><nav aria-label="Ana menü">{links}<a class="nav-cta" href="https://github.com/dernekyazilimi">GitHub ↗</a></nav></header>
{body}
<footer class="wrap site-footer"><a class="brand" href="/">{BRAND}</a><p>Ortak ihtiyaçlar. Özgür çözümler.</p><div><a href="/hakkinda/#logo">Logo</a><a href="/lisans/">Lisans</a><a href="/katki/">Katkı</a><a href="https://github.com/dernekyazilimi">GitHub ↗</a></div></footer>
</body></html>'''

home = (ROOT/'content/ana-sayfa.html').read_text()
(ROOT/'index.html').write_text(shell('', 'Özgür Dernek Yönetim Yazılımı', 'Üyelik, aidat, bağış ve gönüllü süreçlerini bir araya getiren özgür dernek yönetim yazılımı.', home))
for i,(slug,label,headline,description,sources) in enumerate(PAGES):
    content = (ROOT/f'content/{slug}.html').read_text()
    content = content.replace('{{LICENSE}}', escape((ROOT/'content/LICENSE.txt').read_text()))
    headings = re.findall(r'<section id="([^"]+)"><h2>(.*?)</h2>', content)
    toc = ''.join(f'<a href="#{anchor}">{heading}</a>' for anchor,heading in headings)
    source_links = ' · '.join(f'<a href="{REPO}{name}">{name}</a>' for name in sources)
    next_slug,next_label,*_ = PAGES[(i+1)%len(PAGES)]
    body = f'''<main id="icerik"><div class="wrap document-hero"><p class="breadcrumb"><a href="/">Ana sayfa</a> / {label}</p><p class="eyebrow">DERNEK YAZILIMI / {label.upper()}</p><h1>{headline}</h1><p class="intro">{description}</p></div><div class="wrap document-layout"><aside class="toc"><p class="eyebrow">BU SAYFADA</p><nav aria-label="Sayfa içeriği">{toc}</nav></aside><article class="document">{content}<div class="source-note"><strong>Bu sayfanın kaynakları</strong><p>{source_links}</p><p>Proje belgelerinden uyarlanmıştır. Belge inceleme tarihi: 28 Ekim 2026. Kuruma özgü sunucu ve erişim bilgileri bu rehbere dahil edilmemiştir.</p></div><a class="next-page" href="/{next_slug}/"><span>Sıradaki sayfa</span><strong>{next_label} →</strong></a></article></div></main>'''
    folder = ROOT/slug
    folder.mkdir(exist_ok=True)
    (folder/'index.html').write_text(shell(slug,label,description,body))
urls = [BASE+'/'] + [BASE+'/'+p[0]+'/' for p in PAGES]
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls)+'</urlset>\n')
(ROOT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nDisallow: /content/\nDisallow: /scripts/\n\nSitemap: {BASE}/sitemap.xml\n')
print(f'Generated {len(urls)} pages, sitemap and robots.txt.')
