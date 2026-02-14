#!/usr/bin/env python3
import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app
from app.models import Manufacturer, ManufacturerContent
from app.services.content_scraper_service import ContentScraperService
from app import db
from datetime import datetime

app = create_app()
with app.app_context():
    m = Manufacturer.query.filter_by(slug='exagres').first()
    if not m:
        print('Manufacturer exagres not found')
        sys.exit(1)
    print(f"Manufacturer: {m.name} (id={m.id})")

    scraper = ContentScraperService()
    all_content = scraper.extract_all_content('exagres')

    count_added = 0
    count_skipped = 0

    # collections
    collections = all_content.get('collections', [])
    print(f"Processing collections: {len(collections)}")
    for item in collections:
        if not item.get('image_url'):
            print('  Skipped collection without image:', item.get('title'))
            count_skipped += 1
            continue
        if not item.get('title') or len(item.get('title',''))<2:
            print('  Skipped collection without title')
            count_skipped += 1
            continue
        # avoid duplicates by source_url
        exists = ManufacturerContent.query.filter_by(manufacturer_id=m.id, source_url=item.get('source_url')).first()
        if exists:
            print('  Exists, skip:', item.get('title'))
            count_skipped += 1
            continue
        content = ManufacturerContent(
            manufacturer_id=m.id,
            content_type='collection',
            title=item.get('title',''),
            description=item.get('description',''),
            full_content=item.get('full_content',''),
            technical_specs=item.get('technical_specs',''),
            image_url=item.get('image_url',''),
            source_url=item.get('source_url',''),
            published=True
        )
        db.session.add(content)
        count_added += 1
        print('  Added collection:', item.get('title'))

    # projects
    projects = all_content.get('projects', [])
    print(f"Processing projects: {len(projects)}")
    for item in projects:
        exists = ManufacturerContent.query.filter_by(manufacturer_id=m.id, source_url=item.get('source_url')).first()
        if exists:
            count_skipped += 1
            continue
        content = ManufacturerContent(
            manufacturer_id=m.id,
            content_type='project',
            title=item.get('title',''),
            description=item.get('description',''),
            image_url=item.get('image_url',''),
            source_url=item.get('source_url',''),
            published=True
        )
        db.session.add(content)
        count_added += 1
        print('  Added project:', item.get('title'))

    # blog posts
    blog_posts = all_content.get('blog_posts', [])
    print(f"Processing blog posts: {len(blog_posts)}")
    for item in blog_posts:
        exists = ManufacturerContent.query.filter_by(manufacturer_id=m.id, source_url=item.get('source_url')).first()
        if exists:
            count_skipped += 1
            continue
        content = ManufacturerContent(
            manufacturer_id=m.id,
            content_type='blog_post',
            title=item.get('title',''),
            description=item.get('description',''),
            image_url=item.get('image_url',''),
            source_url=item.get('source_url',''),
            published=item.get('published', True)
        )
        db.session.add(content)
        count_added += 1
        print('  Added blog post:', item.get('title'))

    db.session.commit()
    print(f"Done. Added: {count_added} Skipped: {count_skipped}")
