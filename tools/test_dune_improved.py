#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.manufacturer_parsers import DuneParser

# Test with a few collections
test_urls = [
    'https://duneceramics.com/de/serien/agadir',
    'https://duneceramics.com/de/serien/altea',
    'https://duneceramics.com/de/serien/crackle',
]

parser = DuneParser()

for url in test_urls:
    print(f"\n{'='*60}")
    print(f"Testing: {url}")
    print('='*60)
    
    detail = parser.extract_collection_detail(url)
    
    print(f"\nDescription: {detail.get('description', '')[:80]}...")
    print(f"\nImages found: {len(detail.get('images', []))}")
    
    images = detail.get('images', [])
    for i, img in enumerate(images):
        # Extract the filename from the path
        fname = img.split('/')[-1] if '/' in img else img
        print(f"  {i+1}. {fname}")
