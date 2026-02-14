#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

base_url = "https://eceramico.com/en"

# Check collections page
print("=== COLLECTIONS PAGE ===")
url = urljoin(base_url, "/collections/")
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
soup = BeautifulSoup(response.content, 'html.parser')

collection_items = soup.find_all(['a', 'div'], class_=lambda x: x and ('collection' in str(x).lower() or 'item' in str(x).lower() or 'product' in str(x).lower() or 'card' in str(x).lower()))
print(f"Found {len(collection_items)} collection items")

# Look for actual collection links
all_links = soup.find_all('a', href=True)
collection_links = [a for a in all_links if '/collections/' in a.get('href') and a.get('href') != urljoin(base_url, '/collections/')]
print(f"Found {len(collection_links)} links to specific collections")
for a in collection_links[:5]:
    href = a.get('href')
    text = a.get_text(strip=True)[:50]
    print(f"  {href} -> {text}")

# Check one collection detail page to see structure
if collection_links:
    first_collection = urljoin(base_url, collection_links[0].get('href'))
    print(f"\n=== SAMPLE COLLECTION PAGE ===")
    print(f"URL: {first_collection}")
    response = requests.get(first_collection, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Look for title
    title = soup.find(['h1', 'h2', 'header'])
    if title:
        print(f"Title: {title.get_text(strip=True)[:80]}")
    
    # Look for images
    imgs = soup.find_all('img')
    print(f"Images on page: {len(imgs)}")
    good_imgs = [img for img in imgs if img.get('src') and not 'logo' in img.get('src').lower()]
    print(f"Non-logo images: {len(good_imgs)}")
    if good_imgs:
        print(f"  Sample: {good_imgs[0].get('src')[:80]}")
    
    # Look for description
    desc = soup.find(['div', 'p'], class_=lambda x: x and ('description' in str(x).lower() or 'intro' in str(x).lower() or 'content' in str(x).lower()))
    if desc:
        text = desc.get_text(strip=True)[:100]
        print(f"Description: {text}...")

# Check blog page
print("\n=== BLOG PAGE ===")
url = urljoin(base_url, "/blog/")
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
soup = BeautifulSoup(response.content, 'html.parser')

blog_links = soup.find_all('a', href=lambda x: x and '/blog/' in x)
blog_articles = [a for a in blog_links if a.get('href') != urljoin(base_url, '/blog/')]
print(f"Found {len(blog_articles)} blog article links (first 5):")
for a in blog_articles[:5]:
    href = a.get('href')
    text = a.get_text(strip=True)[:50]
    print(f"  {href} -> {text}")

# Check projects page
print("\n=== PROJECTS PAGE ===")
url = urljoin(base_url, "/projects/")
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
soup = BeautifulSoup(response.content, 'html.parser')

project_links = soup.find_all('a', href=lambda x: x and '/projects/' in x)
projects = [a for a in project_links if a.get('href') != urljoin(base_url, '/projects/')]
print(f"Found {len(projects)} project links (first 5):")
for a in projects[:5]:
    href = a.get('href')
    text = a.get_text(strip=True)[:50]
    print(f"  {href} -> {text}")

print("\n=== LOGO CHECK ===")
response = requests.get(base_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
soup = BeautifulSoup(response.content, 'html.parser')
logo_candidates = soup.find_all('img', alt=lambda x: x and 'logo' in x.lower())
print(f"Found {len(logo_candidates)} logo images")
if logo_candidates:
    print(f"  Sample: {logo_candidates[0].get('src')[:80]}")
