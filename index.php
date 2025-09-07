<?php
require_once 'config/config.php';

$pageTitle = 'Home';
include 'includes/header.php';

// Get articles by sections for homepage layout
$sections = getHomepageSections();
?>

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
    padding: 12px 20px;
    border-right: 1px solid #e5e5e5;
    transition: all 0.2s ease;
}

.primary-nav .nav-link:hover {
    background-color: #e9ecef;
    color: #000000;
}

/* Section Styling */
.section-title {
    font-family: 'Georgia', 'Times New Roman', serif;
    font-weight: 700;
    font-size: 1.5rem;
    color: #000000;
    margin-bottom: 1.5rem;
    position: relative;
}

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

<div class="masthead bg-white">
    <div class="container">
        <div class="text-center">
            <h1 class="site-title">Echhapa News</h1>
            <div class="site-tagline">Your Trusted Source for News</div>
        </div>
    </div>
</div>

<nav class="primary-nav">
    <div class="container">
        <div class="row">
            <div class="col">
                <ul class="nav">
                    <li class="nav-item">
                        <a class="nav-link" href="<?php echo url(''); ?>">Home</a>
                    </li>
                    <?php 
                    $categories = getCategories();
                    foreach(array_slice($categories, 0, 6) as $category): 
                    ?>
                    <li class="nav-item">
                        <a class="nav-link" href="<?php echo url('category.php?slug=' . $category['slug']); ?>"><?php echo $category['name']; ?></a>
                    </li>
                    <?php endforeach; ?>
                    <li class="nav-item">
                        <a class="nav-link" href="<?php echo url('contact.php'); ?>">Contact</a>
                    </li>
                </ul>
            </div>
        </div>
    </div>
</nav>

