#!/usr/bin/env python
"""Sync Roced content to database"""

import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import Manufacturer, ManufacturerContent
from app.services.manufacturer_parsers import ManufacturerParserFactory

app = create_app()

def sync_roced():
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
        
        # Extract collections
        collections = parser.extract_collections()
        print(f"\n✅ Found collections: {len(collections)}")
        
        # Extract projects
        projects = parser.extract_projects()
        print(f"✅ Found projects: {len(projects)}")
        
        # Extract blog posts
        blog_posts = parser.extract_blog_posts()
        print(f"✅ Found blog posts: {len(blog_posts)}")
        
        # Add collections to database
        print("\nProcessing collections:")
        added_colls = 0
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
                    full_content=coll.get('full_content', ''),
                    technical_specs=coll.get('technical_specs', ''),
                    image_url=coll.get('image_url'),
                    source_url=coll['source_url']
                )
                db.session.add(content)
                added_colls += 1
        
        db.session.commit()
        print(f"  Added collection: {added_colls}")
        
        # Add projects
        if projects:
            print("\nProcessing projects:")
            added_projs = 0
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
                        description=proj.get('description', ''),
                        image_url=proj.get('image_url'),
                        source_url=proj['source_url']
                    )
                    db.session.add(content)
                    added_projs += 1
            
            db.session.commit()
            print(f"  Added project: {added_projs}")
        
        # Add blog posts
        if blog_posts:
            print("\nProcessing blog posts:")
            added_blogs = 0
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
                        description=post.get('description', ''),
                        image_url=post.get('image_url'),
                        source_url=post['source_url']
                    )
                    db.session.add(content)
                    added_blogs += 1
            
            db.session.commit()
            print(f"  Added blog post: {added_blogs}")
        
        total_added = added_colls + (added_projs if projects else 0) + (added_blogs if blog_posts else 0)
        print(f"\n✅ Done. Added: {total_added}")

if __name__ == '__main__':
    sync_roced()
