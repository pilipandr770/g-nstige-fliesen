#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print('🔍 Deep dive into Exagres collections page HTML...\n')

url = 'https://www.exagres.es/colecciones-residencial/'
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, 'html.parser')

# Find the main content area
main = soup.find('main') or soup.find('div', class_=lambda x: x and 'main' in str(x).lower())

# Look for specific collection patterns
print('Looking for collection items with different patterns:\n')

# Pattern 1: Cards with image and title
cards = soup.find_all('div', class_=lambda x: x and 'card' in str(x).lower())
print(f'1. Cards found: {len(cards)}')
if cards:
    for card in cards[:2]:
        title = card.find(['h2', 'h3', 'span'])
        img = card.find('img')
        link = card.find('a')
        if title:
            print(f'   Title: {title.get_text(strip=True)[:50]}')
        if img:
            print(f'   Image alt: {img.get("alt", "")[:50]}')
        if link:
            print(f'   Link: {link.get("href", "")[:80]}')
    print()

# Pattern 2: Look for wpml or custom post type patterns
collections = soup.find_all(['article'], class_=lambda x: x and not ('comment' in str(x).lower()))
print(f'2. Articles found: {len(collections)}')
if collections:
    for article in collections[:2]:
        h = article.find(['h1', 'h2', 'h3', 'h4'])
        if h:
            print(f'   {h.get_text(strip=True)[:50]}')
    print()

# Pattern 3: Look at all links in a grid pattern
grids = soup.find_all('div', class_=lambda x: x and any(word in str(x).lower() for word in ['grid', 'row', 'gallery', 'gallery-item']))
print(f'3. Grid elements found: {len(grids)}')

# Let's look at actual structure more carefully
print('\n\nAnalyzing actual HTML structure:\n')

# Find main content container
content = soup.find('div', class_=lambda x: x and 'content' in str(x).lower())
if not content:
    content = soup.find('main')
if not content:
    content = soup.body

# Look for collection-like structures
items = content.find_all('div', class_=lambda x: x and any(word in str(x).lower() for word in ['item', 'producto', 'product', 'tile', 'box', 'entry']))

print(f'Items (producto/product/tile/box/entry) found: {len(items)}')
if items:
    for i, item in enumerate(items[:5], 1):
        # Try to extract information
        link = item.find('a')
        img = item.find('img')
        h_tag = item.find(['h2', 'h3', 'h4', 'h5', 'span'])
        
        if link or img or h_tag:
            print(f'\n  Item {i}:')
            if h_tag:
                print(f'    Title: {h_tag.get_text(strip=True)[:60]}')
            if img:
                alt_text = img.get('alt', '')
                src = img.get('src', '')
                print(f'    Image alt: {alt_text[:60]}')
                print(f'    Image src: {src[:80]}')
            if link:
                href = link.get('href', '')
                print(f'    Link: {href[:80]}')

print('\n\n' + '='*80)
print('🔍 Deep dive into blog page HTML...\n')

blog_url = 'https://www.exagres.es/blog/'
r = requests.get(blog_url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, 'html.parser')

# Find blog posts
articles = soup.find_all('article')
print(f'Articles found: {len(articles)}')

if articles:
    for article in articles[:3]:
        title = article.find(['h1', 'h2', 'h3', 'h4', 'h5'])
        link = article.find('a')
        img = article.find('img')
        
        print(f'\n  Article:')
        if title:
            print(f'    Title: {title.get_text(strip=True)[:60]}')
        if link:
            href = link.get('href', '')
            if '/blog/' in href:
                print(f'    Link: {href}')
        if img:
            print(f'    Image: {img.get("src", "")[:80]}')
