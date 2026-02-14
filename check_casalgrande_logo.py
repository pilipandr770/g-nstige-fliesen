"""
Check Casalgrande logo: run parser, check file, check DB
"""
from app.services.manufacturer_parsers import ManufacturerParserFactory
from app import create_app, db
from app.models import Manufacturer
import os

print('='*60)
print('CHECK CASALGRANDE LOGO')
print('='*60)

# 1) Run parser.extract_logo()
parser = ManufacturerParserFactory.get_parser('casalgrande')
if not parser:
    print('Parser not found for casalgrande')
else:
    print('Running parser.extract_logo()...')
    logo = parser.extract_logo()
    print('Returned:', logo)

# 2) Check filesystem
if logo:
    path = os.path.join('app', 'static', 'uploads', logo)
    print('Expected file path:', path)
    print('Exists:', os.path.exists(path))
    if os.path.exists(path):
        print('Size:', os.path.getsize(path), 'bytes')

# 3) Check DB entry for manufacturer
app = create_app()
with app.app_context():
    m = Manufacturer.query.filter_by(slug='casalgrande').first()
    if not m:
        print('Manufacturer casalgrande not found in DB')
    else:
        print('Manufacturer in DB:', m.name)
        print('Logo in DB:', m.logo)
        if logo and (not m.logo or m.logo != logo):
            print('\nLogo exists on disk but not stored in DB or different. Updating DB...')
            m.logo = logo
            db.session.commit()
            print('DB updated. New logo:', m.logo)

print('\nDone')
