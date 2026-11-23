#!/usr/bin/env python3
"""Generate the static site from curated documentation. Python standard library only."""
from pathlib import Path
from html import escape, unescape
import re
import json
import os

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://www.dernekyazilimi.org'
REPO = 'https://github.com/dernekyazilimi/dernekyazilimi/blob/main/'
PAGES = [
 ('hakkinda', 'Proje hakkında', 'Proje Hakkında: Açık Kaynak Dernek Yazılımı', 'Ortak ihtiyaçlardan doğan özgür yazılım.', 'Linux Kullanıcıları Derneği deneyiminden doğan ücretsiz ve açık kaynak dernek yazılımının hikâyesi, mimarisi ve teknik temeli.', ['README.md', 'CLAUDE.md']),
 ('moduller', 'Modüller', 'Modüller: Üye, Aidat, Bağış ve e-Yazışma', 'Modüller: Üye Takibi, Aidat, Bağış ve e-Yazışma', 'Üye takip, aidat yönetimi, bağış tahsilatı, gönüllü organizasyonu, duyurular ve e-Yazışma resmî evrak süreçlerini kapsayan modüler dernek araçları.', ['CLAUDE.md', 'config/modules.php']),
 ('entegrasyonlar', 'Entegrasyonlar', 'Entegrasyonlar: Ödeme, SMS, e-İmza ve DERBİS', 'Derneğinizin araçlarıyla bağlantıda.', 'iyzico kartlı ödeme, NetGSM SMS, e-posta, eyazisma.com.tr e-imza araçları, DERBİS üye aktarımı ve WordPress web sitesi API entegrasyonları.', ['CLAUDE.md', 'INSTALLING.md']),
 ('kurulum', 'Kurulum', 'Kurulum Rehberi: Sunucu ve Ortam Gereksinimleri', 'Kendi sunucunuzda, kendi derneğiniz için kurulum rehberi.', 'Self-hosted dernek yazılımı kurulumu: PHP 8.4, Laravel ve MySQL gereksinimleri, yerel geliştirme ortamı, ortam değişkenleri ve canlı sunucu işletim rehberi.', ['INSTALLING.md', 'CLAUDE.md', 'composer.json', 'package.json']),
 ('katki', 'Katkıda bulunun', 'Katkıda Bulunun: Geliştirici Rehberi', 'Bir katkı, birçok derneğe fayda.', 'Dernek Yazılımı\'na kod, test, dokümantasyon, hata bildirimi ve kullanım deneyimiyle katkıda bulunma rehberi ve topluluk kuralları.', ['CONTRIBUTING.md', 'CLAUDE.md']),
 ('lisans', 'Lisans', 'Lisans: GNU GPLv3 Açık Kaynak Lisansı', 'Özgür yazılımın ortak zemini.', 'Dernek Yazılımı\'nın özgür yazılım ilkelerini ve kullanıcı haklarını koruyan GNU General Public License v3 (GPLv3) tam lisans metni.', ['README.md', 'LICENSE', 'LICENSE.md']),
]
NAV = [('hakkinda', 'Proje'), ('moduller', 'Modüller'), ('entegrasyonlar', 'Entegrasyonlar'), ('kurulum', 'Kurulum'), ('katki', 'Katkı'), ('sss', 'SSS')]
BRAND = '<img class="brand-svg" src="/assets/logo/logo.svg" alt="Dernek Yazılımı" width="209" height="40">'
GTM_ID = os.environ.get('GTM_ID', 'GTM-MW95NM39')
if GTM_ID and not re.fullmatch(r'GTM-[A-Z0-9]+', GTM_ID):
    raise ValueError('Invalid GTM_ID')
TEMPLATES = ROOT/'scripts/templates'
CONSENT_HEAD = (TEMPLATES/'consent-head.html').read_text().replace('{{GTM_ID}}', GTM_ID) if GTM_ID else ''
CONSENT_BODY = (TEMPLATES/'consent-body.html').read_text() if GTM_ID else ''
PREFERENCES = '<button type="button" data-cookie-preferences hidden>Çerez tercihleri</button>' if GTM_ID else ''
POLICIES = [('cerez-politikasi', 'Çerez politikası'), ('kvkk', 'KVKK aydınlatma metni'), ('gizlilik', 'Gizlilik politikası')]
policy_links = ''.join(f'<a href="/{slug}/">{label}</a>' for slug, label in POLICIES)

