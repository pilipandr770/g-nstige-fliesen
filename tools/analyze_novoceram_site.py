import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

base_url = 'https://www.novoceram.fr'

print(f"Analyzing Novoceram site structure...")
print(f"Base URL: {base_url}\n")

# Try different possible paths for collections
possible_paths = [
    '/colecciones',
    '/collections',
    '/productos',
    '/products',
    '/catalogo',
    '/catalog',
    '/categorias',
    '/categories',
    '/tienda',
]

for path in possible_paths:
    try:
        url = urljoin(base_url, path)
        resp = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'html.parser')
            links = len(soup.find_all('a'))
            title = soup.title.string if soup.title else 'No title'
            print(f"✓ {path}: {resp.status_code} - {title[:50]}")
            print(f"  Links found: {links}\n")
    except Exception as e:
        pass

# Check homepage for navigation
print("\nChecking homepage navigation...")
try:
    resp = requests.get(base_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(resp.content, 'html.parser')
    
    # Look for nav elements
    nav = soup.find('nav') or soup.find('header')
    if nav:
        print("Navigation found:")
        for link in nav.find_all('a', limit=15):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            if text:
                print(f"  - {text[:40]} → {href[:60]}")
except Exception as e:
    print(f"Error: {e}")
