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
