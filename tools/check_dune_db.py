import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app
from app.models import Manufacturer, ManufacturerContent

app = create_app()
with app.app_context():
    m = Manufacturer.query.filter_by(slug='dune').first()
    if not m:
        print('Dune not found')
        sys.exit(1)
    print(f"Manufacturer: {m.name} (id={m.id})")
    for t in ['collection','project','blog','news','other']:
        c = ManufacturerContent.query.filter_by(manufacturer_id=m.id, content_type=t).count()
        print(f'  {t}: {c}')
    total = ManufacturerContent.query.filter_by(manufacturer_id=m.id).count()
    print('  total:', total)
