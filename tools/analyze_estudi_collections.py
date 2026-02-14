#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

base_url = "https://eceramico.com/en"

# Check collections page more carefully
print("=== COLLECTIONS PAGE - DETAILED ===")
url = urljoin(base_url, "/collections/")
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
soup = BeautifulSoup(response.content, 'html.parser')

# Look for all links and their containers
print("\nAll links on collections page:")
all_links = soup.find_all('a', href=True)
unique_hrefs = set()
for a in all_links:
    href = a.get('href')
    if '/collection' in href.lower() or '/tile' in href.lower() or '/serie' in href.lower():
        if href not in unique_hrefs:
            unique_hrefs.add(href)
            text = a.get_text(strip=True)[:60]
            print(f"  {href[:80]} -> '{text}'")

# Look for article/post elements
print("\nArticle/post-like elements:")
articles = soup.find_all(['article', 'div'], class_=lambda x: x and ('post' in str(x).lower() or 'item' in str(x).lower() or 'tile' in str(x).lower()))
print(f"Found {len(articles)} article-like elements")
if articles:
    for article in articles[:3]:
        # Find link in article
        link = article.find('a', href=True)
        if link:
            print(f"  Article link: {link.get('href')[:80]}")
            # Find image
            img = article.find('img')
            if img:
                print(f"    Image: {img.get('src')[:80]}")

# Check if there's a specific collections listing (maybe it's paginated or loaded via JS)
print("\nLooking for tile series/collections containers:")
tile_containers = soup.find_all(['div', 'section'], class_=lambda x: x and any(k in str(x).lower() for k in ['series', 'collection', 'product', 'catalog']))
print(f"Found {len(tile_containers)} containers")
for i, container in enumerate(tile_containers[:3]):
    titles = container.find_all(['h2', 'h3', 'h4'])
    print(f"  Container {i}: {len(titles)} titles found")
    for title in titles[:2]:
        print(f"    - {title.get_text(strip=True)[:60]}")
