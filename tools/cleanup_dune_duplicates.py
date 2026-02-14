#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import ManufacturerContent, db

app = create_app()

with app.app_context():
    # Find and delete records using the nav image
    nav_image = 'manufacturers/dune_0bc1ff2ac7.jpg'
    records_to_delete = ManufacturerContent.query.filter_by(
        manufacturer_id=7,
        image_url=nav_image
    ).all()
    
    print(f"Found {len(records_to_delete)} records using nav image: {nav_image}")
    
    if records_to_delete:
        ids_to_delete = [r.id for r in records_to_delete]
        print(f"Deleting IDs: {ids_to_delete[:20]}...")
        
        for record in records_to_delete:
            db.session.delete(record)
        
        db.session.commit()
        print(f"Deleted {len(records_to_delete)} records")
    
    # Check remaining Dune content
    remaining = ManufacturerContent.query.filter_by(manufacturer_id=7).all()
    print(f"\nRemaining Dune records: {len(remaining)}")
    
    # Count by content_type
    by_type = {}
    for r in remaining:
        ct = r.content_type
        if ct not in by_type:
            by_type[ct] = 0
        by_type[ct] += 1
    
    print(f"By type: {by_type}")
