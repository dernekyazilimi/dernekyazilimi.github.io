"""Validate generated page links, anchors, metadata and navigation."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
ROOT = Path(__file__).resolve().parent.parent
class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(); self.links=[]; self.ids=[]; self.h1=0; self.canonical=0
        self.feed(path.read_text())
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag=='h1': self.h1+=1
        if tag=='a': self.links.append(a.get('href',''))
        if tag=='link' and a.get('rel')=='canonical': self.canonical+=1
        if tag=='link' and a.get('rel') in ('stylesheet','icon'): self.links.append(a['href'])
pages={p:Page(p) for p in ROOT.rglob('index.html')}
for path,p in pages.items():
    assert p.h1==1 and p.canonical==1,path
    assert len(p.ids)==len(set(p.ids)),path
    for link in p.links:
        u=urlsplit(link)
        if u.scheme or u.netloc: continue
        if u.path.startswith('/blog/'): continue  # ayrı proje sitesi (blog deposu)
        target=(ROOT/u.path.lstrip('/')) if u.path.startswith('/') else (path.parent/u.path if u.path else path)
        if target.is_dir(): target=target/'index.html'
        assert target.exists(),(path,link)
        if u.fragment: assert u.fragment in pages[target].ids,(path,link)
print(f'{len(pages)} pages: all internal links, anchors and metadata pass.')

# SEO output must agree with the canonical page inventory.
import json
import re
import struct
from xml.etree import ElementTree as ET
BASE='https://www.dernekyazilimi.org'
canonical_urls=[]
for path in pages:
    html=path.read_text()
    tags={}
    for attrs in re.findall(r'<meta\s+([^>]+)>',html):
        values=dict(re.findall(r'([\w:-]+)="([^"]*)"',attrs))
        key=values.get('name',values.get('property'))
        if key:
            assert key not in tags,(path,key,'duplicate')
            tags[key]=values.get('content','')
    for key in ['description','robots','og:title','og:description','og:url','og:site_name','og:image','og:image:alt','og:image:width','og:image:height','twitter:card','twitter:title','twitter:description','twitter:image','twitter:image:alt']:
        assert tags.get(key),(path,key)
    canonical=re.search(r'<link rel="canonical" href="([^"]+)"',html)[1]
    canonical_urls.append(canonical)
    assert tags['og:url']==canonical
    assert tags['twitter:card']=='summary_large_image'
    assert 'noindex' not in tags['robots']
    for key in ['og:image','twitter:image']:
        assert tags[key].startswith(BASE+'/')
        image=ROOT/tags[key].removeprefix(BASE+'/')
        assert image.exists()
        assert struct.unpack('>II',image.read_bytes()[16:24])==(1200,630)
    data=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',html,re.S)[1])
    graph=data['@graph']
    page=next(x for x in graph if x['@type']=='WebPage')
    assert page['url']==canonical
    if path==ROOT/'index.html':
        software=next(x for x in graph if x['@type']=='SoftwareApplication')
        assert software['url']==BASE+'/'
    if path!=ROOT/'index.html':
        crumb=next(x for x in graph if x['@type']=='BreadcrumbList')
        assert crumb['itemListElement'][-1]['item']==canonical
SM='{http://www.sitemaps.org/schemas/sitemap/0.9}'
sitemap=ET.parse(ROOT/'sitemap-pages.xml')
urls=[n.text for n in sitemap.findall('.//'+SM+'loc')]
assert len(urls)==len(set(urls)) and set(urls)==set(canonical_urls)
# sitemap.xml bir sitemap index olmalı ve sayfa + blog sitemaplerini göstermeli
index=ET.parse(ROOT/'sitemap.xml')
assert index.getroot().tag==SM+'sitemapindex', 'sitemap.xml must be a sitemap index'
child=[n.text for n in index.findall('.//'+SM+'loc')]
assert set(child)=={BASE+'/sitemap-pages.xml', BASE+'/blog/sitemap.xml'},(child,'sitemap index')
robots=(ROOT/'robots.txt').read_text()
assert f'Sitemap: {BASE}/sitemap.xml' in robots
from urllib.robotparser import RobotFileParser
policy=RobotFileParser(); policy.parse(robots.splitlines())
assert all(policy.can_fetch('Googlebot',url) for url in urls)
assert policy.can_fetch('Googlebot',BASE+'/assets/seo/sosyal-paylasim.png')
print('SEO: sitemap, robots, canonical, social images and JSON-LD pass.')

llms=(ROOT/'llms.txt').read_text()
assert llms.startswith('# Dernek Yazılımı')
assert '\n> ' in llms
assert f'{BASE}/' in llms
for p in ['hakkinda', 'moduller', 'entegrasyonlar', 'kurulum', 'katki', 'lisans']:
    assert f'{BASE}/{p}/' in llms, f'{p} missing from llms.txt'
assert policy.can_fetch('Googlebot',BASE+'/llms.txt')
print('llms.txt passes specification and link checks.')

not_found = ROOT/'404.html'
assert not_found.exists(), '404.html missing'
html = not_found.read_text()
assert html.count('<h1>') == 1, '404.html must have exactly one h1'
assert '<link rel="canonical"' not in html, '404.html must not declare a canonical URL'
assert 'content="noindex, follow"' in html, '404.html must be noindex'
assert BASE + '/404.html' not in urls, '404.html must stay out of the sitemap'
assert (ROOT/'sss/index.html').exists(), 'sss page missing'
sss = (ROOT/'sss/index.html').read_text()
sss_data = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', sss, re.S)[1])
sss_faq = next(x for x in sss_data['@graph'] if x['@type'] == 'FAQPage')
assert len(sss_faq['mainEntity']) >= 10, 'sss page needs a complete FAQPage'
assert 'href="/sss/"' in (ROOT/'index.html').read_text(), 'homepage must link to the sss page'

# 404 page internal links must resolve too.
for link in re.findall(r'href="(/[^"#]*)(#[^"]*)?"', html):
    path, fragment = link
    path = path.split('?')[0]
    if path.startswith('/blog/'): continue  # ayrı proje sitesi (blog deposu)
    target = ROOT/path.lstrip('/')
    if target.is_dir():
        target = target/'index.html'
    assert target.exists(), (link, '404.html')
    if fragment:
        assert fragment.lstrip('#') in pages[target].ids, (link, '404.html')
print('404 and SSS pages pass checks.')
