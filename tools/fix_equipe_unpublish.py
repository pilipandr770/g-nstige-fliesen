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
    uploads_dir = os.path.join(ROOT, 'app', 'static', 'uploads', 'manufacturers')
    rows = ManufacturerContent.query.filter_by(manufacturer_id=m.id).all()

    logo = m.logo or ''
    logo_name = os.path.basename(logo) if logo else None

    to_unpublish = []
    for r in rows:
        img = r.image_url or ''
        img_name = os.path.basename(img) if img else None
        if not img_name:
            to_unpublish.append((r, 'no-image'))
            continue
        if logo_name and img_name == logo_name:
            to_unpublish.append((r, 'logo-used'))
            continue
        img_path = os.path.join(uploads_dir, img_name)
        if not os.path.exists(img_path):
            to_unpublish.append((r, 'missing-file'))
            continue
        # else considered OK

    if not to_unpublish:
        print('No entries to unpublish')
        sys.exit(0)

    print(f'Entries to unpublish: {len(to_unpublish)}')
    for r, reason in to_unpublish:
        r.published = False
    from app import db
    db.session.commit()
    print('Committed. Updated rows:', len(to_unpublish))
