import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app
from app.models import Manufacturer

app = create_app()
with app.app_context():
    ms = Manufacturer.query.order_by(Manufacturer.id).all()
    print(f"Total manufacturers: {len(ms)}")
    for m in ms:
        print(f"id={m.id} slug={m.slug!r} name={m.name!r} website={m.website}")
