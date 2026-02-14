"""
Find collections inside porcelanico category
"""
import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

base_url = 'https://baldocer.com'
category_url = base_url + '/producto/porcelanico/'

print("="*80)
print("PORCELANICO CATEGORY - COLLECTIONS")
print("="*80)

try:
    response = requests.get(category_url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print(f"Status: {response.status_code}\n")
    
    # Look for all images with parent links
    all_imgs = soup.find_all('img')
    print(f"Total images: {len(all_imgs)}\n")
    
    collections = {}
    
    for img in all_imgs:
        # Find parent link
        parent_link = img.find_parent('a')
        if not parent_link:
            continue
        
        href = parent_link.get('href')
        if not href:
            continue
        
        # Check if it's a collection link (deeper than category)
        # /producto/porcelanico/collection-name
        match = re.search(r'/producto/porcelanico/([^/]+)/?$', href)
        if match:
            collection_slug = match.group(1)
            
            # Get text
            text = parent_link.get_text(strip=True) or img.get('alt', '') or collection_slug
            
            # Get image
            src = img.get('src') or img.get('data-src')
            
            if collection_slug not in collections:
                collections[collection_slug] = {
                    'name': text,
                    'url': href,
                    'image': src
                }
    
    print(f"Found {len(collections)} collections\n")
    
    for idx, (slug, data) in enumerate(collections.items(), 1):
        print(f"{idx}. {data['name']}")
        print(f"   Slug: {slug}")
        print(f"   URL: {data['url']}")
        if data['image']:
            print(f"   Image: {data['image'][:100]}")
        print()
    
    # If no collections found, check what links exist
    if len(collections) == 0:
        print("\nNo collections found. Checking all links on page...\n")
        all_links = soup.find_all('a', href=True)
        product_links = [l for l in all_links if '/producto/' in l.get('href', '')]
        print(f"Total product links: {len(product_links)}\n")
        
        for link in product_links[:15]:
            href = link.get('href')
            text = link.get_text(strip=True)
            print(f"- {text[:50]}")
            print(f"  {href}")
            print()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
