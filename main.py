#!/usr/bin/env python3
"""
Echhapa News Portal - Flask Version
Converted from PHP to demonstrate the news portal functionality
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, session
import os
import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-change-in-production")

# Database connection
def get_db():
    """Get database connection"""
    try:
        conn = psycopg2.connect(
            host=os.environ.get('PGHOST', 'localhost'),
            port=os.environ.get('PGPORT', '5432'),
            database=os.environ.get('PGDATABASE', 'postgres'),
            user=os.environ.get('PGUSER', 'postgres'),
            password=os.environ.get('PGPASSWORD', '')
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Initialize database
def init_db():
    """Initialize database with basic structure"""
    conn = get_db()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        # Drop and recreate articles table to fix any schema issues
        cur.execute("DROP TABLE IF EXISTS articles CASCADE")
        cur.execute("""
            CREATE TABLE articles (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                author VARCHAR(100) DEFAULT 'Admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'published'
            )
        """)
        
        # Drop and recreate users table to fix any schema issues  
        cur.execute("DROP TABLE IF EXISTS users CASCADE")
        cur.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'admin'
            )
        """)
        
        # Insert default admin user (admin/admin123)
        cur.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        count_result = cur.fetchone()
        if count_result and count_result[0] == 0:
            password_hash = generate_password_hash('admin123')
            cur.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                       ('admin', password_hash, 'admin'))
        
        # Insert sample articles if none exist
        cur.execute("SELECT COUNT(*) FROM articles")
        count_result = cur.fetchone()
        if count_result and count_result[0] == 0:
            sample_articles = [
                ("Breaking: Major Economic Development Announced", "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris. This is a sample article to demonstrate the news portal functionality."),
                ("Technology Advances in 2025", "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium. Totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt. The technology sector continues to evolve rapidly."),
                ("Global Climate Summit Results", "At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores. International cooperation on climate change reaches new milestones."),
                ("Sports Championship Update", "Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit. The championship season brings exciting developments."),
                ("Cultural Festival Highlights", "Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint. Local cultural events showcase community spirit and diversity.")
            ]
            
            for title, content in sample_articles:
                cur.execute("INSERT INTO articles (title, content) VALUES (%s, %s)", (title, content))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

