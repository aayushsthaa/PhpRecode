<?php
require_once 'config/config.php';

$pageTitle = 'Home';
include 'includes/header.php';

// Get articles by sections for homepage layout
$sections = getHomepageSections();
?>

<!-- Custom CSS embedded for homepage -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Crimson+Text:wght@400;600&display=swap" rel="stylesheet">
<style>
/* Modern News Homepage Design - Inspired by BBC/CNN/Reuters */
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    line-height: 1.6;
    color: #1e293b;
    background-color: #ffffff;
    margin: 0;
    padding: 0;
}

/* Modern Typography */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    line-height: 1.2;
    color: #0f172a;
    margin-bottom: 0.75rem;
}

/* Modern Header */
.modern-header {
    background: #ffffff;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 100;
}

.masthead {
    border-bottom: 1px solid #e2e8f0;
    padding: 20px 0;
}

.site-title {
    font-family: 'Crimson Text', serif;
    font-weight: 600;
    font-size: 2.75rem;
    color: #0f172a;
    text-decoration: none;
    letter-spacing: -0.025em;
}

.site-tagline {
    font-size: 0.875rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 8px;
    font-weight: 500;
}

/* Modern Navigation */
.modern-nav {
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
}

.nav-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
}

.nav-links {
    display: flex;
    gap: 0;
    list-style: none;
    margin: 0;
    padding: 0;
    overflow-x: auto;
}

.nav-links li {
    flex-shrink: 0;
}

.nav-links a {
    display: block;
    padding: 16px 24px;
    font-weight: 500;
    font-size: 0.875rem;
    color: #374151;
    text-decoration: none;
    text-transform: uppercase;
    letter-spacing: 0.025em;
    border-bottom: 3px solid transparent;
    transition: all 0.2s ease;
}

.nav-links a:hover {
    color: #0f172a;
    background: #ffffff;
    border-bottom-color: #3b82f6;
}

/* Breaking News Bar */
.breaking-bar {
    background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
    color: white;
    padding: 12px 0;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.025em;
    font-size: 0.875rem;
}

.breaking-text {
    display: flex;
    align-items: center;
    gap: 12px;
}

.breaking-label {
    background: rgba(255, 255, 255, 0.2);
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 700;
}

/* Modern Layout Grid */
.homepage-grid {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 24px;
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 40px;
}

/* Hero Section */
.hero-section {
    margin-bottom: 40px;
}

.hero-article {
    position: relative;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    margin-bottom: 32px;
}

.hero-article img {
    width: 100%;
    height: 400px;
    object-fit: cover;
}

.hero-content {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
    padding: 40px 32px 32px;
    color: white;
}

.hero-category {
    display: inline-block;
    background: #3b82f6;
    color: white;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.025em;
    margin-bottom: 12px;
}

.hero-title {
    font-size: 2rem;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 12px;
    color: white;
}

.hero-excerpt {
    font-size: 1.125rem;
    line-height: 1.4;
    color: #e2e8f0;
    margin-bottom: 16px;
}

.hero-meta {
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: 0.875rem;
    color: #cbd5e1;
}

/* Section Titles */
.section-title {
    font-size: 1.5rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 24px;
    padding-bottom: 12px;
    border-bottom: 3px solid #3b82f6;
    position: relative;
}

.section-title::after {
    content: '';
    position: absolute;
    bottom: -3px;
    right: 0;
    width: 50%;
    height: 3px;
    background: #e2e8f0;
}

/* Article Cards */
.article-grid {
    display: grid;
    gap: 24px;
}

.article-card {
    display: flex;
    gap: 16px;
    padding: 20px;
    background: white;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    transition: all 0.2s ease;
    text-decoration: none;
    color: inherit;
}

.article-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    border-color: #3b82f6;
    text-decoration: none;
    color: inherit;
}

.article-image {
    width: 120px;
    height: 80px;
    border-radius: 8px;
    object-fit: cover;
    flex-shrink: 0;
}

.article-content {
    flex: 1;
}

.article-category {
    display: inline-block;
    background: #f1f5f9;
    color: #3b82f6;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.article-title {
    font-size: 1rem;
    font-weight: 600;
    line-height: 1.3;
    margin-bottom: 8px;
    color: #0f172a;
}

.article-excerpt {
    font-size: 0.875rem;
    color: #64748b;
    line-height: 1.4;
    margin-bottom: 8px;
}

.article-meta {
    font-size: 0.75rem;
    color: #94a3b8;
    display: flex;
    gap: 12px;
}

/* Modern Sidebar Styles */
.sidebar-content {
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    padding: 24px;
    position: sticky;
    top: 100px;
}

