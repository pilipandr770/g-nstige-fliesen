#!/usr/bin/env python3
import os
import sys
ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app
from app.services.content_scraper_service import ContentScraperService

app = create_app()
with app.app_context():
    scraper = ContentScraperService()
    all_content = scraper.extract_all_content('etile')
    
    collections = all_content.get('collections', [])
    print(f'Parser found: {len(collections)} collections\n')
    
    # Check all collections and their source_urls
    for i, col in enumerate(collections, 1):
        title = col.get('title')
        source = col.get('source_url')
        has_img = 'YES' if col.get('image_url') else 'NO'
        print(f'{i:2}. {title:20} | image: {has_img:3} | {source}')
