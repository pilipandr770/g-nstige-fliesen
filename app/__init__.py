import os
import click
from sqlalchemy import text
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    schema = os.getenv("DB_SCHEMA")
    if schema:
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "connect_args": {
                "options": f"-csearch_path={schema}"
            }
        }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Flask-Login setup
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Bitte melden Sie sich an."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    from .routes import public_routes, admin_routes, api_routes, auth_routes
    app.register_blueprint(public_routes)
    app.register_blueprint(admin_routes, url_prefix="/admin")
    app.register_blueprint(api_routes, url_prefix="/api")
    app.register_blueprint(auth_routes, url_prefix="/auth")

    with app.app_context():
        if schema:
            with db.engine.begin() as connection:
                connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
        from . import models
        db.create_all()

    # CLI command: flask create-admin
    @app.cli.command("create-admin")
    @click.option("--username", default="admin", help="Admin username")
    @click.option("--email", default="admin@fliesen-showroom.de", help="Admin email")
    @click.option("--password", default="admin123", help="Admin password")
    def create_admin(username, email, password):
        """Create an admin user."""
        from .models import User
        with app.app_context():
            if User.query.filter_by(username=username).first():
                click.echo(f"User '{username}' already exists.")
                return
            user = User(username=username, email=email, is_admin=True)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            click.echo(f"Admin '{username}' created successfully!")

    # CLI command: flask generate-blog
    @app.cli.command("generate-blog")
    @click.option("--count", default=1, help="Number of articles to generate")
    @click.option("--category", default=None, help="Article category")
    @click.option("--manufacturer", default=None, help="Manufacturer slug")
    @click.option("--dry-run", is_flag=True, help="Preview without saving")
    def generate_blog(count, category, manufacturer, dry_run):
        """Generate blog articles using AI from collected news."""
        from .services.blog_generator_service import get_blog_generator
        from .models import ChatConfig

        # Check if auto generation is enabled (skip check for manual CLI runs)
        generator = get_blog_generator()

        if dry_run:
            click.echo(f"DRY RUN: Would generate {count} article(s)")
            if manufacturer:
                result = generator.generate_from_topic(
                    f"Neuigkeiten von {manufacturer}",
                    category
                )
            else:
                topics = generator._get_fallback_topics()
                result = generator.generate_from_topic(topics[0], category)

            if 'error' in result:
                click.echo(f"Error: {result['error']}")
            else:
                click.echo(f"Title: {result.get('title', '')}")
                click.echo(f"Category: {result.get('category', '')}")
                click.echo(f"Tags: {result.get('tags', '')}")
                click.echo(f"Tokens: {result.get('tokens_used', 0)}")
            return

        results = generator.auto_generate(count=count)
        for r in results:
            if r.get('success'):
                click.echo(f"Created: {r['title']} (ID: {r['id']})")
            else:
                click.echo(f"Error: {r.get('error', 'Unknown')}")

        click.echo(f"\nDone: {sum(1 for r in results if r.get('success'))}/{count} articles generated.")

    # CLI command: flask fetch-news
    @app.cli.command("fetch-news")
    def fetch_news():
        """Fetch latest news from all configured sources."""
        from .services.news_scraper_service import get_news_scraper

        scraper = get_news_scraper()
        items = scraper.fetch_all_news()
        click.echo(f"Fetched {len(items)} news items from active sources.")
        for item in items[:5]:
            click.echo(f"  - {item.get('title', 'No title')[:60]}")

    # CLI command: flask publish-scheduled
    @app.cli.command("publish-scheduled")
    def publish_scheduled():
        """Publish blog posts that are scheduled for now or earlier."""
        from .models import BlogPost
        from datetime import datetime

        posts = BlogPost.query.filter(
            BlogPost.status == 'scheduled',
            BlogPost.scheduled_at <= datetime.utcnow()
        ).all()

        count = 0
        for post in posts:
            post.published = True
            post.status = 'published'
            post.published_at = datetime.utcnow()
            count += 1

        db.session.commit()
        click.echo(f"Published {count} scheduled post(s).")

    # Статичные логотипы производителей — вшиты в код, не зависят от БД
    MANUFACTURER_LOGOS = {
        'aparici':          'manufacturers/aparici_8b8cce0928.gif',
        'ape':              'manufacturers/ape_cfd2dad717.svg',
        'lafabbrica':       'manufacturers/lafabbrica_d2d1fa5492.png',
        'baldocer':         'manufacturers/baldocer_d14b8028fe.png',
        'casalgrande':      'manufacturers/casalgrande_679b1723dc.jpg',
        'distrimat':        'manufacturers/distrimat_e5ec30a1d3.png',
        'dune':             'manufacturers/dune_1131c5db6b.png',
        'equipe':           'manufacturers/equipe_adbdedc5d9.png',
        'estudi-ceramico':  'manufacturers/estudi-ceramico_252c218fcc.svg',
        'etile':            'manufacturers/etile_1324a28845.png',
        'exagres':          'manufacturers/exagres_cfe6fb02d8.png',
        'gazzini':          'manufacturers/gazzini_51c2b0973c.ico',
        'halcon':           'manufacturers/halcon_7d53c05499.png',
        'novoceram':        'manufacturers/novoceram_1b957a28fe.png',
        'roced':            'manufacturers/roced_8307875706.jpg',
        'tuscania':         'manufacturers/tuscania_2920fd3bc3.png',
        'unicom-starker':   'manufacturers/unicom-starker_11d58c949a.png',
    }

    # Context processor for global template variables
    @app.context_processor
    def inject_globals():
        from .models import SocialLink
        social_links = SocialLink.query.order_by(SocialLink.order).all()
        return {
            "social_links": social_links,
            "manufacturer_logos": MANUFACTURER_LOGOS,
        }

    return app