import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

print("=" * 60)
print("NOVOCERAM SITE ANALYSIS")
print("=" * 60)

# 1. Check collections page
print("\n1. COLLECTIONS PAGE")
print("-" * 60)
url = 'https://www.novoceram.fr/carrelage/'
resp = requests.get(url, timeout=10)
soup = BeautifulSoup(resp.content, 'html.parser')

collections = []
for link in soup.find_all('a'):
    href = link.get('href', '')
    text = link.get_text(strip=True)
    if href and '/carrelage/' in href and len(text) > 2 and text != 'Toutes les Collections':
        if href not in [c['url'] for c in collections]:
            collections.append({'name': text, 'url': urljoin(url, href)})

print(f"Found {len(collections)} collection links:")
for i, c in enumerate(sorted(collections, key=lambda x: x['name'])[:20]):
    print(f"  {i+1}. {c['name'][:35]:35} → .../{c['url'].split('/')[-2]}")

# 2. Check blog page
print("\n2. BLOG PAGE")
print("-" * 60)
url_blog = 'https://www.novoceram.fr/blog'
resp_blog = requests.get(url_blog, timeout=10)
soup_blog = BeautifulSoup(resp_blog.content, 'html.parser')

blog_posts = []
for link in soup_blog.find_all('a'):
    href = link.get('href', '')
    text = link.get_text(strip=True)
    if href and '/blog/' in href and len(text) > 3:
        if href not in [p['url'] for p in blog_posts]:
            blog_posts.append({'title': text, 'url': urljoin(url_blog, href)})

print(f"Found {len(blog_posts)} blog post links:")
for i, p in enumerate(blog_posts[:15]):
    print(f"  {i+1}. {p['title'][:40]:40}")

# 3. Check one collection detail page for image structure
print("\n3. SAMPLE COLLECTION DETAIL")
print("-" * 60)
if collections:
    sample_url = collections[0]['url']
    print(f"Analyzing: {collections[0]['name']}")
    resp = requests.get(sample_url, timeout=10)
    soup = BeautifulSoup(resp.content, 'html.parser')
    
    imgs = soup.find_all('img')
    print(f"Total images on page: {len(imgs)}")
    
    # Show first few images with src
    for i, img in enumerate(imgs[:5]):
        src = img.get('src', '')
        alt = img.get('alt', '')
        if src:
            short_src = src.split('/')[-1][:50] if '/' in src else src[:50]
            print(f"  {i+1}. {alt[:30]:30} → {short_src}")
