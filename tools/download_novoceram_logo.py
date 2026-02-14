"""Download Novoceram logo"""
import requests
from bs4 import BeautifulSoup
import hashlib
import os

url = 'https://www.novoceram.fr'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

r = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(r.content, 'html.parser')

# Find logo
candidates = []

# Check header/nav for logo
for img in soup.find_all('img'):
    src = img.get('src', '') or img.get('data-src', '')
    alt = img.get('alt', '')
    cls = ' '.join(img.get('class', []))
    if 'logo' in src.lower() or 'logo' in alt.lower() or 'logo' in cls.lower():
        candidates.append(('img-logo', src, alt))

# Check SVG logos
for svg in soup.find_all('svg'):
    cls = ' '.join(svg.get('class', []))
    if 'logo' in cls.lower():
        candidates.append(('svg-logo', str(svg)[:100], cls))

# Check link icons
for link in soup.find_all('link', rel=True):
    rel = ' '.join(link.get('rel', []))
    if 'icon' in rel:
        candidates.append(('link-icon', link.get('href', ''), rel))

# Check meta og:image
meta = soup.find('meta', property='og:image')
if meta:
    candidates.append(('og:image', meta.get('content', ''), ''))

# Check header
header = soup.find('header')
if header:
    for img in header.find_all('img'):
        src = img.get('src', '') or img.get('data-src', '')
        candidates.append(('header-img', src, img.get('alt', '')))
    for svg in header.find_all('svg'):
        candidates.append(('header-svg', str(svg)[:200], ''))

print("Logo candidates found:")
for type_, src, extra in candidates:
    print(f"  [{type_}] {src[:120]} | {extra}")

# Try downloading first good candidate
for type_, src, _ in candidates:
    if type_ in ('img-logo', 'header-img', 'og:image', 'link-icon') and src.startswith('http'):
        print(f"\nDownloading: {src}")
        try:
            resp = requests.get(src, headers=headers, timeout=15)
            if resp.status_code == 200 and len(resp.content) > 500:
                url_hash = hashlib.md5(src.encode()).hexdigest()[:10]
                ext = os.path.splitext(src.split('?')[0])[1] or '.png'
                if len(ext) > 5:
                    ext = '.png'
                filename = f"novoceram_{url_hash}{ext}"
                filepath = os.path.join('app', 'static', 'uploads', 'manufacturers', filename)
                with open(filepath, 'wb') as f:
                    f.write(resp.content)
                print(f"Saved: {filename} ({len(resp.content)} bytes)")
                break
        except Exception as e:
            print(f"Error: {e}")
    elif type_ in ('img-logo', 'header-img') and src.startswith('/'):
        full_url = f"https://www.novoceram.fr{src}"
        print(f"\nDownloading: {full_url}")
        try:
            resp = requests.get(full_url, headers=headers, timeout=15)
            if resp.status_code == 200 and len(resp.content) > 500:
                url_hash = hashlib.md5(full_url.encode()).hexdigest()[:10]
                ext = os.path.splitext(src.split('?')[0])[1] or '.png'
                if len(ext) > 5:
                    ext = '.png'
                filename = f"novoceram_{url_hash}{ext}"
                filepath = os.path.join('app', 'static', 'uploads', 'manufacturers', filename)
                with open(filepath, 'wb') as f:
                    f.write(resp.content)
                print(f"Saved: {filename} ({len(resp.content)} bytes)")
                break
        except Exception as e:
            print(f"Error: {e}")
