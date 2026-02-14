#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from app.services.manufacturer_parsers import DuneParser

p = DuneParser()
cols = p.extract_collections()
print(f'Found {len(cols)} collections')
if cols:
    for c in cols[:5]:
        print(f'  - {c["title"]}: {c.get("image_url", "NO IMAGE")[:60]}')
