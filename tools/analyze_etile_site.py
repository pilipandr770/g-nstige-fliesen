#!/usr/bin/env python3
"""
Analyze Etile website structure
"""
import requests
from bs4 import BeautifulSoup
import re

base_url = "https://de.etile.es"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Fetch main page
print(f"Fetching {base_url}...")
response = requests.get(base_url, headers=headers, timeout=20)
soup = BeautifulSoup(response.content, 'html.parser')

print(f"Status: {response.status_code}")
print(f"Title: {soup.find('title').text if soup.find('title') else 'No title'}")

# Look for menu/navigation
print("\n=== Navigation Links ===")
nav = soup.find('nav') or soup.find(['header', 'ul'])
if nav:
    for link in nav.find_all('a', limit=20):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if href and text:
            print(f"  {text}: {href}")

# Look for collections page
print("\n=== Looking for Collections/Products ===")
collection_patterns = [
    r'/colecciones',
    r'/collections',
    r'/kategorien',
    r'/kategorias',
    r'/productos',
    r'/products'
]

for link in soup.find_all('a'):
    href = link.get('href', '').lower()
    text = link.get_text(strip=True)
    if any(pattern in href for pattern in collection_patterns):
        print(f"  {text}: {link.get('href')}")

# Look for logo
print("\n=== Logo ===")
for img in soup.find_all('img'):
    alt = img.get('alt', '').lower()
    src = img.get('src', '')
    if 'logo' in alt or (src and 'logo' in src.lower()):
        print(f"  {alt}: {src}")
        break

# Look for projects
print("\n=== Looking for Projects/Inspirations ===")
project_patterns = [
    r'/proyectos',
    r'/projects',
    r'/inspirationen',
    r'/inspirations',
    r'/realizaciones'
]

for link in soup.find_all('a'):
    href = link.get('href', '').lower()
    text = link.get_text(strip=True)
    if any(pattern in href for pattern in project_patterns):
        print(f"  {text}: {link.get('href')}")

# Look for blog
print("\n=== Looking for Blog/News ===")
blog_patterns = [
    r'/blog',
    r'/news',
    r'/aktualizaciones',
    r'/actualidades',
    r'/novedades'
]

for link in soup.find_all('a'):
    href = link.get('href', '').lower()
    text = link.get_text(strip=True)
    if any(pattern in href for pattern in blog_patterns):
        print(f"  {text}: {link.get('href')}")

# Check if there's a collection/products listing
print("\n=== Common product/collection URLs to try ===")
urls_to_try = [
    f"{base_url}/colecciones",
    f"{base_url}/collections",
    f"{base_url}/kategorien",
    f"{base_url}/produtos",
    f"{base_url}/products",
    f"{base_url}/en/collections"
]

for url in urls_to_try:
    try:
        r = requests.head(url, headers=headers, timeout=10)
        print(f"  {url}: {r.status_code}")
    except:
        pass
