from app import create_app, db
from app.services.manufacturer_parsers import ManufacturerParserFactory
from app.models import Manufacturer, ManufacturerContent

app = create_app()
with app.app_context():
    print('='*60)
    print('SYNC DISTRIMAT CONTENT')
    print('='*60)

    parser = ManufacturerParserFactory.get_parser('distrimat')
    if not parser:
        print('Parser not found for distrimat')
        exit(1)

    # 1) Ensure manufacturer exists
    m = Manufacturer.query.filter_by(slug='distrimat').first()
    if not m:
        print('Manufacturer distrimat not found in DB')
        exit(1)

    # 2) Update logo if parser found one
    logo = parser.extract_logo()
    if logo:
        if not m.logo or m.logo != logo:
            print('Updating DB logo for distrimat ->', logo)
            m.logo = logo
            db.session.commit()
        else:
            print('DB logo already set and matches')
    else:
        print('Parser did not return a logo')

    # 3) Extract collections and create ManufacturerContent entries
    collections = parser.extract_collections()
    print(f'Found {len(collections)} collections, syncing...')

    created = 0
    skipped = 0
    for c in collections:
        src = c.get('source_url') or ''
        src_full = parser.normalize_url(src)
        title = (c.get('title') or 'Untitled')[:255]
        # Check existing by source_url or title
        existing = None
        if src_full:
            existing = ManufacturerContent.query.filter_by(manufacturer_id=m.id, source_url=src_full).first()
        if not existing:
            existing = ManufacturerContent.query.filter_by(manufacturer_id=m.id, title=title).first()
        if existing:
            skipped += 1
            continue

        mc = ManufacturerContent(
            manufacturer_id=m.id,
            content_type='collection',
            title=title,
            description=c.get('description') or '',
            full_content=c.get('full_content') or '',
            image_url=c.get('image_url') or None,
            source_url=src_full,
            published=True
        )
        db.session.add(mc)
        created += 1

    db.session.commit()
    print(f'Created: {created}, Skipped: {skipped}')
    print('\nDone')
