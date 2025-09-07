<?php
// Database configuration for PostgreSQL
define('DB_HOST', $_ENV['PGHOST'] ?? 'localhost');
define('DB_NAME', $_ENV['PGDATABASE'] ?? 'echhapa_cms');
define('DB_USER', $_ENV['PGUSER'] ?? 'postgres');
define('DB_PASS', $_ENV['PGPASSWORD'] ?? '');
define('DB_PORT', $_ENV['PGPORT'] ?? '5432');

try {
    $dsn = "pgsql:host=" . DB_HOST . ";port=" . DB_PORT . ";dbname=" . DB_NAME . ";";
    $pdo = new PDO($dsn, DB_USER, DB_PASS);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
} catch(PDOException $e) {
    die("Connection failed: " . $e->getMessage());
}

// Create tables if they don't exist
function createTables($pdo) {
    $tables = [
        // Users table
        "CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) DEFAULT 'author' CHECK (role IN ('admin', 'editor', 'author')),
            is_active BOOLEAN DEFAULT TRUE,
            last_login TIMESTAMP DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )",
        
        // Categories table
        "CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            slug VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            parent_id INTEGER DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )",
        
        // Tags table
        "CREATE TABLE IF NOT EXISTS tags (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) UNIQUE NOT NULL,
            slug VARCHAR(50) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )",
        
        // Articles table
        "CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            slug VARCHAR(255) UNIQUE NOT NULL,
            excerpt TEXT,
            content TEXT NOT NULL,
            featured_image VARCHAR(255),
            author_id INTEGER NOT NULL,
            category_id INTEGER,
            status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'scheduled')),
            published_at TIMESTAMP NULL,
            views INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )",
        
        // Article tags relationship
        "CREATE TABLE IF NOT EXISTS article_tags (
            article_id INTEGER,
            tag_id INTEGER,
            PRIMARY KEY (article_id, tag_id)
        )",
        
        // Homepage sections
        "CREATE TABLE IF NOT EXISTS homepage_sections (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            slug VARCHAR(100) UNIQUE NOT NULL,
            layout_type VARCHAR(20) DEFAULT 'grid' CHECK (layout_type IN ('featured', 'grid', 'list', 'carousel')),
            max_articles INTEGER DEFAULT 6,
            sort_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )",
        
        // Section articles relationship
        "CREATE TABLE IF NOT EXISTS section_articles (
            id SERIAL PRIMARY KEY,
            section_id INTEGER NOT NULL,
            article_id INTEGER NOT NULL,
            position INTEGER DEFAULT 0,
            is_featured BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )",
        
        // Sidebar widgets
        "CREATE TABLE IF NOT EXISTS sidebar_widgets (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100),
            widget_type VARCHAR(30) NOT NULL CHECK (widget_type IN ('recent_articles', 'popular_articles', 'categories', 'tags', 'custom_html', 'newsletter')),
            content TEXT,
            position INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )",
        
        // Site settings
        "CREATE TABLE IF NOT EXISTS site_settings (
            id SERIAL PRIMARY KEY,
            setting_key VARCHAR(100) UNIQUE NOT NULL,
            setting_value TEXT,
            setting_type VARCHAR(20) DEFAULT 'text' CHECK (setting_type IN ('text', 'textarea', 'boolean', 'json')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )",
        
        // Media uploads
        "CREATE TABLE IF NOT EXISTS media (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            original_name VARCHAR(255) NOT NULL,
            file_path VARCHAR(500) NOT NULL,
            file_type VARCHAR(100),
            file_size INTEGER,
            uploaded_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"
    ];
    
    foreach ($tables as $table) {
        $pdo->exec($table);
    }
    
    // Add foreign key constraints after all tables are created
    $constraints = [
        "ALTER TABLE categories ADD CONSTRAINT fk_categories_parent FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL",
        "ALTER TABLE articles ADD CONSTRAINT fk_articles_author FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE",
        "ALTER TABLE articles ADD CONSTRAINT fk_articles_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL",
        "ALTER TABLE article_tags ADD CONSTRAINT fk_article_tags_article FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE",
        "ALTER TABLE article_tags ADD CONSTRAINT fk_article_tags_tag FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE",
        "ALTER TABLE section_articles ADD CONSTRAINT fk_section_articles_section FOREIGN KEY (section_id) REFERENCES homepage_sections(id) ON DELETE CASCADE",
        "ALTER TABLE section_articles ADD CONSTRAINT fk_section_articles_article FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE",
        "ALTER TABLE media ADD CONSTRAINT fk_media_uploader FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL"
    ];
    
    foreach ($constraints as $constraint) {
        try {
            $pdo->exec($constraint);
        } catch (PDOException $e) {
            // Ignore if constraint already exists
        }
    }
}

