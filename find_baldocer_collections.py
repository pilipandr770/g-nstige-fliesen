"""
Find all Baldocer collections from main product page
"""
import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

base_url = 'https://baldocer.com'

print("="*80)
print("BALDOCER ALL COLLECTIONS")
print("="*80)

try:
    response = requests.get(base_url + '/producto/', headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print(f"Status: {response.status_code}\n")
    
    # Find all links
    links = soup.find_all('a', href=True)
    
    collections = {}
    
    for link in links:
        href = link.get('href')
        
        # Skip if not a product link
        if not href or '/producto/' not in href:
            continue
        
        # Clean URL
        if href.startswith('/'):
            href = base_url + href
        
        # Extract path
        path = href.replace(base_url, '').replace('/producto/', '')
        
        # Skip categories and empty
        if not path or path == '/' or not path.strip('/'):
            continue
        
        # Single level products are collections (e.g., /producto/stoneland/)
        parts = path.strip('/').split('/')
        if len(parts) == 1:  # Single name = collection
            text = link.get_text(strip=True)
            if text and len(text) > 1 and len(text) < 100:
                collections[href] = text
    
    print(f"Found {len(collections)} unique collections\n")
    
    for idx, (href, text) in enumerate(list(collections.items())[:30], 1):
        print(f"{idx}. {text}")
        print(f"   URL: {href}")
        print()
    
    # Also try another approach: look for specific patterns in HTML
    print("\n" + "="*80)
    print("SEARCHING FOR COLLECTION PATTERNS")
    print("="*80 + "\n")
    
    # Look for image+link combos
    all_imgs = soup.find_all('img')
    print(f"Total images on page: {len(all_imgs)}\n")
    
    # Find images with product/collection URLs
    collection_images = []
    for img in all_imgs:
        src = img.get('src') or img.get('data-src')
        if src and '/uploads/' in src:
            # Find parent link
            parent = img.find_parent('a')
            if parent:
                href = parent.get('href')
                if href and '/producto/' in href:
                    # Extract collection name from URL
                    match = re.search(r'/producto/([^/]+)/?$', href)
                    if match:
                        collection_name = match.group(1)
                        alt = img.get('alt', collection_name)
                        collection_images.append((collection_name, href, src, alt))
    
    # Remove duplicates
    unique_img_collections = {}
    for name, href, src, alt in collection_images:
        if name not in unique_img_collections:
            unique_img_collections[name] = (href, src, alt)
    
    print(f"Found {len(unique_img_collections)} collections with images\n")
    
    for idx, (name, (href, src, alt)) in enumerate(list(unique_img_collections.items())[:20], 1):
        print(f"{idx}. {name} ({alt})")
        print(f"   URL: {href}")
        print(f"   Image: {src[:100]}")
        print()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