def shell(slug, title, description, body, breadcrumb_label=None, brand_in_title=False, extra_graph=None,
          canonical=True, noindex=False, page_url=None):
    url = page_url or BASE + ('/' + slug + '/' if slug else '/')
    full_title = title if brand_in_title else f'{title} — Dernek Yazılımı'
    canonical_tag = f'<link rel="canonical" href="{url}">' if canonical else ''
    og_url_tag = f'<meta property="og:url" content="{url}">' if canonical else ''
    robots = 'noindex, follow' if noindex else 'index, follow, max-image-preview:large'
    graph = [
        {'@type': 'WebSite', '@id': BASE+'/#website', 'url': BASE+'/', 'name': 'Dernek Yazılımı', 'inLanguage': 'tr-TR'},
        {'@type': 'WebPage', '@id': url+'#webpage', 'url': url, 'name': full_title,
         'description': description, 'inLanguage': 'tr-TR', 'isPartOf': {'@id': BASE+'/#website'},
         'primaryImageOfPage': {'@type': 'ImageObject', 'url': BASE+'/assets/seo/sosyal-paylasim.png', 'width': 1200, 'height': 630}}
    ]
    if url == BASE + '/':
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
    graph.extend(extra_graph or [])
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
{CONSENT_HEAD}
<meta name="theme-color" content="#163e33"><title>{escape(full_title)}</title>
<meta name="description" content="{escape(description, quote=True)}">
{canonical_tag}<meta property="og:title" content="{escape(full_title, quote=True)}">
<meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:type" content="website"><meta property="og:locale" content="tr_TR">{og_url_tag}
<meta name="google-site-verification" content="j6_uljYlRGv56WpgYGPcqRMnV8SQH3b9RziaYasDpI0">
<meta name="robots" content="{robots}">
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
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css?v=20261123-sss3">
</head><body>
<a class="skip" href="#icerik">İçeriğe geç</a>
<header class="header wrap site-header"><a class="brand" href="/" aria-label="Dernek Yazılımı ana sayfa">{BRAND}</a><nav aria-label="Ana menü">{links}<a class="nav-cta" href="https://github.com/dernekyazilimi">GitHub ↗</a></nav></header>
{body}
<footer class="wrap site-footer"><div class="footer-brand"><a class="brand" href="/">{BRAND}</a><p>Ortak ihtiyaçlar. Özgür çözümler.</p></div><nav aria-labelledby="footer-project-title"><span class="footer-title" id="footer-project-title">Proje</span><a href="/hakkinda/#logo">Proje Logosu</a><a href="/lisans/">Proje Lisansı</a><a href="/katki/">Katkıda Bulunma Rehberi</a><a href="/sss/">Sık Sorulan Sorular</a><a href="https://github.com/dernekyazilimi">GitHub Proje Depoları ↗</a></nav><nav class="footer-legal" aria-labelledby="footer-legal-title"><span class="footer-title" id="footer-legal-title">Sözleşmeler ve politikalar</span>{policy_links}{PREFERENCES}</nav></footer>
{CONSENT_BODY}
</body></html>'''

def faq_nodes(html, page_id):
    items = []
    for question, answer in re.findall(r'<details>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>', html, re.S):
        items.append({
            '@type': 'Question',
            'name': unescape(re.sub(r'<[^>]+>', '', question)).strip(),
            'acceptedAnswer': {'@type': 'Answer', 'text': unescape(re.sub(r'<[^>]+>', '', answer)).strip()},
        })
    return [{'@type': 'FAQPage', '@id': page_id, 'mainEntity': items}] if items else None


home = (ROOT/'content/ana-sayfa.html').read_text()
extra_graph = faq_nodes(home, BASE+'/#faq')
(ROOT/'index.html').write_text(shell('', 'Dernek Yazılımı — Ücretsiz, Açık Kaynak, Self-Hosted', 'Ücretsiz, açık kaynak ve self-hosted dernek yazılımı: üye takibi, aidat, bağış, gönüllü ve resmî yazışma süreçleri tek çatı altında.', home, brand_in_title=True, extra_graph=extra_graph))
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
for slug, title in POLICIES:
    content = (ROOT/f'content/{slug}.html').read_text().replace('{{PREFERENCES}}', PREFERENCES)
    body = f'<main id="icerik" class="wrap document"><h1>{title}</h1><p>Yürürlük tarihi: 17 Kasım 2026</p>{content}</main>'
    folder = ROOT/slug
    folder.mkdir(exist_ok=True)
    (folder/'index.html').write_text(shell(slug, title, title + ' — Dernek Yazılımı tanıtım sitesi.', body))

# Sık sorulan sorular: bağımsız sayfa, ana sayfadaki SSS'den daha kapsamlı.
SSS_TITLE = 'SSS: Ücretsiz Dernek Yazılımı — Kurulum, Lisans, Entegrasyon'
SSS_H1 = 'Sık Sorulan Sorular: Ücretsiz Dernek Yazılımı'
SSS_DESCRIPTION = ('Ücretsiz dernek yazılımının lisansı, kurulumu, ödeme entegrasyonları, veri güvenliği '
                   've katkı süreçleri hakkında sık sorulan sorular ve yanıtları.')
sss_content = (ROOT/'content/sss.html').read_text()
sss_headings = re.findall(r'<section id="([^"]+)"><h2>(.*?)</h2>', sss_content)
sss_toc = ''.join(f'<a href="#{anchor}">{heading}</a>' for anchor, heading in sss_headings)
sss_body = (
    f'<main id="icerik"><div class="wrap document-hero">'
    f'<p class="breadcrumb"><a href="/">Ana sayfa</a> / Sık sorulan sorular</p>'
    f'<p class="eyebrow">DERNEK YAZILIMI / SSS</p>'
    f'<h1>{SSS_H1}</h1>'
    f'<p class="intro">{SSS_DESCRIPTION} Aradığınız yanıt burada yoksa '
    f'<a href="https://github.com/dernekyazilimi/dernekyazilimi/issues">GitHub üzerinden sorabilirsiniz</a>.</p></div>'
    f'<div class="wrap document-layout"><aside class="toc"><p class="eyebrow">BU SAYFADA</p>'
    f'<nav aria-label="Sayfa içeriği">{sss_toc}</nav></aside>'
    f'<article class="document">{sss_content}'
    f'<div class="source-note"><strong>Daha fazlası</strong>'
    f'<p><a href="/moduller/">Modüller</a> · <a href="/entegrasyonlar/">Entegrasyonlar</a> · '
    f'<a href="/kurulum/">Kurulum rehberi</a> · <a href="/lisans/">Lisans</a> · <a href="/katki/">Katkı rehberi</a></p>'
    f'<p>Yanıtlar 23 Kasım 2026 tarihinde güncellenmiştir. Yazılım sürümüne göre ayrıntılar değişebilir; '
    f'kesin bilgi için proje belgelerine başvurun.</p></div>'
    f'<a class="next-page" href="/katki/"><span>Sıradaki sayfa</span><strong>Katkıda bulunun →</strong></a>'
    f'</article></div></main>'
)
(ROOT/'sss').mkdir(exist_ok=True)
(ROOT/'sss/index.html').write_text(shell('sss', SSS_TITLE, SSS_DESCRIPTION, sss_body,
                                         breadcrumb_label='Sık sorulan sorular',
                                         brand_in_title=True,
                                         extra_graph=faq_nodes(sss_content, BASE + '/sss/#faq')))

# 404: GitHub Pages kök dizindeki 404.html dosyasını sunar.
not_found_body = (
    '<main id="icerik" class="wrap document error-page">'
    '<p class="eyebrow">404 / SAYFA BULUNAMADI</p>'
    '<h1>Bu sayfa taşınmış olabilir.</h1>'
    '<p>Aradığınız adres değişmiş ya da hiç var olmamış olabilir. Aşağıdaki bağlantılardan devam edebilirsiniz.</p>'
    '<div class="start-grid">'
    '<a href="/"><span class="step">01</span><h3>Ana sayfa <span aria-hidden="true">↗</span></h3>'
    '<p>Dernek Yazılımı genel bakış</p></a>'
    '<a href="/moduller/"><span class="step">02</span><h3>Modüller <span aria-hidden="true">↗</span></h3>'
    '<p>Üye, aidat, bağış ve e-Yazışma</p></a>'
    '<a href="/sss/"><span class="step">03</span><h3>Sık sorulan sorular <span aria-hidden="true">↗</span></h3>'
    '<p>Merak edilenler ve yanıtları</p></a>'
    '</div>'
    '<p class="setup-note">Bağlantı kırıksa <a href="https://github.com/dernekyazilimi/dernekyazilimi.github.io/issues">'
    'bildirebilirsiniz</a>.</p>'
    '</main>'
)
(ROOT/'404.html').write_text(shell('', 'Sayfa bulunamadı', 'Aradığınız sayfa bulunamadı.',
                                   not_found_body, page_url=BASE + '/404.html',
                                   canonical=False, noindex=True))
today = '2026-11-17'
urls = [BASE+'/'] + [BASE+'/'+p[0]+'/' for p in PAGES + POLICIES] + [BASE+'/sss/']
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n  </url>\n' for u in urls)+'</urlset>\n')
(ROOT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nDisallow: /content/\nDisallow: /scripts/\n\nSitemap: {BASE}/sitemap.xml\n')
llms_lines = [
    '# Dernek Yazılımı',
    '> Üyelik, aidat, bağış, gönüllülük ve resmî yazışma süreçlerini tek bir çatı altında birleştiren, PHP/Laravel tabanlı ücretsiz, açık kaynak ve self-hosted dernek yazılımı (GNU GPLv3).',
    '',
    '## Dokümantasyon ve Sayfalar',
    f'- [Ana Sayfa]({BASE}/): Dernek Yazılımı genel tanıtımı, temel ilkeler ve genel bakış.',
]
for slug, label, title, headline, description, _ in PAGES:
    llms_lines.append(f'- [{label}]({BASE}/{slug}/): {headline} {description}')
llms_lines.append(f'- [Sık sorulan sorular]({BASE}/sss/): {SSS_DESCRIPTION}')

llms_lines.extend([
    '',
    '## Kaynaklar ve Depolar',
    '- [GitHub Organizasyonu](https://github.com/dernekyazilimi): Dernek Yazılımı açık kaynak organizasyonu.',
    '- [Kaynak Kod Deposu](https://github.com/dernekyazilimi/dernekyazilimi): Dernek Yazılımı ana uygulama deposu (Laravel).',
    '- [Web Sitesi Deposu](https://github.com/dernekyazilimi/dernekyazilimi.github.io): Statik tanıtım ve dokümantasyon sitesi deposu.',
    '',
    '## Temel Harici Entegrasyonlar ve Araçlar',
    '- [Kurulum hizmeti](https://www.kalehost.net/dernek-yazilimi): Portalın sizin için kurulmasını isteyen dernekler için ücretli kurulum hizmeti; yazılımın kendisi ücretsizdir.',
    '- [eyazisma.com.tr](https://www.eyazisma.com.tr/): Resmî yazışma modülü için elektronik imza araçları ve e-Yazışma kütüphaneleri.',
    '- [iyzico](https://www.iyzico.com/): Kredi ve banka kartıyla aidat ve bağış tahsilatı (Checkout Form).',
    '- [qpdf](https://qpdf.sourceforge.io/): e-Yazışma paketlerindeki PDF kopyalarının işlenmesi ve dönüştürülmesi.',
    ''
])
(ROOT/'llms.txt').write_text('\n'.join(llms_lines))
print(f'Generated {len(urls)} pages, sitemap, robots.txt and llms.txt.')
