"""
Check pasta-blanca category
"""
import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0'}
r = requests.get('https://baldocer.com/producto/pasta-blanca/', headers=headers, timeout=15)
soup = BeautifulSoup(r.content, 'html.parser')

links = soup.find_all('a', href=True)
product_links = [l for l in links if '/producto/pasta-blanca/' in l.get('href', '') and l.get('href', '').count('/') > 3]

unique_urls = set([l.get('href') for l in product_links])

print(f'Found {len(unique_urls)} unique collection links in pasta-blanca\n')

for i, url in enumerate(list(unique_urls)[:15], 1):
    print(f'{i}. {url}')
    
# Also check images
imgs = soup.find_all('img')
print(f'\n\nTotal images: {len(imgs)}')
print('Sample images:')
for img in imgs[:10]:
    src = img.get('src') or img.get('data-src')
    alt = img.get('alt', 'no alt')
    print(f'- {alt[:40]} | {src[:80] if src else "no src"}')
