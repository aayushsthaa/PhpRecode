#!/usr/bin/env python3
"""
Echhapa News Portal - Flask Version with MySQL
Professional CMS with full functionality
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify
import os
import pymysql
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-change-in-production")

# Database connection
def get_db():
    """Get database connection"""
    try:
        conn = pymysql.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            port=int(os.environ.get('MYSQL_PORT', '3306')),
            database=os.environ.get('MYSQL_DATABASE', 'echhapa_news'),
            user=os.environ.get('MYSQL_USER', 'root'),
            password=os.environ.get('MYSQL_PASSWORD', ''),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        # For local development, create a simple in-memory fallback
        return None

# Initialize database
def init_db():
    """Initialize database with basic structure"""
    conn = get_db()
    if not conn:
        print("Database not available - using fallback mode")
        return False
    
    try:
        cur = conn.cursor()
        
        # Create database if it doesn't exist
        cur.execute("CREATE DATABASE IF NOT EXISTS echhapa_news")
        cur.execute("USE echhapa_news")
        
        # Drop and recreate articles table
        cur.execute("DROP TABLE IF EXISTS articles")
        cur.execute("""
            CREATE TABLE articles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                author VARCHAR(100) DEFAULT 'Admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'published',
                slug VARCHAR(255) UNIQUE
            )
        """)
        
        # Drop and recreate users table
        cur.execute("DROP TABLE IF EXISTS users")
        cur.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create categories table
        cur.execute("DROP TABLE IF EXISTS categories")
        cur.execute("""
            CREATE TABLE categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                slug VARCHAR(100) UNIQUE NOT NULL,
                description TEXT
            )
        """)
        
        # Insert default admin user (admin/admin123)
        cur.execute("SELECT COUNT(*) as count FROM users WHERE username = 'admin'")
        result = cur.fetchone()
        if result['count'] == 0:
            password_hash = generate_password_hash('admin123')
            cur.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                       ('admin', password_hash, 'admin'))
        
        # Insert default categories
        categories = [
            ('World News', 'world-news', 'International news and global events'),
            ('Technology', 'technology', 'Latest tech trends and innovations'),
            ('Business', 'business', 'Business news and market updates'),
            ('Sports', 'sports', 'Sports news and championships'),
            ('Entertainment', 'entertainment', 'Entertainment and celebrity news')
        ]
        
        for name, slug, desc in categories:
            cur.execute("INSERT IGNORE INTO categories (name, slug, description) VALUES (%s, %s, %s)",
                       (name, slug, desc))
        
        # Insert sample articles if none exist
        cur.execute("SELECT COUNT(*) as count FROM articles")
        result = cur.fetchone()
        if result['count'] == 0:
            sample_articles = [
                ("Breaking: Major Economic Development Announced", "In a significant move that could reshape the global economy, world leaders announced a comprehensive economic development package today. This landmark agreement promises to boost international trade, create millions of jobs, and foster sustainable growth across multiple sectors. The initiative includes substantial investments in renewable energy, digital infrastructure, and education systems worldwide.", "breaking-economic-development"),
                ("Technology Advances Revolutionize 2025", "The technology sector continues to evolve at an unprecedented pace in 2025. From artificial intelligence breakthroughs to quantum computing milestones, this year has marked several historic achievements. Major tech companies have unveiled revolutionary products that promise to transform how we work, communicate, and interact with the digital world.", "technology-advances-2025"),
                ("Global Climate Summit Delivers Historic Results", "The latest Global Climate Summit concluded with groundbreaking agreements and commitments from over 150 nations. International cooperation on climate change has reached new heights, with countries pledging substantial resources towards renewable energy transition and carbon reduction initiatives. This summit marks a turning point in global environmental policy.", "global-climate-summit-results"),
                ("Sports Championship Season Brings Excitement", "The current championship season has delivered some of the most thrilling moments in sports history. Athletes from around the world have showcased exceptional talent and determination, breaking records and inspiring millions of fans. From football to tennis, this season has been marked by unprecedented competition and sportsmanship.", "sports-championship-update"),
                ("Cultural Festival Celebrates Global Diversity", "Communities worldwide are coming together to celebrate cultural diversity through vibrant festivals and events. These gatherings showcase the rich tapestry of global traditions, arts, and customs, promoting understanding and unity among different cultures. Local cultural events continue to strengthen community bonds and preserve heritage.", "cultural-festival-highlights")
            ]
            
            for title, content, slug in sample_articles:
                cur.execute("INSERT INTO articles (title, content, slug) VALUES (%s, %s, %s)", 
                           (title, content, slug))
        
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
        'title': "Breaking: Major Economic Development Announced",
        'content': "In a significant move that could reshape the global economy, world leaders announced a comprehensive economic development package today. This landmark agreement promises to boost international trade, create millions of jobs, and foster sustainable growth across multiple sectors.",
        'author': 'Admin',
        'created_at': datetime.now(),
        'status': 'published',
        'slug': 'breaking-economic-development'
    },
    {
        'id': 2,
        'title': "Technology Advances Revolutionize 2025",
        'content': "The technology sector continues to evolve at an unprecedented pace in 2025. From artificial intelligence breakthroughs to quantum computing milestones, this year has marked several historic achievements.",
        'author': 'Admin',
        'created_at': datetime.now(),
        'status': 'published',
        'slug': 'technology-advances-2025'
    }
]

def get_articles(limit=10):
    """Get articles from database or fallback"""
    conn = get_db()
    if not conn:
        return fallback_articles[:limit]
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM articles WHERE status = 'published' ORDER BY created_at DESC LIMIT %s", (limit,))
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
        cur = conn.cursor()
        cur.execute("SELECT * FROM articles WHERE slug = %s AND status = 'published'", (slug,))
        article = cur.fetchone()
        cur.close()
        conn.close()
        return article
    except Exception as e:
        print(f"Error fetching article: {e}")
        return None

# Homepage
@app.route('/')
def index():
    """Homepage with news articles"""
    articles = get_articles(10)
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en" data-bs-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Echhapa News - Your Trusted Source</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .navbar-brand { font-family: 'Times New Roman', serif; font-weight: 900; color: #d42828 !important; }
        .breaking-news { background: linear-gradient(45deg, #dc3545, #e74c3c); }
        .featured-article h3 { font-size: 2.2rem; font-weight: 800; }
        .card { transition: transform 0.2s ease-in-out; }
        .card:hover { transform: translateY(-2px); box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15); }
        .border-left-primary { border-left: 4px solid #dc3545; }
        .article-link { text-decoration: none; color: inherit; }
        .article-link:hover { color: #dc3545; }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom shadow-sm">
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
    
    <!-- Breaking News -->
    <div class="breaking-news text-white py-2">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-auto">
                    <strong><i class="fas fa-bolt me-2"></i>BREAKING NEWS</strong>
                </div>
                <div class="col">
                    <marquee>Welcome to Echhapa News - Your comprehensive news portal with MySQL database!</marquee>
                </div>
            </div>
        </div>
    </div>

    <div class="container-fluid px-0 py-4">
        <div class="row">
            <!-- Main Content -->
            <div class="col-lg-9">
                <div class="container">
                    <!-- Featured Article -->
                    {% if articles %}
                    <section class="py-4 border-bottom">
                        <h2 class="section-title border-start border-danger border-4 ps-3 mb-4">Top Stories</h2>
                        <div class="row">
                            <div class="col-lg-8">
                                <div class="featured-article">
                                    <h3>
                                        <a href="/article/{{ articles[0].slug or articles[0].id }}" class="article-link">
                                            {{ articles[0].title }}
                                        </a>
                                    </h3>
                                    <p class="text-muted mb-2">
                                        <small>By {{ articles[0].author }} • {{ articles[0].created_at.strftime('%B %d, %Y') if articles[0].created_at.strftime else articles[0].created_at }}</small>
                                    </p>
                                    <p class="lead">{{ articles[0].content[:200] }}...</p>
                                    <a href="/article/{{ articles[0].slug or articles[0].id }}" class="btn btn-outline-danger">Read More</a>
                                </div>
                            </div>
                            <div class="col-lg-4">
                                {% for article in articles[1:4] %}
                                <div class="side-article mb-3 pb-3 border-bottom">
                                    <h6>
                                        <a href="/article/{{ article.slug or article.id }}" class="article-link">
                                            {{ article.title }}
                                        </a>
                                    </h6>
                                    <p class="text-muted mb-0">
                                        <small>{{ article.created_at.strftime('%B %d, %Y') if article.created_at.strftime else article.created_at }}</small>
                                    </p>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                    </section>
                    {% endif %}

                    <!-- More Articles -->
                    <section class="py-4">
                        <h2 class="section-title border-start border-danger border-4 ps-3 mb-4">Latest News</h2>
                        <div class="row">
                            {% for article in articles[4:] %}
                            <div class="col-lg-4 col-md-6 mb-4">
                                <div class="card h-100 border-0 shadow-sm">
                                    <div class="card-body">
                                        <h5 class="card-title">
                                            <a href="/article/{{ article.slug or article.id }}" class="article-link">
                                                {{ article.title }}
                                            </a>
                                        </h5>
                                        <p class="card-text text-muted">{{ article.content[:100] }}...</p>
                                        <div class="d-flex justify-content-between align-items-center">
                                            <small class="text-muted">By {{ article.author }}</small>
                                            <small class="text-muted">{{ article.created_at.strftime('%b %d') if article.created_at.strftime else article.created_at }}</small>
                                        </div>
                                        <div class="mt-2">
                                            <a href="/article/{{ article.slug or article.id }}" class="btn btn-sm btn-outline-primary">Read More</a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </section>
                </div>
            </div>
            
            <!-- Sidebar -->
            <div class="col-lg-3">
                <div class="sidebar p-4 bg-light border-left-primary">
                    <div class="widget mb-4">
                        <h5 class="widget-title border-bottom pb-2 mb-3">Quick Links</h5>
                        <ul class="list-unstyled">
                            <li class="mb-2"><a href="/" class="text-decoration-none"><i class="fas fa-home me-2"></i>Home</a></li>
                            <li class="mb-2"><a href="/admin" class="text-decoration-none"><i class="fas fa-cog me-2"></i>Admin Dashboard</a></li>
                            <li class="mb-2"><a href="#" class="text-decoration-none"><i class="fas fa-info me-2"></i>About Us</a></li>
                            <li class="mb-2"><a href="#" class="text-decoration-none"><i class="fas fa-envelope me-2"></i>Contact</a></li>
                        </ul>
                    </div>
                    
                    <div class="widget mb-4">
                        <h5 class="widget-title border-bottom pb-2 mb-3">Categories</h5>
                        <ul class="list-unstyled">
                            <li class="mb-2"><a href="#" class="text-decoration-none"><i class="fas fa-globe me-2"></i>World News</a></li>
                            <li class="mb-2"><a href="#" class="text-decoration-none"><i class="fas fa-laptop me-2"></i>Technology</a></li>
                            <li class="mb-2"><a href="#" class="text-decoration-none"><i class="fas fa-chart-line me-2"></i>Business</a></li>
                            <li class="mb-2"><a href="#" class="text-decoration-none"><i class="fas fa-futbol me-2"></i>Sports</a></li>
                        </ul>
                    </div>

                    <div class="widget">
                        <h5 class="widget-title border-bottom pb-2 mb-3">Newsletter</h5>
                        <p>Subscribe to our newsletter for the latest updates.</p>
                        <div class="input-group">
                            <input type="email" class="form-control" placeholder="Your email">
                            <button class="btn btn-danger" type="submit"><i class="fas fa-paper-plane"></i></button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="bg-dark text-light py-5 mt-5">
        <div class="container">
            <div class="row">
                <div class="col-lg-6">
                    <h5><i class="fas fa-newspaper me-2"></i>Echhapa News</h5>
                    <p class="text-muted">Your trusted source for news and information. Built with Flask and MySQL for optimal performance.</p>
                </div>
                <div class="col-lg-6 text-end">
                    <p class="text-muted">&copy; 2025 Echhapa News. All rights reserved.</p>
                    <p class="text-muted">Powered by Flask & MySQL</p>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """, articles=articles)