// Initialize default data
function insertDefaultData($pdo) {
    // Insert default admin user (password: admin123)
    $adminExists = $pdo->query("SELECT COUNT(*) FROM users WHERE username = 'admin'")->fetchColumn();
    if (!$adminExists) {
        $hashedPassword = password_hash('admin123', PASSWORD_DEFAULT);
        $stmt = $pdo->prepare("INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)");
        $stmt->execute(['admin', 'admin@echhapa.com', $hashedPassword, 'admin']);
    }
    
    // Insert default categories
    $categories = [
        ['Top Stories', 'top-stories'],
        ['World News', 'world-news'],
        ['Business', 'business'],
        ['Technology', 'technology'],
        ['Sports', 'sports'],
        ['Entertainment', 'entertainment'],
        ['Health', 'health'],
        ['Politics', 'politics']
    ];
    
    foreach ($categories as $cat) {
        $exists = $pdo->prepare("SELECT COUNT(*) FROM categories WHERE slug = ?");
        $exists->execute([$cat[1]]);
        if (!$exists->fetchColumn()) {
            $stmt = $pdo->prepare("INSERT INTO categories (name, slug) VALUES (?, ?)");
            $stmt->execute($cat);
        }
    }
    
    // Insert default homepage sections
    $sections = [
        ['Top Stories', 'top-stories', 'featured', 3, 1],
        ['World News', 'world-news', 'grid', 6, 2],
        ['Business', 'business', 'list', 4, 3],
        ['Technology', 'technology', 'grid', 6, 4],
        ['Sports', 'sports', 'list', 4, 5]
    ];
    
    foreach ($sections as $section) {
        $exists = $pdo->prepare("SELECT COUNT(*) FROM homepage_sections WHERE slug = ?");
        $exists->execute([$section[1]]);
        if (!$exists->fetchColumn()) {
            $stmt = $pdo->prepare("INSERT INTO homepage_sections (name, slug, layout_type, max_articles, sort_order) VALUES (?, ?, ?, ?, ?)");
            $stmt->execute($section);
        }
    }
    
    // Insert default site settings
    $settings = [
        ['site_name', 'Echhapa News', 'text'],
        ['site_description', 'Your trusted source for news and information', 'text'],
        ['site_keywords', 'news, breaking news, world news, politics, business', 'text'],
        ['contact_email', 'contact@echhapa.com', 'text'],
        ['social_facebook', '', 'text'],
        ['social_twitter', '', 'text'],
        ['social_instagram', '', 'text'],
        ['analytics_code', '', 'textarea'],
        ['header_code', '', 'textarea'],
        ['footer_code', '', 'textarea']
    ];
    
    foreach ($settings as $setting) {
        $exists = $pdo->prepare("SELECT COUNT(*) FROM site_settings WHERE setting_key = ?");
        $exists->execute([$setting[0]]);
        if (!$exists->fetchColumn()) {
            $stmt = $pdo->prepare("INSERT INTO site_settings (setting_key, setting_value, setting_type) VALUES (?, ?, ?)");
            $stmt->execute($setting);
        }
    }
    
    // Insert default sidebar widgets
    $widgets = [
        ['Recent Articles', 'recent_articles', '', 1],
        ['Popular Articles', 'popular_articles', '', 2],
        ['Categories', 'categories', '', 3],
        ['Newsletter', 'newsletter', '<p>Subscribe to our newsletter for the latest updates.</p>', 4]
    ];
    
    foreach ($widgets as $widget) {
        $exists = $pdo->prepare("SELECT COUNT(*) FROM sidebar_widgets WHERE widget_type = ? AND position = ?");
        $exists->execute([$widget[1], $widget[3]]);
        if (!$exists->fetchColumn()) {
            $stmt = $pdo->prepare("INSERT INTO sidebar_widgets (title, widget_type, content, position) VALUES (?, ?, ?, ?)");
            $stmt->execute($widget);
        }
    }
}

// Auto-create tables and insert default data
createTables($pdo);
insertDefaultData($pdo);
?>
