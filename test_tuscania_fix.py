from app import create_app

app = create_app()
with app.app_context():
    print('Testing Tuscania logo fix...\n')
    
    # Test /hersteller page
    with app.test_client() as c:
        r = c.get('/hersteller')
        html = r.data.decode()
        
        # Find all img tags
        import re
        imgs_with_src = re.findall(r'<img[^>]*src=[^>]*>', html)
        valid_logos = [img for img in imgs_with_src if 'manufacturers' in img]
        print(f'\nLogos rendered on /hersteller: {len(valid_logos)}')
        
        # Check Tuscania page
        r = c.get('/hersteller/tuscania')
        if r.status_code == 200:
            print('\n✓ Tuscania page accessible')
            html = r.data.decode()
            # Check if logo img exists
            if 'tuscania_f87078620a' in html:
                print('  ⚠ Still references old tuscania logo file')
            else:
                print('  ✓ Old tuscania logo file reference removed')
            
            # Show what tuscania shows for logo
            header_imgs = re.findall(r'<img[^>]*tuscania[^>]*>', html, re.IGNORECASE)
            if header_imgs:
                print(f'\n  Tuscania img tags found: {len(header_imgs)}')
                print(f'    Logo img: {header_imgs[0][:150]}...')
            else:
                print('  No tuscania imgs in page')
        else:
            print(f'\n✗ Tuscania page error: {r.status_code}')
