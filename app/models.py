import re
from . import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Page(db.Model):
    __tablename__ = "pages"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    slug = db.Column(db.String(300), unique=True, index=True)
    content = db.Column(db.Text)
    excerpt = db.Column(db.Text)
    source_url = db.Column(db.String(500))
    category = db.Column(db.String(100))
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturers.id'))
    manufacturer = db.relationship('Manufacturer', backref='blog_posts')
    image_url = db.Column(db.String(500))
    published = db.Column(db.Boolean, default=True)

    # SEO fields
    meta_title = db.Column(db.String(70))
    meta_description = db.Column(db.String(160))
    tags = db.Column(db.String(500))

    # AI generation metadata
    ai_generated = db.Column(db.Boolean, default=False)
    generation_prompt = db.Column(db.Text)
    source_content = db.Column(db.Text)

    # Publishing workflow
    status = db.Column(db.String(20), default='draft')
    scheduled_at = db.Column(db.DateTime)
    published_at = db.Column(db.DateTime)

    # Analytics
    views = db.Column(db.Integer, default=0)
    reading_time = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def generate_slug(self):
        """Generate URL-safe slug from title."""
        if not self.title:
            return ''
        slug = self.title.lower()
        replacements = {
            '\u00e4': 'ae', '\u00f6': 'oe', '\u00fc': 'ue', '\u00df': 'ss',
            '\u00c4': 'ae', '\u00d6': 'oe', '\u00dc': 'ue',
        }
        for char, repl in replacements.items():
            slug = slug.replace(char, repl)
        slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
        return slug[:290]

    def get_tags_list(self):
        """Return tags as a list."""
        return [t.strip() for t in (self.tags or '').split(',') if t.strip()]

    def calc_reading_time(self):
        """Calculate reading time from content length."""
        if not self.content:
            return 1
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))

class ContentSource(db.Model):
    __tablename__ = "content_sources"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500))
    active = db.Column(db.Boolean, default=True)

class ChatLog(db.Model):
    __tablename__ = "chat_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text)
    bot_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatConfig(db.Model):
    __tablename__ = "chat_config"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get(cls, key, default=None):
        """Get config value by key."""
        config = cls.query.filter_by(key=key).first()
        return config.value if config else default

    @classmethod
    def set(cls, key, value, description=None):
        """Set config value, create if not exists."""
        config = cls.query.filter_by(key=key).first()
        if not config:
            config = cls(key=key, value=value, description=description)
            db.session.add(config)
        else:
            config.value = value
            if description:
                config.description = description
        db.session.commit()
        return config


class SocialLink(db.Model):
    __tablename__ = "social_links"
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), unique=True, nullable=False)  # facebook, instagram, pinterest, etc.
    url = db.Column(db.String(500), nullable=False)
    icon = db.Column(db.String(50))  # bi-facebook, bi-instagram, etc.
    active = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CarouselImage(db.Model):
    __tablename__ = "carousel_images"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    alt_text = db.Column(db.String(255))
    link_url = db.Column(db.String(500))  # Optional: клик по изображению
    order = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CarouselImage {self.filename}>"

class Manufacturer(db.Model):
    __tablename__ = "manufacturers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    slug = db.Column(db.String(255), nullable=False, unique=True)
    logo = db.Column(db.String(255))  # Logo filename
    website = db.Column(db.String(500))
    description = db.Column(db.Text)
    country = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)
    auto_sync = db.Column(db.Boolean, default=False)  # Автоматическая синхронизация контента
    last_sync = db.Column(db.DateTime)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Manufacturer {self.name}>"


class ManufacturerContent(db.Model):
    __tablename__ = "manufacturer_content"
    id = db.Column(db.Integer, primary_key=True)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturers.id'), nullable=False)
    manufacturer = db.relationship('Manufacturer', backref='content_items')
    
    content_type = db.Column(db.String(50), nullable=False)  # collection, project, news, blog
    title = db.Column(db.String(255), nullable=False)
    subtitle = db.Column(db.String(255))
    description = db.Column(db.Text)
    full_content = db.Column(db.Text)  # Полное описание/содержание
    image_url = db.Column(db.String(500))
    source_url = db.Column(db.String(500))  # Ссылка на оригинал
    
    # Дополнительные поля для коллекций
    technical_specs = db.Column(db.Text)  # JSON с техническими характеристиками
    
    # Метаданные
    published = db.Column(db.Boolean, default=True)
    featured = db.Column(db.Boolean, default=False)  # Выделенный контент
    order = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ManufacturerContent {self.title} ({self.content_type})>"

class HeroImage(db.Model):
    __tablename__ = "hero_images"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    alt_text = db.Column(db.String(255))
    order = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<HeroImage {self.filename}>"


class Collection(db.Model):
    __tablename__ = "collections"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subtitle = db.Column(db.String(255))
    description = db.Column(db.Text)
    filename = db.Column(db.String(255))  # background image
    link_url = db.Column(db.String(500))
    order = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Collection {self.title}>"


class NewsSource(db.Model):
    __tablename__ = "news_sources"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    source_type = db.Column(db.String(50), default='rss')
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturers.id'), nullable=True)
    manufacturer = db.relationship('Manufacturer', backref='news_sources')
    active = db.Column(db.Boolean, default=True)
    last_fetched = db.Column(db.DateTime)
    fetch_interval_hours = db.Column(db.Integer, default=24)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<NewsSource {self.name}>"


class BlogGenerationLog(db.Model):
    __tablename__ = "blog_generation_logs"
    id = db.Column(db.Integer, primary_key=True)
    blog_post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=True)
    blog_post = db.relationship('BlogPost', backref='generation_logs')
    source_type = db.Column(db.String(50))
    source_url = db.Column(db.String(500))
    status = db.Column(db.String(20))
    error_message = db.Column(db.Text)
    tokens_used = db.Column(db.Integer)
    cost_estimate = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<BlogGenerationLog {self.status} ({self.created_at})>"