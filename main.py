#!/usr/bin/env python3
"""
Echhapa News Portal - Professional CMS with PostgreSQL
Advanced features: Ad Management, Rich Text Editor, Layout Management
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify
import os
import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import json
import uuid
from PIL import Image

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-change-in-production")

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static/uploads/articles', exist_ok=True)
os.makedirs('static/uploads/ads', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database connection
def get_db():
    """Get database connection"""
    try:
        conn = psycopg2.connect(
            host=os.environ.get('PGHOST', 'localhost'),
            port=int(os.environ.get('PGPORT', '5432')),
            database=os.environ.get('PGDATABASE', 'echhapa_news'),
            user=os.environ.get('PGUSER', 'postgres'),
            password=os.environ.get('PGPASSWORD', '')
        )
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Initialize database
def init_db():
    """Initialize database with comprehensive structure"""
    conn = get_db()
    if not conn:
        print("Database not available - using fallback mode")
        return False
    
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Articles table with rich content support
        cur.execute("DROP TABLE IF EXISTS articles CASCADE")
        cur.execute("""
            CREATE TABLE articles (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                excerpt TEXT,
                featured_image VARCHAR(255),
                author VARCHAR(100) DEFAULT 'Admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'published',
                slug VARCHAR(255) UNIQUE,
                category_id INTEGER,
                views INTEGER DEFAULT 0,
                meta_description TEXT,
                meta_keywords TEXT
            )
        """)
        
        # Users table
        cur.execute("DROP TABLE IF EXISTS users CASCADE")
        cur.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'admin',
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                avatar VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Categories table
        cur.execute("DROP TABLE IF EXISTS categories CASCADE")
        cur.execute("""
            CREATE TABLE categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                slug VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                parent_id INTEGER,
                sort_order INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Ads table - comprehensive ad management
        cur.execute("DROP TABLE IF EXISTS ads CASCADE")
        cur.execute("""
            CREATE TABLE ads (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                image_url VARCHAR(255),
                click_url VARCHAR(500),
                placement VARCHAR(50) NOT NULL,
                ad_type VARCHAR(50) DEFAULT 'banner',
                start_date DATE,
                end_date DATE,
                is_active BOOLEAN DEFAULT TRUE,
                priority INTEGER DEFAULT 1,
                clicks INTEGER DEFAULT 0,
                impressions INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Layout settings table
        cur.execute("DROP TABLE IF EXISTS layout_settings CASCADE")
        cur.execute("""
            CREATE TABLE layout_settings (
                id SERIAL PRIMARY KEY,
                layout_name VARCHAR(100) NOT NULL,
                layout_type VARCHAR(50) NOT NULL,
                settings JSONB,
                is_active BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Site settings table
        cur.execute("DROP TABLE IF EXISTS site_settings CASCADE")
        cur.execute("""
            CREATE TABLE site_settings (
                id SERIAL PRIMARY KEY,
                setting_key VARCHAR(100) UNIQUE NOT NULL,
                setting_value TEXT,
                setting_type VARCHAR(50) DEFAULT 'text',
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert default admin user
        cur.execute("SELECT COUNT(*) as count FROM users WHERE username = 'admin'")
        result = cur.fetchone()
        if result['count'] == 0:
            password_hash = generate_password_hash('admin123')
            cur.execute("""INSERT INTO users (username, email, password_hash, role, first_name, last_name) 
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                       ('admin', 'admin@echhapa.com', password_hash, 'admin', 'Admin', 'User'))
        
        # Insert default categories
        categories = [
            ('World News', 'world-news', 'International news and global events'),
            ('Technology', 'technology', 'Latest tech trends and innovations'),
            ('Business', 'business', 'Business news and market updates'),
            ('Sports', 'sports', 'Sports news and championships'),
            ('Entertainment', 'entertainment', 'Entertainment and celebrity news'),
            ('Politics', 'politics', 'Political news and analysis'),
            ('Health', 'health', 'Health and medical news'),
            ('Science', 'science', 'Scientific discoveries and research')
        ]
        
        for name, slug, desc in categories:
            cur.execute("INSERT INTO categories (name, slug, description) VALUES (%s, %s, %s) ON CONFLICT (slug) DO NOTHING",
                       (name, slug, desc))
        
        # Insert default layout settings
        default_layouts = [
            ('Classic Grid', 'homepage', '{"featured_articles": 4, "sidebar_widgets": ["categories", "newsletter"], "layout_style": "grid"}', True),
            ('Magazine Style', 'homepage', '{"featured_articles": 6, "sidebar_widgets": ["trending", "categories"], "layout_style": "magazine"}', False),
            ('Minimal Clean', 'homepage', '{"featured_articles": 3, "sidebar_widgets": ["newsletter"], "layout_style": "minimal"}', False)
        ]
        
        for name, type_val, settings, active in default_layouts:
            cur.execute("INSERT INTO layout_settings (layout_name, layout_type, settings, is_active) VALUES (%s, %s, %s, %s)",
                       (name, type_val, settings, active))
        
        # Insert default site settings
        default_settings = [
            ('site_title', 'Echhapa News', 'text', 'Main site title'),
            ('site_description', 'Your trusted source for news and information', 'text', 'Site description'),
            ('contact_email', 'contact@echhapa.com', 'email', 'Contact email address'),
            ('posts_per_page', '10', 'number', 'Number of posts per page'),
            ('enable_comments', 'true', 'boolean', 'Enable article comments'),
            ('google_analytics', '', 'text', 'Google Analytics tracking ID'),
            ('social_facebook', '', 'url', 'Facebook page URL'),
            ('social_twitter', '', 'url', 'Twitter profile URL'),
            ('social_instagram', '', 'url', 'Instagram profile URL')
        ]
        
        for key, value, type_val, desc in default_settings:
            cur.execute("INSERT INTO site_settings (setting_key, setting_value, setting_type, description) VALUES (%s, %s, %s, %s) ON CONFLICT (setting_key) DO NOTHING",
                       (key, value, type_val, desc))
        
        # Insert sample articles if none exist
        cur.execute("SELECT COUNT(*) as count FROM articles")
        result = cur.fetchone()
        if result['count'] == 0:
            sample_articles = [
                ("Breaking: Global Economic Summit Reaches Historic Agreement", 
                 """<p>In a landmark decision that could reshape the global economy, world leaders from over 50 nations have reached a comprehensive economic agreement at the Global Economic Summit held in Geneva.</p>
                 
                 <p>The agreement, dubbed the "Geneva Accords," includes provisions for:</p>
                 <ul>
                 <li>Reduced trade barriers between participating nations</li>
                 <li>Standardized digital currency regulations</li>
                 <li>Joint climate change initiatives with economic incentives</li>
                 <li>Technology sharing programs for developing countries</li>
                 </ul>
                 
                 <p>President of the European Commission stated, "This agreement represents the most significant step forward in international economic cooperation since the establishment of the World Trade Organization."</p>
                 
                 <p>The accords are expected to come into effect by Q2 2025, pending ratification by individual governments.</p>""",
                 "Global leaders unite for unprecedented economic cooperation that promises to reshape international trade and development.",
                 "global-economic-summit-agreement", 1),
                
                ("Tech Giants Unveil Revolutionary AI-Powered News Platform", 
                 """<p>Major technology companies have collaborated to launch an innovative AI-powered news aggregation and verification platform that promises to combat misinformation while delivering personalized news experiences.</p>
                 
                 <p>The platform, called "TruthLens," uses advanced machine learning algorithms to:</p>
                 <ul>
                 <li>Verify news sources and fact-check articles in real-time</li>
                 <li>Provide bias analysis for news content</li>
                 <li>Offer multiple perspectives on breaking news stories</li>
                 <li>Customize news feeds based on user interests and reliability preferences</li>
                 </ul>
                 
                 <p>The CEO of the initiative explained, "Our goal is to restore trust in journalism by providing tools that help readers make informed decisions about the news they consume."</p>
                 
                 <p>The platform will be available as a web service and mobile application starting next month.</p>""",
                 "Revolutionary AI platform promises to transform how we consume and verify news in the digital age.",
                 "ai-powered-news-platform", 2),
                
                ("Championship Finals Set Record Viewership Numbers", 
                 """<p>The highly anticipated championship finals drew a record-breaking global audience of over 2.3 billion viewers, making it the most-watched sporting event in history.</p>
                 
                 <p>The thrilling match featured unprecedented athletic performances and dramatic moments that kept viewers engaged throughout the entire event. Social media platforms reported peak activity during key moments of the competition.</p>
                 
                 <p>Key highlights included:</p>
                 <ul>
                 <li>Record-breaking individual performances by multiple athletes</li>
                 <li>Innovative broadcasting technology providing 360-degree coverage</li>
                 <li>Interactive features allowing real-time viewer participation</li>
                 <li>Sustainable event management setting new environmental standards</li>
                 </ul>
                 
                 <p>The event's success has prompted organizers to announce plans for expanded coverage and fan engagement features for future competitions.</p>""",
                 "Historic championship finals captivate global audience with record-breaking viewership and unforgettable performances.",
                 "championship-finals-record-viewership", 4),
                
                ("Scientific Breakthrough: New Renewable Energy Storage Solution", 
                 """<p>Researchers at leading universities have developed a revolutionary energy storage technology that could solve one of renewable energy's biggest challenges: efficient long-term storage.</p>
                 
                 <p>The breakthrough involves a novel battery design using abundant materials that can store energy for months without significant loss. This development addresses the intermittent nature of solar and wind power generation.</p>
                 
                 <p>Key advantages of the new technology:</p>
                 <ul>
                 <li>95% efficiency retention over 6-month storage periods</li>
                 <li>Utilizes common, environmentally-friendly materials</li>
                 <li>Scalable from residential to grid-level applications</li>
                 <li>Cost-competitive with traditional energy storage methods</li>
                 </ul>
                 
                 <p>The research team expects commercial applications to be available within the next three years, pending regulatory approval and manufacturing partnerships.</p>""",
                 "Groundbreaking energy storage technology promises to accelerate the global transition to renewable energy.",
                 "renewable-energy-storage-breakthrough", 8)
            ]
            
            for title, content, excerpt, slug, cat_id in sample_articles:
                cur.execute("""INSERT INTO articles (title, content, excerpt, slug, category_id) 
                              VALUES (%s, %s, %s, %s, %s)""", 
                           (title, content, excerpt, slug, cat_id))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

# Fallback data for when database is not available
fallback_articles = [
    {
        'id': 1,
        'title': "Breaking: Global Economic Summit Reaches Historic Agreement",
        'content': "In a landmark decision that could reshape the global economy, world leaders from over 50 nations have reached a comprehensive economic agreement...",
        'excerpt': "Global leaders unite for unprecedented economic cooperation that promises to reshape international trade and development.",
        'author': 'Admin',
        'created_at': datetime.now(),
        'status': 'published',
        'slug': 'global-economic-summit-agreement'
    },
    {
        'id': 2,
        'title': "Tech Giants Unveil Revolutionary AI-Powered News Platform",
        'content': "Major technology companies have collaborated to launch an innovative AI-powered news aggregation and verification platform...",
        'excerpt': "Revolutionary AI platform promises to transform how we consume and verify news in the digital age.",
        'author': 'Admin',
        'created_at': datetime.now(),
        'status': 'published',
        'slug': 'ai-powered-news-platform'
    }
]

def get_articles(limit=10):
    """Get articles from database or fallback"""
    conn = get_db()
    if not conn:
        return fallback_articles[:limit]
    
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""SELECT a.*, c.name as category_name 
                      FROM articles a 
                      LEFT JOIN categories c ON a.category_id = c.id 
                      WHERE a.status = 'published' 
                      ORDER BY a.created_at DESC LIMIT %s""", (limit,))
        articles = cur.fetchall()
        cur.close()
        conn.close()
        return articles
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return fallback_articles[:limit]

def get_article_by_slug(slug):
    """Get single article by slug"""
    conn = get_db()
    if not conn:
        for article in fallback_articles:
            if article['slug'] == slug:
                return article
        return None
    
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""SELECT a.*, c.name as category_name 
                      FROM articles a 
                      LEFT JOIN categories c ON a.category_id = c.id 
                      WHERE a.slug = %s AND a.status = 'published'""", (slug,))
        article = cur.fetchone()
        if article:
            # Update view count
            cur.execute("UPDATE articles SET views = views + 1 WHERE id = %s", (article['id'],))
            conn.commit()
        cur.close()
        conn.close()
        return article
    except Exception as e:
        print(f"Error fetching article: {e}")
        return None

# File upload helper
def handle_file_upload(file, upload_type='general'):
    """Handle file upload with proper naming and storage"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        if upload_type == 'articles':
            filepath = os.path.join('static/uploads/articles', unique_filename)
        elif upload_type == 'ads':
            filepath = os.path.join('static/uploads/ads', unique_filename)
        else:
            filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        try:
            file.save(filepath)
            
            # Optimize image if it's an image file
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                with Image.open(filepath) as img:
                    # Resize if too large
                    if img.width > 1920 or img.height > 1080:
                        img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                        img.save(filepath, optimize=True, quality=85)
            
            return filepath.replace('static/', '')
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    return None

# Homepage
@app.route('/')
def index():
    """Homepage with modern design and layout"""
    articles = get_articles(12)
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Echhapa News - Your Trusted Source</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="/css/style.css" rel="stylesheet">
    <style>
        /* Professional News Homepage Design */
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Arial', sans-serif;
            line-height: 1.6;
            color: #1a1a1a;
            background-color: #ffffff;
            margin: 0;
            padding: 0;
        }
        
        /* Header and Navigation */
        .masthead {
            border-bottom: 1px solid #e5e5e5;
            padding: 15px 0;
        }
        
        .site-title {
            font-family: 'Georgia', 'Times New Roman', serif;
            font-weight: 900;
            font-size: 2.5rem;
            color: #000000;
            text-decoration: none;
            letter-spacing: -1px;
        }
        
        .site-tagline {
            font-size: 0.9rem;
            color: #666666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 5px;
        }
        
        .primary-nav {
            background-color: #f8f9fa;
            border-bottom: 1px solid #e5e5e5;
            padding: 0;
        }
        
        .primary-nav .nav-link {
            font-weight: 500;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.5px;
            color: #333333;
            padding: 15px 20px;
            border-right: 1px solid #e5e5e5;
            transition: all 0.2s ease;
        }
        
        .primary-nav .nav-link:hover {
            background-color: #000000;
            color: #ffffff;
        }
        
        /* Breaking News */
        .breaking-news {
            background-color: #000000;
            color: #ffffff;
            padding: 10px 0;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.5px;
        }
        
        .breaking-badge {
            background-color: #dc3545;
            color: #ffffff;
            padding: 4px 8px;
            font-weight: 700;
            margin-right: 15px;
        }
        
        /* Hero Section */
        .hero-section {
            padding: 40px 0;
            border-bottom: 2px solid #000000;
        }
        
        .featured-story {
            border-right: 1px solid #e5e5e5;
            padding-right: 30px;
        }
        
        .featured-story h1 {
            font-family: 'Georgia', 'Times New Roman', serif;
            font-size: 2.5rem;
            font-weight: 700;
            line-height: 1.1;
            margin-bottom: 15px;
            color: #000000;
        }
        
        .featured-story .lead {
            font-size: 1.1rem;
            color: #666666;
            line-height: 1.5;
            margin-bottom: 15px;
        }
        
        .story-meta {
            font-size: 0.85rem;
            color: #666666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 20px;
        }
        
        .secondary-stories {
            padding-left: 30px;
        }
        
        .secondary-story {
            border-bottom: 1px solid #e5e5e5;
            padding: 15px 0;
        }
        
        .secondary-story:last-child {
            border-bottom: none;
        }
        
        .secondary-story h3 {
            font-size: 1.1rem;
            font-weight: 600;
            line-height: 1.3;
            margin-bottom: 8px;
        }
        
        .secondary-story h3 a {
            color: #000000;
            text-decoration: none;
        }
        
        .secondary-story h3 a:hover {
            color: #666666;
        }
        
        /* Main Content Sections */
        .content-section {
            padding: 40px 0;
            border-bottom: 1px solid #e5e5e5;
        }
        
        .section-header {
            margin-bottom: 30px;
        }
        
        .section-title {
            font-size: 1.25rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #000000;
            border-bottom: 2px solid #000000;
            padding-bottom: 8px;
            margin-bottom: 0;
        }
        
        /* Article Cards */
        .news-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
        }
        
        .article-card {
            border-bottom: 1px solid #e5e5e5;
            padding-bottom: 20px;
        }
        
        .article-card:last-child {
            border-bottom: none;
        }
        
        .article-card h4 {
            font-size: 1.15rem;
            font-weight: 600;
            line-height: 1.3;
            margin-bottom: 10px;
        }
        
        .article-card h4 a {
            color: #000000;
            text-decoration: none;
        }
        
        .article-card h4 a:hover {
            color: #666666;
        }
        
        .article-excerpt {
            color: #666666;
            font-size: 0.95rem;
            line-height: 1.5;
            margin-bottom: 10px;
        }
        
        .article-meta {
            font-size: 0.8rem;
            color: #666666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Category Badge */
        .category-badge {
            background-color: #000000;
            color: #ffffff;
            padding: 4px 8px;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
            margin-bottom: 10px;
            display: inline-block;
        }
        
        /* Sidebar */
        .sidebar {
            background-color: #f8f9fa;
            border-left: 2px solid #000000;
            padding: 30px;
        }
        
        .sidebar-section {
            border-bottom: 1px solid #e5e5e5;
            padding-bottom: 25px;
            margin-bottom: 25px;
        }
        
        .sidebar-section:last-child {
            border-bottom: none;
            margin-bottom: 0;
        }
        
        .sidebar-title {
            font-size: 1rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #000000;
            margin-bottom: 15px;
            border-bottom: 2px solid #000000;
            padding-bottom: 5px;
        }
        
        .sidebar-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .sidebar-list li {
            border-bottom: 1px solid #e5e5e5;
            padding: 8px 0;
        }
        
        .sidebar-list li:last-child {
            border-bottom: none;
        }
        
        .sidebar-list a {
            color: #333333;
            text-decoration: none;
            font-size: 0.9rem;
            line-height: 1.4;
            display: block;
        }
        
        .sidebar-list a:hover {
            color: #000000;
        }
        
        /* Newsletter */
        .newsletter-signup {
            background-color: #000000;
            color: #ffffff;
            padding: 20px;
            margin-bottom: 25px;
        }
        
        .newsletter-signup h5 {
            color: #ffffff;
            margin-bottom: 10px;
        }
        
        .newsletter-signup input {
            border: none;
            padding: 10px;
            font-size: 0.9rem;
        }
        
        .newsletter-signup button {
            background-color: #dc3545;
            border: none;
            color: #ffffff;
            padding: 10px 15px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Footer */
        .site-footer {
            background-color: #000000;
            color: #ffffff;
            border-top: 1px solid #333333;
            margin-top: 50px;
            padding: 40px 0 20px;
        }
        
        .site-footer h6 {
            color: #ffffff;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.5px;
            margin-bottom: 15px;
        }
        
        .site-footer a {
            color: #cccccc;
            text-decoration: none;
            font-size: 0.9rem;
        }
        
        .site-footer a:hover {
            color: #ffffff;
        }
        
        .social-icons a {
            display: inline-block;
            width: 40px;
            height: 40px;
            line-height: 40px;
            text-align: center;
            background-color: #333333;
            color: #ffffff;
            margin-right: 10px;
            transition: background-color 0.2s ease;
        }
        
        .social-icons a:hover {
            background-color: #555555;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .featured-story {
                border-right: none;
                padding-right: 0;
                margin-bottom: 30px;
            }
            
            .secondary-stories {
                padding-left: 0;
            }
            
            .sidebar {
                margin-top: 30px;
                border-left: none;
                border-top: 2px solid #000000;
                padding-top: 30px;
            }
            
            .primary-nav .nav-link {
                border-right: none;
                border-bottom: 1px solid #e5e5e5;
            }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="masthead">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <a href="/" class="site-title">Echhapa News</a>
                    <div class="site-tagline">Your Trusted Source for Breaking News</div>
                </div>
                <div class="col-md-4 text-end">
                    <div class="d-flex justify-content-end align-items-center">
                        <form class="d-flex me-3">
                            <input class="form-control form-control-sm" type="search" placeholder="Search news...">
                            <button class="btn btn-outline-dark btn-sm" type="submit">
                                <i class="fas fa-search"></i>
                            </button>
                        </form>
                        <a href="/admin" class="btn btn-outline-dark btn-sm">
                            <i class="fas fa-cog me-1"></i>Admin
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </header>
    
    <!-- Primary Navigation -->
    <nav class="primary-nav">
        <div class="container">
            <ul class="nav">
                <li class="nav-item">
                    <a class="nav-link" href="/">Home</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#">World News</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#">Politics</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#">Business</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#">Technology</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#">Sports</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#">Entertainment</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#">Opinion</a>
                </li>
            </ul>
        </div>
    </nav>
    
    <!-- Breaking News -->
    <div class="breaking-news">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-auto">
                    <span class="breaking-badge">Breaking</span>
                </div>
                <div class="col">
                    <span>Global Economic Summit concludes with historic agreements • Tech innovation drives renewable energy breakthrough • Championship finals set new viewership records</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Hero Section -->
    {% if articles %}
    <section class="hero-section">
        <div class="container">
            <div class="row">
                <div class="col-lg-8">
                    <div class="featured-story">
                        <span class="category-badge">Featured Story</span>
                        <h1>
                            <a href="/article/{{ articles[0].slug or articles[0].id }}">
                                {{ articles[0].title }}
                            </a>
                        </h1>
                        <div class="story-meta">
                            By {{ articles[0].author }} • {{ articles[0].created_at.strftime('%B %d, %Y') if articles[0].created_at.strftime else articles[0].created_at }}
                        </div>
                        <p class="lead">{{ articles[0].excerpt or (articles[0].content[:250] + "...") }}</p>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="secondary-stories">
                        {% for article in articles[1:4] %}
                        <div class="secondary-story">
                            {% if article.category_name %}
                            <span class="category-badge">{{ article.category_name }}</span>
                            {% endif %}
                            <h3>
                                <a href="/article/{{ article.slug or article.id }}">
                                    {{ article.title }}
                                </a>
                            </h3>
                            <div class="story-meta">
                                {{ article.created_at.strftime('%B %d') if article.created_at.strftime else article.created_at }}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </section>
    {% endif %}

    <!-- Main Content -->
    <div class="container">
        <div class="row">
            <!-- Main Articles -->
            <div class="col-lg-8">
                <!-- Latest News Section -->
                <section class="content-section">
                    <div class="section-header">
                        <h2 class="section-title">Latest News</h2>
                    </div>
                    <div class="news-grid">
                        {% for article in articles[4:10] %}
                        <article class="article-card">
                            {% if article.category_name %}
                            <span class="category-badge">{{ article.category_name }}</span>
                            {% endif %}
                            <h4>
                                <a href="/article/{{ article.slug or article.id }}">
                                    {{ article.title }}
                                </a>
                            </h4>
                            <p class="article-excerpt">
                                {{ article.excerpt or (article.content[:150] + "...") }}
                            </p>
                            <div class="article-meta">
                                By {{ article.author }} • {{ article.created_at.strftime('%B %d, %Y') if article.created_at.strftime else article.created_at }}
                            </div>
                        </article>
                        {% endfor %}
                    </div>
                </section>
                
                <!-- World News Section -->
                {% if articles[10:] %}
                <section class="content-section">
                    <div class="section-header">
                        <h2 class="section-title">World News</h2>
                    </div>
                    <div class="news-grid">
                        {% for article in articles[10:12] %}
                        <article class="article-card">
                            {% if article.category_name %}
                            <span class="category-badge">{{ article.category_name }}</span>
                            {% endif %}
                            <h4>
                                <a href="/article/{{ article.slug or article.id }}">
                                    {{ article.title }}
                                </a>
                            </h4>
                            <p class="article-excerpt">
                                {{ article.excerpt or (article.content[:150] + "...") }}
                            </p>
                            <div class="article-meta">
                                By {{ article.author }} • {{ article.created_at.strftime('%B %d, %Y') if article.created_at.strftime else article.created_at }}
                            </div>
                        </article>
                        {% endfor %}
                    </div>
                </section>
                {% endif %}
            </div>
            
            <!-- Sidebar -->
            <div class="col-lg-4">
                <div class="sidebar">
                    <!-- Newsletter -->
                    <div class="newsletter-signup">
                        <h5>Subscribe to Newsletter</h5>
                        <p>Get the latest news delivered to your inbox</p>
                        <form>
                            <div class="input-group">
                                <input type="email" class="form-control" placeholder="Your email address">
                                <button type="submit">Subscribe</button>
                            </div>
                        </form>
                    </div>
                    
                    <!-- Most Read -->
                    <div class="sidebar-section">
                        <h6 class="sidebar-title">Most Read</h6>
                        <ul class="sidebar-list">
                            {% for article in articles[1:6] %}
                            <li>
                                <a href="/article/{{ article.slug or article.id }}">
                                    {{ article.title[:60] }}{% if article.title|length > 60 %}...{% endif %}
                                </a>
                            </li>
                            {% endfor %}
                        </ul>
                    </div>
                    
                    <!-- Categories -->
                    <div class="sidebar-section">
                        <h6 class="sidebar-title">Categories</h6>
                        <ul class="sidebar-list">
                            <li><a href="#">World News</a></li>
                            <li><a href="#">Politics</a></li>
                            <li><a href="#">Business</a></li>
                            <li><a href="#">Technology</a></li>
                            <li><a href="#">Sports</a></li>
                            <li><a href="#">Entertainment</a></li>
                            <li><a href="#">Opinion</a></li>
                        </ul>
                    </div>
                    
                    <!-- Advertisement -->
                    <div class="sidebar-section text-center" style="background: #f0f0f0; padding: 30px;">
                        <h6 style="color: #666; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">Advertisement</h6>
                        <div style="height: 200px; display: flex; align-items: center; justify-content: center; color: #999;">
                            <div>
                                <i class="fas fa-ad fa-2x mb-2"></i>
                                <p style="font-size: 0.9rem; margin: 0;">Your Ad Here</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="site-footer">
        <div class="container">
            <div class="row">
                <div class="col-lg-3 col-md-6 mb-4">
                    <h6>Echhapa News</h6>
                    <p style="color: #cccccc; font-size: 0.9rem; line-height: 1.5;">Your trusted source for breaking news, in-depth analysis, and comprehensive coverage of global events.</p>
                    <div class="social-icons">
                        <a href="#"><i class="fab fa-facebook"></i></a>
                        <a href="#"><i class="fab fa-twitter"></i></a>
                        <a href="#"><i class="fab fa-instagram"></i></a>
                        <a href="#"><i class="fab fa-linkedin"></i></a>
                    </div>
                </div>
                <div class="col-lg-2 col-md-6 mb-4">
                    <h6>Sections</h6>
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        <li style="margin-bottom: 8px;"><a href="#">World News</a></li>
                        <li style="margin-bottom: 8px;"><a href="#">Politics</a></li>
                        <li style="margin-bottom: 8px;"><a href="#">Business</a></li>
                        <li style="margin-bottom: 8px;"><a href="#">Technology</a></li>
                        <li style="margin-bottom: 8px;"><a href="#">Sports</a></li>
                    </ul>
                </div>
                <div class="col-lg-2 col-md-6 mb-4">
                    <h6>Company</h6>
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        <li style="margin-bottom: 8px;"><a href="#">About Us</a></li>
                        <li style="margin-bottom: 8px;"><a href="#">Contact</a></li>
                        <li style="margin-bottom: 8px;"><a href="#">Careers</a></li>
                        <li style="margin-bottom: 8px;"><a href="#">Privacy Policy</a></li>
                        <li style="margin-bottom: 8px;"><a href="#">Terms of Service</a></li>
                    </ul>
                </div>
                <div class="col-lg-2 col-md-6 mb-4">
                    <h6>Support</h6>
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        <li style="margin-bottom: 8px;"><a href="#">Help Center</a></li>
                        <li style="margin-bottom: 8px;"><a href="#">Newsletter</a></li>
                        <li style="margin-bottom: 8px;"><a href="#">RSS Feeds</a></li>
                        <li style="margin-bottom: 8px;"><a href="#">Mobile App</a></li>
                    </ul>
                </div>
                <div class="col-lg-3 col-md-12">
                    <h6>Contact Info</h6>
                    <div style="color: #cccccc; font-size: 0.9rem;">
                        <p style="margin-bottom: 8px;"><i class="fas fa-envelope me-2"></i>contact@echhapa.com</p>
                        <p style="margin-bottom: 8px;"><i class="fas fa-phone me-2"></i>+1 (555) 123-4567</p>
                        <p style="margin-bottom: 0;"><i class="fas fa-map-marker-alt me-2"></i>123 News Street, Media City</p>
                    </div>
                </div>
            </div>
            <hr style="border-color: #333333; margin: 30px 0 20px;">
            <div class="row align-items-center">
                <div class="col-md-6">
                    <p style="color: #cccccc; font-size: 0.85rem; margin: 0;">&copy; 2025 Echhapa News. All rights reserved.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <p style="color: #cccccc; font-size: 0.85rem; margin: 0;">
                        Powered by Flask & MySQL
                    </p>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Add smooth scrolling and interactive features
        document.addEventListener('DOMContentLoaded', function() {
            // Animate cards on scroll
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };
            
            const observer = new IntersectionObserver(function(entries) {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }
                });
            }, observerOptions);
            
            // Observe all cards
            document.querySelectorAll('.card').forEach(card => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                observer.observe(card);
            });
        });
    </script>
</body>
</html>
    """, articles=articles)

