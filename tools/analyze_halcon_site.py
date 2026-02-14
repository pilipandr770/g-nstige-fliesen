#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Try different Halcon Ceramicas URLs
urls_to_check = [
    'https://www.halconceramicas.com/',
    'https://halconceramicas.com/',
    'https://www.halcon-ceramicas.com/',
    'https://halcon-ceramicas.com/',
    'https://www.halconceramicas.es/',
]

print('🔍 Searching for Halcon Ceramicas website...\n')

working_url = None
for url in urls_to_check:
    try:
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, 'html.parser')
            title = soup.find('title')
            title_text = title.get_text() if title else 'No title'
            
            print(f'✅ {url}')
            print(f'   Status: {r.status_code}')
            print(f'   Title: {title_text[:80]}')
            print(f'   Final URL: {r.url}')
            print()
            
            if working_url is None:
                working_url = r.url
    except Exception as e:
        print(f'❌ {url}')
        print()

if not working_url:
    print('⚠️  No working Halcon Ceramicas URL found')
    exit(1)

print(f'\n📊 Analyzing main site: {working_url}\n')

r = requests.get(working_url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, 'html.parser')

# Look for key elements
print('Main navigation and content:')
print()

# Find navigation links
all_links = soup.find_all('a', href=True)

# Get unique navigation links
nav_links = {}
for link in all_links[:60]:
    href = link.get('href', '')
    text = link.get_text(strip=True)
    if text and len(text) > 2 and href and not href.startswith('#'):
        if text not in nav_links:
            nav_links[text] = href

for text, href in list(nav_links.items())[:25]:
    print(f'  {text:40} -> {href[:70]}')

print()

# Look for logo
print('Logo:')
logo = soup.find('img', class_=lambda x: x and 'logo' in x.lower())
if not logo:
    logo = soup.find('img', alt=lambda x: x and 'logo' in x.lower())
if logo:
    logo_src = logo.get('src', '')
    logo_url = urljoin(working_url, logo_src)
    print(f'  Found: {logo_url}')
else:
    print('  Not found')

print()

# Look for collections/products
print('Collections/Products pages:')
found_any = False
for text, href in nav_links.items():
    if any(word in text.lower() or word in href.lower() for word in ['collezione', 'collection', 'prodotto', 'product', 'catalogo', 'catalog', 'serie']):
        abs_href = urljoin(working_url, href)
        print(f'  {text:40} -> {abs_href[:70]}')
        found_any = True
if not found_any:
    print('  (checking secondary pages...)')

print()

# Look for blog/news
print('Blog/News:')
found_any = False
for text, href in nav_links.items():
    if any(word in text.lower() or word in href.lower() for word in ['blog', 'news', 'stampa', 'rassegna', 'articolo', 'notizie']):
        abs_href = urljoin(working_url, href)
        print(f'  {text:40} -> {abs_href[:70]}')
        found_any = True
if not found_any:
    print('  (none found in main menu)')
