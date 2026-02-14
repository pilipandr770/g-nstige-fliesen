from app.services.manufacturer_parsers import ManufacturerParserFactory

print('='*60)
print('CHECK EQUIPE')
print('='*60)
parser = ManufacturerParserFactory.get_parser('equipe')
if not parser:
    print('Parser not found for equipe')
    exit(1)

logo = parser.extract_logo()
print('Logo:', logo)

cols = parser.extract_collections()
print('Collections count:', len(cols))
for i, c in enumerate(cols[:5], 1):
    print(f'  {i}.', c.get('title')[:80], '->', c.get('image_url'))

projs = parser.extract_projects()
print('Projects count:', len(projs))
for i, p in enumerate(projs[:5], 1):
    print(f'  {i}.', p.get('title')[:80], '->', p.get('image_url'))

blogs = parser.extract_blog_posts()
print('Blog posts count:', len(blogs))
for i, b in enumerate(blogs[:5], 1):
    print(f'  {i}.', b.get('title')[:80], '->', b.get('image_url'))

print('\nDone')
