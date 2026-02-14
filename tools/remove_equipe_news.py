import os
import sys

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
        sys.exit(1)
    print(f"Manufacturer: {m.name} (id={m.id})")

    news = ManufacturerContent.query.filter_by(manufacturer_id=m.id, content_type='news').all()
    print(f'Found news rows: {len(news)}')
    ids = [r.id for r in news]
    if not ids:
        print('No news rows to delete')
        sys.exit(0)

    for r in news:
        print(f'  Deleting id={r.id} title={r.title!r}')
        from app import db
        db.session.delete(r)
    db.session.commit()
    print(f'Deleted {len(ids)} news rows')