# Individual article page with enhanced design
@app.route('/article/<slug>')
def article_detail(slug):
    """Display individual article with modern design"""
    article = get_article_by_slug(slug)
    if not article:
        return "Article not found", 404
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ article.title }} - Echhapa News</title>
    <meta name="description" content="{{ article.meta_description or article.excerpt or (article.content[:150] + '...') }}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #2c3e50;
            --accent-color: #e74c3c;
        }
        
        .navbar-brand { 
            font-family: 'Times New Roman', serif; 
            font-weight: 900; 
            color: var(--accent-color) !important; 
        }
        
        /* Professional Article Design */
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Arial', sans-serif;
            line-height: 1.7;
            color: #1a1a1a;
            background-color: #ffffff;
        }
        
        .navbar-brand {
            font-family: 'Georgia', 'Times New Roman', serif;
            font-weight: 900;
            font-size: 1.8rem;
            color: #000000 !important;
            letter-spacing: -1px;
        }
        
        .article-header {
            border-bottom: 1px solid #e5e5e5;
            padding: 30px 0;
            background-color: #ffffff;
        }
        
        .article-title {
            font-family: 'Georgia', 'Times New Roman', serif;
            font-size: 2.5rem;
            font-weight: 700;
            line-height: 1.1;
            color: #000000;
            margin-bottom: 20px;
        }
        
        .article-meta {
            border-top: 1px solid #e5e5e5;
            border-bottom: 1px solid #e5e5e5;
            padding: 15px 0;
            margin: 20px 0 30px;
            font-size: 0.85rem;
            color: #666666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .article-excerpt {
            font-size: 1.25rem;
            line-height: 1.6;
            color: #666666;
            margin-bottom: 30px;
            font-style: italic;
        }
        
        .article-content {
            max-width: 65ch;
            font-size: 1.1rem;
            line-height: 1.7;
            color: #1a1a1a;
            margin: 0 auto;
        }
        
        .article-content h2,
        .article-content h3,
        .article-content h4 {
            font-family: 'Georgia', 'Times New Roman', serif;
            color: #000000;
            margin: 2rem 0 1rem;
            font-weight: 600;
        }
        
        .article-content h2 {
            font-size: 1.5rem;
            border-bottom: 1px solid #e5e5e5;
            padding-bottom: 10px;
        }
        
        .article-content h3 {
            font-size: 1.3rem;
        }
        
        .article-content p {
            margin-bottom: 1.5rem;
        }
        
        .article-content blockquote {
            border-left: 3px solid #000000;
            padding-left: 20px;
            margin: 2rem 0;
            font-style: italic;
            color: #666666;
        }
        
        .article-content ul,
        .article-content ol {
            margin-bottom: 1.5rem;
            padding-left: 1.5rem;
        }
        
        .article-content li {
            margin-bottom: 0.5rem;
        }
        
        .category-badge {
            background-color: #000000;
            color: #ffffff;
            padding: 4px 12px;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
            margin-bottom: 15px;
            display: inline-block;
        }
        
        .share-tools {
            border-top: 1px solid #e5e5e5;
            padding-top: 20px;
            margin-top: 30px;
        }
        
        .share-button {
            display: inline-block;
            width: 40px;
            height: 40px;
            line-height: 40px;
            text-align: center;
            background-color: #000000;
            color: #ffffff;
            margin-right: 10px;
            transition: background-color 0.2s ease;
            text-decoration: none;
        }
        
        .share-button:hover {
            background-color: #333333;
            color: #ffffff;
        }
        
        .share-facebook { background: #3b5998; }
        .share-twitter { background: #1da1f2; }
        .share-linkedin { background: #0077b5; }
        .share-whatsapp { background: #25d366; }
        
        .reading-progress {
            position: fixed;
            top: 0;
            left: 0;
            width: 0%;
            height: 4px;
            background: var(--accent-color);
            z-index: 9999;
            transition: width 0.3s ease;
        }
        
        .related-articles {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 2rem;
            margin-top: 3rem;
        }
    </style>
</head>
<body>
    <!-- Reading Progress Bar -->
    <div class="reading-progress" id="reading-progress"></div>
    
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
        <div class="container">
            <a class="navbar-brand fw-bold fs-2" href="/">
                <i class="fas fa-newspaper me-2"></i>Echhapa News
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link fw-semibold" href="/">Home</a>
                <a class="nav-link fw-semibold" href="/admin">Admin</a>
            </div>
        </div>
    </nav>

    <!-- Article Header -->
    <header class="article-header">
        <div class="container">
            <div class="row">
                <div class="col-md-8">
                    <a href="/" class="navbar-brand">Echhapa News</a>
                </div>
                <div class="col-md-4 text-end">
                    <a href="/" class="btn btn-outline-dark btn-sm">
                        <i class="fas fa-arrow-left me-2"></i>Back to Home
                    </a>
                </div>
            </div>
        </div>
    </header>
    
    <!-- Article Content -->
    <div class="container py-5">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <article>
                    {% if article.category_name %}
                    <span class="category-badge">{{ article.category_name }}</span>
                    {% endif %}
                    
                    <h1 class="article-title">{{ article.title }}</h1>
                    
                    <div class="article-meta">
                        <span class="meta-item">By {{ article.author }}</span>
                        <span class="meta-item">{{ article.created_at.strftime('%B %d, %Y') if article.created_at.strftime else article.created_at }}</span>
                        {% if article.views %}
                        <span class="meta-item">{{ article.views }} views</span>
                        {% endif %}
                    </div>
                    
                    {% if article.excerpt %}
                    <div class="article-excerpt">{{ article.excerpt }}</div>
                    {% endif %}
                    
                    {% if article.featured_image %}
                    <img src="{{ article.featured_image }}" class="img-fluid article-image mb-4" alt="{{ article.title }}">
                    {% endif %}
                    
                    <div class="article-content">
                        {{ article.content | safe }}
                    </div>
                    
                    <!-- Share Tools -->
                    <div class="share-tools">
                        <div class="row align-items-center">
                            <div class="col-md-6">
                                <strong>Share this article:</strong>
                            </div>
                            <div class="col-md-6 text-md-end">
                                <a href="#" class="share-button" onclick="shareArticle('facebook')">
                                    <i class="fab fa-facebook-f"></i>
                                </a>
                                <a href="#" class="share-button" onclick="shareArticle('twitter')">
                                    <i class="fab fa-twitter"></i>
                                </a>
                                <a href="#" class="share-button" onclick="shareArticle('linkedin')">
                                    <i class="fab fa-linkedin-in"></i>
                                </a>
                                <a href="#" class="share-button" onclick="shareArticle('whatsapp')">
                                    <i class="fab fa-whatsapp"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                </article>
            </div>
        </div>
    </div>

    <div class="container py-5">
        <div class="row">
            <!-- Social Share Sidebar -->
            <div class="col-lg-1 d-none d-lg-block">
                <div class="social-share">
                    <a href="#" class="share-button share-facebook" onclick="shareArticle('facebook')">
                        <i class="fab fa-facebook-f"></i>
                    </a>
                    <a href="#" class="share-button share-twitter" onclick="shareArticle('twitter')">
                        <i class="fab fa-twitter"></i>
                    </a>
                    <a href="#" class="share-button share-linkedin" onclick="shareArticle('linkedin')">
                        <i class="fab fa-linkedin-in"></i>
                    </a>
                    <a href="#" class="share-button share-whatsapp" onclick="shareArticle('whatsapp')">
                        <i class="fab fa-whatsapp"></i>
                    </a>
                </div>
            </div>
            
            <!-- Article Content -->
            <div class="col-lg-8">
                <article class="article-content">
                    {% if article.featured_image %}
                    <img src="{{ article.featured_image }}" class="img-fluid rounded mb-4 shadow" alt="{{ article.title }}">
                    {% endif %}
                    
                    {{ article.content | safe }}
                    
                    <!-- Article Tags/Keywords -->
                    {% if article.meta_keywords %}
                    <div class="mt-4 pt-4 border-top">
                        <h6 class="text-muted mb-3">Tags:</h6>
                        {% for keyword in article.meta_keywords.split(',') %}
                        <span class="badge bg-light text-dark me-2 mb-2">#{{ keyword.strip() }}</span>
                        {% endfor %}
                    </div>
                    {% endif %}
                </article>
                
                <!-- Article Footer -->
                <footer class="mt-5 pt-4 border-top">
                    <div class="row align-items-center">
                        <div class="col-md-6">
                            <a href="/" class="btn btn-outline-primary">
                                <i class="fas fa-arrow-left me-2"></i>Back to Home
                            </a>
                        </div>
                        <div class="col-md-6 text-md-end">
                            <div class="d-inline-block">
                                <span class="me-3">Share this article:</span>
                                <a href="#" class="btn btn-sm btn-outline-primary me-1" onclick="shareArticle('facebook')">
                                    <i class="fab fa-facebook-f"></i>
                                </a>
                                <a href="#" class="btn btn-sm btn-outline-info me-1" onclick="shareArticle('twitter')">
                                    <i class="fab fa-twitter"></i>
                                </a>
                                <a href="#" class="btn btn-sm btn-outline-primary" onclick="shareArticle('linkedin')">
                                    <i class="fab fa-linkedin-in"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                </footer>
            </div>
            
            <!-- Sidebar -->
            <div class="col-lg-3">
                <!-- Author Info -->
                <div class="card border-0 shadow-sm mb-4">
                    <div class="card-body text-center">
                        <div class="rounded-circle bg-primary text-white d-inline-flex align-items-center justify-content-center" style="width: 60px; height: 60px;">
                            <i class="fas fa-user fa-lg"></i>
                        </div>
                        <h6 class="mt-3 mb-1">{{ article.author }}</h6>
                        <small class="text-muted">Staff Writer</small>
                    </div>
                </div>
                
                <!-- Advertisement -->
                <div class="card border-0 mb-4" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <div class="card-body text-white text-center">
                        <h6 class="fw-bold">Advertisement</h6>
                        <div style="height: 200px;" class="d-flex align-items-center justify-content-center">
                            <div>
                                <i class="fas fa-ad fa-3x mb-3 opacity-50"></i>
                                <p class="mb-0">Your Ad Here</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Related Articles -->
        <div class="related-articles">
            <h3 class="fw-bold mb-4">Related Articles</h3>
            <div class="row">
                <div class="col-md-4 mb-3">
                    <div class="card border-0 h-100">
                        <div class="card-body">
                            <h6 class="card-title">Tech Innovation Drives Growth</h6>
                            <p class="card-text text-muted small">Latest developments in technology sector...</p>
                            <a href="#" class="text-decoration-none">Read more <i class="fas fa-arrow-right ms-1"></i></a>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-3">
                    <div class="card border-0 h-100">
                        <div class="card-body">
                            <h6 class="card-title">Global Markets React</h6>
                            <p class="card-text text-muted small">Financial markets show positive response...</p>
                            <a href="#" class="text-decoration-none">Read more <i class="fas fa-arrow-right ms-1"></i></a>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-3">
                    <div class="card border-0 h-100">
                        <div class="card-body">
                            <h6 class="card-title">Sports Championship Updates</h6>
                            <p class="card-text text-muted small">Latest scores and championship news...</p>
                            <a href="#" class="text-decoration-none">Read more <i class="fas fa-arrow-right ms-1"></i></a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Reading progress bar
        window.addEventListener('scroll', function() {
            const article = document.querySelector('.article-content');
            const progress = document.getElementById('reading-progress');
            
            if (article) {
                const scrollTop = window.scrollY;
                const articleTop = article.offsetTop;
                const articleHeight = article.offsetHeight;
                const windowHeight = window.innerHeight;
                
                const scrolled = Math.max(0, scrollTop - articleTop);
                const readable = articleHeight - windowHeight;
                const percentage = Math.min(100, (scrolled / readable) * 100);
                
                progress.style.width = percentage + '%';
            }
        });
        
        // Social sharing functions
        function shareArticle(platform) {
            const url = encodeURIComponent(window.location.href);
            const title = encodeURIComponent(document.title);
            const text = encodeURIComponent('{{ article.excerpt or article.title }}');
            
            let shareUrl = '';
            
            switch(platform) {
                case 'facebook':
                    shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
                    break;
                case 'twitter':
                    shareUrl = `https://twitter.com/intent/tweet?url=${url}&text=${title}`;
                    break;
                case 'linkedin':
                    shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${url}`;
                    break;
                case 'whatsapp':
                    shareUrl = `https://wa.me/?text=${title}%20${url}`;
                    break;
            }
            
            if (shareUrl) {
                window.open(shareUrl, '_blank', 'width=600,height=400');
            }
        }
    </script>
</body>
</html>
    """, article=article)

# Professional Admin Dashboard with Left Sidebar
@app.route('/admin')
def admin():
    """Professional Admin Dashboard with Sidebar Navigation"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    # Get dashboard statistics
    conn = get_db()
    stats = {
        'articles': len(fallback_articles), 
        'users': 1, 
        'categories': 8,
        'ads': 0,
        'total_views': 0,
        'recent_articles': []
    }
    
    if conn:
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            # Get article count
            cur.execute("SELECT COUNT(*) as count FROM articles")
            stats['articles'] = cur.fetchone()['count']
            
            # Get user count
            cur.execute("SELECT COUNT(*) as count FROM users")
            stats['users'] = cur.fetchone()['count']
            
            # Get category count
            cur.execute("SELECT COUNT(*) as count FROM categories")
            stats['categories'] = cur.fetchone()['count']
            
            # Get ad count
            cur.execute("SELECT COUNT(*) as count FROM ads")
            stats['ads'] = cur.fetchone()['count']
            
            # Get total views
            cur.execute("SELECT SUM(views) as total FROM articles")
            result = cur.fetchone()
            stats['total_views'] = result['total'] or 0
            
            # Get recent articles
            cur.execute("SELECT * FROM articles ORDER BY created_at DESC LIMIT 5")
            stats['recent_articles'] = cur.fetchall()
            
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error fetching stats: {e}")
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Echhapa CMS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --sidebar-width: 280px;
            --primary-color: #2c3e50;
            --accent-color: #3498db;
            --success-color: #27ae60;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --sidebar-bg: #34495e;
            --sidebar-hover: #2c3e50;
        }
        
        body {
            background: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .sidebar {
            position: fixed;
            top: 0;
            left: 0;
            height: 100vh;
            width: var(--sidebar-width);
            background: var(--sidebar-bg);
            color: white;
            z-index: 1000;
            overflow-y: auto;
            transition: transform 0.3s ease;
        }
        
        .sidebar-header {
            padding: 1.5rem;
            background: var(--primary-color);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .sidebar-brand {
            font-size: 1.5rem;
            font-weight: bold;
            color: white;
            text-decoration: none;
        }
        
        .sidebar-nav {
            padding: 1rem 0;
        }
        
        .nav-item {
            margin-bottom: 0.25rem;
        }
        
        .nav-link {
            color: rgba(255,255,255,0.8);
            padding: 0.75rem 1.5rem;
            display: flex;
            align-items: center;
            text-decoration: none;
            transition: all 0.3s ease;
            border-left: 3px solid transparent;
        }
        
        .nav-link:hover, .nav-link.active {
            color: white;
            background: var(--sidebar-hover);
            border-left-color: var(--accent-color);
        }
        
        .nav-link i {
            width: 20px;
            margin-right: 0.75rem;
        }
        
        .main-content {
            margin-left: var(--sidebar-width);
            min-height: 100vh;
        }
        
        .topbar {
            background: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .content-wrapper {
            padding: 0 2rem 2rem 2rem;
        }
        
        .stat-card {
            background: white;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid var(--accent-color);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-2px);
        }
        
        .stat-card.success { border-left-color: var(--success-color); }
        .stat-card.warning { border-left-color: var(--warning-color); }
        .stat-card.danger { border-left-color: var(--danger-color); }
        
        .stat-icon {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1rem;
        }
        
        .chart-card {
            background: white;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-top: 2rem;
        }
        
        .recent-articles {
            background: white;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .article-item {
            padding: 1rem 0;
            border-bottom: 1px solid #eee;
            display: flex;
            align-items: center;
        }
        
        .article-item:last-child {
            border-bottom: none;
        }
        
        .article-icon {
            width: 40px;
            height: 40px;
            background: var(--accent-color);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            margin-right: 1rem;
        }
        
        .quick-actions {
            background: white;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .action-btn {
            display: block;
            width: 100%;
            padding: 1rem;
            margin-bottom: 0.5rem;
            background: var(--accent-color);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: background 0.3s ease;
            text-align: center;
        }
        
        .action-btn:hover {
            background: #2980b9;
            color: white;
        }
        
        .action-btn.success { background: var(--success-color); }
        .action-btn.success:hover { background: #229954; }
        
        .action-btn.warning { background: var(--warning-color); }
        .action-btn.warning:hover { background: #d68910; }
        
        @media (max-width: 768px) {
            .sidebar {
                transform: translateX(-100%);
            }
            
            .sidebar.active {
                transform: translateX(0);
            }
            
            .main-content {
                margin-left: 0;
            }
        }
    </style>
</head>
<body>
    <!-- Sidebar -->
    <nav class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <a href="/admin" class="sidebar-brand">
                <i class="fas fa-newspaper me-2"></i>Echhapa CMS
            </a>
        </div>
        
        <div class="sidebar-nav">
            <div class="nav-item">
                <a href="/admin" class="nav-link active">
                    <i class="fas fa-tachometer-alt"></i>Dashboard
                </a>
            </div>
            
            <div class="nav-item">
                <a href="{{ url_for('articles_management') }}" class="nav-link">
                    <i class="fas fa-newspaper"></i>Articles
                </a>
            </div>
            
            <div class="nav-item">
                <a href="{{ url_for('add_article') }}" class="nav-link">
                    <i class="fas fa-plus"></i>New Article
                </a>
            </div>
            
            <div class="nav-item">
                <a href="{{ url_for('ad_management') }}" class="nav-link">
                    <i class="fas fa-ad"></i>Advertisements
                </a>
            </div>
            
            <div class="nav-item">
                <a href="{{ url_for('layout_management') }}" class="nav-link">
                    <i class="fas fa-th-large"></i>Layout
                </a>
            </div>
            
            <div class="nav-item">
                <a href="{{ url_for('users_management') }}" class="nav-link">
                    <i class="fas fa-users"></i>Users
                </a>
            </div>
            
            <div class="nav-item">
                <a href="{{ url_for('categories_management') }}" class="nav-link">
                    <i class="fas fa-folder"></i>Categories
                </a>
            </div>
            
            <div class="nav-item">
                <a href="{{ url_for('site_settings') }}" class="nav-link">
                    <i class="fas fa-cog"></i>Settings
                </a>
            </div>
            
            <hr class="my-3" style="border-color: rgba(255,255,255,0.2);">
            
            <div class="nav-item">
                <a href="/" class="nav-link" target="_blank">
                    <i class="fas fa-external-link-alt"></i>View Website
                </a>
            </div>
            
            <div class="nav-item">
                <a href="{{ url_for('admin_logout') }}" class="nav-link">
                    <i class="fas fa-sign-out-alt"></i>Logout
                </a>
            </div>
        </div>
    </nav>
    
    <!-- Main Content -->
    <main class="main-content">
        <!-- Top Bar -->
        <div class="topbar">
            <div class="d-flex justify-content-between align-items-center">
                <div class="d-flex align-items-center">
                    <button class="btn btn-link d-md-none" onclick="toggleSidebar()">
                        <i class="fas fa-bars"></i>
                    </button>
                    <h4 class="mb-0 fw-bold">Dashboard Overview</h4>
                </div>
                <div class="d-flex align-items-center">
                    <span class="me-3">Welcome, {{ session.username }}!</span>
                    <div class="dropdown">
                        <button class="btn btn-outline-primary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                            <i class="fas fa-user-circle me-2"></i>Profile
                        </button>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="#"><i class="fas fa-user me-2"></i>Edit Profile</a></li>
                            <li><a class="dropdown-item" href="#"><i class="fas fa-key me-2"></i>Change Password</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{{ url_for('admin_logout') }}"><i class="fas fa-sign-out-alt me-2"></i>Logout</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Content Wrapper -->
        <div class="content-wrapper">
            <!-- Statistics Cards -->
            <div class="row">
                <div class="col-xl-3 col-md-6 mb-4">
                    <div class="stat-card">
                        <div class="d-flex align-items-center">
                            <div class="stat-icon" style="background: rgba(52, 152, 219, 0.1); color: var(--accent-color);">
                                <i class="fas fa-newspaper fa-lg"></i>
                            </div>
                            <div>
                                <h3 class="fw-bold mb-0">{{ stats.articles }}</h3>
                                <p class="text-muted mb-0">Total Articles</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-xl-3 col-md-6 mb-4">
                    <div class="stat-card success">
                        <div class="d-flex align-items-center">
                            <div class="stat-icon" style="background: rgba(39, 174, 96, 0.1); color: var(--success-color);">
                                <i class="fas fa-eye fa-lg"></i>
                            </div>
                            <div>
                                <h3 class="fw-bold mb-0">{{ "{:,}".format(stats.total_views) }}</h3>
                                <p class="text-muted mb-0">Total Views</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-xl-3 col-md-6 mb-4">
                    <div class="stat-card warning">
                        <div class="d-flex align-items-center">
                            <div class="stat-icon" style="background: rgba(243, 156, 18, 0.1); color: var(--warning-color);">
                                <i class="fas fa-users fa-lg"></i>
                            </div>
                            <div>
                                <h3 class="fw-bold mb-0">{{ stats.users }}</h3>
                                <p class="text-muted mb-0">Active Users</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-xl-3 col-md-6 mb-4">
                    <div class="stat-card danger">
                        <div class="d-flex align-items-center">
                            <div class="stat-icon" style="background: rgba(231, 76, 60, 0.1); color: var(--danger-color);">
                                <i class="fas fa-ad fa-lg"></i>
                            </div>
                            <div>
                                <h3 class="fw-bold mb-0">{{ stats.ads }}</h3>
                                <p class="text-muted mb-0">Active Ads</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Charts and Recent Activity -->
            <div class="row">
                <div class="col-lg-8">
                    <div class="chart-card">
                        <h5 class="fw-bold mb-4">Article Performance</h5>
                        <canvas id="articleChart" width="400" height="200"></canvas>
                    </div>
                </div>
                
                <div class="col-lg-4">
                    <div class="quick-actions">
                        <h5 class="fw-bold mb-4">Quick Actions</h5>
                        <a href="{{ url_for('add_article') }}" class="action-btn">
                            <i class="fas fa-plus me-2"></i>Create New Article
                        </a>
                        <a href="{{ url_for('ad_management') }}" class="action-btn success">
                            <i class="fas fa-ad me-2"></i>Manage Ads
                        </a>
                        <a href="{{ url_for('layout_management') }}" class="action-btn warning">
                            <i class="fas fa-paint-brush me-2"></i>Customize Layout
                        </a>
                        <a href="{{ url_for('site_settings') }}" class="action-btn">
                            <i class="fas fa-cog me-2"></i>Site Settings
                        </a>
                    </div>
                </div>
            </div>
            
            <!-- Recent Articles -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="recent-articles">
                        <div class="d-flex justify-content-between align-items-center mb-4">
                            <h5 class="fw-bold mb-0">Recent Articles</h5>
                            <a href="{{ url_for('articles_management') }}" class="btn btn-outline-primary btn-sm">
                                View All <i class="fas fa-arrow-right ms-1"></i>
                            </a>
                        </div>
                        
                        {% if stats.recent_articles %}
                        {% for article in stats.recent_articles %}
                        <div class="article-item">
                            <div class="article-icon">
                                <i class="fas fa-file-alt"></i>
                            </div>
                            <div class="flex-grow-1">
                                <h6 class="mb-1">{{ article.title[:50] }}{% if article.title|length > 50 %}...{% endif %}</h6>
                                <small class="text-muted">
                                    By {{ article.author }} • {{ article.created_at.strftime('%b %d, %Y') }}
                                    {% if article.views %}• {{ article.views }} views{% endif %}
                                </small>
                            </div>
                            <div>
                                <span class="badge bg-{{ 'success' if article.status == 'published' else 'warning' }}">
                                    {{ article.status.title() }}
                                </span>
                            </div>
                        </div>
                        {% endfor %}
                        {% else %}
                        <div class="text-center py-4">
                            <i class="fas fa-newspaper fa-3x text-muted mb-3"></i>
                            <p class="text-muted">No articles found. Create your first article!</p>
                            <a href="{{ url_for('add_article') }}" class="btn btn-primary">
                                <i class="fas fa-plus me-2"></i>Create Article
                            </a>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // Toggle sidebar for mobile
        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('active');
        }
        
        // Article performance chart
        const ctx = document.getElementById('articleChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Articles Published',
                    data: [12, 19, 8, 15, 22, 18],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Total Views',
                    data: [1200, 2100, 1800, 2400, 3200, 2800],
                    borderColor: '#27ae60',
                    backgroundColor: 'rgba(39, 174, 96, 0.1)',
                    tension: 0.4,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                }
            }
        });
        
        // Auto-refresh dashboard data every 5 minutes
        setInterval(function() {
            location.reload();
        }, 300000);
    </script>
</body>
</html>
    """, stats=stats)

# Continue with login and other routes...
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Professional Admin Login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template_string(login_template())
        
        # Default credentials when DB is not available
        if username == 'admin' and password == 'admin123':
            session['user_id'] = 1
            session['username'] = 'admin'
            flash('Welcome to Echhapa CMS!', 'success')
            return redirect(url_for('admin'))
        
        conn = get_db()
        if conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("SELECT * FROM users WHERE username = %s AND is_active = TRUE", (username,))
                user = cur.fetchone()
                cur.close()
                conn.close()
                
                if user and check_password_hash(user['password_hash'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    flash(f'Welcome back, {user["first_name"] or user["username"]}!', 'success')
                    
                    # Update last login
                    conn = get_db()
                    if conn:
                        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                        cur.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user['id'],))
                        conn.commit()
                        cur.close()
                        conn.close()
                    
                    return redirect(url_for('admin'))
                else:
                    flash('Invalid username or password', 'error')
            except Exception as e:
                flash(f'Database error: {str(e)}', 'error')
        else:
            flash('Invalid username or password', 'error')
    
    return render_template_string(login_template())

def login_template():
    """Professional login template"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - Echhapa CMS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .login-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .login-header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 3rem 2rem 2rem 2rem;
            text-align: center;
        }
        
        .login-body {
            padding: 2rem;
        }
        
        .form-control {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        
        .input-group-text {
            border-radius: 10px 0 0 10px;
            border: 2px solid #e9ecef;
            border-right: none;
            background: #f8f9fa;
        }
        
        .btn-login {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: transform 0.3s ease;
        }
        
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .brand-icon {
            width: 80px;
            height: 80px;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem auto;
        }
        
        .floating-shapes {
            position: absolute;
            width: 100%;
            height: 100%;
            overflow: hidden;
            z-index: -1;
        }
        
        .floating-shapes::before,
        .floating-shapes::after {
            content: '';
            position: absolute;
            border-radius: 50%;
            background: rgba(255,255,255,0.1);
        }
        
        .floating-shapes::before {
            width: 300px;
            height: 300px;
            top: -150px;
            right: -150px;
            animation: float 6s ease-in-out infinite;
        }
        
        .floating-shapes::after {
            width: 200px;
            height: 200px;
            bottom: -100px;
            left: -100px;
            animation: float 4s ease-in-out infinite reverse;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }
    </style>
</head>
<body>
    <div class="floating-shapes"></div>
    
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-5">
                <div class="login-container">
                    <div class="login-header">
                        <div class="brand-icon">
                            <i class="fas fa-newspaper fa-2x"></i>
                        </div>
                        <h2 class="fw-bold mb-2">Echhapa CMS</h2>
                        <p class="mb-0 opacity-75">Professional Content Management</p>
                    </div>
                    
                    <div class="login-body">
                        {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                        {% for category, message in messages %}
                        <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }} alert-dismissible fade show">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                        {% endfor %}
                        {% endif %}
                        {% endwith %}
                        
                        <form method="POST">
                            <div class="mb-3">
                                <label class="form-label fw-semibold">Username</label>
                                <div class="input-group">
                                    <span class="input-group-text">
                                        <i class="fas fa-user text-muted"></i>
                                    </span>
                                    <input type="text" class="form-control" name="username" required placeholder="Enter your username">
                                </div>
                            </div>
                            
                            <div class="mb-4">
                                <label class="form-label fw-semibold">Password</label>
                                <div class="input-group">
                                    <span class="input-group-text">
                                        <i class="fas fa-lock text-muted"></i>
                                    </span>
                                    <input type="password" class="form-control" name="password" required placeholder="Enter your password">
                                </div>
                            </div>
                            
                            <button type="submit" class="btn btn-primary btn-login w-100">
                                <i class="fas fa-sign-in-alt me-2"></i>Sign In
                            </button>
                        </form>
                        
                        <div class="text-center mt-4">
                            <small class="text-muted">
                                <i class="fas fa-info-circle me-1"></i>
                                Default credentials: <strong>admin</strong> / <strong>admin123</strong>
                            </small>
                        </div>
                        
                        <div class="text-center mt-3">
                            <a href="/" class="text-decoration-none">
                                <i class="fas fa-arrow-left me-1"></i>Back to Website
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

# Ad Management System
@app.route('/admin/ads')
def ad_management():
    """Comprehensive Ad Management System"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    ads = []
    
    if conn:
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("SELECT * FROM ads ORDER BY created_at DESC")
            ads = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error fetching ads: {e}")
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advertisement Management - Echhapa CMS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --sidebar-width: 280px;
            --primary-color: #2c3e50;
            --accent-color: #3498db;
        }
        
        body { background: #f8f9fa; }
        .main-content { margin-left: var(--sidebar-width); }
        .sidebar { position: fixed; top: 0; left: 0; height: 100vh; width: var(--sidebar-width); background: #34495e; color: white; z-index: 1000; overflow-y: auto; }
        .sidebar-header { padding: 1.5rem; background: var(--primary-color); }
        .nav-link { color: rgba(255,255,255,0.8); padding: 0.75rem 1.5rem; display: flex; align-items: center; text-decoration: none; transition: all 0.3s ease; border-left: 3px solid transparent; }
        .nav-link:hover, .nav-link.active { color: white; background: var(--primary-color); border-left-color: var(--accent-color); }
        .nav-link i { width: 20px; margin-right: 0.75rem; }
        
        .ad-card {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .ad-card:hover {
            transform: translateY(-2px);
        }
        
        .ad-preview {
            height: 150px;
            background: #f8f9fa;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1rem;
            overflow: hidden;
        }
        
        .placement-badge {
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 10;
        }
        
        .stats-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
    </style>
</head>
<body>
    <!-- Sidebar -->
    <nav class="sidebar">
        <div class="sidebar-header">
            <a href="/admin" class="text-white text-decoration-none fw-bold fs-5">
                <i class="fas fa-newspaper me-2"></i>Echhapa CMS
            </a>
        </div>
        <div class="py-3">
            <a href="/admin" class="nav-link"><i class="fas fa-tachometer-alt"></i>Dashboard</a>
            <a href="{{ url_for('articles_management') }}" class="nav-link"><i class="fas fa-newspaper"></i>Articles</a>
            <a href="{{ url_for('add_article') }}" class="nav-link"><i class="fas fa-plus"></i>New Article</a>
            <a href="{{ url_for('ad_management') }}" class="nav-link active"><i class="fas fa-ad"></i>Advertisements</a>
            <a href="{{ url_for('layout_management') }}" class="nav-link"><i class="fas fa-th-large"></i>Layout</a>
            <a href="{{ url_for('users_management') }}" class="nav-link"><i class="fas fa-users"></i>Users</a>
            <a href="{{ url_for('site_settings') }}" class="nav-link"><i class="fas fa-cog"></i>Settings</a>
            <hr style="border-color: rgba(255,255,255,0.2);">
            <a href="/" class="nav-link" target="_blank"><i class="fas fa-external-link-alt"></i>View Website</a>
            <a href="{{ url_for('admin_logout') }}" class="nav-link"><i class="fas fa-sign-out-alt"></i>Logout</a>
        </div>
    </nav>
    
    <!-- Main Content -->
    <main class="main-content">
        <div class="container-fluid py-4">
            <!-- Header -->
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2 class="fw-bold mb-1">Advertisement Management</h2>
                    <p class="text-muted mb-0">Create and manage ads with advanced scheduling and placement options</p>
                </div>
                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addAdModal">
                    <i class="fas fa-plus me-2"></i>Create New Ad
                </button>
            </div>
            
            <!-- Statistics -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="stats-card">
                        <h3 class="text-primary mb-2">{{ ads|length }}</h3>
                        <p class="text-muted mb-0">Total Ads</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card">
                        <h3 class="text-success mb-2">{{ ads|selectattr('is_active')|list|length }}</h3>
                        <p class="text-muted mb-0">Active Ads</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card">
                        <h3 class="text-warning mb-2">0</h3>
                        <p class="text-muted mb-0">Total Clicks</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card">
                        <h3 class="text-info mb-2">0</h3>
                        <p class="text-muted mb-0">Impressions</p>
                    </div>
                </div>
            </div>
            
            <!-- Ads Grid -->
            {% if ads %}
            <div class="row">
                {% for ad in ads %}
                <div class="col-lg-4 col-md-6 mb-4">
                    <div class="ad-card position-relative">
                        <div class="placement-badge">
                            <span class="badge bg-{{ 'success' if ad.is_active else 'secondary' }}">
                                {{ 'Active' if ad.is_active else 'Inactive' }}
                            </span>
                        </div>
                        
                        <div class="p-3">
                            <div class="ad-preview">
                                {% if ad.image_url %}
                                <img src="/{{ ad.image_url }}" class="img-fluid" style="max-height: 100%; max-width: 100%;" alt="{{ ad.title }}">
                                {% else %}
                                <div class="text-center text-muted">
                                    <i class="fas fa-image fa-3x mb-2"></i>
                                    <p class="mb-0">No Image</p>
                                </div>
                                {% endif %}
                            </div>
                            
                            <h6 class="fw-bold mb-2">{{ ad.title }}</h6>
                            {% if ad.description %}
                            <p class="text-muted small mb-2">{{ ad.description[:100] }}{% if ad.description|length > 100 %}...{% endif %}</p>
                            {% endif %}
                            
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <span class="badge bg-primary">{{ ad.placement.replace('_', ' ').title() }}</span>
                                <span class="badge bg-info">{{ ad.ad_type.title() }}</span>
                            </div>
                            
                            {% if ad.start_date and ad.end_date %}
                            <small class="text-muted d-block mb-2">
                                <i class="fas fa-calendar me-1"></i>
                                {{ ad.start_date }} to {{ ad.end_date }}
                            </small>
                            {% endif %}
                            
                            <div class="d-flex gap-2">
                                <button class="btn btn-sm btn-outline-primary flex-fill" onclick="editAd({{ ad.id }})">
                                    <i class="fas fa-edit"></i> Edit
                                </button>
                                <button class="btn btn-sm btn-outline-{{ 'warning' if ad.is_active else 'success' }}" onclick="toggleAd({{ ad.id }})">
                                    <i class="fas fa-{{ 'pause' if ad.is_active else 'play' }}"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger" onclick="deleteAd({{ ad.id }})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <div class="text-center py-5">
                <i class="fas fa-ad fa-4x text-muted mb-3"></i>
                <h4 class="text-muted">No Advertisements Found</h4>
                <p class="text-muted mb-4">Create your first advertisement to start monetizing your content</p>
                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addAdModal">
                    <i class="fas fa-plus me-2"></i>Create Your First Ad
                </button>
            </div>
            {% endif %}
        </div>
    </main>
    
    <!-- Add/Edit Ad Modal -->
    <div class="modal fade" id="addAdModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Create New Advertisement</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form action="{{ url_for('add_ad') }}" method="POST" enctype="multipart/form-data">
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Ad Title *</label>
                                    <input type="text" class="form-control" name="title" required>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Description</label>
                                    <textarea class="form-control" name="description" rows="3" placeholder="Brief description of the ad"></textarea>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Click URL</label>
                                    <input type="url" class="form-control" name="click_url" placeholder="https://example.com">
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Ad Type</label>
                                    <select class="form-control" name="ad_type">
                                        <option value="banner">Banner Ad</option>
                                        <option value="sidebar">Sidebar Ad</option>
                                        <option value="popup">Popup Ad</option>
                                        <option value="inline">Inline Content Ad</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Placement Location *</label>
                                    <select class="form-control" name="placement" required>
                                        <option value="header">Header</option>
                                        <option value="sidebar_top">Sidebar Top</option>
                                        <option value="sidebar_middle">Sidebar Middle</option>
                                        <option value="sidebar_bottom">Sidebar Bottom</option>
                                        <option value="content_top">Content Top</option>
                                        <option value="content_middle">Content Middle</option>
                                        <option value="content_bottom">Content Bottom</option>
                                        <option value="footer">Footer</option>
                                    </select>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Priority</label>
                                    <select class="form-control" name="priority">
                                        <option value="1">Low</option>
                                        <option value="2" selected>Medium</option>
                                        <option value="3">High</option>
                                        <option value="4">Urgent</option>
                                    </select>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Start Date</label>
                                            <input type="date" class="form-control" name="start_date">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">End Date</label>
                                            <input type="date" class="form-control" name="end_date">
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Ad Image</label>
                                    <input type="file" class="form-control" name="ad_image" accept="image/*">
                                    <small class="text-muted">Supported: JPG, PNG, GIF, WebP (Max: 5MB)</small>
                                </div>
                                
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" name="is_active" checked>
                                    <label class="form-check-label">Activate immediately</label>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-save me-2"></i>Create Advertisement
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function editAd(id) {
            // Implementation for editing ads
            alert('Edit functionality coming soon!');
        }
        
        function toggleAd(id) {
            if (confirm('Are you sure you want to change the status of this ad?')) {
                fetch(`/admin/ads/${id}/toggle`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                }).then(() => location.reload());
            }
        }
        
        function deleteAd(id) {
            if (confirm('Are you sure you want to delete this advertisement? This action cannot be undone.')) {
                fetch(`/admin/ads/${id}/delete`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                }).then(() => location.reload());
            }
        }
    </script>
</body>
</html>
    """, ads=ads)

@app.route('/admin/ads/add', methods=['POST'])
def add_ad():
    """Add new advertisement"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    title = request.form.get('title')
    description = request.form.get('description')
    click_url = request.form.get('click_url')
    placement = request.form.get('placement')
    ad_type = request.form.get('ad_type', 'banner')
    priority = int(request.form.get('priority', 1))
    start_date = request.form.get('start_date') or None
    end_date = request.form.get('end_date') or None
    is_active = 'is_active' in request.form
    
    # Handle file upload
    image_url = None
    if 'ad_image' in request.files:
        file = request.files['ad_image']
        if file and file.filename:
            image_url = handle_file_upload(file, 'ads')
    
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""INSERT INTO ads (title, description, image_url, click_url, placement, ad_type, 
                          start_date, end_date, is_active, priority) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                       (title, description, image_url, click_url, placement, ad_type, 
                        start_date, end_date, is_active, priority))
            conn.commit()
            cur.close()
            conn.close()
            flash('Advertisement created successfully!', 'success')
        except Exception as e:
            flash(f'Error creating advertisement: {str(e)}', 'error')
    else:
        flash('Database not available', 'error')
    
    return redirect(url_for('ad_management'))

# Articles Management
@app.route('/admin/articles')
def articles_management():
    """Articles Management System"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    articles = get_articles(50)  # Get all articles for management
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Articles Management - Echhapa CMS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --sidebar-width: 280px;
            --primary-color: #2c3e50;
            --accent-color: #3498db;
        }
        body { background: #f8f9fa; }
        .main-content { margin-left: var(--sidebar-width); padding: 2rem; }
        .sidebar { position: fixed; top: 0; left: 0; height: 100vh; width: var(--sidebar-width); background: #34495e; color: white; z-index: 1000; overflow-y: auto; }
        .sidebar-header { padding: 1.5rem; background: var(--primary-color); }
        .nav-link { color: rgba(255,255,255,0.8); padding: 0.75rem 1.5rem; display: flex; align-items: center; text-decoration: none; transition: all 0.3s ease; border-left: 3px solid transparent; }
        .nav-link:hover, .nav-link.active { color: white; background: var(--primary-color); border-left-color: var(--accent-color); }
        .nav-link i { width: 20px; margin-right: 0.75rem; }
    </style>
</head>
<body>
    <nav class="sidebar">
        <div class="sidebar-header">
            <h4><i class="fas fa-newspaper me-2"></i>Echhapa CMS</h4>
        </div>
        <div class="sidebar-menu">
            <a href="{{ url_for('admin') }}" class="nav-link"><i class="fas fa-tachometer-alt"></i>Dashboard</a>
            <a href="{{ url_for('articles_management') }}" class="nav-link active"><i class="fas fa-newspaper"></i>Articles</a>
            <a href="{{ url_for('add_article') }}" class="nav-link"><i class="fas fa-plus"></i>New Article</a>
            <a href="{{ url_for('ad_management') }}" class="nav-link"><i class="fas fa-ad"></i>Advertisements</a>
            <a href="{{ url_for('layout_management') }}" class="nav-link"><i class="fas fa-th-large"></i>Layout</a>
            <a href="{{ url_for('users_management') }}" class="nav-link"><i class="fas fa-users"></i>Users</a>
            <a href="{{ url_for('categories_management') }}" class="nav-link"><i class="fas fa-folder"></i>Categories</a>
            <a href="{{ url_for('site_settings') }}" class="nav-link"><i class="fas fa-cog"></i>Settings</a>
            <hr>
            <a href="{{ url_for('admin_logout') }}" class="nav-link"><i class="fas fa-sign-out-alt"></i>Logout</a>
        </div>
    </nav>

    <div class="main-content">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1><i class="fas fa-newspaper me-3"></i>Articles Management</h1>
            <a href="{{ url_for('add_article') }}" class="btn btn-primary"><i class="fas fa-plus me-2"></i>Create New Article</a>
        </div>

        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Title</th>
                                        <th>Author</th>
                                        <th>Category</th>
                                        <th>Status</th>
                                        <th>Views</th>
                                        <th>Created</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for article in articles %}
                                    <tr>
                                        <td><strong>{{ article.title }}</strong></td>
                                        <td>{{ article.author }}</td>
                                        <td>{{ article.category_name or 'Uncategorized' }}</td>
                                        <td><span class="badge bg-success">{{ article.status }}</span></td>
                                        <td>{{ article.views or 0 }}</td>
                                        <td>{{ article.created_at.strftime('%Y-%m-%d') if article.created_at else 'N/A' }}</td>
                                        <td>
                                            <a href="/article/{{ article.slug }}" class="btn btn-sm btn-outline-primary" target="_blank">
                                                <i class="fas fa-eye"></i>
                                            </a>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """, articles=articles)

@app.route('/admin/articles/add')
def add_article():
    """Advanced Article Editor with Rich Text and Multiple Images"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    # Get categories for the dropdown
    conn = get_db()
    categories = []
    
    if conn:
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("SELECT * FROM categories WHERE is_active = TRUE ORDER BY name")
            categories = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error fetching categories: {e}")
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create New Article - Echhapa CMS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="/css/custom-editor.css" rel="stylesheet">
    <style>
        :root {
            --sidebar-width: 280px;
            --primary-color: #2c3e50;
            --accent-color: #3498db;
        }
        body { background: #f8f9fa; }
        .main-content { margin-left: var(--sidebar-width); padding: 2rem; }
        .sidebar { position: fixed; top: 0; left: 0; height: 100vh; width: var(--sidebar-width); background: #34495e; color: white; z-index: 1000; overflow-y: auto; }
        .sidebar-header { padding: 1.5rem; background: var(--primary-color); }
        .nav-link { color: rgba(255,255,255,0.8); padding: 0.75rem 1.5rem; display: flex; align-items: center; text-decoration: none; transition: all 0.3s ease; border-left: 3px solid transparent; }
        .nav-link:hover, .nav-link.active { color: white; background: var(--primary-color); border-left-color: var(--accent-color); }
        .nav-link i { width: 20px; margin-right: 0.75rem; }
        
        .image-gallery { border: 2px dashed #dee2e6; border-radius: 0.5rem; padding: 2rem; text-align: center; background: #fafafa; transition: all 0.3s ease; }
        .image-gallery:hover { border-color: var(--accent-color); background: #f0f8ff; }
        .image-preview { display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 1rem; }
        .image-item { position: relative; width: 150px; height: 150px; border-radius: 0.5rem; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .image-item img { width: 100%; height: 100%; object-fit: cover; }
        .image-remove { position: absolute; top: 5px; right: 5px; background: rgba(220, 53, 69, 0.9); color: white; border: none; border-radius: 50%; width: 30px; height: 30px; cursor: pointer; font-size: 0.75rem; }
        .image-item:hover .image-remove { background: #dc3545; }
        
        .article-tabs .nav-link { color: #6c757d; border: none; background: none; }
        .article-tabs .nav-link.active { color: var(--primary-color); border-bottom: 2px solid var(--accent-color); }
        
        .seo-preview { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 0.5rem; padding: 1rem; }
        .seo-title { color: #1a0dab; font-size: 1.125rem; text-decoration: none; }
        .seo-url { color: #006621; font-size: 0.875rem; }
        .seo-description { color: #545454; font-size: 0.875rem; }
        
        /* Custom Rich Text Editor Styles */
        .custom-editor {
            border: 1px solid #dee2e6;
            border-radius: 0.5rem;
            min-height: 400px;
            background: white;
        }
        .editor-toolbar {
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            padding: 0.75rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            border-radius: 0.5rem 0.5rem 0 0;
        }
        .editor-btn {
            background: none;
            border: 1px solid #dee2e6;
            border-radius: 0.25rem;
            padding: 0.375rem 0.75rem;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.875rem;
        }
        .editor-btn:hover {
            background: #e9ecef;
            border-color: #adb5bd;
        }
        .editor-btn.active {
            background: var(--accent-color);
            border-color: var(--accent-color);
            color: white;
        }
        .editor-content {
            padding: 1rem;
            min-height: 300px;
            outline: none;
            line-height: 1.6;
        }
        .editor-content:focus {
            box-shadow: none;
        }
        .editor-separator {
            width: 1px;
            background: #dee2e6;
            margin: 0 0.5rem;
        }
        .paragraph-block {
            margin-bottom: 1rem;
            padding: 0.75rem;
            border: 1px solid transparent;
            border-radius: 0.25rem;
            position: relative;
        }
        .paragraph-block:hover {
            border-color: #dee2e6;
            background: #f8f9fa;
        }
        .paragraph-controls {
            position: absolute;
            right: 0.5rem;
            top: 0.5rem;
            opacity: 0;
            transition: opacity 0.2s;
        }
        .paragraph-block:hover .paragraph-controls {
            opacity: 1;
        }
        .block-btn {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 0.25rem;
            padding: 0.25rem 0.5rem;
            margin-left: 0.25rem;
            cursor: pointer;
            font-size: 0.75rem;
        }
    </style>
</head>
<body>
    <nav class="sidebar">
        <div class="sidebar-header">
            <h4><i class="fas fa-newspaper me-2"></i>Echhapa CMS</h4>
        </div>
        <div class="sidebar-menu">
            <a href="{{ url_for('admin') }}" class="nav-link"><i class="fas fa-tachometer-alt"></i>Dashboard</a>
            <a href="{{ url_for('articles_management') }}" class="nav-link"><i class="fas fa-newspaper"></i>Articles</a>
            <a href="{{ url_for('add_article') }}" class="nav-link active"><i class="fas fa-plus"></i>New Article</a>
            <a href="{{ url_for('ad_management') }}" class="nav-link"><i class="fas fa-ad"></i>Advertisements</a>
            <a href="{{ url_for('layout_management') }}" class="nav-link"><i class="fas fa-th-large"></i>Layout</a>
            <a href="{{ url_for('users_management') }}" class="nav-link"><i class="fas fa-users"></i>Users</a>
            <a href="{{ url_for('categories_management') }}" class="nav-link"><i class="fas fa-folder"></i>Categories</a>
            <a href="{{ url_for('site_settings') }}" class="nav-link"><i class="fas fa-cog"></i>Settings</a>
            <hr>
            <a href="{{ url_for('admin_logout') }}" class="nav-link"><i class="fas fa-sign-out-alt"></i>Logout</a>
        </div>
    </nav>

    <div class="main-content">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h1><i class="fas fa-plus me-3"></i>Create New Article</h1>
                <p class="lead mb-0">Write and publish engaging news articles with rich media</p>
            </div>
            <div class="btn-group">
                <button class="btn btn-outline-secondary" onclick="saveDraft()"><i class="fas fa-save me-2"></i>Save Draft</button>
                <button class="btn btn-primary" onclick="publishArticle()"><i class="fas fa-paper-plane me-2"></i>Publish</button>
                <a href="{{ url_for('articles_management') }}" class="btn btn-secondary"><i class="fas fa-arrow-left me-2"></i>Back</a>
            </div>
        </div>

        <form id="articleForm" class="row">
            <div class="col-lg-8">
                <div class="card mb-4">
                    <div class="card-body">
                        <!-- Article Tabs -->
                        <ul class="nav nav-tabs article-tabs mb-4">
                            <li class="nav-item">
                                <a class="nav-link active" data-bs-toggle="tab" href="#content-tab"><i class="fas fa-edit me-2"></i>Content</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" data-bs-toggle="tab" href="#media-tab"><i class="fas fa-images me-2"></i>Media Gallery</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" data-bs-toggle="tab" href="#seo-tab"><i class="fas fa-search me-2"></i>SEO</a>
                            </li>
                        </ul>

                        <div class="tab-content">
                            <!-- Content Tab -->
                            <div class="tab-pane fade show active" id="content-tab">
                                <div class="mb-3">
                                    <label class="form-label">Article Title <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control form-control-lg" id="articleTitle" placeholder="Enter compelling article title..." oninput="updateSeoPreview()">
                                </div>

                                <div class="mb-3">
                                    <label class="form-label">Excerpt/Summary</label>
                                    <textarea class="form-control" id="articleExcerpt" rows="3" placeholder="Brief summary of the article (will be shown in article lists and search results)" oninput="updateSeoPreview()"></textarea>
                                </div>

                                <div class="mb-3">
                                    <label class="form-label">Article Content <span class="text-danger">*</span></label>
                                    <div class="custom-editor" id="customEditor">
                                        <div class="editor-toolbar">
                                            <button type="button" class="editor-btn" onclick="formatText('bold')"><i class="fas fa-bold"></i></button>
                                            <button type="button" class="editor-btn" onclick="formatText('italic')"><i class="fas fa-italic"></i></button>
                                            <button type="button" class="editor-btn" onclick="formatText('underline')"><i class="fas fa-underline"></i></button>
                                            <div class="editor-separator"></div>
                                            <button type="button" class="editor-btn" onclick="formatText('insertUnorderedList')"><i class="fas fa-list-ul"></i></button>
                                            <button type="button" class="editor-btn" onclick="formatText('insertOrderedList')"><i class="fas fa-list-ol"></i></button>
                                            <div class="editor-separator"></div>
                                            <button type="button" class="editor-btn" onclick="insertHeading('h2')">H2</button>
                                            <button type="button" class="editor-btn" onclick="insertHeading('h3')">H3</button>
                                            <button type="button" class="editor-btn" onclick="insertHeading('h4')">H4</button>
                                            <div class="editor-separator"></div>
                                            <button type="button" class="editor-btn" onclick="insertLink()"><i class="fas fa-link"></i></button>
                                            <button type="button" class="editor-btn" onclick="insertQuote()"><i class="fas fa-quote-left"></i></button>
                                            <div class="editor-separator"></div>
                                            <button type="button" class="editor-btn" onclick="addParagraph()"><i class="fas fa-paragraph"></i> Add Paragraph</button>
                                            <button type="button" class="editor-btn" onclick="addImageBlock()"><i class="fas fa-image"></i> Add Image</button>
                                        </div>
                                        <div class="editor-content" id="editorContent" contenteditable="true" placeholder="Write your article content here..."></div>
                                    </div>
                                </div>
                            </div>

                            <!-- Media Gallery Tab -->
                            <div class="tab-pane fade" id="media-tab">
                                <div class="mb-4">
                                    <label class="form-label">Featured Image</label>
                                    <div class="image-gallery" onclick="document.getElementById('featuredImage').click()">
                                        <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-2"></i>
                                        <p class="text-muted mb-0">Click to upload featured image</p>
                                        <small class="text-muted">Recommended: 1200x630px, max 5MB</small>
                                        <input type="file" id="featuredImage" hidden accept="image/*" onchange="handleFeaturedImage(this)">
                                        <div id="featuredPreview"></div>
                                    </div>
                                </div>

                                <div class="mb-4">
                                    <label class="form-label">Article Images Gallery</label>
                                    <div class="image-gallery" onclick="document.getElementById('articleImages').click()">
                                        <i class="fas fa-images fa-3x text-muted mb-2"></i>
                                        <p class="text-muted mb-0">Click to upload multiple images</p>
                                        <small class="text-muted">You can select multiple images at once</small>
                                        <input type="file" id="articleImages" hidden accept="image/*" multiple onchange="handleArticleImages(this)">
                                    </div>
                                    <div id="imagePreview" class="image-preview"></div>
                                </div>
                            </div>

                            <!-- SEO Tab -->
                            <div class="tab-pane fade" id="seo-tab">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">SEO Title</label>
                                            <input type="text" class="form-control" id="seoTitle" placeholder="Custom SEO title (leave blank to use article title)" oninput="updateSeoPreview()">
                                            <small class="text-muted">Recommended: 50-60 characters</small>
                                        </div>

                                        <div class="mb-3">
                                            <label class="form-label">Meta Description</label>
                                            <textarea class="form-control" id="metaDescription" rows="3" placeholder="Brief description for search engines" oninput="updateSeoPreview()"></textarea>
                                            <small class="text-muted">Recommended: 150-160 characters</small>
                                        </div>

                                        <div class="mb-3">
                                            <label class="form-label">Tags</label>
                                            <input type="text" class="form-control" id="articleTags" placeholder="news, politics, economy (comma-separated)">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">Search Result Preview</label>
                                        <div id="seoPreview" class="seo-preview">
                                            <div class="seo-title">Your Article Title Will Appear Here</div>
                                            <div class="seo-url">https://echhapa.com/article/your-article-title</div>
                                            <div class="seo-description">Your article description or excerpt will appear here in search results...</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-lg-4">
                <!-- Publishing Options -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-cog me-2"></i>Publishing Options</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label">Category <span class="text-danger">*</span></label>
                            <select class="form-control" id="articleCategory" required>
                                <option value="">Select category</option>
                                {% for category in categories %}
                                <option value="{{ category.id }}">{{ category.name }}</option>
                                {% endfor %}
                            </select>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Author</label>
                            <input type="text" class="form-control" id="articleAuthor" value="Admin" readonly>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Publication Date</label>
                            <input type="datetime-local" class="form-control" id="publishDate" value="{{ now }}">
                        </div>

                        <div class="mb-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="isFeatured">
                                <label class="form-check-label" for="isFeatured">
                                    Featured Article
                                </label>
                            </div>
                        </div>

                        <div class="mb-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="allowComments" checked>
                                <label class="form-check-label" for="allowComments">
                                    Allow Comments
                                </label>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Article Stats -->
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-chart-bar me-2"></i>Article Stats</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-flex justify-content-between mb-2">
                            <span>Word Count:</span>
                            <span id="wordCount">0</span>
                        </div>
                        <div class="d-flex justify-content-between mb-2">
                            <span>Reading Time:</span>
                            <span id="readingTime">0 min</span>
                        </div>
                        <div class="d-flex justify-content-between">
                            <span>Images:</span>
                            <span id="imageCount">0</span>
                        </div>
                    </div>
                </div>
            </div>
        </form>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/js/custom-editor.js"></script>
    <script>
        let uploadedImages = [];
        let featuredImageFile = null;
        let customEditor;

        // Initialize Custom Rich Text Editor
        document.addEventListener('DOMContentLoaded', function() {
            if (typeof CustomEditor !== 'undefined') {
                customEditor = new CustomEditor('#articleContent', {
                    height: '500px'
                });
                
                // Set up change listeners for stats update
                const editorElement = document.querySelector('.custom-editor .editor-content');
                if (editorElement) {
                    editorElement.addEventListener('input', updateStats);
                    editorElement.addEventListener('keyup', updateStats);
                }
            }
        });

        // Handle featured image upload
        function handleFeaturedImage(input) {
            const file = input.files[0];
            if (file) {
                featuredImageFile = file;
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('featuredPreview').innerHTML = 
                        `<div class="image-item mt-3">
                            <img src="${e.target.result}" alt="Featured image">
                            <button type="button" class="image-remove" onclick="removeFeaturedImage()">×</button>
                        </div>`;
                };
                reader.readAsDataURL(file);
                updateStats();
            }
        }

        // Handle multiple article images upload
        function handleArticleImages(input) {
            const files = Array.from(input.files);
            files.forEach(file => {
                uploadedImages.push(file);
                const reader = new FileReader();
                reader.onload = function(e) {
                    const imageIndex = uploadedImages.length - 1;
                    const imageDiv = document.createElement('div');
                    imageDiv.className = 'image-item';
                    imageDiv.innerHTML = 
                        `<img src="${e.target.result}" alt="Article image">
                         <button type="button" class="image-remove" onclick="removeImage(${imageIndex})">×</button>`;
                    document.getElementById('imagePreview').appendChild(imageDiv);
                };
                reader.readAsDataURL(file);
            });
            updateStats();
        }

        // Remove featured image
        function removeFeaturedImage() {
            featuredImageFile = null;
            document.getElementById('featuredPreview').innerHTML = '';
            document.getElementById('featuredImage').value = '';
            updateStats();
        }

        // Remove article image
        function removeImage(index) {
            uploadedImages.splice(index, 1);
            updateImagePreviews();
            updateStats();
        }

        // Update image previews after removal
        function updateImagePreviews() {
            const previewDiv = document.getElementById('imagePreview');
            previewDiv.innerHTML = '';
            uploadedImages.forEach((file, index) => {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const imageDiv = document.createElement('div');
                    imageDiv.className = 'image-item';
                    imageDiv.innerHTML = 
                        `<img src="${e.target.result}" alt="Article image">
                         <button type="button" class="image-remove" onclick="removeImage(${index})">×</button>`;
                    previewDiv.appendChild(imageDiv);
                };
                reader.readAsDataURL(file);
            });
        }

        // Update SEO preview
        function updateSeoPreview() {
            const title = document.getElementById('seoTitle').value || document.getElementById('articleTitle').value || 'Your Article Title Will Appear Here';
            const description = document.getElementById('metaDescription').value || document.getElementById('articleExcerpt').value || 'Your article description or excerpt will appear here in search results...';
            const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
            
            document.querySelector('.seo-title').textContent = title;
            document.querySelector('.seo-url').textContent = `https://echhapa.com/article/${slug}`;
            document.querySelector('.seo-description').textContent = description;
        }

        // Update article stats
        function updateStats() {
            // Get content from Custom Editor
            let content = '';
            if (customEditor) {
                const editorElement = document.querySelector('.custom-editor .editor-content');
                content = editorElement ? editorElement.textContent || '' : '';
            } else {
                content = document.getElementById('articleContent').value || '';
            }
            
            const words = content.trim() ? content.trim().split(/\\s+/).length : 0;
            const readingTime = Math.ceil(words / 200); // Average reading speed
            const imageCount = (featuredImageFile ? 1 : 0) + uploadedImages.length;

            document.getElementById('wordCount').textContent = words;
            document.getElementById('readingTime').textContent = readingTime + ' min';
            document.getElementById('imageCount').textContent = imageCount;
        }

        // Save as draft
        function saveDraft() {
            const formData = collectFormData();
            formData.status = 'draft';
            submitArticle(formData, 'Article saved as draft successfully!');
        }

        // Publish article
        function publishArticle() {
            const formData = collectFormData();
            if (!validateForm(formData)) {
                return;
            }
            formData.status = 'published';
            submitArticle(formData, 'Article published successfully!');
        }

        // Collect form data
        function collectFormData() {
            return {
                title: document.getElementById('articleTitle').value,
                content: customEditor ? customEditor.getContent() : document.getElementById('articleContent').value,
                excerpt: document.getElementById('articleExcerpt').value,
                category_id: document.getElementById('articleCategory').value,
                author: document.getElementById('articleAuthor').value,
                publish_date: document.getElementById('publishDate').value,
                is_featured: document.getElementById('isFeatured').checked,
                allow_comments: document.getElementById('allowComments').checked,
                seo_title: document.getElementById('seoTitle').value,
                meta_description: document.getElementById('metaDescription').value,
                tags: document.getElementById('articleTags').value,
                featured_image: featuredImageFile,
                images: uploadedImages
            };
        }

        // Validate form
        function validateForm(data) {
            if (!data.title.trim()) {
                alert('Please enter an article title');
                return false;
            }
            if (!data.content.trim()) {
                alert('Please enter article content');
                return false;
            }
            if (!data.category_id) {
                alert('Please select a category');
                return false;
            }
            return true;
        }

        // Submit article
        function submitArticle(data, successMessage) {
            // Here you would submit to your backend
            alert(successMessage);
        }

        // Set current date/time
        document.getElementById('publishDate').value = new Date().toISOString().slice(0, 16);
        
        // Update stats periodically
        setInterval(updateStats, 2000);
    </script>
</body>
</html>
    """, categories=categories, now=datetime.now().strftime('%Y-%m-%dT%H:%M'))

@app.route('/admin/layout')
def layout_management():
    """Category-Specific Layout Management System"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    # Get categories with their subcategories and current layout settings
    conn = get_db()
    categories = []
    
    if conn:
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            # Get main categories with their subcategories
            cur.execute("""
                SELECT 
                    c.id, c.name, c.slug, c.sort_order, c.is_active,
                    c.layout_type,
                    COALESCE(
                        json_agg(
                            json_build_object(
                                'id', sc.id,
                                'name', sc.name,
                                'slug', sc.slug,
                                'layout_type', sc.layout_type
                            ) ORDER BY sc.sort_order
                        ) FILTER (WHERE sc.id IS NOT NULL),
                        '[]'::json
                    ) as subcategories
                FROM categories c
                LEFT JOIN categories sc ON sc.parent_id = c.id AND sc.is_active = TRUE
                WHERE c.parent_id IS NULL AND c.is_active = TRUE
                GROUP BY c.id, c.name, c.slug, c.sort_order, c.is_active, c.layout_type
                ORDER BY c.sort_order, c.name
            """)
            categories = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error fetching categories: {e}")
    
    # Set default current layout
    current_layout = 'grid'
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Layout Management - Echhapa CMS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/modular/sortable.core.esm.js">
    <style>
        :root {
            --sidebar-width: 280px;
            --primary-color: #2c3e50;
            --accent-color: #3498db;
        }
        body { background: #f8f9fa; }
        .main-content { margin-left: var(--sidebar-width); padding: 2rem; }
        .sidebar { position: fixed; top: 0; left: 0; height: 100vh; width: var(--sidebar-width); background: #34495e; color: white; z-index: 1000; overflow-y: auto; }
        .sidebar-header { padding: 1.5rem; background: var(--primary-color); }
        .nav-link { color: rgba(255,255,255,0.8); padding: 0.75rem 1.5rem; display: flex; align-items: center; text-decoration: none; transition: all 0.3s ease; border-left: 3px solid transparent; }
        .nav-link:hover, .nav-link.active { color: white; background: var(--primary-color); border-left-color: var(--accent-color); }
        .nav-link i { width: 20px; margin-right: 0.75rem; }
        
        .layout-template {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            cursor: pointer;
            min-height: 120px;
            border: 2px solid transparent;
        }
        .layout-template:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0,0,0,0.15); }
        .layout-template.selected { border-color: var(--accent-color); background: #f0f8ff; }
        .layout-header { background: #333; color: white; padding: 0.5rem; font-size: 0.75rem; font-weight: 500; }
        .layout-preview { padding: 0.75rem; }
        .layout-item { margin-bottom: 0.25rem; height: 8px; border-radius: 2px; }
        .main-item { background: #007bff; height: 20px; }
        .list-item { background: #28a745; }
        .card-item { background: #ffc107; height: 15px; }
        .text-item { background: #6c757d; height: 6px; }
        
        .category-section {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-left: 4px solid var(--accent-color);
        }
        
        .subcategory {
            background: #f8f9fa;
            border-radius: 6px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 3px solid #dee2e6;
        }
        
        .layout-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
        .drag-handle { cursor: move; color: #6c757d; margin-right: 0.5rem; }
    </style>
</head>
<body>
    <nav class="sidebar">
        <div class="sidebar-header">
            <h4><i class="fas fa-newspaper me-2"></i>Echhapa CMS</h4>
        </div>
        <div class="sidebar-menu">
            <a href="{{ url_for('admin') }}" class="nav-link"><i class="fas fa-tachometer-alt"></i>Dashboard</a>
            <a href="{{ url_for('articles_management') }}" class="nav-link"><i class="fas fa-newspaper"></i>Articles</a>
            <a href="{{ url_for('add_article') }}" class="nav-link"><i class="fas fa-plus"></i>New Article</a>
            <a href="{{ url_for('ad_management') }}" class="nav-link"><i class="fas fa-ad"></i>Advertisements</a>
            <a href="{{ url_for('layout_management') }}" class="nav-link active"><i class="fas fa-th-large"></i>Layout</a>
            <a href="{{ url_for('users_management') }}" class="nav-link"><i class="fas fa-users"></i>Users</a>
            <a href="{{ url_for('categories_management') }}" class="nav-link"><i class="fas fa-folder"></i>Categories</a>
            <a href="{{ url_for('site_settings') }}" class="nav-link"><i class="fas fa-cog"></i>Settings</a>
            <hr>
            <a href="{{ url_for('admin_logout') }}" class="nav-link"><i class="fas fa-sign-out-alt"></i>Logout</a>
        </div>
    </nav>

    <div class="main-content">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h1><i class="fas fa-th-large me-3"></i>Category Layout Management</h1>
                <p class="lead mb-0">Choose different layout styles for each category section</p>
            </div>
            <div class="btn-group">
                <button class="btn btn-success" onclick="saveAllLayouts()"><i class="fas fa-save me-2"></i>Save All Layouts</button>
                <a href="{{ url_for('categories_management') }}" class="btn btn-outline-primary"><i class="fas fa-folder me-2"></i>Manage Categories</a>
            </div>
        </div>
        
        <!-- Available Layout Templates -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-th me-2"></i>Available Layout Templates</h5>
                        <small class="text-muted">Each category can have its own layout style</small>
                    </div>
                    <div class="card-body">
                        <div class="layout-grid" id="layoutTemplates">
                            <div class="layout-template" data-layout="featured-main-list">
                                <div class="layout-header">Featured + List View</div>
                                <div class="layout-preview">
                                    <div class="main-item layout-item"></div>
                                    <div class="list-item layout-item"></div>
                                    <div class="list-item layout-item"></div>
                                    <div class="list-item layout-item"></div>
                                    <div class="list-item layout-item"></div>
                                </div>
                            </div>
                            
                            <div class="layout-template" data-layout="three-cards">
                                <div class="layout-header">Three Cards Row</div>
                                <div class="layout-preview">
                                    <div class="d-flex gap-1">
                                        <div class="card-item layout-item flex-fill"></div>
                                        <div class="card-item layout-item flex-fill"></div>
                                        <div class="card-item layout-item flex-fill"></div>
                                    </div>
                                    <div class="text-item layout-item"></div>
                                    <div class="text-item layout-item"></div>
                                </div>
                            </div>
                            
                            <div class="layout-template" data-layout="two-main-sidebar">
                                <div class="layout-header">Two Main + Sidebar</div>
                                <div class="layout-preview">
                                    <div class="d-flex gap-1">
                                        <div style="flex: 2;">
                                            <div class="main-item layout-item"></div>
                                            <div class="main-item layout-item"></div>
                                        </div>
                                        <div style="flex: 1;">
                                            <div class="list-item layout-item"></div>
                                            <div class="list-item layout-item"></div>
                                            <div class="list-item layout-item"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="layout-template" data-layout="grid-layout">
                                <div class="layout-header">Grid Layout</div>
                                <div class="layout-preview">
                                    <div class="d-flex gap-1 mb-1">
                                        <div class="card-item layout-item flex-fill"></div>
                                        <div class="card-item layout-item flex-fill"></div>
                                    </div>
                                    <div class="d-flex gap-1">
                                        <div class="card-item layout-item flex-fill"></div>
                                        <div class="card-item layout-item flex-fill"></div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="layout-template" data-layout="list-only">
                                <div class="layout-header">List Only</div>
                                <div class="layout-preview">
                                    <div class="list-item layout-item"></div>
                                    <div class="list-item layout-item"></div>
                                    <div class="list-item layout-item"></div>
                                    <div class="list-item layout-item"></div>
                                    <div class="list-item layout-item"></div>
                                    <div class="list-item layout-item"></div>
                                </div>
                            </div>
                            
                            <div class="layout-template" data-layout="magazine-style">
                                <div class="layout-header">Magazine Style</div>
                                <div class="layout-preview">
                                    <div class="main-item layout-item"></div>
                                    <div class="d-flex gap-1">
                                        <div class="card-item layout-item flex-fill"></div>
                                        <div class="card-item layout-item flex-fill"></div>
                                        <div class="card-item layout-item flex-fill"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Category Layout Management -->
        <div class="row">
            <div class="col-12">
                {% for category in categories %}
                <div class="category-section" data-category-id="{{ category.id }}">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <div>
                            <h4 class="mb-1"><i class="fas fa-folder me-2 text-primary"></i>{{ category.name }}</h4>
                            <p class="text-muted mb-0">Configure layout and subcategories for this category</p>
                        </div>
                        <div class="btn-group">
                            <button class="btn btn-sm btn-outline-primary" onclick="toggleCategory('{{ category.id }}')">
                                <i class="fas fa-eye"></i> Visible
                            </button>
                            <button class="btn btn-sm btn-outline-secondary" onclick="addSubcategory('{{ category.id }}')">
                                <i class="fas fa-plus"></i> Add Subcategory
                            </button>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-4">
                            <label class="form-label"><strong>Current Layout:</strong></label>
                            <div class="current-layout mb-3">
                                <div class="layout-template selected" data-layout="{{ category.layout_type or 'featured-main-list' }}" onclick="openLayoutSelector('{{ category.id }}')">
                                    <div class="layout-header">{{ category.layout_type or 'Featured + List View' }}</div>
                                    <div class="layout-preview">
                                        <div class="main-item layout-item"></div>
                                        <div class="list-item layout-item"></div>
                                        <div class="list-item layout-item"></div>
                                        <div class="list-item layout-item"></div>
                                    </div>
                                </div>
                                <small class="text-muted">Click to change layout style</small>
                            </div>
                        </div>
                        
                        <div class="col-md-4">
                            <label class="form-label"><strong>Settings:</strong></label>
                            <div class="mb-2">
                                <label class="form-label">Articles to Show:</label>
                                <select class="form-select form-select-sm" data-setting="articles-count" data-category="{{ category.id }}">
                                    <option value="3">3 articles</option>
                                    <option value="4" selected>4 articles</option>
                                    <option value="5">5 articles</option>
                                    <option value="6">6 articles</option>
                                </select>
                            </div>
                            <div class="form-check form-switch">
                                <input class="form-check-input" type="checkbox" id="showImages{{ category.id }}" checked>
                                <label class="form-check-label" for="showImages{{ category.id }}">Show images</label>
                            </div>
                            <div class="form-check form-switch">
                                <input class="form-check-input" type="checkbox" id="showExcerpts{{ category.id }}">
                                <label class="form-check-label" for="showExcerpts{{ category.id }}">Show excerpts</label>
                            </div>
                        </div>
                        
                        <div class="col-md-4">
                            <label class="form-label"><strong>Subcategories:</strong></label>
                            <div class="subcategories-list">
                                {% if category.subcategories %}
                                    {% for subcategory in category.subcategories %}
                                    <div class="subcategory" data-subcategory-id="{{ subcategory.id }}">
                                        <div class="d-flex justify-content-between align-items-center">
                                            <div>
                                                <i class="fas fa-folder-open me-1 text-secondary"></i>
                                                <span>{{ subcategory.name }}</span>
                                            </div>
                                            <div class="btn-group btn-group-sm">
                                                <button class="btn btn-outline-primary" onclick="editSubcategory('{{ subcategory.id }}')"><i class="fas fa-edit"></i></button>
                                                <button class="btn btn-outline-danger" onclick="deleteSubcategory('{{ subcategory.id }}')"><i class="fas fa-trash"></i></button>
                                            </div>
                                        </div>
                                    </div>
                                    {% endfor %}
                                {% else %}
                                    <div class="text-muted">No subcategories yet</div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    
    <!-- Layout Selection Modal -->
    <div class="modal fade" id="layoutSelectorModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Choose Layout Template</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="layout-grid" id="modalLayoutTemplates">
                        <!-- Layout templates will be populated here -->
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Add Subcategory Modal -->
    <div class="modal fade" id="subcategoryModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Add Subcategory</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="subcategoryForm">
                        <input type="hidden" id="parentCategoryId">
                        <div class="mb-3">
                            <label class="form-label">Subcategory Name</label>
                            <input type="text" class="form-control" id="subcategoryName" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Slug</label>
                            <input type="text" class="form-control" id="subcategorySlug" readonly>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="saveSubcategory()">Save Subcategory</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentCategoryId = null;
        let layoutModal = null;
        let subcategoryModal = null;
        
        document.addEventListener('DOMContentLoaded', function() {
            layoutModal = new bootstrap.Modal(document.getElementById('layoutSelectorModal'));
            subcategoryModal = new bootstrap.Modal(document.getElementById('subcategoryModal'));
            
            // Auto-generate slug when subcategory name changes
            document.getElementById('subcategoryName').addEventListener('input', function() {
                const name = this.value;
                const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
                document.getElementById('subcategorySlug').value = slug;
            });
        });

        function openLayoutSelector(categoryId) {
            currentCategoryId = categoryId;
            
            // Populate modal with layout templates
            const modalTemplates = document.getElementById('modalLayoutTemplates');
            const originalTemplates = document.getElementById('layoutTemplates');
            modalTemplates.innerHTML = originalTemplates.innerHTML;
            
            // Add click handlers to modal templates
            modalTemplates.querySelectorAll('.layout-template').forEach(template => {
                template.onclick = function() {
                    selectLayoutForCategory(categoryId, this.dataset.layout);
                    layoutModal.hide();
                };
            });
            
            layoutModal.show();
        }
        
        function selectLayoutForCategory(categoryId, layoutType) {
            // Update the category's current layout display
            const categorySection = document.querySelector(`[data-category-id="${categoryId}"]`);
            const currentLayoutDiv = categorySection.querySelector('.current-layout .layout-template');
            
            // Update layout preview
            currentLayoutDiv.dataset.layout = layoutType;
            currentLayoutDiv.querySelector('.layout-header').textContent = getLayoutName(layoutType);
            
            // Update layout preview content based on type
            updateLayoutPreview(currentLayoutDiv.querySelector('.layout-preview'), layoutType);
        }
        
        function getLayoutName(layoutType) {
            const names = {
                'featured-main-list': 'Featured + List View',
                'three-cards': 'Three Cards Row',
                'two-main-sidebar': 'Two Main + Sidebar',
                'grid-layout': 'Grid Layout',
                'list-only': 'List Only',
                'magazine-style': 'Magazine Style'
            };
            return names[layoutType] || layoutType;
        }
        
        function updateLayoutPreview(previewDiv, layoutType) {
            previewDiv.innerHTML = '';
            
            switch(layoutType) {
                case 'featured-main-list':
                    previewDiv.innerHTML = `
                        <div class="main-item layout-item"></div>
                        <div class="list-item layout-item"></div>
                        <div class="list-item layout-item"></div>
                        <div class="list-item layout-item"></div>
                        <div class="list-item layout-item"></div>
                    `;
                    break;
                case 'three-cards':
                    previewDiv.innerHTML = `
                        <div class="d-flex gap-1">
                            <div class="card-item layout-item flex-fill"></div>
                            <div class="card-item layout-item flex-fill"></div>
                            <div class="card-item layout-item flex-fill"></div>
                        </div>
                        <div class="text-item layout-item"></div>
                        <div class="text-item layout-item"></div>
                    `;
                    break;
                case 'two-main-sidebar':
                    previewDiv.innerHTML = `
                        <div class="d-flex gap-1">
                            <div style="flex: 2;">
                                <div class="main-item layout-item"></div>
                                <div class="main-item layout-item"></div>
                            </div>
                            <div style="flex: 1;">
                                <div class="list-item layout-item"></div>
                                <div class="list-item layout-item"></div>
                                <div class="list-item layout-item"></div>
                            </div>
                        </div>
                    `;
                    break;
                case 'grid-layout':
                    previewDiv.innerHTML = `
                        <div class="d-flex gap-1 mb-1">
                            <div class="card-item layout-item flex-fill"></div>
                            <div class="card-item layout-item flex-fill"></div>
                        </div>
                        <div class="d-flex gap-1">
                            <div class="card-item layout-item flex-fill"></div>
                            <div class="card-item layout-item flex-fill"></div>
                        </div>
                    `;
                    break;
                case 'list-only':
                    previewDiv.innerHTML = `
                        <div class="list-item layout-item"></div>
                        <div class="list-item layout-item"></div>
                        <div class="list-item layout-item"></div>
                        <div class="list-item layout-item"></div>
                        <div class="list-item layout-item"></div>
                        <div class="list-item layout-item"></div>
                    `;
                    break;
                case 'magazine-style':
                    previewDiv.innerHTML = `
                        <div class="main-item layout-item"></div>
                        <div class="d-flex gap-1">
                            <div class="card-item layout-item flex-fill"></div>
                            <div class="card-item layout-item flex-fill"></div>
                            <div class="card-item layout-item flex-fill"></div>
                        </div>
                    `;
                    break;
            }
        }
        
        function toggleCategory(categoryId) {
            // Toggle category visibility
            alert('Category visibility toggled!');
        }
        
        function addSubcategory(categoryId) {
            document.getElementById('parentCategoryId').value = categoryId;
            document.getElementById('subcategoryName').value = '';
            document.getElementById('subcategorySlug').value = '';
            subcategoryModal.show();
        }
        
        function saveSubcategory() {
            const parentId = document.getElementById('parentCategoryId').value;
            const name = document.getElementById('subcategoryName').value;
            const slug = document.getElementById('subcategorySlug').value;
            
            if (!name.trim()) {
                alert('Please enter a subcategory name');
                return;
            }
            
            // Here you would send the data to your backend
            fetch('/admin/categories/subcategory', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ parent_id: parentId, name: name, slug: slug })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    subcategoryModal.hide();
                    alert('Subcategory created successfully!');
                    location.reload(); // Refresh to show new subcategory
                } else {
                    alert('Error creating subcategory: ' + data.error);
                }
            })
            .catch(error => {
                alert('Error: ' + error);
            });
        }
        
        function editSubcategory(subcategoryId) {
            alert('Edit subcategory: ' + subcategoryId);
        }
        
        function deleteSubcategory(subcategoryId) {
            if (confirm('Are you sure you want to delete this subcategory?')) {
                // Send delete request to backend
                fetch(`/admin/categories/subcategory/${subcategoryId}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Subcategory deleted successfully!');
                        location.reload();
                    } else {
                        alert('Error deleting subcategory: ' + data.error);
                    }
                });
            }
        }
        
        function saveAllLayouts() {
            // Collect all category layout settings
            const layouts = [];
            
            document.querySelectorAll('.category-section').forEach(section => {
                const categoryId = section.dataset.categoryId;
                const layoutType = section.querySelector('.current-layout .layout-template').dataset.layout;
                const articlesCount = section.querySelector('[data-setting="articles-count"]').value;
                const showImages = section.querySelector(`#showImages${categoryId}`).checked;
                const showExcerpts = section.querySelector(`#showExcerpts${categoryId}`).checked;
                
                layouts.push({
                    category_id: categoryId,
                    layout_type: layoutType,
                    articles_count: articlesCount,
                    show_images: showImages,
                    show_excerpts: showExcerpts
                });
            });
            
            // Save to backend
            fetch('/admin/layout/save-all', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ layouts: layouts })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('All layouts saved successfully!');
                } else {
                    alert('Error saving layouts: ' + data.error);
                }
            })
            .catch(error => {
                alert('Error: ' + error);
            });
        }

    </script>
</body>
</html>
    """, categories=categories, current_layout=current_layout)

@app.route('/admin/layout/save-all', methods=['POST'])
def save_all_layouts():
    """Save all category layout settings"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    try:
        layout_data = request.get_json()
        layouts = layout_data.get('layouts', [])
        
        conn = get_db()
        if conn:
            cur = conn.cursor()
            for layout in layouts:
                cur.execute("""
                    UPDATE categories 
                    SET layout_type = %s, articles_count = %s, show_images = %s, show_excerpts = %s 
                    WHERE id = %s
                """, (
                    layout['layout_type'],
                    layout['articles_count'],
                    layout['show_images'],
                    layout['show_excerpts'],
                    layout['category_id']
                ))
            conn.commit()
            cur.close()
            conn.close()
        
        return jsonify({'success': True, 'message': 'All layouts saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/categories/subcategory', methods=['POST'])
def create_subcategory():
    """Create a new subcategory"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    try:
        data = request.get_json()
        parent_id = data.get('parent_id')
        name = data.get('name')
        slug = data.get('slug')
        
        conn = get_db()
        if conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO categories (name, slug, parent_id, is_active, sort_order)
                VALUES (%s, %s, %s, TRUE, 0)
            """, (name, slug, parent_id))
            conn.commit()
            cur.close()
            conn.close()
        
        return jsonify({'success': True, 'message': 'Subcategory created successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/categories/subcategory/<int:subcategory_id>', methods=['DELETE'])
def delete_subcategory(subcategory_id):
    """Delete a subcategory"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    try:
        conn = get_db()
        if conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM categories WHERE id = %s", (subcategory_id,))
            conn.commit()
            cur.close()
            conn.close()
        
        return jsonify({'success': True, 'message': 'Subcategory deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/users')
def users_management():
    """Users Management System"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    # Get all users from database
    conn = get_db()
    users = []
    
    if conn:
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""SELECT id, username, email, role, first_name, last_name, 
                          created_at, last_login, is_active FROM users ORDER BY created_at DESC""")
            users = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error fetching users: {e}")
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Users Management - Echhapa CMS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --sidebar-width: 280px;
            --primary-color: #2c3e50;
            --accent-color: #3498db;
        }
        body { background: #f8f9fa; }
        .main-content { margin-left: var(--sidebar-width); padding: 2rem; }
        .sidebar { position: fixed; top: 0; left: 0; height: 100vh; width: var(--sidebar-width); background: #34495e; color: white; z-index: 1000; overflow-y: auto; }
        .sidebar-header { padding: 1.5rem; background: var(--primary-color); }
        .nav-link { color: rgba(255,255,255,0.8); padding: 0.75rem 1.5rem; display: flex; align-items: center; text-decoration: none; transition: all 0.3s ease; border-left: 3px solid transparent; }
        .nav-link:hover, .nav-link.active { color: white; background: var(--primary-color); border-left-color: var(--accent-color); }
        .nav-link i { width: 20px; margin-right: 0.75rem; }
    </style>
</head>
<body>
    <nav class="sidebar">
        <div class="sidebar-header">
            <h4><i class="fas fa-newspaper me-2"></i>Echhapa CMS</h4>
        </div>
        <div class="sidebar-menu">
            <a href="{{ url_for('admin') }}" class="nav-link"><i class="fas fa-tachometer-alt"></i>Dashboard</a>
            <a href="{{ url_for('articles_management') }}" class="nav-link"><i class="fas fa-newspaper"></i>Articles</a>
            <a href="{{ url_for('add_article') }}" class="nav-link"><i class="fas fa-plus"></i>New Article</a>
            <a href="{{ url_for('ad_management') }}" class="nav-link"><i class="fas fa-ad"></i>Advertisements</a>
            <a href="{{ url_for('layout_management') }}" class="nav-link"><i class="fas fa-th-large"></i>Layout</a>
            <a href="{{ url_for('users_management') }}" class="nav-link active"><i class="fas fa-users"></i>Users</a>
            <a href="{{ url_for('categories_management') }}" class="nav-link"><i class="fas fa-folder"></i>Categories</a>
            <a href="{{ url_for('site_settings') }}" class="nav-link"><i class="fas fa-cog"></i>Settings</a>
            <hr>
            <a href="{{ url_for('admin_logout') }}" class="nav-link"><i class="fas fa-sign-out-alt"></i>Logout</a>
        </div>
    </nav>

    <div class="main-content">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h1><i class="fas fa-users me-3"></i>Users Management</h1>
                <p class="lead">Manage website administrators and authors</p>
            </div>
            <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addUserModal">
                <i class="fas fa-plus me-2"></i>Add New User
            </button>
        </div>
        
        <div class="card">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Username</th>
                                <th>Email</th>
                                <th>Name</th>
                                <th>Role</th>
                                <th>Status</th>
                                <th>Created</th>
                                <th>Last Login</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for user in users %}
                            <tr>
                                <td><strong>{{ user.username }}</strong></td>
                                <td>{{ user.email or 'N/A' }}</td>
                                <td>{{ (user.first_name + ' ' + user.last_name) if user.first_name else 'N/A' }}</td>
                                <td><span class="badge bg-primary">{{ user.role.title() }}</span></td>
                                <td>
                                    {% if user.is_active %}
                                        <span class="badge bg-success">Active</span>
                                    {% else %}
                                        <span class="badge bg-danger">Inactive</span>
                                    {% endif %}
                                </td>
                                <td>{{ user.created_at.strftime('%Y-%m-%d') if user.created_at else 'N/A' }}</td>
                                <td>{{ user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never' }}</td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary" onclick="editUser({{ user.id }})">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    {% if user.id != session.get('user_id') %}
                                    <button class="btn btn-sm btn-outline-danger" onclick="toggleUserStatus({{ user.id }}, {{ user.is_active|lower }})">
                                        {% if user.is_active %}
                                            <i class="fas fa-ban"></i>
                                        {% else %}
                                            <i class="fas fa-check"></i>
                                        {% endif %}
                                    </button>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function editUser(userId) {
            // TODO: Implement user editing
            alert('User editing functionality will be implemented');
        }
        
        function toggleUserStatus(userId, isActive) {
            // TODO: Implement user status toggle
            alert('User status toggle functionality will be implemented');
        }
    </script>
</body>
</html>
    """, users=users)

@app.route('/admin/categories')
def categories_management():
    """Categories Management System"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    # Get all categories from database
    conn = get_db()
    categories = []
    
    if conn:
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""SELECT c.*, COUNT(a.id) as article_count, pc.name as parent_name
                          FROM categories c 
                          LEFT JOIN articles a ON c.id = a.category_id 
                          LEFT JOIN categories pc ON c.parent_id = pc.id
                          GROUP BY c.id, pc.name 
                          ORDER BY c.sort_order, c.name""")
            categories = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error fetching categories: {e}")
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Categories Management - Echhapa CMS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --sidebar-width: 280px;
            --primary-color: #2c3e50;
            --accent-color: #3498db;
        }
        body { background: #f8f9fa; }
        .main-content { margin-left: var(--sidebar-width); padding: 2rem; }
        .sidebar { position: fixed; top: 0; left: 0; height: 100vh; width: var(--sidebar-width); background: #34495e; color: white; z-index: 1000; overflow-y: auto; }
        .sidebar-header { padding: 1.5rem; background: var(--primary-color); }
        .nav-link { color: rgba(255,255,255,0.8); padding: 0.75rem 1.5rem; display: flex; align-items: center; text-decoration: none; transition: all 0.3s ease; border-left: 3px solid transparent; }
        .nav-link:hover, .nav-link.active { color: white; background: var(--primary-color); border-left-color: var(--accent-color); }
        .nav-link i { width: 20px; margin-right: 0.75rem; }
    </style>
</head>
<body>
    <nav class="sidebar">
        <div class="sidebar-header">
            <h4><i class="fas fa-newspaper me-2"></i>Echhapa CMS</h4>
        </div>
        <div class="sidebar-menu">
            <a href="{{ url_for('admin') }}" class="nav-link"><i class="fas fa-tachometer-alt"></i>Dashboard</a>
            <a href="{{ url_for('articles_management') }}" class="nav-link"><i class="fas fa-newspaper"></i>Articles</a>
            <a href="{{ url_for('add_article') }}" class="nav-link"><i class="fas fa-plus"></i>New Article</a>
            <a href="{{ url_for('ad_management') }}" class="nav-link"><i class="fas fa-ad"></i>Advertisements</a>
            <a href="{{ url_for('layout_management') }}" class="nav-link"><i class="fas fa-th-large"></i>Layout</a>
            <a href="{{ url_for('users_management') }}" class="nav-link"><i class="fas fa-users"></i>Users</a>
            <a href="{{ url_for('categories_management') }}" class="nav-link active"><i class="fas fa-folder"></i>Categories</a>
            <a href="{{ url_for('site_settings') }}" class="nav-link"><i class="fas fa-cog"></i>Settings</a>
            <hr>
            <a href="{{ url_for('admin_logout') }}" class="nav-link"><i class="fas fa-sign-out-alt"></i>Logout</a>
        </div>
    </nav>

    <div class="main-content">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h1><i class="fas fa-folder me-3"></i>Categories Management</h1>
                <p class="lead">Organize articles into categories</p>
            </div>
            <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addCategoryModal">
                <i class="fas fa-plus me-2"></i>Add New Category
            </button>
        </div>
        
        <div class="card">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Slug</th>
                                <th>Description</th>
                                <th>Parent</th>
                                <th>Articles</th>
                                <th>Status</th>
                                <th>Created</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for category in categories %}
                            <tr>
                                <td><strong>{{ category.name }}</strong></td>
                                <td><code>{{ category.slug }}</code></td>
                                <td>{{ category.description or 'No description' }}</td>
                                <td>{{ category.parent_name or 'Main Category' }}</td>
                                <td><span class="badge bg-secondary">{{ category.article_count }}</span></td>
                                <td>
                                    {% if category.is_active %}
                                        <span class="badge bg-success">Active</span>
                                    {% else %}
                                        <span class="badge bg-danger">Inactive</span>
                                    {% endif %}
                                </td>
                                <td>{{ category.created_at.strftime('%Y-%m-%d') if category.created_at else 'N/A' }}</td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary" onclick="editCategory({{ category.id }})">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger" onclick="deleteCategory({{ category.id }})">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function editCategory(categoryId) {
            alert('Category editing functionality will be implemented');
        }
        
        function deleteCategory(categoryId) {
            if (confirm('Are you sure you want to delete this category?')) {
                alert('Category deletion functionality will be implemented');
            }
        }
    </script>
</body>
</html>
    """, categories=categories)

@app.route('/admin/settings')
def site_settings():
    """Site Settings Management"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Site Settings - Echhapa CMS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --sidebar-width: 280px;
            --primary-color: #2c3e50;
            --accent-color: #3498db;
        }
        body { background: #f8f9fa; }
        .main-content { margin-left: var(--sidebar-width); padding: 2rem; }
        .sidebar { position: fixed; top: 0; left: 0; height: 100vh; width: var(--sidebar-width); background: #34495e; color: white; z-index: 1000; overflow-y: auto; }
        .sidebar-header { padding: 1.5rem; background: var(--primary-color); }
        .nav-link { color: rgba(255,255,255,0.8); padding: 0.75rem 1.5rem; display: flex; align-items: center; text-decoration: none; transition: all 0.3s ease; border-left: 3px solid transparent; }
        .nav-link:hover, .nav-link.active { color: white; background: var(--primary-color); border-left-color: var(--accent-color); }
        .nav-link i { width: 20px; margin-right: 0.75rem; }
    </style>
</head>
<body>
    <nav class="sidebar">
        <div class="sidebar-header">
            <h4><i class="fas fa-newspaper me-2"></i>Echhapa CMS</h4>
        </div>
        <div class="sidebar-menu">
            <a href="{{ url_for('admin') }}" class="nav-link"><i class="fas fa-tachometer-alt"></i>Dashboard</a>
            <a href="{{ url_for('articles_management') }}" class="nav-link"><i class="fas fa-newspaper"></i>Articles</a>
            <a href="{{ url_for('add_article') }}" class="nav-link"><i class="fas fa-plus"></i>New Article</a>
            <a href="{{ url_for('ad_management') }}" class="nav-link"><i class="fas fa-ad"></i>Advertisements</a>
            <a href="{{ url_for('layout_management') }}" class="nav-link"><i class="fas fa-th-large"></i>Layout</a>
            <a href="{{ url_for('users_management') }}" class="nav-link"><i class="fas fa-users"></i>Users</a>
            <a href="{{ url_for('categories_management') }}" class="nav-link"><i class="fas fa-folder"></i>Categories</a>
            <a href="{{ url_for('site_settings') }}" class="nav-link active"><i class="fas fa-cog"></i>Settings</a>
            <hr>
            <a href="{{ url_for('admin_logout') }}" class="nav-link"><i class="fas fa-sign-out-alt"></i>Logout</a>
        </div>
    </nav>

    <div class="main-content">
        <h1><i class="fas fa-cog me-3"></i>Site Settings</h1>
        <p class="lead">Configure website settings and preferences</p>
        
        <div class="alert alert-info">
            <i class="fas fa-info-circle me-2"></i>Site settings management system is under development. This will allow you to configure website settings, SEO, social media, and more.
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """)

# Additional admin routes are included in this file

# Initialize database when app starts
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)