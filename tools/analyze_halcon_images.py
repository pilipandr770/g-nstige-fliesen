#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0'}

# Check one collection page structure
url = 'https://www.halconceramicas.com/colecciones/coleccion-capri'
r = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(r.content, 'html.parser')

print(f'Analyzing: {url}\n')

# Look at all img tags
img_tags = soup.find_all('img')
print(f'Total images found: {len(img_tags)}\n')

for i, img in enumerate(img_tags[:15], 1):
    src = img.get('src', '')
    alt = img.get('alt', '')
    
    # Get parent info
    parent = img.parent
    parent_class = parent.get('class', []) if parent else []
    
    print(f'{i}. {alt[:40]:40} -> {src[-80:]:80}')
    print(f'   Parent: <{parent.name} class="{" ".join(parent_class)}">')
    print()