# Individual article page
@app.route('/article/<slug>')
def article_detail(slug):
    """Display individual article"""
    article = get_article_by_slug(slug)
    if not article:
        return "Article not found", 404
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en" data-bs-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ article.title }} - Echhapa News</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .navbar-brand { font-family: 'Times New Roman', serif; font-weight: 900; color: #d42828 !important; }
        .article-content { font-size: 1.1rem; line-height: 1.8; }
        .article-meta { border-bottom: 2px solid #dee2e6; }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom shadow-sm">
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

    <div class="container py-5">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <article>
                    <header class="article-meta pb-4 mb-4">
                        <h1 class="display-5 fw-bold">{{ article.title }}</h1>
                        <div class="d-flex align-items-center text-muted mt-3">
                            <i class="fas fa-user me-2"></i>
                            <span class="me-3">By {{ article.author }}</span>
                            <i class="fas fa-calendar me-2"></i>
                            <span>{{ article.created_at.strftime('%B %d, %Y') if article.created_at.strftime else article.created_at }}</span>
                        </div>
                    </header>
                    
                    <div class="article-content">
                        {{ article.content | replace('\n', '<br>') | safe }}
                    </div>
                    
                    <footer class="mt-5 pt-4 border-top">
                        <div class="d-flex justify-content-between align-items-center">
                            <a href="/" class="btn btn-outline-primary">
                                <i class="fas fa-arrow-left me-2"></i>Back to Home
                            </a>
                            <div class="social-share">
                                <span class="me-2">Share:</span>
                                <a href="#" class="btn btn-sm btn-outline-primary me-1"><i class="fab fa-twitter"></i></a>
                                <a href="#" class="btn btn-sm btn-outline-primary me-1"><i class="fab fa-facebook"></i></a>
                                <a href="#" class="btn btn-sm btn-outline-primary"><i class="fab fa-linkedin"></i></a>
                            </div>
                        </div>
                    </footer>
                </article>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """, article=article)

# Admin Dashboard
@app.route('/admin')
def admin():
    """Professional Admin Dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    # Get statistics
    conn = get_db()
    stats = {'articles': len(fallback_articles), 'users': 1, 'categories': 5}
    
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) as count FROM articles")
            stats['articles'] = cur.fetchone()['count']
            cur.execute("SELECT COUNT(*) as count FROM users")
            stats['users'] = cur.fetchone()['count']
            cur.execute("SELECT COUNT(*) as count FROM categories")
            stats['categories'] = cur.fetchone()['count']
            cur.close()
            conn.close()
        except:
            pass
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Echhapa News</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%); }
        .dashboard-card { 
            background: rgba(255, 255, 255, 0.1); 
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
        }
        .dashboard-card:hover { 
            transform: translateY(-5px); 
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
        }
        .navbar-brand { color: #fff !important; }
        .glass-effect {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <!-- Top Navigation -->
    <nav class="navbar navbar-expand-lg glass-effect mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold fs-3" href="/admin">
                <i class="fas fa-tachometer-alt me-2"></i>Echhapa CMS
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/" target="_blank">
                    <i class="fas fa-external-link-alt me-1"></i>View Site
                </a>
                <a class="nav-link text-white" href="{{ url_for('admin_logout') }}">
                    <i class="fas fa-sign-out-alt me-1"></i>Logout
                </a>
            </div>
        </div>
    </nav>

    <div class="container">
        <!-- Welcome Section -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="glass-effect rounded p-4">
                    <h1 class="text-white mb-2">
                        <i class="fas fa-crown text-warning me-2"></i>
                        Welcome to Echhapa CMS Dashboard
                    </h1>
                    <p class="text-light opacity-75 mb-0">Manage your news portal with professional tools and analytics</p>
                </div>
            </div>
        </div>

        <!-- Statistics Cards -->
        <div class="row mb-5">
            <div class="col-lg-4 col-md-6 mb-3">
                <div class="card stat-card text-white">
                    <div class="card-body text-center">
                        <i class="fas fa-newspaper fa-3x mb-3 opacity-75"></i>
                        <h3 class="card-title">{{ stats.articles }}</h3>
                        <p class="card-text">Total Articles</p>
                    </div>
                </div>
            </div>
            <div class="col-lg-4 col-md-6 mb-3">
                <div class="card stat-card text-white">
                    <div class="card-body text-center">
                        <i class="fas fa-users fa-3x mb-3 opacity-75"></i>
                        <h3 class="card-title">{{ stats.users }}</h3>
                        <p class="card-text">Total Users</p>
                    </div>
                </div>
            </div>
            <div class="col-lg-4 col-md-6 mb-3">
                <div class="card stat-card text-white">
                    <div class="card-body text-center">
                        <i class="fas fa-tags fa-3x mb-3 opacity-75"></i>
                        <h3 class="card-title">{{ stats.categories }}</h3>
                        <p class="card-text">Categories</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Management Modules -->
        <div class="row">
            <div class="col-lg-6 col-md-6 mb-4">
                <div class="card dashboard-card text-white h-100">
                    <div class="card-body text-center p-4">
                        <div class="mb-4">
                            <i class="fas fa-newspaper fa-4x text-primary"></i>
                        </div>
                        <h4 class="card-title">Article Management</h4>
                        <p class="card-text opacity-75">Create, edit, and manage news articles. Control publication status and organize content.</p>
                        <a href="{{ url_for('articles_management') }}" class="btn btn-primary btn-lg">
                            <i class="fas fa-edit me-2"></i>Manage Articles
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="col-lg-6 col-md-6 mb-4">
                <div class="card dashboard-card text-white h-100">
                    <div class="card-body text-center p-4">
                        <div class="mb-4">
                            <i class="fas fa-th-large fa-4x text-info"></i>
                        </div>
                        <h4 class="card-title">Layout Management</h4>
                        <p class="card-text opacity-75">Customize homepage layouts, sidebar content, and overall site appearance.</p>
                        <a href="{{ url_for('layout_management') }}" class="btn btn-info btn-lg">
                            <i class="fas fa-paint-brush me-2"></i>Manage Layouts
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="col-lg-6 col-md-6 mb-4">
                <div class="card dashboard-card text-white h-100">
                    <div class="card-body text-center p-4">
                        <div class="mb-4">
                            <i class="fas fa-users fa-4x text-success"></i>
                        </div>
                        <h4 class="card-title">User Management</h4>
                        <p class="card-text opacity-75">Manage user accounts, roles, and permissions. Control access to admin features.</p>
                        <a href="{{ url_for('users_management') }}" class="btn btn-success btn-lg">
                            <i class="fas fa-user-cog me-2"></i>Manage Users
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="col-lg-6 col-md-6 mb-4">
                <div class="card dashboard-card text-white h-100">
                    <div class="card-body text-center p-4">
                        <div class="mb-4">
                            <i class="fas fa-cog fa-4x text-warning"></i>
                        </div>
                        <h4 class="card-title">Site Settings</h4>
                        <p class="card-text opacity-75">Configure site settings, SEO options, and general preferences.</p>
                        <a href="{{ url_for('site_settings') }}" class="btn btn-warning btn-lg">
                            <i class="fas fa-tools me-2"></i>Site Settings
                        </a>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Quick Actions -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="glass-effect rounded p-4">
                    <h5 class="text-white mb-3">
                        <i class="fas fa-bolt text-warning me-2"></i>Quick Actions
                    </h5>
                    <div class="d-flex flex-wrap gap-2">
                        <a href="{{ url_for('add_article') }}" class="btn btn-outline-light">
                            <i class="fas fa-plus me-2"></i>New Article
                        </a>
                        <a href="{{ url_for('articles_management') }}" class="btn btn-outline-light">
                            <i class="fas fa-list me-2"></i>View All Articles
                        </a>
                        <a href="/" target="_blank" class="btn btn-outline-light">
                            <i class="fas fa-eye me-2"></i>Preview Site
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """, stats=stats)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template_string(login_template())
        
        # For simplicity, use default credentials when DB is not available
        if username == 'admin' and password == 'admin123':
            session['user_id'] = 1
            session['username'] = 'admin'
            return redirect(url_for('admin'))
        
        conn = get_db()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cur.fetchone()
                cur.close()
                conn.close()
                
                if user and check_password_hash(user['password_hash'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    return redirect(url_for('admin'))
                else:
                    flash('Invalid username or password', 'error')
            except Exception as e:
                flash(f'Database error: {str(e)}', 'error')
        else:
            flash('Invalid username or password', 'error')
    
    return render_template_string(login_template())

def login_template():
    """Return the login template HTML"""
    return """
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - Echhapa News</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
            min-height: 100vh;
        }
        .login-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
    </style>
</head>
<body class="d-flex align-items-center">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-4">
                <div class="card login-card shadow-lg">
                    <div class="card-body p-5">
                        <div class="text-center mb-4">
                            <i class="fas fa-newspaper fa-3x text-primary mb-3"></i>
                            <h2 class="text-white">Echhapa CMS</h2>
                            <p class="text-muted">Admin Login</p>
                        </div>
                        
                        {% with messages = get_flashed_messages() %}
                        {% if messages %}
                        {% for message in messages %}
                        <div class="alert alert-danger">{{ message }}</div>
                        {% endfor %}
                        {% endif %}
                        {% endwith %}
                        
                        <form method="POST">
                            <div class="mb-3">
                                <label class="form-label text-white">Username</label>
                                <div class="input-group">
                                    <span class="input-group-text"><i class="fas fa-user"></i></span>
                                    <input type="text" class="form-control" name="username" required>
                                </div>
                            </div>
                            <div class="mb-4">
                                <label class="form-label text-white">Password</label>
                                <div class="input-group">
                                    <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                    <input type="password" class="form-control" name="password" required>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-primary w-100 btn-lg">
                                <i class="fas fa-sign-in-alt me-2"></i>Login
                            </button>
                        </form>
                        
                        <div class="text-center mt-4">
                            <small class="text-muted">Default: admin / admin123</small><br>
                            <a href="/" class="text-muted">&larr; Back to Website</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    """

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.clear()
    return redirect(url_for('index'))

# Article Management Routes
@app.route('/admin/articles')
def articles_management():
    """Articles management page"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    articles = get_articles(50)  # Get more articles for management
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Article Management - Echhapa News</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%); }
        .glass-effect {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg glass-effect mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/admin">
                <i class="fas fa-tachometer-alt me-2"></i>Echhapa CMS
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/admin">Dashboard</a>
                <a class="nav-link text-white" href="/">View Site</a>
                <a class="nav-link text-white" href="{{ url_for('admin_logout') }}">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1 class="text-white"><i class="fas fa-newspaper me-2"></i>Article Management</h1>
            <a href="{{ url_for('add_article') }}" class="btn btn-primary">
                <i class="fas fa-plus me-2"></i>Add New Article
            </a>
        </div>

        <div class="glass-effect rounded p-4">
            <div class="table-responsive">
                <table class="table table-dark table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Title</th>
                            <th>Author</th>
                            <th>Status</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for article in articles %}
                        <tr>
                            <td>{{ article.id }}</td>
                            <td>{{ article.title[:50] }}{% if article.title|length > 50 %}...{% endif %}</td>
                            <td>{{ article.author }}</td>
                            <td>
                                <span class="badge bg-success">{{ article.status.title() }}</span>
                            </td>
                            <td>{{ article.created_at.strftime('%Y-%m-%d') if article.created_at.strftime else article.created_at }}</td>
                            <td>
                                <a href="/article/{{ article.slug or article.id }}" class="btn btn-sm btn-outline-info" target="_blank">
                                    <i class="fas fa-eye"></i>
                                </a>
                                <a href="{{ url_for('edit_article', id=article.id) }}" class="btn btn-sm btn-outline-warning">
                                    <i class="fas fa-edit"></i>
                                </a>
                                <button class="btn btn-sm btn-outline-danger" onclick="deleteArticle({{ article.id }})">
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

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function deleteArticle(id) {
            if (confirm('Are you sure you want to delete this article?')) {
                fetch('/admin/articles/' + id + '/delete', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                }).then(() => location.reload());
            }
        }
    </script>
