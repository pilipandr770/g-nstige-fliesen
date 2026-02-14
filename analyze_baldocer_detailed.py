"""
Detailed Baldocer structure analysis
"""
import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

base_url = 'https://baldocer.com'

print("="*80)
print("BALDOCER DETAILED STRUCTURE")
print("="*80)

# Try different language versions
for lang in ['', '/es', '/en', '/de']:
    print(f"\n{'='*80}")
    print(f"LANGUAGE: {lang if lang else '(default)'}")
    print(f"{'='*80}")
    
    try:
        url = base_url + lang
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find menu/navigation
        nav = soup.find(['nav', 'menu', 'ul'], class_=lambda x: x and 'menu' in str(x).lower())
        if nav:
            print("\nMenu found! Links:")
            menu_links = nav.find_all('a', href=True)
            for link in menu_links[:15]:
                href = link.get('href')
                text = link.get_text(strip=True)
                if text and len(text) < 50:
                    print(f"  {text}: {href}")
        
        # Try to find products/collections
        print("\nSearching for product/collection links...")
        links = soup.find_all('a', href=True)
        product_keywords = ['product', 'collection', 'serie', 'coleccion', 'kollektion']
        
        found_products = []
        for link in links:
            href = link.get('href', '').lower()
            for keyword in product_keywords:
                if keyword in href and len(href) > 10:
                    text = link.get_text(strip=True)
                    if text:
                        found_products.append((text[:40], href[:60]))
                    break
        
        if found_products:
            print(f"Found {len(found_products)} product-related links:")
            for text, href in found_products[:10]:
                print(f"  {text}: {href}")
        
        # Search for project links
        print("\nSearching for project links...")
        project_keywords = ['project', 'proyecto', 'referenz', 'work']
        found_projects = []
        for link in links:
            href = link.get('href', '').lower()
            for keyword in project_keywords:
                if keyword in href and len(href) > 10:
                    text = link.get_text(strip=True)
                    if text:
                        found_projects.append((text[:40], href[:60]))
                    break
        
        if found_projects:
            print(f"Found {len(found_projects)} project-related links:")
            for text, href in found_projects[:10]:
                print(f"  {text}: {href}")
        
        # Only check first language version in detail
        if not lang:
            break
            
    except Exception as e:
        print(f"Error for {lang}: {str(e)}")

print("\n" + "="*80)
