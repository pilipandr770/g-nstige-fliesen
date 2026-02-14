#!/usr/bin/env python
"""Sync Tuscania and Unicom Starker content to database"""

from app import create_app, db
from app.models import Manufacturer, ManufacturerContent
from app.services.manufacturer_parsers import ManufacturerParserFactory

def sync_manufacturer(slug):
    app = create_app()
    with app.app_context():
        manufacturer = Manufacturer.query.filter_by(slug=slug).first()
        if not manufacturer:
            print(f"{slug} manufacturer not found")
            return
        
        parser = ManufacturerParserFactory.get_parser(slug)
        if not parser:
            print(f"{slug} parser not found")
            return
        
        print(f"\nManufacturer: {manufacturer.name} (id={manufacturer.id})\n")
        print(f"==== Extracting content for {slug} ====")
        
        collections = parser.extract_collections()
        projects = parser.extract_projects()
        blog_posts = parser.extract_blog_posts()
        
        added = 0
        
        print("\nProcessing collections:", len(collections))
        for coll in collections:
            existing = ManufacturerContent.query.filter_by(
                manufacturer_id=manufacturer.id,
                source_url=coll['source_url']
            ).first()
            
            if not existing:
                content = ManufacturerContent(
                    manufacturer_id=manufacturer.id,
                    title=coll['title'],
                    content_type='collection',
                    description=coll.get('description', ''),
                    image_url=coll.get('image_url'),
                    source_url=coll['source_url']
                )
                db.session.add(content)
                print("  Added:", coll['title'])
                added += 1
        
        db.session.commit()
        
        for proj in projects + blog_posts:
            existing = ManufacturerContent.query.filter_by(
                manufacturer_id=manufacturer.id,
                source_url=proj['source_url']
            ).first()
            if not existing:
                content_type = 'project' if 'project' in str(proj) else 'blog'
                content = ManufacturerContent(
                    manufacturer_id=manufacturer.id,
                    title=proj['title'],
                    content_type=content_type,
                    image_url=proj.get('image_url'),
                    source_url=proj['source_url']
                )
                db.session.add(content)
                print(f"  Added {content_type}:", proj['title'])
                added += 1
        
        db.session.commit()
        print(f"\nDone. Added: {added}")

if __name__ == '__main__':
    sync_manufacturer('tuscania')
    sync_manufacturer('unicom-starker')