</body>
</html>
    """, articles=articles)

@app.route('/admin/articles/add', methods=['GET', 'POST'])
def add_article():
    """Add new article"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        author = request.form.get('author', 'Admin')
        status = request.form.get('status', 'published')
        slug = title.lower().replace(' ', '-').replace(',', '').replace(':', '') if title else ''
        
        conn = get_db()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("INSERT INTO articles (title, content, author, status, slug) VALUES (%s, %s, %s, %s, %s)",
                           (title, content, author, status, slug))
                conn.commit()
                cur.close()
                conn.close()
                flash('Article added successfully!', 'success')
                return redirect(url_for('articles_management'))
            except Exception as e:
                flash(f'Error adding article: {str(e)}', 'error')
        else:
            flash('Database not available', 'error')
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add Article - Echhapa News</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%); }
        .glass-effect {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg glass-effect mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/admin">
                <i class="fas fa-tachometer-alt me-2"></i>Echhapa CMS
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/admin">Dashboard</a>
                <a class="nav-link text-white" href="{{ url_for('articles_management') }}">Articles</a>
                <a class="nav-link text-white" href="{{ url_for('admin_logout') }}">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container">
        <h1 class="text-white mb-4"><i class="fas fa-plus me-2"></i>Add New Article</h1>

        {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
        {% for category, message in messages %}
        <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }}">{{ message }}</div>
        {% endfor %}
        {% endif %}
        {% endwith %}

        <div class="glass-effect rounded p-4">
            <form method="POST">
                <div class="mb-3">
                    <label class="form-label text-white">Title</label>
                    <input type="text" class="form-control" name="title" required>
                </div>
                
                <div class="mb-3">
                    <label class="form-label text-white">Author</label>
                    <input type="text" class="form-control" name="author" value="Admin">
                </div>
                
                <div class="mb-3">
                    <label class="form-label text-white">Status</label>
                    <select class="form-control" name="status">
                        <option value="published">Published</option>
                        <option value="draft">Draft</option>
                    </select>
                </div>
                
                <div class="mb-3">
                    <label class="form-label text-white">Content</label>
                    <textarea class="form-control" name="content" rows="15" required placeholder="Write your article content here..."></textarea>
                </div>
                
                <div class="d-flex gap-2">
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save me-2"></i>Save Article
                    </button>
                    <a href="{{ url_for('articles_management') }}" class="btn btn-secondary">
                        <i class="fas fa-times me-2"></i>Cancel
                    </a>
                </div>
            </form>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """)

@app.route('/admin/articles/<int:id>/edit', methods=['GET', 'POST'])
def edit_article(id):
    """Edit article"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    # Get article
    article = None
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM articles WHERE id = %s", (id,))
            article = cur.fetchone()
            cur.close()
            conn.close()
        except:
            pass
    
    if not article:
        flash('Article not found', 'error')
        return redirect(url_for('articles_management'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        author = request.form.get('author', 'Admin')
        status = request.form.get('status', 'published')
        slug = title.lower().replace(' ', '-').replace(',', '').replace(':', '') if title else article['slug']
        
        conn = get_db()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("UPDATE articles SET title=%s, content=%s, author=%s, status=%s, slug=%s WHERE id=%s",
                           (title, content, author, status, slug, id))
                conn.commit()
                cur.close()
                conn.close()
                flash('Article updated successfully!', 'success')
                return redirect(url_for('articles_management'))
            except Exception as e:
                flash(f'Error updating article: {str(e)}', 'error')
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Article - Echhapa News</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%); }
        .glass-effect {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg glass-effect mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/admin">
                <i class="fas fa-tachometer-alt me-2"></i>Echhapa CMS
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/admin">Dashboard</a>
                <a class="nav-link text-white" href="{{ url_for('articles_management') }}">Articles</a>
                <a class="nav-link text-white" href="{{ url_for('admin_logout') }}">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container">
        <h1 class="text-white mb-4"><i class="fas fa-edit me-2"></i>Edit Article</h1>

        {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
        {% for category, message in messages %}
        <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }}">{{ message }}</div>
        {% endfor %}
        {% endif %}
        {% endwith %}

        <div class="glass-effect rounded p-4">
            <form method="POST">
                <div class="mb-3">
                    <label class="form-label text-white">Title</label>
                    <input type="text" class="form-control" name="title" value="{{ article.title }}" required>
                </div>
                
                <div class="mb-3">
                    <label class="form-label text-white">Author</label>
                    <input type="text" class="form-control" name="author" value="{{ article.author }}">
                </div>
                
                <div class="mb-3">
                    <label class="form-label text-white">Status</label>
                    <select class="form-control" name="status">
                        <option value="published" {% if article.status == 'published' %}selected{% endif %}>Published</option>
                        <option value="draft" {% if article.status == 'draft' %}selected{% endif %}>Draft</option>
                    </select>
                </div>
                
                <div class="mb-3">
                    <label class="form-label text-white">Content</label>
                    <textarea class="form-control" name="content" rows="15" required>{{ article.content }}</textarea>
                </div>
                
                <div class="d-flex gap-2">
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save me-2"></i>Update Article
                    </button>
                    <a href="{{ url_for('articles_management') }}" class="btn btn-secondary">
                        <i class="fas fa-times me-2"></i>Cancel
                    </a>
                </div>
            </form>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """, article=article)

@app.route('/admin/articles/<int:id>/delete', methods=['POST'])
def delete_article(id):
    """Delete article"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM articles WHERE id = %s", (id,))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Database not available'}), 500

