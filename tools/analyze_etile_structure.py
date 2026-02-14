#!/usr/bin/env python3
"""
Deep analysis of Etile website structure
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

base_url = "https://de.etile.es"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("=== ETILE WEBSITE STRUCTURE ANALYSIS ===\n")

# Fetch main page
print(f"Fetching {base_url}...")
response = requests.get(base_url, headers=headers, timeout=20)
soup = BeautifulSoup(response.content, 'html.parser')

# Find all links with keywords
print("\n=== All links containing 'kolle' or 'proje' or 'news' ===")
all_links = set()
for link in soup.find_all('a', href=True):
    href = link.get('href', '')
    text = link.get_text(strip=True)
    href_lower = href.lower()
    
    if any(word in href_lower for word in ['kolle', 'proje', 'news', 'blog', 'neuig', 'article']):
        full_url = urljoin(base_url, href)
        all_links.add((text, full_url))
        print(f"  {text}: {full_url}")

# Try structure discovery
print("\n=== Trying standard WordPress URLs ===")
wp_urls = [
    f"{base_url}/",
    f"{base_url}/sitemap.xml",
    f"{base_url}/wp-sitemap.xml",
]

for url in wp_urls:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200 and 'sitemap' in url:
            print(f"\n{url}: Found sitemap!")
            # Parse sitemap to find collection URLs
            sitemap_soup = BeautifulSoup(r.content, 'xml')
            for loc in sitemap_soup.find_all('loc')[:30]:
                loc_url = loc.text
                if any(word in loc_url.lower() for word in ['kolle', 'proje', 'product']):
                    print(f"    {loc_url}")
    except:
        pass

# Check page structure
print("\n=== Page structure analysis ===")
# Look for main content areas
main = soup.find('main') or soup.find('div', class_=lambda x: x and 'content' in x.lower())
if main:
    # Count element types
    sections = main.find_all(['section', 'article', 'div'], class_=lambda x: x and any(k in str(x).lower() for k in ['product', 'kollek', 'proje']))
    print(f"Found {len(sections)} potential content sections")
    for sec in sections[:5]:
        classes = sec.get('class', [])
        print(f"  {sec.name}: {' '.join(classes)}")

# Try to get sitemap
print("\n=== Sitemap extraction ===")
try:
    sitemap_url = f"{base_url}/sitemap.xml"
    r = requests.get(sitemap_url, headers=headers, timeout=10)
    if r.status_code == 200:
        lines = r.text.split('\n')
        collection_urls = [line for line in lines if 'kolle' in line.lower() or 'product' in line.lower()]
        print(f"Collection URLs in sitemap:")
        for url_line in collection_urls[:10]:
            if '<loc>' in url_line:
                url = url_line.replace('<loc>', '').replace('</loc>', '').strip()
                print(f"  {url}")
except Exception as e:
    print(f"Error fetching sitemap: {e}")

# Look at page menus
print("\n=== Menu analysis ===")
menus = soup.find_all(['nav', 'menu', 'ul'], class_=lambda x: x and ('menu' in str(x).lower() or 'nav' in str(x).lower()))
for i, menu in enumerate(menus[:3]):
    print(f"\nMenu {i+1}:")
    for link in menu.find_all('a', limit=15):
        print(f"  {link.get_text(strip=True)}: {link.get('href')}")
