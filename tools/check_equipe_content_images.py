import os
import sys
from pathlib import Path

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app
from app.models import Manufacturer, ManufacturerContent

# thresholds
MIN_BYTES = 5 * 1024  # 5 KB

app = create_app()
with app.app_context():
    m = Manufacturer.query.filter_by(slug='equipe').first()
    if not m:
        print('Equipe manufacturer not found')
        sys.exit(1)
    print(f"Manufacturer: {m.name} (id={m.id})")
    uploads_dir = os.path.join(ROOT, 'app', 'static', 'uploads', 'manufacturers')

    rows = ManufacturerContent.query.filter_by(manufacturer_id=m.id).all()
    total = len(rows)
    logo = m.logo or ''
    logo_name = os.path.basename(logo) if logo else None

    problems = []
    missing = []
    small = []
    logo_used = []
    ok = 0

    for r in rows:
        img = r.image_url or ''
        img_name = os.path.basename(img) if img else None
        if not img_name:
            missing.append(r.id)
            problems.append((r.id, 'no-image'))
            continue
        img_path = os.path.join(uploads_dir, img_name)
        if logo_name and img_name == logo_name:
            logo_used.append(r.id)
            problems.append((r.id, 'logo-used'))
            continue
        if not os.path.exists(img_path):
            missing.append(r.id)
            problems.append((r.id, 'missing-file'))
            continue
        size = os.path.getsize(img_path)
        if size < MIN_BYTES:
            small.append((r.id, size))
            problems.append((r.id, f'small:{size}'))
            continue
        ok += 1

    print(f"Total ManufacturerContent rows: {total}")
    print(f" OK (has image, not logo, size>={MIN_BYTES}): {ok}")
    print(f" Missing image field: {len(missing)}")
    print(f" Image file missing on disk: {len(missing)}")
    print(f" Small images (<{MIN_BYTES} bytes): {len(small)}")
    print(f" Using manufacturer logo as image: {len(logo_used)}")

    if problems:
        print('\nProblem rows (id, reason):')
        for p in problems[:200]:
            print(' ', p)
    else:
        print('No problems found')
