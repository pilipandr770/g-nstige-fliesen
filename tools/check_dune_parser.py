import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.services.manufacturer_parsers import DuneParser
from app import create_app
from app.models import Manufacturer, ManufacturerContent

app = create_app()
with app.app_context():
    parser = DuneParser()
    print('Checking Dune parser: base_url=', parser.base_url)

    print('\nExtracting logo...')
    logo = parser.extract_logo()
    print('Logo:', logo)

    print('\nExtracting collections...')
    cols = parser.extract_collections()
    print('Collections found:', len(cols))
    for c in cols[:5]:
        print(' -', c.get('title'), c.get('image_url'), c.get('source_url'))

    print('\nExtracting blog posts...')
    posts = parser.extract_blog_posts()
    print('Blog posts found:', len(posts))

    m = Manufacturer.query.filter_by(slug='dune').first()
    if m:
        total = ManufacturerContent.query.filter_by(manufacturer_id=m.id).count()
        print('\nDB ManufacturerContent rows:', total)
    else:
        print('\nManufacturer dune not found in DB')
