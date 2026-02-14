"""
Check Baldocer HTML structure
"""
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

url = 'https://baldocer.com/producto/porcelanico/'

try:
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print("Status:", response.status_code)
    print()
    
    # Find main content area
    main = soup.find('main') or soup.find('div', {'id': 'main'}) or soup.find('div', {'class': 'main'})
    if main:
        print("Found main content area")
        print()
        
        # Find all divs with classes in main
        divs = main.find_all('div', class_=True, limit=50)
        print(f"First 20 divs with classes in main:")
        for idx, div in enumerate(divs[:20], 1):
            classes = ' '.join(div.get('class', []))
            # Check for links/images
            has_link = bool(div.find('a'))
            has_img = bool(div.find('img'))
            
            print(f"{idx}. class=\"{classes}\" | link={has_link} img={has_img}")
            
            if has_link and has_img:
                link = div.find('a')
                img = div.find('img')
                print(f"   -> Link: {link.get('href', 'N/A')[:80]}")
                print(f"   -> Img: {(img.get('src') or img.get('data-src', 'N/A'))[:80]}")
        
        print()
        
        # Check for specific sections
        print("Looking for series/collections containers...")
        for tag in ['section', 'article', 'div']:
            for keyword in ['serie', 'product', 'collection', 'item', 'portfolio']:
                elements = main.find_all(tag, class_=lambda x: x and keyword in str(x).lower())
                if elements:
                    print(f"Found {len(elements)} {tag} with class containing '{keyword}'")
                    for elem in elements[:2]:
                        print(f"  Class: {elem.get('class')}")
    else:
        print("No main content area found")
        print()
        print("Page title:", soup.find('title'))
        print()
        print("Sample of all divs:")
        divs = soup.find_all('div', class_=True, limit=30)
        for idx, div in enumerate(divs[:15], 1):
            classes = ' '.join(div.get('class', []))
            print(f"{idx}. {classes}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
