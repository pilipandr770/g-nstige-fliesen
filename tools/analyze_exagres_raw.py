#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Save the collections page HTML for analysis
url = 'https://www.exagres.es/colecciones-residencial/'
r = requests.get(url, headers=headers, timeout=10)

# Save to file
with open('exagres_collections_raw.html', 'w', encoding='utf-8') as f:
    f.write(r.text[:10000])  # First 10KB

print('✅ Saved collections page HTML to exagres_collections_raw.html')

# Now analyze it
soup = BeautifulSoup(r.content, 'html.parser')

# Remove script and style tags
for tag in soup(['script', 'style']):
    tag.decompose()

# Get all text content
text = soup.get_text(separator=' ', strip=True)

# Find collection names mentioned (look for common patterns)
print('\n📊 Text content analysis:')
print(f'Total page text length: {len(text)} characters')

# Look for specific keywords
keywords = ['colección', 'collection', 'producto', 'residencial', 'gresan']
for keyword in keywords:
    count = text.lower().count(keyword.lower())
    print(f'  Occurrences of "{keyword}": {count}')

# Try different approaches to find collections
print('\n🔍 Different parsing approaches:\n')

soup2 = BeautifulSoup(r.content, 'html.parser')

# Approach 1: Look for all divs and see what's in them
print('1. Looking for content divs:')
all_divs = soup2.find_all('div')
print(f'   Total divs: {len(all_divs)}')

# Approach 2: Look for specific data attributes that might indicate collections
print('\n2. Looking for data attributes:')
all_with_data = soup2.find_all(lambda tag: tag.attrs and any(attr.startswith('data-') for attr in tag.attrs))
print(f'   Elements with data-* attributes: {len(all_with_data)}')
for elem in all_with_data[:5]:
    data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
    print(f'   {elem.name} with {data_attrs}')

# Approach 3: Look at the actual page structure more carefully
print('\n3. Checking for collection links:')
all_links = soup2.find_all('a', href=True)
collection_links = []
for link in all_links:
    href = link.get('href', '')
    text = link.get_text(strip=True)
    
    # Check if this might be a collection
    if any(keyword in href.lower() for keyword in ['gresan', 'pavim', 'piscina', 'torelo', 'fachada', 'peldano']):
        collection_links.append((text, href))

if collection_links:
    print(f'   Found {len(collection_links)} potential collection links:')
    for text, href in collection_links[:10]:
        print(f'   "{text[:40]}" -> {href}')
else:
    print('   No collection links found')

# Approach 4: Check if it's a JavaScript-heavy page
if 'react' in r.text.lower() or 'vue' in r.text.lower() or 'angular' in r.text.lower():
    print('\n4. Page appears to be JavaScript-heavy (React/Vue/Angular)')
    print('   Collections may be loaded dynamically - need different approach')
else:
    print('\n4. Page does not appear to be heavily JavaScript-based')

# Check for JSON data in window object
if '<script' in r.text and 'window.' in r.text:
    print('   Found script tags with window object - may contain collection data')
