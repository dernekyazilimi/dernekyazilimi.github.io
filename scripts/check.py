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
BASE='https://dernekyazilimi.github.io'
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
    if path!=ROOT/'index.html':
        crumb=next(x for x in graph if x['@type']=='BreadcrumbList')
        assert crumb['itemListElement'][-1]['item']==canonical
sitemap=ET.parse(ROOT/'sitemap.xml')
urls=[n.text for n in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert len(urls)==len(set(urls)) and set(urls)==set(canonical_urls)
robots=(ROOT/'robots.txt').read_text()
assert f'Sitemap: {BASE}/sitemap.xml' in robots
from urllib.robotparser import RobotFileParser
policy=RobotFileParser(); policy.parse(robots.splitlines())
assert all(policy.can_fetch('Googlebot',url) for url in urls)
assert policy.can_fetch('Googlebot',BASE+'/assets/seo/sosyal-paylasim.png')
print('SEO: sitemap, robots, canonical, social images and JSON-LD pass.')