# Layout Management
@app.route('/admin/layout')
def layout_management():
    """Layout management page"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Layout Management - Echhapa News</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%); }
        .glass-effect {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg glass-effect mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/admin">
                <i class="fas fa-tachometer-alt me-2"></i>Echhapa CMS
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/admin">Dashboard</a>
                <a class="nav-link text-white" href="/">View Site</a>
                <a class="nav-link text-white" href="{{ url_for('admin_logout') }}">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container">
        <h1 class="text-white mb-4"><i class="fas fa-th-large me-2"></i>Layout Management</h1>

        <div class="row">
            <div class="col-lg-4 mb-4">
                <div class="glass-effect rounded p-4 text-center">
                    <i class="fas fa-palette fa-3x text-primary mb-3"></i>
                    <h5 class="text-white">Theme Settings</h5>
                    <p class="text-muted">Customize colors, fonts, and overall appearance</p>
                    <button class="btn btn-primary">Configure Theme</button>
                </div>
            </div>
            
            <div class="col-lg-4 mb-4">
                <div class="glass-effect rounded p-4 text-center">
                    <i class="fas fa-columns fa-3x text-info mb-3"></i>
                    <h5 class="text-white">Sidebar Management</h5>
                    <p class="text-muted">Configure sidebar widgets and content</p>
                    <button class="btn btn-info">Manage Sidebar</button>
                </div>
            </div>
            
            <div class="col-lg-4 mb-4">
                <div class="glass-effect rounded p-4 text-center">
                    <i class="fas fa-home fa-3x text-success mb-3"></i>
                    <h5 class="text-white">Homepage Layout</h5>
                    <p class="text-muted">Arrange homepage sections and featured content</p>
                    <button class="btn btn-success">Edit Homepage</button>
                </div>
            </div>
        </div>

        <div class="glass-effect rounded p-4 mt-4">
            <h5 class="text-white mb-3">Quick Layout Options</h5>
            <div class="row">
                <div class="col-md-6">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" checked>
                        <label class="form-check-label text-white">Show Breaking News Ticker</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" checked>
                        <label class="form-check-label text-white">Display Newsletter Signup</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" checked>
                        <label class="form-check-label text-white">Show Social Media Links</label>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" checked>
                        <label class="form-check-label text-white">Enable Search Functionality</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" checked>
                        <label class="form-check-label text-white">Show Categories in Sidebar</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox">
                        <label class="form-check-label text-white">Dark Mode Toggle</label>
                    </div>
                </div>
            </div>
            <button class="btn btn-primary mt-3">Save Layout Settings</button>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """)

