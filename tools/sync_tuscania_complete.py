#!/usr/bin/env python
"""Complete sync of Tuscania content to database"""

import sys
sys.path.insert(0, '.')
from app import create_app, db
from app.models import Manufacturer, ManufacturerContent
from app.services.manufacturer_parsers import ManufacturerParserFactory

app = create_app()

def sync_manufacturer(slug):
    with app.app_context():
        # Get manufacturer
        manufacturer = Manufacturer.query.filter_by(slug=slug).first()
        if not manufacturer:
            print(f"✗ Manufacturer '{slug}' not found")
            return
        
        print(f"\n{'='*70}")
        print(f"Syncing: {manufacturer.name} (ID={manufacturer.id})")
        print(f"{'='*70}")
        
        # Get parser
        try:
            parser = ManufacturerParserFactory.get_parser(slug)
            if not parser:
                print(f"✗ No parser available for {slug}")
                return
        except Exception as e:
            print(f"✗ Failed to create parser: {e}")
            return
        
        # Parse collections
        print(f"\n[1/4] Extracting collections...")
        try:
            collections = parser.extract_collections()
            print(f"  Found {len(collections)} collections")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            collections = []
        
        collections_added = 0
        for i, item in enumerate(collections, 1):
            try:
                # Check if already exists
                existing = ManufacturerContent.query.filter_by(
                    manufacturer_id=manufacturer.id,
                    source_url=item['source_url']
                ).first()
                
                if existing:
                    print(f"  [{i}/{len(collections)}] {item['title'][:50]:50} - EXISTS", end='')
                else:
                    # Create new content
                    content = ManufacturerContent(
                        manufacturer_id=manufacturer.id,
                        title=item['title'],
                        content_type='collection',
                        description=item.get('description', ''),
                        image_url=item.get('image_url'),
                        source_url=item['source_url']
                    )
                    db.session.add(content)
                    collections_added += 1
                    print(f"  [{i}/{len(collections)}] {item['title'][:50]:50} - NEW", end='')
                
                if i % 5 == 0 or i == len(collections):
                    db.session.commit()
                    print(" ✓")
                else:
                    print()
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")
                db.session.rollback()
        
        print(f"\n  Collections added: {collections_added}")
        
        # Parse projects
        print(f"\n[2/4] Extracting projects...")
        try:
            projects = parser.extract_projects()
            print(f"  Found {len(projects)} projects")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            projects = []
        
        projects_added = 0
        for i, item in enumerate(projects, 1):
            try:
                existing = ManufacturerContent.query.filter_by(
                    manufacturer_id=manufacturer.id,
                    source_url=item['source_url']
                ).first()
                
                if existing:
                    print(f"  [{i}/{len(projects)}] {item['title'][:50]:50} - EXISTS", end='')
                else:
                    content = ManufacturerContent(
                        manufacturer_id=manufacturer.id,
                        title=item['title'],
                        content_type='project',
                        description=item.get('description', ''),
                        image_url=item.get('image_url'),
                        source_url=item['source_url']
                    )
                    db.session.add(content)
                    projects_added += 1
                    print(f"  [{i}/{len(projects)}] {item['title'][:50]:50} - NEW", end='')
                
                if i % 5 == 0 or i == len(projects):
                    db.session.commit()
                    print(" ✓")
                else:
                    print()
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")
                db.session.rollback()
        
        print(f"\n  Projects added: {projects_added}")
        
        # Parse blog posts
        print(f"\n[3/4] Extracting blog posts...")
        try:
            blog_posts = parser.extract_blog_posts()
            print(f"  Found {len(blog_posts)} blog posts")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            blog_posts = []
        
        blog_added = 0
        for i, item in enumerate(blog_posts, 1):
            try:
                existing = ManufacturerContent.query.filter_by(
                    manufacturer_id=manufacturer.id,
                    source_url=item['source_url']
                ).first()
                
                if existing:
                    print(f"  [{i}/{len(blog_posts)}] {item['title'][:50]:50} - EXISTS", end='')
                else:
                    content = ManufacturerContent(
                        manufacturer_id=manufacturer.id,
                        title=item['title'],
                        content_type='blog',
                        description=item.get('description', ''),
                        image_url=item.get('image_url'),
                        source_url=item['source_url']
                    )
                    db.session.add(content)
                    blog_added += 1
                    print(f"  [{i}/{len(blog_posts)}] {item['title'][:50]:50} - NEW", end='')
                
                if i % 5 == 0 or i == len(blog_posts):
                    db.session.commit()
                    print(" ✓")
                else:
                    print()
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")
                db.session.rollback()
        
        print(f"\n  Blog posts added: {blog_added}")
        
        # Summary
        print(f"\n[4/4] Verification...")
        total_items = ManufacturerContent.query.filter_by(manufacturer_id=manufacturer.id).count()
        print(f"\n{'='*70}")
        print(f"SUMMARY: {manufacturer.name}")
        print(f"{'='*70}")
        print(f"  Collections added: {collections_added}")
        print(f"  Projects added:    {projects_added}")
        print(f"  Blog posts added:  {blog_added}")
        print(f"  ───────────────────────")
        print(f"  TOTAL NEW:         {collections_added + projects_added + blog_added}")
        print(f"  TOTAL IN DB:       {total_items}")
        print(f"{'='*70}\n")

if __name__ == '__main__':
    sync_manufacturer('tuscania')
