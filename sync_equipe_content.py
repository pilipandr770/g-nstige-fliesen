from app import create_app, db
from app.services.manufacturer_parsers import ManufacturerParserFactory
from app.models import Manufacturer, ManufacturerContent

app = create_app()
with app.app_context():
    print('='*60)
    print('SYNC EQUIPE CONTENT')
    print('='*60)

    parser = ManufacturerParserFactory.get_parser('equipe')
    if not parser:
        print('Parser not found for equipe')
        exit(1)

    m = Manufacturer.query.filter_by(slug='equipe').first()
    if not m:
        print('Manufacturer equipe not found in DB')
        exit(1)

    # 1) Update logo if needed
    logo = parser.extract_logo()
    if logo:
        if not m.logo or m.logo != logo:
            print('Updating DB logo for equipe ->', logo)
            m.logo = logo
            db.session.commit()
        else:
            print('DB logo already set and matches')
    else:
        print('Parser did not return a logo')

    created = 0
    skipped = 0

    # 2) Collections
    collections = parser.extract_collections()
    print(f'Found {len(collections)} collections, syncing...')
    for c in collections[:200]:
        src = c.get('source_url') or ''
        src_full = parser.normalize_url(src)
        title = (c.get('title') or 'Untitled')[:255]
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

    # 3) Projects
    projects = parser.extract_projects()
    print(f'Found {len(projects)} projects, syncing...')
    for p in projects[:200]:
        src = p.get('source_url') or ''
        src_full = parser.normalize_url(src)
        title = (p.get('title') or 'Untitled')[:255]
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
            content_type='project',
            title=title,
            description=p.get('description') or '',
            full_content=p.get('full_content') or '',
            image_url=p.get('image_url') or None,
            source_url=src_full,
            published=True
        )
        db.session.add(mc)
        created += 1

    # 4) News/Blog
    posts = parser.extract_blog_posts()
    print(f'Found {len(posts)} blog/news posts, syncing...')
    for b in posts[:200]:
        src = b.get('url') or ''
        src_full = parser.normalize_url(src)
        title = (b.get('title') or 'Untitled')[:255]
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
            content_type='news',
            title=title,
            description=b.get('excerpt') or '',
            full_content=b.get('full_content') or '',
            image_url=b.get('image_url') or None,
            source_url=src_full,
            published=True
        )
        db.session.add(mc)
        created += 1

    db.session.commit()
    print(f'Created: {created}, Skipped: {skipped}')
    print('\nDone')
