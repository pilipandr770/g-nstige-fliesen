#!/usr/bin/env python
"""Sync Roced content to database"""

from app import create_app, db
from app.models import Manufacturer, ManufacturerContent
from app.services.manufacturer_parsers import ManufacturerParserFactory

def sync_roced():
    app = create_app()
    with app.app_context():
        manufacturer = Manufacturer.query.filter_by(slug='roced').first()
        if not manufacturer:
            print("Roced manufacturer not found")
            return
        
        parser = ManufacturerParserFactory.get_parser('roced')
        if not parser:
            print("Roced parser not found")
            return
        
        print(f"\nManufacturer: {manufacturer.name} (id={manufacturer.id})\n")
        print("==== Extracting content for roced ====")
        
        collections = parser.extract_collections()
        projects = parser.extract_projects()
        blog_posts = parser.extract_blog_posts()
        
        # Add to database
        added = 0
        skipped = 0
        
        print("\nProcessing collections:", len(collections))
        for coll in collections:
            # Check if exists
            existing = ManufacturerContent.query.filter_by(
                manufacturer_id=manufacturer.id,
                source_url=coll['source_url']
            ).first()
            
            if existing:
                print("  Skipped (exists):", coll['title'])
                skipped += 1
            else:
                content = ManufacturerContent(
                    manufacturer_id=manufacturer.id,
                    title=coll['title'],
                    content_type='collection',
                    description=coll['description'],
                    full_content=coll['full_content'],
                    technical_specs=coll['technical_specs'],
                    image_url=coll['image_url'],
                    source_url=coll['source_url']
                )
                db.session.add(content)
                print("  Added collection:", coll['title'])
                added += 1
        
        db.session.commit()
        
        print("\nProcessing projects:", len(projects))
        for proj in projects:
            existing = ManufacturerContent.query.filter_by(
                manufacturer_id=manufacturer.id,
                source_url=proj['source_url']
            ).first()
            if not existing:
                content = ManufacturerContent(
                    manufacturer_id=manufacturer.id,
                    title=proj['title'],
                    content_type='project',
                    image_url=proj['image_url'],
                    source_url=proj['source_url']
                )
                db.session.add(content)
                print("  Added project:", proj['title'])
                added += 1
        
        db.session.commit()
        
        print("\nProcessing blog posts:", len(blog_posts))
        for post in blog_posts:
            existing = ManufacturerContent.query.filter_by(
                manufacturer_id=manufacturer.id,
                source_url=post['source_url']
            ).first()
            if not existing:
                content = ManufacturerContent(
                    manufacturer_id=manufacturer.id,
                    title=post['title'],
                    content_type='blog',
                    description=post['description'],
                    image_url=post['image_url'],
                    source_url=post['source_url']
                )
                db.session.add(content)
                print("  Added blog post:", post['title'])
                added += 1
        
        db.session.commit()
        
        print(f"\nDone. Added: {added} Skipped: {skipped}")

if __name__ == '__main__':
    sync_roced()