# Homepage
@app.route('/')
def index():
    """Homepage with news articles"""
    conn = get_db()
    if not conn:
        return "Database connection error", 500
    
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM articles WHERE status = 'published' ORDER BY created_at DESC LIMIT 10")
        articles = cur.fetchall()
        cur.close()
        conn.close()
        
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
        .navbar-brand { font-family: 'Times New Roman', serif; font-weight: 900; }
        .breaking-news { background: linear-gradient(45deg, #dc3545, #e74c3c); }
        .featured-article h3 { font-size: 2.2rem; font-weight: 800; }
        .card:hover { transform: translateY(-2px); box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15); }
        .border-left-primary { border-left: 4px solid #dc3545; }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom">
        <div class="container">
            <a class="navbar-brand fw-bold fs-2" href="/">Echhapa News</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">Home</a>
                <a class="nav-link" href="/admin">Admin</a>
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
                    <marquee>Welcome to Echhapa News - Your comprehensive news portal converted from React/Node.js to PHP and now Flask!</marquee>
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
                                    <h3><a href="#" class="text-decoration-none text-dark">{{ articles[0].title }}</a></h3>
                                    <p class="text-muted mb-2">
                                        <small>By {{ articles[0].author }} • {{ articles[0].created_at.strftime('%B %d, %Y') }}</small>
                                    </p>
                                    <p class="lead">{{ articles[0].content[:200] }}...</p>
                                </div>
                            </div>
                            <div class="col-lg-4">
                                {% for article in articles[1:4] %}
                                <div class="side-article mb-3 pb-3 border-bottom">
                                    <h6><a href="#" class="text-decoration-none text-dark">{{ article.title }}</a></h6>
                                    <p class="text-muted mb-0">
                                        <small>{{ article.created_at.strftime('%B %d, %Y') }}</small>
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
                                            <a href="#" class="text-decoration-none text-dark">{{ article.title }}</a>
                                        </h5>
                                        <p class="card-text text-muted">{{ article.content[:100] }}...</p>
                                        <div class="d-flex justify-content-between align-items-center">
                                            <small class="text-muted">By {{ article.author }}</small>
                                            <small class="text-muted">{{ article.created_at.strftime('%b %d') }}</small>
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
                            <li class="mb-2"><a href="/" class="text-decoration-none">Home</a></li>
                            <li class="mb-2"><a href="/admin" class="text-decoration-none">Admin Dashboard</a></li>
                            <li class="mb-2"><a href="#" class="text-decoration-none">About Us</a></li>
                            <li class="mb-2"><a href="#" class="text-decoration-none">Contact</a></li>
                        </ul>
                    </div>
                    
                    <div class="widget mb-4">
                        <h5 class="widget-title border-bottom pb-2 mb-3">Categories</h5>
                        <ul class="list-unstyled">
                            <li class="mb-2"><a href="#" class="text-decoration-none">World News</a></li>
                            <li class="mb-2"><a href="#" class="text-decoration-none">Technology</a></li>
                            <li class="mb-2"><a href="#" class="text-decoration-none">Business</a></li>
                            <li class="mb-2"><a href="#" class="text-decoration-none">Sports</a></li>
                        </ul>
                    </div>

                    <div class="widget">
                        <h5 class="widget-title border-bottom pb-2 mb-3">Newsletter</h5>
                        <p>Subscribe to our newsletter for the latest updates.</p>
                        <div class="input-group">
                            <input type="email" class="form-control" placeholder="Your email">
                            <button class="btn btn-primary" type="submit">Subscribe</button>
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
                    <h5>Echhapa News</h5>
                    <p class="text-muted">Your trusted source for news and information. Originally a React/Express app, converted to PHP, now running on Flask for demonstration.</p>
                </div>
                <div class="col-lg-6 text-end">
                    <p class="text-muted">&copy; 2025 Echhapa News. All rights reserved.</p>
                    <p class="text-muted">Powered by Flask & PostgreSQL</p>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        """, articles=articles)
        
    except Exception as e:
        return f"Error loading articles: {str(e)}", 500

# Admin login
@app.route('/admin')
def admin():
    """Admin dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Echhapa News</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="text-center mb-5">
            <h1><i class="fas fa-tachometer-alt me-3"></i>Echhapa CMS Dashboard</h1>
            <p class="lead">Content Management System</p>
        </div>
        
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-body text-center">
                        <i class="fas fa-newspaper fa-3x text-primary mb-3"></i>
                        <h5>Article Management</h5>
                        <p>Create, edit, and manage news articles</p>
                        <a href="#" class="btn btn-primary">Manage Articles</a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-body text-center">
                        <i class="fas fa-th-large fa-3x text-info mb-3"></i>
                        <h5>Layout Management</h5>
                        <p>Customize homepage and sidebar layouts</p>
                        <a href="#" class="btn btn-info">Manage Layouts</a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-body text-center">
                        <i class="fas fa-users fa-3x text-success mb-3"></i>
                        <h5>User Management</h5>
                        <p>Manage user accounts and permissions</p>
                        <a href="#" class="btn btn-success">Manage Users</a>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-body text-center">
                        <i class="fas fa-cog fa-3x text-warning mb-3"></i>
                        <h5>Settings</h5>
                        <p>Configure site settings and SEO</p>
                        <a href="#" class="btn btn-warning">Site Settings</a>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="text-center mt-4">
            <a href="/" class="btn btn-outline-secondary me-3"><i class="fas fa-eye me-2"></i>View Website</a>
            <a href="{{ url_for('admin_logout') }}" class="btn btn-outline-danger"><i class="fas fa-sign-out-alt me-2"></i>Logout</a>
        </div>
        
        <div class="alert alert-info mt-4">
            <h6><i class="fas fa-info-circle me-2"></i>Demo Information</h6>
            <p class="mb-0">This is a working demonstration of the Echhapa News CMS. The original React/Express/Node.js application has been successfully converted to PHP (with PostgreSQL) and is now running as a Flask application for demonstration purposes.</p>
        </div>
    </div>
</body>
</html>
    """)

def login_template():
    """Return the login template HTML"""
    return """
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - Echhapa News</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-4">
                <div class="card mt-5 shadow">
                    <div class="card-body p-5">
                        <div class="text-center mb-4">
                            <h2>Echhapa CMS</h2>
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
                                <label class="form-label">Username</label>
                                <input type="text" class="form-control" name="username" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Password</label>
                                <input type="password" class="form-control" name="password" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Login</button>
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

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template_string(login_template())
        
        conn = get_db()
        if conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
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
    
    return render_template_string(login_template())

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.clear()
    return redirect(url_for('index'))

# Initialize database when app starts
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)