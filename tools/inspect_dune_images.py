#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys
import os

# Add parent dir to path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

url = "https://duneceramics.com/de/serien/agadir"

response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
soup = BeautifulSoup(response.content, 'html.parser')

# Find all img tags and print their structure
print("\n=== ALL IMG TAGS ===")
img_count = 0
src_counts = {}

for img in soup.find_all('img'):
    src = img.get('src') or img.get('data-src') or img.get('data-lazy')
    if not src:
        continue
    
    # Skip data URIs
    if src.startswith('data:'):
        continue
    
    # Normalize URL
    if not src.startswith('http'):
        src = urljoin(url, src)
    
    img_count += 1
    
    # Count occurrences
    if src not in src_counts:
        src_counts[src] = 0
    src_counts[src] += 1

print(f"\nTotal img tags: {img_count}")
print(f"Unique image URLs: {len(src_counts)}")

print("\n=== Image URL frequency ===")
for src, count in sorted(src_counts.items(), key=lambda x: -x[1]):
    if count > 1 or 'logo' not in src.lower():
        print(f"  {count}x {src[:100]}")

# Also check main image containers/galleries
print("\n=== Looking for gallery/collection containers ===")
gallery_divs = soup.find_all(['div', 'figure', 'section'], class_=lambda x: x and ('gallery' in x.lower() or 'product' in x.lower() or 'image' in x.lower()))
print(f"Found {len(gallery_divs)} potential gallery containers")

for i, div in enumerate(gallery_divs[:5]):
    print(f"\nContainer {i}: {div.name} class={div.get('class')}")
    imgs = div.find_all('img')
    print(f"  Contains {len(imgs)} images")
    for j, img in enumerate(imgs[:3]):
        src = img.get('src') or img.get('data-src')
        if src:
            print(f"    {j}: {src[:80]}")
