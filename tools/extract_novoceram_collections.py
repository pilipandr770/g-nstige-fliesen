import requests
from bs4 import BeautifulSoup

url = 'https://www.novoceram.fr/carrelage/collections'
resp = requests.get(url, timeout=10)
soup = BeautifulSoup(resp.content, 'html.parser')

# Find all divs with IDs containing product/collection
product_divs = soup.find_all(id=lambda x: x and any(y in (x or '').lower() for y in ['product', 'collection', 'item']))

print('Found {} product/collection containers'.format(len(product_divs)))

collections = []
for div in product_divs:
    # Get the ID and text content
    div_id = div.get('id', '')
    
    # Try to find a link inside
    link = div.find('a')
    if link:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if href and text and '/carrelage/' in href:
            # Skip filter links
            if not any(x in href.lower() for x in ['/effect', '/de/', '/format', '/couleur', '/pour']):
                collections.append({'name': text, 'url': href, 'id': div_id})

# Deduplicate
seen = set()
unique = []
for c in collections:
    if c['url'] not in seen:
        seen.add(c['url'])
        unique.append(c)

print('Found {} unique collections:'.format(len(unique)))
for i, c in enumerate(unique):
    short_name = c['url'].split('/carrelage/')[-1].rstrip('/')
    print('  {}. {} → {}'.format(i+1, c['name'][:40], short_name))