.widget {
    margin-bottom: 40px;
}

.widget:last-child {
    margin-bottom: 0;
}

.widget-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 2px solid #3b82f6;
}

/* Trending Stories */
.trending-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.trending-item {
    display: flex;
    gap: 12px;
    padding: 16px;
    background: #f8fafc;
    border-radius: 12px;
    text-decoration: none;
    color: inherit;
    transition: all 0.2s ease;
}

.trending-item:hover {
    background: #f1f5f9;
    transform: translateY(-1px);
    text-decoration: none;
    color: inherit;
}

.trending-number {
    width: 32px;
    height: 32px;
    background: #3b82f6;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.875rem;
    flex-shrink: 0;
}

.trending-content h4 {
    font-size: 0.875rem;
    font-weight: 600;
    line-height: 1.3;
    margin-bottom: 8px;
    color: #0f172a;
}

.trending-meta {
    display: flex;
    gap: 8px;
    font-size: 0.75rem;
    color: #64748b;
}

/* Categories Grid */
.categories-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.category-tag {
    padding: 6px 12px;
    background: #f1f5f9;
    color: #3b82f6;
    text-decoration: none;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.025em;
    transition: all 0.2s ease;
}

.category-tag:hover {
    background: #3b82f6;
    color: white;
    text-decoration: none;
}

/* Newsletter Widget */
.newsletter-widget {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    color: white;
    border-radius: 16px;
}

.newsletter-widget .widget-title {
    color: white;
    border-bottom-color: rgba(255, 255, 255, 0.2);
}

.newsletter-widget p {
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 20px;
}

.newsletter-form {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.form-input {
    padding: 12px 16px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.1);
    color: white;
    font-size: 0.875rem;
}

.form-input::placeholder {
    color: rgba(255, 255, 255, 0.6);
}

.form-input:focus {
    outline: none;
    border-color: white;
    background: rgba(255, 255, 255, 0.15);
}

.newsletter-btn {
    padding: 12px 20px;
    background: white;
    color: #3b82f6;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.newsletter-btn:hover {
    background: #f8fafc;
    transform: translateY(-1px);
}

/* Responsive Design */
@media (max-width: 768px) {
    .homepage-grid {
        grid-template-columns: 1fr;
        gap: 24px;
        padding: 24px 16px;
    }
    
    .hero-article {
        margin-bottom: 24px;
    }
    
    .hero-content {
        padding: 24px 20px 20px;
    }
    
    .hero-title {
        font-size: 1.5rem;
    }
    
    .hero-excerpt {
        font-size: 1rem;
    }
    
    .nav-links {
        overflow-x: auto;
        scrollbar-width: none;
        -ms-overflow-style: none;
    }
    
    .nav-links::-webkit-scrollbar {
        display: none;
    }
    
    .sidebar-content {
        position: static;
    }
    
    .article-grid {
        gap: 16px;
    }
    
    .article-card {
        flex-direction: column;
        gap: 12px;
    }
    
    .article-image {
        width: 100%;
        height: 120px;
    }
}
</style>

.section-title::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 0;
    width: 60px;
    height: 3px;
    background-color: #dc3545;
}

/* Featured Layout Styling */
.featured-article {
    background-color: #ffffff;
    border-radius: 0;
    overflow: hidden;
    box-shadow: none;
}

.featured-article img {
    width: 100%;
    height: auto;
    object-fit: cover;
    border-radius: 0;
}

.featured-article h3 {
    font-family: 'Georgia', 'Times New Roman', serif;
    font-weight: 700;
    font-size: 1.75rem;
    line-height: 1.2;
    margin-bottom: 1rem;
}

.featured-article h3 a {
    color: #000000;
    text-decoration: none;
    transition: color 0.2s ease;
}

.featured-article h3 a:hover {
    color: #dc3545;
}

.featured-article .lead {
    font-size: 1.1rem;
    line-height: 1.5;
    color: #333333;
    margin-bottom: 1.5rem;
}

/* Side Articles */
.side-article {
    border-bottom: 1px solid #e5e5e5;
    padding-bottom: 1rem;
    margin-bottom: 1rem;
}

.side-article:last-child {
    border-bottom: none;
}

.side-article h6 {
    font-family: 'Georgia', 'Times New Roman', serif;
    font-weight: 600;
    font-size: 1rem;
    line-height: 1.3;
    margin-bottom: 0.5rem;
}

.side-article h6 a {
    color: #000000;
    text-decoration: none;
    transition: color 0.2s ease;
}

.side-article h6 a:hover {
    color: #dc3545;
}

.side-article img {
    width: 100%;
    height: auto;
    object-fit: cover;
    border-radius: 2px;
}

