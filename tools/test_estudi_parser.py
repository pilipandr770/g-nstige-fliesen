#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from app.services.manufacturer_parsers import EstudiCeremicoParser

p = EstudiCeremicoParser()
print('Testing EstudiCeremicoParser...\n')

# Test logo
logo = p.extract_logo()
print(f'Logo: {logo}\n')

# Test collections (small sample for speed)
cols = p.extract_collections()
print(f'Found {len(cols)} collections')
if cols:
    for c in cols[:5]:
        img = c.get('image_url', 'NO IMAGE')
        print(f'  - {c["title"]}: {img[:60] if img else "NO IMAGE"}')
