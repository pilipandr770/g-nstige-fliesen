import requests
from bs4 import BeautifulSoup

test_urls = [
    'https://www.halconceramicas.com/colecciones/coleccion-capri',
    'https://www.halconceramicas.com/colecciones/coleccion-tempo',
    'https://www.halconceramicas.com/colecciones/coleccion-mood'
]

for url in test_urls:
    name = url.split('/')[-1]
    print(f'\n{name}:')
    try:
        resp = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        imgs = soup.find_all('img')
        storage_imgs = [img.get('src', '') for img in imgs if '/storage/' in img.get('src', '').lower()]
        
        print(f'  Total /storage/ images: {len(storage_imgs)}')
        seen_hashes = set()
        for i, img in enumerate(storage_imgs[:15]):
            # Extract hash from filename to see if images are shared
            parts = img.split('/')
            filename = parts[-1] if parts else ''
            
            # Check if this image appears on other collection pages
            if 'medium' in img:
                tag = 'MEDIUM'
            elif any(coll in img.lower() for coll in ['capri', 'tempo', 'mood']):
                tag = 'UNIQUE'
            else:
                tag = 'SHARED'
            
            short = img.split('/storage/')[-1][:65]
            if filename:
                # Extract just the filename before query params
                fn = filename.split('?')[0]
                if fn not in seen_hashes:
                    print(f'    {i+1}. [{tag}] {short}')
                    seen_hashes.add(fn)
    except Exception as e:
        print(f'  Error: {e}')
