import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.services.manufacturer_parsers import DuneParser

p = DuneParser()
url = p.base_url + '/serien/agadir'
print('Fetching detail:', url)
d = p.extract_collection_detail(url)
print('\nTitle:', d.get('title'))
print('Description length:', len(d.get('description','')))
print('Images found:', len(d.get('images',[])))
for i, img in enumerate(d.get('images',[])):
    print(' ', i, img)

    # Also print raw image src attributes from the page for inspection
    soup = p.fetch_page(url)
    if soup:
        print('\nRaw img src samples:')
        for idx, img in enumerate(soup.find_all('img')[:30]):
            src = img.get('src') or img.get('data-src') or img.get('data-lazy')
            print(' ', idx, src)
