#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from collections import Counter

url = "https://eceramico.com/en"

print(f"Fetching: {url}")
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
soup = BeautifulSoup(response.content, 'html.parser')

# Check main structure
print("\n=== Page Structure ===")
print(f"Title: {soup.title.string if soup.title else 'N/A'}")

# Look for collections/products links
print("\n=== Navigation Links ===")
nav_links = soup.find_all('a', href=True)
collection_links = [a for a in nav_links if any(x in a.get('href', '').lower() for x in ['collection', 'product', 'catalog', 'series', 'category'])]
print(f"Found {len(collection_links)} collection-like links")
for a in collection_links[:10]:
    href = a.get('href')
    text = a.get_text(strip=True)[:50]
    print(f"  {href[:60]} -> {text}")

# Check for main menus
print("\n=== Menu Structure ===")
menus = soup.find_all(['nav', 'menu'], class_=lambda x: x and ('menu' in str(x).lower() or 'nav' in str(x).lower()))
print(f"Found {len(menus)} menu elements")
for menu in menus[:3]:
    menu_links = menu.find_all('a', href=True)
    print(f"  Menu with {len(menu_links)} links")
    for a in menu_links[:5]:
        href = a.get('href')
        text = a.get_text(strip=True)[:40]
        print(f"    {href[:50]} -> {text}")

# Check for blog/news section
print("\n=== Blog/News ===")
blog_links = [a for a in nav_links if any(x in a.get('href', '').lower() for x in ['blog', 'news', 'article', 'post'])]
print(f"Found {len(blog_links)} blog-like links")
for a in blog_links[:5]:
    href = a.get('href')
    text = a.get_text(strip=True)[:50]
    print(f"  {href[:60]} -> {text}")

# Check for projects/showcase
print("\n=== Projects ===")
project_links = [a for a in nav_links if any(x in a.get('href', '').lower() for x in ['project', 'portfolio', 'gallery', 'showcase'])]
print(f"Found {len(project_links)} project-like links")
for a in project_links[:5]:
    href = a.get('href')
    text = a.get_text(strip=True)[:50]
    print(f"  {href[:60]} -> {text}")
