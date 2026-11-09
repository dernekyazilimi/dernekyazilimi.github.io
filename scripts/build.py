#!/usr/bin/env python3
"""Generate the static site from curated documentation. Python standard library only."""
from pathlib import Path
from html import escape
import re
import json

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://www.dernekyazilimi.org'
REPO = 'https://github.com/dernekyazilimi/dernekyazilimi/blob/main/'
PAGES = [
 ('hakkinda', 'Proje hakkında', 'Proje Hakkında', 'Ortak ihtiyaçlardan doğan özgür yazılım.', 'Linux Kullanıcıları Derneği deneyiminden doğan açık kaynaklı dernek yönetim sisteminin hikâyesi, mimarisi ve teknik temeli.', ['README.md', 'CLAUDE.md']),
 ('moduller', 'Modüller', 'Dernek Modülleri: Üye Takip, Aidat, Bağış ve e-Yazışma', 'Her ihtiyaca bir araç. Hepsi bir arada.', 'Üye takip, aidat yönetimi, bağış tahsilatı, gönüllü organizasyonu, duyurular ve e-Yazışma resmî evrak süreçlerini kapsayan modüler dernek araçları.', ['CLAUDE.md', 'config/modules.php']),
 ('entegrasyonlar', 'Entegrasyonlar', 'Entegrasyonlar: Ödeme, SMS, e-İmza ve DERBİS', 'Derneğinizin araçlarıyla bağlantıda.', 'iyzico kartlı ödeme, NetGSM SMS, e-posta, eyazisma.com.tr e-imza araçları, DERBİS üye aktarımı ve WordPress web sitesi API entegrasyonları.', ['CLAUDE.md', 'INSTALLING.md']),
 ('kurulum', 'Kurulum', 'Kurulum Rehberi: Sunucu ve Ortam Gereksinimleri', 'Kendi sunucunuzda, kendi derneğiniz için.', 'PHP 8.4, Laravel ve MySQL gereksinimleri, yerel geliştirme ortamı hazırlığı, ortam değişkenleri ve canlı sunucu işletim rehberi.', ['INSTALLING.md', 'CLAUDE.md', 'composer.json', 'package.json']),
 ('katki', 'Katkıda bulunun', 'Katkıda Bulunun: Açık Kaynak Geliştirme Rehberi', 'Bir katkı, birçok derneğe fayda.', 'Dernek Yazılımı\'na kod, test, dokümantasyon, hata bildirimi ve kullanım deneyimiyle katkıda bulunma rehberi ve topluluk kuralları.', ['CONTRIBUTING.md', 'CLAUDE.md']),
 ('lisans', 'Lisans', 'Lisans: GNU General Public License v3 (GPLv3)', 'Özgür yazılımın ortak zemini.', 'Dernek Yazılımı\'nın özgür yazılım ilkelerini ve kullanıcı haklarını koruyan GNU General Public License v3 (GPLv3) tam lisans metni.', ['README.md', 'LICENSE', 'LICENSE.md']),
]
NAV = [('hakkinda', 'Proje'), ('moduller', 'Modüller'), ('entegrasyonlar', 'Entegrasyonlar'), ('kurulum', 'Kurulum'), ('katki', 'Katkı')]
BRAND = '<img class="brand-svg" src="/assets/logo/logo.svg" alt="Dernek Yazılımı" width="209" height="40">'
def shell(slug, title, description, body, breadcrumb_label=None):
    url = BASE + ('/' + slug + '/' if slug else '/')
    full_title = f'{title} — Dernek Yazılımı'
    graph = [
        {'@type': 'WebSite', '@id': BASE+'/#website', 'url': BASE+'/', 'name': 'Dernek Yazılımı', 'inLanguage': 'tr-TR'},
        {'@type': 'WebPage', '@id': url+'#webpage', 'url': url, 'name': full_title,
         'description': description, 'inLanguage': 'tr-TR', 'isPartOf': {'@id': BASE+'/#website'},
         'primaryImageOfPage': {'@type': 'ImageObject', 'url': BASE+'/assets/seo/sosyal-paylasim.png', 'width': 1200, 'height': 630}}
    ]
    if not slug:
        graph.append({
            '@type': 'SoftwareApplication',
            '@id': BASE+'/#software',
            'name': 'Dernek Yazılımı',
            'applicationCategory': 'BusinessApplication',
            'operatingSystem': 'Web, Linux',
            'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'TRY'},
            'license': 'https://www.gnu.org/licenses/gpl-3.0.html',
            'description': description,
            'url': BASE+'/'
        })
    if slug:
        graph[1]['breadcrumb'] = {'@id': url+'#breadcrumb'}
        graph.append({'@type': 'BreadcrumbList', '@id': url+'#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Ana sayfa', 'item': BASE+'/'},
            {'@type': 'ListItem', 'position': 2, 'name': breadcrumb_label or title, 'item': url}
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
(ROOT/'index.html').write_text(shell('', 'Özgür Dernek Yönetim Yazılımı', 'Üye takibi, aidat, bağış, gönüllü ve resmî yazışma süreçlerini tek bir çatı altında birleştiren açık kaynaklı ve özgür dernek yönetim yazılımı.', home))
for i,(slug,label,title,headline,description,sources) in enumerate(PAGES):
    content = (ROOT/f'content/{slug}.html').read_text()
    content = content.replace('{{LICENSE}}', escape((ROOT/'content/LICENSE.txt').read_text()))
    headings = re.findall(r'<section id="([^"]+)"><h2>(.*?)</h2>', content)
    toc = ''.join(f'<a href="#{anchor}">{heading}</a>' for anchor,heading in headings)
    source_links = ' · '.join(f'<a href="{REPO}{name}">{name}</a>' for name in sources)
    next_slug,next_label,*_ = PAGES[(i+1)%len(PAGES)]
    body = f'''<main id="icerik"><div class="wrap document-hero"><p class="breadcrumb"><a href="/">Ana sayfa</a> / {label}</p><p class="eyebrow">DERNEK YAZILIMI / {label.upper()}</p><h1>{headline}</h1><p class="intro">{description}</p></div><div class="wrap document-layout"><aside class="toc"><p class="eyebrow">BU SAYFADA</p><nav aria-label="Sayfa içeriği">{toc}</nav></aside><article class="document">{content}<div class="source-note"><strong>Bu sayfanın kaynakları</strong><p>{source_links}</p><p>Proje belgelerinden uyarlanmıştır. Belge inceleme tarihi: 28 Ekim 2026. Kuruma özgü sunucu ve erişim bilgileri bu rehbere dahil edilmemiştir.</p></div><a class="next-page" href="/{next_slug}/"><span>Sıradaki sayfa</span><strong>{next_label} →</strong></a></article></div></main>'''
    folder = ROOT/slug
    folder.mkdir(exist_ok=True)
    (folder/'index.html').write_text(shell(slug,title,description,body,breadcrumb_label=label))
today = '2026-11-09'
urls = [BASE+'/'] + [BASE+'/'+p[0]+'/' for p in PAGES]
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n  </url>\n' for u in urls)+'</urlset>\n')
(ROOT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nDisallow: /content/\nDisallow: /scripts/\n\nSitemap: {BASE}/sitemap.xml\n')
llms_lines = [
    '# Dernek Yazılımı',
    '> Üyelik, aidat, bağış, gönüllülük ve resmî yazışma süreçlerini tek bir çatı altında birleştiren, PHP/Laravel tabanlı özgür ve açık kaynaklı dernek yönetim yazılımı (GNU GPLv3).',
    '',
    '## Dokümantasyon ve Sayfalar',
    f'- [Ana Sayfa]({BASE}/): Dernek Yazılımı genel tanıtımı, temel ilkeler ve genel bakış.',
]
for slug, label, title, headline, description, _ in PAGES:
    llms_lines.append(f'- [{label}]({BASE}/{slug}/): {headline} {description}')

llms_lines.extend([
    '',
    '## Kaynaklar ve Depolar',
    '- [GitHub Organizasyonu](https://github.com/dernekyazilimi): Dernek Yazılımı açık kaynak organizasyonu.',
    '- [Kaynak Kod Deposu](https://github.com/dernekyazilimi/dernekyazilimi): Dernek Yazılımı ana uygulama deposu (Laravel).',
    '- [Web Sitesi Deposu](https://github.com/dernekyazilimi/dernekyazilimi.github.io): Statik tanıtım ve dokümantasyon sitesi deposu.',
    '',
    '## Temel Harici Entegrasyonlar ve Araçlar',
    '- [eyazisma.com.tr](https://www.eyazisma.com.tr/): Resmî yazışma modülü için elektronik imza araçları ve e-Yazışma kütüphaneleri.',
    '- [iyzico](https://www.iyzico.com/): Kredi ve banka kartıyla aidat ve bağış tahsilatı (Checkout Form).',
    '- [qpdf](https://qpdf.sourceforge.io/): e-Yazışma paketlerindeki PDF kopyalarının işlenmesi ve dönüştürülmesi.',
    ''
])
(ROOT/'llms.txt').write_text('\n'.join(llms_lines))
print(f'Generated {len(urls)} pages, sitemap, robots.txt and llms.txt.')