<div class="container-fluid mt-4">
    <div class="row">
        <!-- Main Content -->
        <div class="col-lg-9">
            <?php
            foreach ($sections as $section):
                $articles = getSectionArticles($section['id'], $section['max_articles']);
                if (empty($articles)) continue;
            ?>
            
            <section class="py-4 border-bottom">
                <div class="container">
                    <div class="row mb-4">
                        <div class="col">
                            <h2 class="section-title"><?php echo htmlspecialchars($section['name']); ?></h2>
                        </div>
                    </div>
                    
                    <?php if ($section['layout_type'] == 'featured'): ?>
                    <!-- Featured Layout -->
                    <div class="row">
                        <?php foreach ($articles as $index => $article): ?>
                        <?php if ($index == 0): ?>
                        <!-- Main Featured Article -->
                        <div class="col-lg-8">
                            <div class="featured-article">
                                <?php if ($article['featured_image']): ?>
                                <img src="<?php echo asset($article['featured_image']); ?>" class="img-fluid mb-3" alt="<?php echo htmlspecialchars($article['title']); ?>">
                                <?php endif; ?>
                                <h3><a href="<?php echo url('article.php?slug=' . $article['slug']); ?>"><?php echo htmlspecialchars($article['title']); ?></a></h3>
                                <div class="meta-info mb-2">
                                    By <?php echo htmlspecialchars($article['author_name'] ?? 'Admin'); ?> • <?php echo formatDate($article['created_at']); ?>
                                </div>
                                <p class="lead"><?php echo htmlspecialchars(truncateText($article['excerpt'] ?: strip_tags($article['content']), 200)); ?></p>
                            </div>
                        </div>
                        <div class="col-lg-4">
                        <?php else: ?>
                        <!-- Side Articles -->
                            <div class="side-article">
                                <div class="row">
                                    <?php if ($article['featured_image']): ?>
                                    <div class="col-4">
                                        <img src="<?php echo asset($article['featured_image']); ?>" class="img-fluid" alt="<?php echo htmlspecialchars($article['title']); ?>">
                                    </div>
                                    <div class="col-8">
                                    <?php else: ?>
                                    <div class="col-12">
                                    <?php endif; ?>
                                        <h6><a href="<?php echo url('article.php?slug=' . $article['slug']); ?>"><?php echo htmlspecialchars($article['title']); ?></a></h6>
                                        <div class="meta-info">
                                            <?php echo formatDate($article['created_at']); ?>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        <?php endif; ?>
                        <?php endforeach; ?>
                        </div>
                    </div>
                    
                    <?php elseif ($section['layout_type'] == 'grid'): ?>
                    <!-- Grid Layout -->
                    <div class="row">
                        <?php foreach ($articles as $article): ?>
                        <div class="col-lg-4 col-md-6 mb-4">
                            <div class="card h-100">
                                <?php if ($article['featured_image']): ?>
                                <img src="<?php echo asset($article['featured_image']); ?>" class="card-img-top" alt="<?php echo htmlspecialchars($article['title']); ?>">
                                <?php endif; ?>
                                <div class="card-body">
                                    <h5 class="card-title">
                                        <a href="<?php echo url('article.php?slug=' . $article['slug']); ?>"><?php echo htmlspecialchars($article['title']); ?></a>
                                    </h5>
                                    <p class="card-text"><?php echo htmlspecialchars(truncateText($article['excerpt'] ?: strip_tags($article['content']), 120)); ?></p>
                                    <div class="d-flex justify-content-between align-items-center">
                                        <small class="text-muted">By <?php echo htmlspecialchars($article['author_name'] ?? 'Admin'); ?></small>
                                        <small class="text-muted"><?php echo formatDate($article['created_at']); ?></small>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <?php endforeach; ?>
                    </div>
                    
                    <?php else: ?>
                    <!-- List Layout -->
                    <div class="row">
                        <?php foreach ($articles as $article): ?>
                        <div class="col-12">
                            <div class="list-article">
                                <div class="row">
                                    <?php if ($article['featured_image']): ?>
                                    <div class="col-md-3">
                                        <img src="<?php echo asset($article['featured_image']); ?>" class="img-fluid" alt="<?php echo htmlspecialchars($article['title']); ?>">
                                    </div>
                                    <div class="col-md-9">
                                    <?php else: ?>
                                    <div class="col-12">
                                    <?php endif; ?>
                                        <h5><a href="<?php echo url('article.php?slug=' . $article['slug']); ?>"><?php echo htmlspecialchars($article['title']); ?></a></h5>
                                        <div class="meta-info">
                                            By <?php echo htmlspecialchars($article['author_name'] ?? 'Admin'); ?> • <?php echo formatDate($article['created_at']); ?>
                                        </div>
                                        <p><?php echo htmlspecialchars(truncateText($article['excerpt'] ?: strip_tags($article['content']), 150)); ?></p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <?php endforeach; ?>
                    </div>
                    <?php endif; ?>
                </div>
            </section>
            
            <?php endforeach; ?>
        </div>
        
        <!-- Sidebar -->
        <div class="col-lg-3">
            <div class="sidebar">
                <h4>Latest News</h4>
                <?php
                $recentArticles = getArticles(5);
                foreach($recentArticles as $article):
                ?>
                <div class="side-article">
                    <h6><a href="<?php echo url('article.php?slug=' . $article['slug']); ?>"><?php echo htmlspecialchars($article['title']); ?></a></h6>
                    <div class="meta-info">
                        <?php echo formatDate($article['created_at']); ?>
                    </div>
                </div>
                <?php endforeach; ?>
                
                <h4 class="mt-4">Categories</h4>
                <ul class="list-unstyled">
                    <?php foreach(getCategories() as $category): ?>
                    <li class="mb-2">
                        <a href="<?php echo url('category.php?slug=' . $category['slug']); ?>" class="text-decoration-none"><?php echo htmlspecialchars($category['name']); ?></a>
                    </li>
                    <?php endforeach; ?>
                </ul>
                
                <h4 class="mt-4">Newsletter</h4>
                <p>Subscribe to get the latest news delivered to your inbox.</p>
                <form class="mb-3">
                    <div class="mb-3">
                        <input type="email" class="form-control" placeholder="Enter your email">
                    </div>
                    <button type="submit" class="btn btn-danger">Subscribe</button>
                </form>
            </div>
        </div>
    </div>
</div>

<?php include 'includes/footer.php'; ?>