# User Management
@app.route('/admin/users')
def users_management():
    """User management page"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Management - Echhapa News</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%); }
        .glass-effect {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg glass-effect mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/admin">
                <i class="fas fa-tachometer-alt me-2"></i>Echhapa CMS
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/admin">Dashboard</a>
                <a class="nav-link text-white" href="/">View Site</a>
                <a class="nav-link text-white" href="{{ url_for('admin_logout') }}">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1 class="text-white"><i class="fas fa-users me-2"></i>User Management</h1>
            <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addUserModal">
                <i class="fas fa-plus me-2"></i>Add New User
            </button>
        </div>

        <div class="glass-effect rounded p-4">
            <div class="table-responsive">
                <table class="table table-dark table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Role</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>1</td>
                            <td>admin</td>
                            <td><span class="badge bg-danger">Admin</span></td>
                            <td>2025-01-01</td>
                            <td>
                                <button class="btn btn-sm btn-outline-warning">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-info">
                                    <i class="fas fa-key"></i>
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- User Roles Management -->
        <div class="glass-effect rounded p-4 mt-4">
            <h5 class="text-white mb-3">User Roles & Permissions</h5>
            <div class="row">
                <div class="col-md-4">
                    <div class="card bg-danger">
                        <div class="card-body text-center">
                            <i class="fas fa-crown fa-2x mb-2"></i>
                            <h6>Administrator</h6>
                            <small>Full access to all features</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-warning">
                        <div class="card-body text-center">
                            <i class="fas fa-user-edit fa-2x mb-2"></i>
                            <h6>Editor</h6>
                            <small>Can create and edit articles</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-info">
                        <div class="card-body text-center">
                            <i class="fas fa-user fa-2x mb-2"></i>
                            <h6>Author</h6>
                            <small>Can create own articles</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Add User Modal -->
    <div class="modal fade" id="addUserModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content bg-dark">
                <div class="modal-header">
                    <h5 class="modal-title text-white">Add New User</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form>
                        <div class="mb-3">
                            <label class="form-label text-white">Username</label>
                            <input type="text" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label text-white">Password</label>
                            <input type="password" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label text-white">Role</label>
                            <select class="form-control">
                                <option value="admin">Administrator</option>
                                <option value="editor">Editor</option>
                                <option value="author">Author</option>
                            </select>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary">Add User</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """)

