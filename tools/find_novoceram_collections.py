import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = 'https://www.novoceram.fr/carrelage/collections'
resp = requests.get(url, timeout=10)
soup = BeautifulSoup(resp.content, 'html.parser')

# Find collection links
collections = []
for link in soup.find_all('a'):
    href = link.get('href', '')
    text = link.get_text(strip=True)
  # Look for links that are collection pages
    if href and '/carrelage/' in href and text and len(text) > 2:
        # Filter out navigation/filter links
        is_nav = any(x in href.lower() for x in ['/effect', '/de/', '/format', '/couleur', '/pour', 'recherche', 'collections'])
        if not is_nav:
            collections.append({'name': text, 'url': urljoin(url, href)})

# Deduplicate
seen = set()
unique = []
for c in collections:
    if c['url'] not in seen:
        seen.add(c['url'])
        unique.append(c)

print('Found {} collections:'.format(len(unique)))
for i, c in enumerate(unique[:50]):
    coll_name = c['url'].replace('/carrelage/', '').rstrip('/')
    print('  {}. {}'.format(i+1, c['name'][:45]))

print('\\nTotal: {} collections'.format(len(unique)))

# Show first few URLs
print('\\nSample URLs:')
for c in unique[:5]:
    print('  ' + c['url'])
