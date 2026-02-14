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
    mfr = Manufacturer.query.filter_by(slug='exagres').first()
    if not mfr:
        print('❌ Exagres manufacturer not found')
        sys.exit(1)
    
    print(f"📥 Downloading logo for {mfr.name}...")
    
    logo_url = 'https://www.exagres.es/wp-content/uploads/2023/09/logo_Exagres_blanco_2000px.png'
    
    try:
        print(f"  ⬇️  {logo_url}...")
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
            filename = f"exagres_{url_hash}{ext}"
            
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
        print(f"  ❌ Error: {str(e)}")
        sys.exit(1)
