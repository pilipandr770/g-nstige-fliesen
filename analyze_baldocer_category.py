"""
Analyze Baldocer category page (porcelanico)
"""
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

base_url = 'https://baldocer.com'

print("="*80)
print("BALDOCER CATEGORY: PORCELANICO")
print("="*80)

try:
    response = requests.get(base_url + '/producto/porcelanico/', headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print(f"Status: {response.status_code}\n")
    
    # Find all links starting from /producto/porcelanico/
    links = soup.find_all('a', href=True)
    
    collection_links = []
    for link in links:
        href = link.get('href')
        # Collection links should be deeper: /producto/porcelanico/collection-name
        if href and '/producto/porcelanico/' in href and href.count('/') > 3:
            text = link.get_text(strip=True)
            if text and len(text) > 1 and len(text) < 80:
                collection_links.append((text, href))
    
    # Remove duplicates
    unique_collections = {}
    for text, href in collection_links:
        if href not in unique_collections:
            unique_collections[href] = text
    
    print(f"Found {len(unique_collections)} collections in porcelanico category\n")
    
    for idx, (href, text) in enumerate(list(unique_collections.items())[:15], 1):
        print(f"{idx}. {text}")
        print(f"   URL: {href}")
        
        # Find image
        link_elem = soup.find('a', href=href)
        if link_elem:
            # Search for img
            img = link_elem.find('img')
            if not img:
                # Try parent
                parent = link_elem.parent
                if parent:
                    img = parent.find('img')
                    if not img:
                        # Try parent of parent
                        grandparent = parent.parent
                        if grandparent:
                            img = grandparent.find('img')
            
            if img:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src:
                    print(f"   Image: {src}")
        print()
    
    # Also check divs/sections that might contain collections
    print("\nSearching for collection containers...")
    divs_with_class = soup.find_all(['div', 'article', 'section'], class_=True)
    classes_found = set()
    for div in divs_with_class:
        classes = div.get('class', [])
        for cls in classes:
            if any(keyword in cls.lower() for keyword in ['product', 'collection', 'item', 'card', 'serie']):
                classes_found.add(cls)
    
    if classes_found:
        print("Relevant classes found:")
        for cls in sorted(list(classes_found))[:10]:
            print(f"  - {cls}")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
