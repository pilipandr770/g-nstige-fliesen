#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

base_url = 'https://www.halconceramicas.com'

print('🔍 Analyzing Halcon Ceramicas collections structure...\n')

# Check collections page
r = requests.get(f'{base_url}/colecciones', headers=headers, timeout=10)
soup = BeautifulSoup(r.content, 'html.parser')

title = soup.find('title')
print(f'Collections page: {base_url}/colecciones')
print(f'Title: {title.get_text() if title else "No title"}')
print()

# Look for collection items
print('Looking for collection items:')

# Method 1: Find all links with /colecciones in href
collection_links = []
for link in soup.find_all('a', href=lambda x: x and '/colecciones/' in x):
    href = link.get('href', '')
    text = link.get_text(strip=True)
    if text and len(text) > 2:
        if href not in [c[1] for c in collection_links]:
            collection_links.append((text, href))

print(f'Found {len(collection_links)} collection links:')
for text, href in collection_links[:15]:
    print(f'  {text:30} -> {href}')

print()
print(f'\n📷 Checking collection page structure...\n')

# Check one collection to understand structure
if collection_links:
    test_url = collection_links[0][1]
    if not test_url.startswith('http'):
        test_url = f'{base_url}{test_url}'
    
    print(f'Testing first collection: {test_url}')
    r = requests.get(test_url, headers=headers, timeout=10)
    soup = requests.get(test_url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.content, 'html.parser')
    
    # Look for images
    imgs = soup.find_all('img')
    print(f'Images found: {len(imgs)}')
    
    # Look for description
    paras = soup.find_all('p')
    print(f'Paragraphs found: {len(paras)}')
    if paras:
        first_p = paras[0].get_text(strip=True)
        print(f'First paragraph: {first_p[:100]}...')
    
    print()

# Check blog page
print('\n🔍 Analyzing blog structure...\n')

r = requests.get(f'{base_url}/blog', headers=headers, timeout=10)
soup = BeautifulSoup(r.content, 'html.parser')

title = soup.find('title')
print(f'Blog page: {base_url}/blog')
print(f'Title: {title.get_text() if title else "No title"}')
print()

# Find blog posts
blog_links = []
for link in soup.find_all('a', href=lambda x: x and '/blog/' in x):
    href = link.get('href', '')
    text = link.get_text(strip=True)
    if text and len(text) > 5 and href.count('/') > 3:  # Must be actual post, not category
        if href not in [b[1] for b in blog_links]:
            blog_links.append((text, href))

print(f'Found {len(blog_links)} blog post links:')
for text, href in blog_links[:10]:
    print(f'  {text:50} -> {href}')

print()

# Look for logo
print('\n🔍 Looking for logo...\n')

r = requests.get(base_url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, 'html.parser')

# Try different approaches
logo = soup.find('img', class_=lambda x: x and 'logo' in x.lower())
if not logo:
    logo = soup.find('img', alt=lambda x: x and 'logo' in x.lower())
if not logo:
    logo = soup.find('img', src=lambda x: x and 'logo' in x.lower())

if logo:
    print(f'Logo found: {logo.get("src", "")[:100]}')
else:
    # Try to find header/nav images
    header = soup.find('header')
    if header:
        imgs = header.find_all('img')
        if imgs:
            print(f'Header images: {len(imgs)} found')
            for i, img in enumerate(imgs[:3]):
                src = img.get('src', '')
                alt = img.get('alt', '')
                print(f'  {i+1}. {alt:30} -> {src[:80]}')
    else:
        print('No logo found, checking homepage images...')
        imgs = soup.find_all('img')[:5]
        for img in imgs:
            alt = img.get('alt', '')
            src = img.get('src', '')
            if 'halcon' in src.lower() or 'logo' in alt.lower():
                print(f'  Potential logo: {src[:80]}')
