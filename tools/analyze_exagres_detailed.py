#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Analyze the Spanish Exagres site
url = 'https://www.exagres.es/'

print(f'📊 Detailed analysis of {url}\n')

r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, 'html.parser')

# Find title
title = soup.find('title')
print(f'Page title: {title.get_text() if title else "No title"}')
print()

# Look for all links to understand navigation
print('Navigation links:')
for link in soup.find_all('a', href=True)[:20]:
    href = link.get('href')
    text = link.get_text(strip=True)[:40]
    if text and href and not href.startswith('#'):
        print(f'  {text:40} -> {href}')
        
print()

# Look for collections specifically
print('Looking for collections:\n')

# Check for common patterns
patterns = [
    ('div', {'class': lambda x: x and 'collection' in x.lower()}),
    ('div', {'class': lambda x: x and 'product' in x.lower()}),
    ('section', {}),
]

for tag, attrs in patterns:
    elements = soup.find_all(tag, attrs)
    if elements:
        print(f'Found {len(elements)} <{tag}> elements:')
        for elem in elements[:3]:
            title_elem = elem.find(['h1', 'h2', 'h3', 'h4', 'span'])
            title_text = title_elem.get_text(strip=True) if title_elem else 'No title'
            href = elem.find('a')
            href_val = href.get('href') if href else 'No link'
            print(f'  - {title_text[:50]}')
            if href_val and href_val != 'No link':
                print(f'    Link: {href_val}')
        print()

# Look for blog/news
print('\nLooking for blog/news:')
news_links = []
for link in soup.find_all('a', href=True):
    href = link.get('href', '').lower()
    text = link.get_text(strip=True)
    if any(keyword in href for keyword in ['blog', 'news', 'prensa', 'articulo', 'noticia']):
        news_links.append((text, href))

if news_links:
    print(f'Found {len(news_links)} potential blog links:')
    for text, href in news_links[:5]:
        print(f'  {text:40} -> {href}')
else:
    print('No blog/news links found')

# Look for logo
print('\nLooking for logo:')
logo = soup.find('img', class_=lambda x: x and 'logo' in x.lower())
if not logo:
    logo = soup.find('img', alt=lambda x: x and 'logo' in x.lower())
if logo:
    logo_src = logo.get('src', '')
    print(f'Logo found: {logo_src}')
    # Make absolute URL
    logo_url = urljoin(url, logo_src)
    print(f'Absolute URL: {logo_url}')
else:
    print('Logo not found in expected locations')
