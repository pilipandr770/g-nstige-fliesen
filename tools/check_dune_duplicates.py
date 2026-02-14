#!/usr/bin/env python3
import sys
import os
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import ManufacturerContent

app = create_app()

with app.app_context():
    # Get all Dune content
    dune_content = ManufacturerContent.query.filter_by(manufacturer_id=7).all()
    
    print(f"\nTotal Dune records: {len(dune_content)}")
    
    # Count image usage
    image_counts = Counter()
    for item in dune_content:
        if item.image_url:
            image_counts[item.image_url] += 1
    
    print(f"\nImage URL frequency:")
    duplicates = {}
    for img_url, count in image_counts.most_common():
        if count > 1:
            duplicates[img_url] = count
            items = [c for c in dune_content if c.image_url == img_url]
            print(f"\n  {count}x {img_url}")
            for item in items:
                print(f"    - [{item.id}] {item.content_type}: {item.title[:50]}")
    
    print(f"\n\nTotal duplicate images: {len(duplicates)}")
    print(f"Total records with duplicate images: {sum(duplicates.values())}")
    
    # Check for nav/menu category images
    nav_images = ['pavimentos', 'revestimientos', 'mosaicos', 'lavabolos']
    nav_records = []
    for item in dune_content:
        if item.image_url and any(nav in item.image_url.lower() for nav in nav_images):
            nav_records.append(item)
    
    print(f"\nRecords using nav/menu images (should be excluded):")
    for item in nav_records:
        print(f"  [{item.id}] {item.content_type}: {item.title} -> {item.image_url}")
