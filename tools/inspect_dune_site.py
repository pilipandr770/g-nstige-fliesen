import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.services.manufacturer_parsers import DuneParser

p = DuneParser()
print('Fetching', p.base_url)
soup = p.fetch_page(p.base_url)
if soup:
    print('\nPage title:', soup.title.string if soup.title else 'N/A')
    links = set()
    for a in soup.find_all('a', href=True):
        href = a.get('href')
        if href and ('serie' in href or 'series' in href or 'collection' in href or 'produkt' in href or 'product' in href):
            links.add(href)
    print('\nFound candidate links on base page (filtered):')
    for l in list(links)[:30]:
        print(' ', l)

print('\nFetching /serien page')
soup2 = p.fetch_page(p.base_url + '/serien')
if soup2:
    print('\nPage title:', soup2.title.string if soup2.title else 'N/A')
    # print first 30 anchors
    anchors = soup2.find_all('a', href=True)
    print('\nTotal anchors on /serien:', len(anchors))
    for a in anchors[:100]:
        href = a.get('href')
        txt = a.get_text(strip=True)[:60]
        print(' ', href, '->', txt)
else:
    print('Could not fetch /serien')