# Site Settings
@app.route('/admin/settings')
def site_settings():
    """Site settings page"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Site Settings - Echhapa News</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%); }
        .glass-effect {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg glass-effect mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold text-white" href="/admin">
                <i class="fas fa-tachometer-alt me-2"></i>Echhapa CMS
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/admin">Dashboard</a>
                <a class="nav-link text-white" href="/">View Site</a>
                <a class="nav-link text-white" href="{{ url_for('admin_logout') }}">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container">
        <h1 class="text-white mb-4"><i class="fas fa-cog me-2"></i>Site Settings</h1>

        <div class="row">
            <div class="col-lg-8">
                <div class="glass-effect rounded p-4 mb-4">
                    <h5 class="text-white mb-3">General Settings</h5>
                    <form>
                        <div class="mb-3">
                            <label class="form-label text-white">Site Title</label>
                            <input type="text" class="form-control" value="Echhapa News">
                        </div>
                        <div class="mb-3">
                            <label class="form-label text-white">Site Description</label>
                            <textarea class="form-control" rows="3">Your trusted source for news and information</textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label text-white">Contact Email</label>
                            <input type="email" class="form-control" value="admin@echhapa.com">
                        </div>
                        <div class="mb-3">
                            <label class="form-label text-white">Timezone</label>
                            <select class="form-control">
                                <option>UTC</option>
                                <option>America/New_York</option>
                                <option>Europe/London</option>
                                <option>Asia/Tokyo</option>
                            </select>
                        </div>
                    </form>
                </div>

                <div class="glass-effect rounded p-4 mb-4">
                    <h5 class="text-white mb-3">SEO Settings</h5>
                    <form>
                        <div class="mb-3">
                            <label class="form-label text-white">Meta Description</label>
                            <textarea class="form-control" rows="2">Echhapa News - Your trusted source for breaking news, technology updates, and global coverage</textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label text-white">Meta Keywords</label>
                            <input type="text" class="form-control" value="news, breaking news, technology, global, updates">
                        </div>
                        <div class="mb-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" checked>
                                <label class="form-check-label text-white">Enable Search Engine Indexing</label>
                            </div>
                        </div>
                    </form>
                </div>
            </div>

            <div class="col-lg-4">
                <div class="glass-effect rounded p-4 mb-4">
                    <h5 class="text-white mb-3">Database Settings</h5>
                    <div class="mb-3">
                        <label class="text-white">Database Type</label>
                        <p class="text-success"><i class="fas fa-database me-2"></i>MySQL</p>
                    </div>
                    <div class="mb-3">
                        <label class="text-white">Connection Status</label>
                        <p class="text-warning"><i class="fas fa-exclamation-triangle me-2"></i>Ready for Local Setup</p>
                    </div>
                    <small class="text-muted">Configure your local MySQL database connection when deploying.</small>
                </div>

                <div class="glass-effect rounded p-4 mb-4">
                    <h5 class="text-white mb-3">Performance</h5>
                    <div class="mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" checked>
                            <label class="form-check-label text-white">Enable Caching</label>
                        </div>
                    </div>
                    <div class="mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox">
                            <label class="form-check-label text-white">Compress Images</label>
                        </div>
                    </div>
                    <div class="mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" checked>
                            <label class="form-check-label text-white">Minify CSS/JS</label>
                        </div>
                    </div>
                </div>

                <div class="glass-effect rounded p-4">
                    <h5 class="text-white mb-3">Security</h5>
                    <div class="mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" checked>
                            <label class="form-check-label text-white">Force HTTPS</label>
                        </div>
                    </div>
                    <div class="mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" checked>
                            <label class="form-check-label text-white">Enable CSRF Protection</label>
                        </div>
                    </div>
                    <button class="btn btn-warning btn-sm">Change Admin Password</button>
                </div>
            </div>
        </div>

        <div class="text-center mt-4">
            <button class="btn btn-success btn-lg">
                <i class="fas fa-save me-2"></i>Save All Settings
            </button>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """)

# Initialize database when app starts
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)