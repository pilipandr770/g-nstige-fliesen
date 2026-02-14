#!/usr/bin/env python3
import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import requests
from app import create_app, db
from app.models import Manufacturer
import hashlib
from urllib.parse import urlparse

app = create_app()
with app.app_context():
    mfr = Manufacturer.query.filter_by(slug='halcon').first()
    if not mfr:
        print('❌ Halcon manufacturer not found')
        sys.exit(1)
    
    print(f"📥 Downloading logo for {mfr.name}...")
    
    # Try to find logo on the website
    logo_url = None
    
    # First, try to fetch the homepage and look for logo
    r = requests.get('https://www.halconceramicas.com', headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.content, 'html.parser')
    
    # Look for logo in header/nav
    for img in soup.find_all('img'):
        src = img.get('src', '')
        alt = img.get('alt', '')
        if 'halcon' in src.lower() or 'logo' in alt.lower():
            logo_url = src
            if not logo_url.startswith('http'):
                logo_url = 'https://www.halconceramicas.com' + logo_url
            break
    
    if not logo_url:
        # Fallback to typical WordPress logo location
        logo_url = 'https://www.halconceramicas.com/wp-content/uploads/2024/01/logo-halcon-ceramicas.png'
    
    try:
        print(f"  ⬇️  {logo_url[:80]}...")
        response = requests.get(logo_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        response.raise_for_status()
        
        # Check file size
        file_size = len(response.content)
        print(f"  Size: {file_size} bytes")
        
        if file_size < 100:
            print(f"  ⚠️  File too small, skipping")
        else:
            # Generate filename
            url_hash = hashlib.md5(logo_url.encode()).hexdigest()[:10]
            ext = '.png'
            filename = f"halcon_{url_hash}{ext}"
            
            # Save file
            upload_dir = os.path.join('app', 'static', 'uploads', 'manufacturers')
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Update database
            mfr.logo = f'manufacturers/{filename}'
            db.session.commit()
            
            print(f"  ✓ Logo saved: manufacturers/{filename}")
    
    except Exception as e:
        print(f"  ⚠️  Could not download logo: {str(e)}")
        # Try alternative approach - create placeholder or use generic logo
        print("  Continuing without logo")