/* Grid Layout */
.card {
    border: none;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    border-radius: 0;
    transition: box-shadow 0.2s ease;
}

.card:hover {
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.card-img-top {
    height: 200px;
    object-fit: cover;
    border-radius: 0;
}

.card-title {
    font-family: 'Georgia', 'Times New Roman', serif;
    font-weight: 600;
    font-size: 1.1rem;
    line-height: 1.3;
    margin-bottom: 0.75rem;
}

.card-title a {
    color: #000000;
    text-decoration: none;
    transition: color 0.2s ease;
}

.card-title a:hover {
    color: #dc3545;
}

.card-text {
    font-size: 0.9rem;
    line-height: 1.4;
    color: #666666;
}

/* List Layout */
.list-article {
    border-bottom: 1px solid #e5e5e5;
    padding-bottom: 1.5rem;
    margin-bottom: 1.5rem;
}

.list-article:last-child {
    border-bottom: none;
}

.list-article h5 {
    font-family: 'Georgia', 'Times New Roman', serif;
    font-weight: 600;
    font-size: 1.25rem;
    line-height: 1.3;
    margin-bottom: 0.75rem;
}

.list-article h5 a {
    color: #000000;
    text-decoration: none;
    transition: color 0.2s ease;
}

.list-article h5 a:hover {
    color: #dc3545;
}

.list-article img {
    width: 100%;
    height: 150px;
    object-fit: cover;
    border-radius: 2px;
}

/* Sidebar Styling */
.sidebar {
    background-color: #f8f9fa;
    padding: 2rem 1.5rem;
    min-height: 500px;
}

.sidebar h4 {
    font-family: 'Georgia', 'Times New Roman', serif;
    font-weight: 700;
    font-size: 1.3rem;
    color: #000000;
    margin-bottom: 1.5rem;
    position: relative;
}

.sidebar h4::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 0;
    width: 40px;
    height: 2px;
    background-color: #dc3545;
}

/* Meta Information */
.meta-info {
    font-size: 0.85rem;
    color: #666666;
    margin-bottom: 1rem;
}

.meta-info a {
    color: #666666;
    text-decoration: none;
}

.meta-info a:hover {
    color: #dc3545;
    text-decoration: underline;
}

/* Responsive Design */
@media (max-width: 768px) {
    .site-title {
        font-size: 2rem;
    }
    
    .section-title {
        font-size: 1.3rem;
    }
    
    .featured-article h3 {
        font-size: 1.5rem;
    }
    
    .primary-nav .nav-link {
        padding: 10px 15px;
        font-size: 0.8rem;
    }
}
</style>

<!-- Modern News Header -->
<header class="modern-header">
    <!-- Breaking News Bar -->
    <?php 
    $breakingNews = getArticles(1, 0, 'published');
    if (!empty($breakingNews)):
    ?>
    <div class="breaking-bar">
        <div class="nav-container">
            <div class="breaking-text">
                <span class="breaking-label">Breaking</span>
                <span><?php echo htmlspecialchars($breakingNews[0]['title']); ?></span>
            </div>
        </div>
    </div>
    <?php endif; ?>
    
    <!-- Site Header -->
    <div class="masthead">
        <div class="nav-container">
            <div class="text-center">
                <a href="<?php echo url(''); ?>" class="site-title">Echhapa</a>
                <div class="site-tagline">Trusted News, Global Perspective</div>
            </div>
        </div>
    </div>
    
    <!-- Modern Navigation -->
    <nav class="modern-nav">
        <div class="nav-container">
            <ul class="nav-links">
                <li><a href="<?php echo url(''); ?>">Home</a></li>
                <?php 
                $categories = getCategories();
                foreach(array_slice($categories, 0, 7) as $category): 
                ?>
                <li><a href="<?php echo url('category.php?slug=' . $category['slug']); ?>"><?php echo $category['name']; ?></a></li>
                <?php endforeach; ?>
                <li><a href="<?php echo url('contact.php'); ?>">Contact</a></li>
            </ul>
        </div>
    </nav>
</header>

