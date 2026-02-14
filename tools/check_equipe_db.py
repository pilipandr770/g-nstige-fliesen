import os
import sys

# Ensure project root is on sys.path so `app` package can be imported
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app
from app.models import Manufacturer, ManufacturerContent

app = create_app()
with app.app_context():
    m = Manufacturer.query.filter_by(slug='equipe').first()
    if not m:
        print('Equipe manufacturer not found')
    else:
        print(f"Manufacturer: {m.name} (id={m.id})")
        types = ['collection', 'project', 'news']
        total = 0
        for t in types:
            c = ManufacturerContent.query.filter_by(manufacturer_id=m.id, content_type=t).count()
            print(f"  {t}: {c}")
            total += c
        other = ManufacturerContent.query.filter(ManufacturerContent.manufacturer_id==m.id, ~ManufacturerContent.content_type.in_(types)).count()
        print(f"  other: {other}")
        total += other
        print(f"  total: {total}")
