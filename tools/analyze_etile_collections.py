#!/usr/bin/env python3
"""
Analyze Etile page structure for collections
"""
import requests
from bs4 import BeautifulSoup

url = 'https://en.etile.es/etile/'
r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(r.content, 'html.parser')

# Find element with id main-product
main_product = soup.find(id='main-product')
if main_product:
    print('Found #main-product section')
    print()
    
    # Get all links in this section
    links = main_product.find_all('a')
    print('Found ' + str(len(links)) + ' links in main-product')
    
    collection_links = set()
    for link in links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if href and text and 'etile' in href.lower():
            collection_links.add((text, href))
    
    print()
    print('Collection links:')
    for text, href in sorted(collection_links)[:30]:
        print('  ' + text + ': ' + href)
else:
    print('main-product section not found')
    
    # Look for DIVs with 'product' class
    for elem in soup.find_all(['div', 'section'], class_=lambda x: x):
        classes = str(elem.get('class', []))
        if 'product' in classes.lower() or 'collection' in classes.lower():
            print('Found element: ' + str(elem.get('class')))
