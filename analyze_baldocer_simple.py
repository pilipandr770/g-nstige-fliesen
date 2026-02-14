"""
Simple Baldocer site analysis
"""
import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

base_url = 'https://baldocer.com'

print("="*80)
print("BALDOCER SITE ANALYSIS")
print("="*80)

# 1. Test main page
print("\n1. MAIN PAGE")
print("-"*80)
try:
    response = requests.get(base_url, headers=headers, timeout=15, allow_redirects=True)
    print(f"Status: {response.status_code}")
    print(f"URL: {response.url}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title')
        if title:
            print(f"Title: {title.get_text()}")
        
        # Find logo
        print("\n2. LOGO SEARCH")
        img_logo = soup.find('img', src=re.compile(r'logo', re.I))
        if img_logo:
            print(f"Logo found: {img_logo.get('src')}")
        
        # Find all links to check structure
        print("\n3. NAVIGATION LINKS (first 20)")
        links = soup.find_all('a', href=True)
        unique_paths = set()
        for link in links[:50]:
            href = link.get('href')
            if href and href.startswith('/') and len(href) > 2:
                # Get first 2-3 segments
                parts = href.split('/')[:3]
                path = '/'.join(parts)
                unique_paths.add(path)
        
        for path in sorted(list(unique_paths))[:20]:
            print(f"  {path}")
        
except Exception as e:
    print(f"Error: {str(e)}")

# 4. Check common sections
print("\n4. CHECKING SECTIONS")
print("-"*80)
test_urls = [
    '/products',
    '/collections',
    '/proyectos',
    '/projects',
    '/blog',
    '/noticias',
    '/es',
    '/en',
    '/de'
]

for path in test_urls:
    try:
        url = base_url + path
        r = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
        if r.status_code == 200:
            print(f"  OK: {path} -> {r.status_code}")
    except:
        pass

print("\n" + "="*80)
