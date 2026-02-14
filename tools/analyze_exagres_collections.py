#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print('🔍 Analyzing Exagres collections page...\n')

# Check collections page
url = 'https://www.exagres.es/colecciones-residencial/'
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, 'html.parser')

# Get title
title = soup.find('title')
print(f'Page: {url}')
print(f'Title: {title.get_text() if title else "No title"}')
print()

# Look for collection items
print('Looking for collection items:\n')

# Look for common collection container patterns
collection_items = soup.find_all(['a', 'div', 'li'], class_=lambda x: x and any(keyword in str(x).lower() for keyword in ['item', 'product', 'collection', 'post', 'card']))

print(f'Found {len(collection_items)} potential collection items\n')

for i, item in enumerate(collection_items[:10]):
    if item.name == 'a':
        href = item.get('href', '')
        text = item.get_text(strip=True)[:60]
        if text and href:
            # Check if it looks like a product link
            if any(keyword in href.lower() for keyword in ['.es/', 'producto']):
                print(f'  {i+1}. {text}')
                print(f'     Link: {href}')

print()

# Check blog page
print('\n🔍 Analyzing Exagres blog page...\n')

blog_url = 'https://www.exagres.es/blog/'
r = requests.get(blog_url, headers=headers, timeout=10)
if r.status_code == 200:
    soup = BeautifulSoup(r.content, 'html.parser')
    
    title = soup.find('title')
    print(f'Blog page: {blog_url}')
    print(f'Title: {title.get_text() if title else "No title"}')
    print()
    
    # Find blog posts
    posts = soup.find_all(['article', 'div', 'li'], class_=lambda x: x and 'post' in str(x).lower())
    if not posts:
        posts = soup.find_all('h2')
    
    print(f'Found {len(posts)} potential blog posts')
    
    # Look for blog post titles and links
    blog_posts = []
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if 'blog' in href and len(text) > 5 and '/blog/' in href:
            if href not in [p[0] for p in blog_posts]:
                blog_posts.append((href, text))
    
    if blog_posts:
        print(f'\nBlog posts found: {len(blog_posts)}')
        for url, title in blog_posts[:5]:
            print(f'  - {title[:60]}')
            print(f'    {url}')
else:
    print(f'Could not access blog: {r.status_code}')

print('\n\n📺 Checking for product/collection structure...\n')

# Try to find specific product structure
prod_url = 'https://www.exagres.es/producto/'
r = requests.get(prod_url, headers=headers, timeout=10)
if r.status_code == 200:
    soup = BeautifulSoup(r.content, 'html.parser')
    
    title = soup.find('title')
    print(f'Product page: {prod_url}')
    print(f'Title: {title.get_text() if title else "No title"}')
    
    # Count products
    products = soup.find_all('div', class_=lambda x: x and 'product' in str(x).lower())
    print(f'Product divs found: {len(products)}')
    
    # Look for links that might be collections
    for link in soup.find_all('a', href=True)[:15]:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if href and text and len(text) > 3 and not href.startswith('#'):
            print(f'  {text[:40]:40} -> {href}')
