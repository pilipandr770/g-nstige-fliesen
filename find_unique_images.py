import requests
from bs4 import BeautifulSoup

url = 'https://www.halconceramicas.com/colecciones/coleccion-capri'
resp = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(resp.content, 'html.parser')

print("Looking for collection-specific images...")
print("\nAll /storage/ images with 'capri' in the filename:")

imgs = soup.find_all('img')
capri_imgs = []
for img in imgs:
    src = img.get('src', '')
    if '/storage/' in src.lower() and 'capri' in src.lower():
        capri_imgs.append(src)
        short = src.split('/storage/')[-1][:80]
        print(f"  {short}")

print(f"\nFound {len(capri_imgs)} images with 'capri' in filename")

# Also look for images in a specific location on page
print("\nChecking image parent elements...")
for img in imgs[:30]:
    src = img.get('src', '')
    if '/storage/' in src and 'medium' in src.lower():
        parent = img.parent
        parent_classes = parent.get('class', []) if parent else []
        parent_id = parent.get('id', '') if parent else ''
        if 'capri' in src.lower() or 'product' in str(parent_classes).lower():
            print(f"  Parent: {parent_classes} {parent_id}")
            print(f"    Image: {src.split('/storage/')[-1][:60]}")
