#!/usr/bin/env python3
import os
import sys
ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Try different Exagres URLs
urls_to_check = [
    'https://www.exagres.com/',
    'https://en.exagres.com/',
    'https://www.exagres.es/',
    'https://exagres.com/',
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print('🔍 Searching for Exagres website...\n')

for url in urls_to_check:
    try:
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, 'html.parser')
            title = soup.find('title')
            title_text = title.get_text() if title else 'No title'
            
            # Count main structural elements
            collections = soup.find_all('div', class_=lambda x: x and 'collection' in x.lower())
            products = soup.find_all(lambda tag: tag.name in ['li', 'div'] and 'product' in str(tag.get('class', '')).lower())
            
            print(f'✅ {url}')
            print(f'   Status: {r.status_code}')
            print(f'   Title: {title_text[:80]}')
            print(f'   URL after redirects: {r.url}')
            print(f'   Collections/product divs found: {len(collections) + len(products)}')
            print()
    except Exception as e:
        print(f'❌ {url}: {str(e)[:60]}')
        print()

print('\n📄 Now let\'s analyze the main site structure...\n')

# Try the most likely URL
main_url = 'https://www.exagres.com/'
try:
    r = requests.get(main_url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.content, 'html.parser')
    
    print(f'Main site: {main_url}')
    print(f'Status: {r.status_code}')
    print()
    
    # Look for collections/galleries/products
    print('Key page elements:')
    
    # Check for navigation links
    nav_links = soup.find_all('a', href=lambda x: x and ('collection' in x.lower() or 'product' in x.lower()))
    if nav_links:
        print(f'\n  Collections/Products links: {len(nav_links)} found')
        for link in nav_links[:3]:
            href = link.get('href', '')
            text = link.get_text(strip=True)[:40]
            print(f'    - {text}: {href[:60]}')
    
    # Check for logo
    logo = soup.find('img', class_=lambda x: x and 'logo' in x.lower()) or soup.find('img', alt=lambda x: x and 'logo' in x.lower())
    if logo:
        logo_src = logo.get('src', '')
        print(f'\n  Logo found: {logo_src[:80]}')
    
    # Check for blog/news
    blog_links = soup.find_all('a', href=lambda x: x and ('blog' in x.lower() or 'news' in x.lower() or 'prensa' in x.lower()))
    if blog_links:
        print(f'\n  Blog/News links: {len(blog_links)} found')
        for link in blog_links[:2]:
            href = link.get('href', '')
            text = link.get_text(strip=True)[:40]
            print(f'    - {text}: {href[:60]}')
    
except Exception as e:
    print(f'Error: {str(e)}')