<!-- Modern Homepage Layout -->
<main>
    <!-- Hero Section -->
    <?php 
    $heroArticles = getArticles(1, 0, 'published');
    if (!empty($heroArticles)):
        $hero = $heroArticles[0];
    ?>
    <section class="hero-section">
        <div class="nav-container">
            <a href="<?php echo url('article.php?slug=' . $hero['slug']); ?>" class="hero-article">
                <img src="<?php echo asset($hero['featured_image'] ?: 'images/default-news.jpg'); ?>" alt="<?php echo htmlspecialchars($hero['title']); ?>">
                <div class="hero-content">
                    <span class="hero-category"><?php echo $hero['category_name'] ?: 'News'; ?></span>
                    <h1 class="hero-title"><?php echo htmlspecialchars($hero['title']); ?></h1>
                    <p class="hero-excerpt"><?php echo htmlspecialchars(truncateText($hero['excerpt'] ?: strip_tags($hero['content']), 150)); ?></p>
                    <div class="hero-meta">
                        <span><i class="fas fa-user"></i> <?php echo $hero['author_name'] ?? 'Admin'; ?></span>
                        <span><i class="fas fa-clock"></i> <?php echo formatDate($hero['created_at']); ?></span>
                    </div>
                </div>
            </a>
        </div>
    </section>
    <?php endif; ?>
    
    <!-- Main Content Grid -->
    <div class="homepage-grid">
        <!-- Main Content -->
        <div class="main-content">
            <?php
            foreach ($sections as $section):
                $articles = getSectionArticles($section['id'], $section['max_articles']);
                if (empty($articles)) continue;
            ?>
            
            <section class="content-section">
                <h2 class="section-title"><?php echo htmlspecialchars($section['name']); ?></h2>
                
                <div class="article-grid">
                    <?php foreach ($articles as $article): ?>
                    <a href="<?php echo url('article.php?slug=' . $article['slug']); ?>" class="article-card">
                        <?php if ($article['featured_image']): ?>
                        <img src="<?php echo asset($article['featured_image']); ?>" alt="<?php echo htmlspecialchars($article['title']); ?>" class="article-image">
                        <?php else: ?>
                        <div class="article-image" style="background: linear-gradient(135deg, #f1f5f9, #e2e8f0); display: flex; align-items: center; justify-content: center; color: #64748b;">
                            <i class="fas fa-newspaper" style="font-size: 24px;"></i>
                        </div>
                        <?php endif; ?>
                        <div class="article-content">
                            <span class="article-category"><?php echo $article['category_name'] ?: 'News'; ?></span>
                            <h3 class="article-title"><?php echo htmlspecialchars($article['title']); ?></h3>
                            <p class="article-excerpt"><?php echo htmlspecialchars(truncateText($article['excerpt'] ?: strip_tags($article['content']), 100)); ?></p>
                            <div class="article-meta">
                                <span><i class="fas fa-user"></i> <?php echo $article['author_name'] ?? 'Admin'; ?></span>
                                <span><i class="fas fa-clock"></i> <?php echo formatDate($article['created_at']); ?></span>
                            </div>
                        </div>
                    </a>
                    <?php endforeach; ?>
                </div>
            </section>
            
            <?php endforeach; ?>
        </div>
        
        <!-- Modern Sidebar -->
        <aside class="sidebar-content">
            <!-- Trending Stories -->
            <div class="widget">
                <h3 class="widget-title">Trending Stories</h3>
                <div class="trending-list">
                    <?php
                    $trendingArticles = getArticles(5, 0, 'published');
                    foreach($trendingArticles as $index => $article):
                    ?>
                    <a href="<?php echo url('article.php?slug=' . $article['slug']); ?>" class="trending-item">
                        <div class="trending-number"><?php echo $index + 1; ?></div>
                        <div class="trending-content">
                            <h4><?php echo htmlspecialchars($article['title']); ?></h4>
                            <div class="trending-meta">
                                <span><?php echo $article['category_name'] ?: 'News'; ?></span>
                                <span><?php echo formatDate($article['created_at']); ?></span>
                            </div>
                        </div>
                    </a>
                    <?php endforeach; ?>
                </div>
            </div>
            
            <!-- Categories Widget -->
            <div class="widget">
                <h3 class="widget-title">Categories</h3>
                <div class="categories-grid">
                    <?php foreach(getCategories() as $category): ?>
                    <a href="<?php echo url('category.php?slug=' . $category['slug']); ?>" class="category-tag">
                        <?php echo htmlspecialchars($category['name']); ?>
                    </a>
                    <?php endforeach; ?>
                </div>
            </div>
            
            <!-- Newsletter Widget -->
            <div class="widget newsletter-widget">
                <h3 class="widget-title">Stay Updated</h3>
                <p>Get the latest news and updates delivered to your inbox.</p>
                <form class="newsletter-form" action="#" method="POST">
                    <div class="form-group">
                        <input type="email" class="form-input" placeholder="Enter your email" required>
                    </div>
                    <button type="submit" class="newsletter-btn">
                        <i class="fas fa-paper-plane"></i>
                        Subscribe Now
                    </button>
                </form>
            </div>
        </aside>
    </div>
</main>

<?php include 'includes/footer.php'; ?>