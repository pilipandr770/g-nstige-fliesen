"""
Analyze Baldocer products page
"""
import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

base_url = 'https://baldocer.com'

print("="*80)
print("BALDOCER PRODUCTS ANALYSIS")
print("="*80)

# 1. Main products page
print("\n1. PRODUCTS PAGE")
print("-"*80)
try:
    response = requests.get(base_url + '/producto/', headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all links to products/collections
    all_links = soup.find_all('a', href=True)
    
    collection_links = []
    for link in all_links:
        href = link.get('href')
        # Filter product links
        if href and '/producto/' in href and href.count('/') > 2:
            text = link.get_text(strip=True)
            if text and len(text) < 80:
                collection_links.append((text, href))
    
    # Remove duplicates
    unique_collections = {}
    for text, href in collection_links:
        if href not in unique_collections:
            unique_collections[href] = text
    
    print(f"Found {len(unique_collections)} unique collections")
    
    for idx, (href, text) in enumerate(list(unique_collections.items())[:15], 1):
        print(f"\n  {idx}. {text}")
        print(f"     URL: {href}")
        
        # Check if has image
        # Find the link element again
        link_elem = soup.find('a', href=href)
        if link_elem:
            img = link_elem.find('img')
            if not img and link_elem.parent:
                img = link_elem.parent.find('img')
            
            if img:
                src = img.get('src') or img.get('data-src')
                if src:
                    print(f"     Image: {src[:60]}...")
        
except Exception as e:
    print(f"Error: {str(e)}")

# 2. Check news/blog page
print("\n\n2. NEWS PAGE")
print("-"*80)
try:
    response = requests.get(base_url + '/noticias/', headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find news/blog links
    news_links = soup.find_all('a', href=re.compile(r'/noticias/.+'))
    
    unique_news = {}
    for link in news_links:
        href = link.get('href')
        if href and href.count('/') > 2:  # Only full articles
            text = link.get_text(strip=True)
            if text and len(text) > 5:
                unique_news[href] = text
    
    print(f"Found {len(unique_news)} news articles")
    
    for idx, (href, text) in enumerate(list(unique_news.items())[:5], 1):
        print(f"\n  {idx}. {text[:60]}")
        print(f"     URL: {href}")
        
except Exception as e:
    print(f"Error: {str(e)}")

print("\n" + "="*80)
