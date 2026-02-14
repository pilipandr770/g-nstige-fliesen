from app.services.manufacturer_parsers import ManufacturerParserFactory

print('='*60)
print('CHECK DISTRIMAT')
print('='*60)
parser = ManufacturerParserFactory.get_parser('distrimat')
if not parser:
    print('Parser not found for distrimat')
else:
    logo = parser.extract_logo()
    print('Logo returned:', logo)
    cols = parser.extract_collections()
    print('Collections found:', len(cols))
    if cols:
        print('First collection:', cols[0])

print('\nDone')
