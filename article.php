<?php
require_once 'config/config.php';

// Get article slug from URL parameter
$slug = $_GET['slug'] ?? '';

if (empty($slug)) {
    header('HTTP/1.0 404 Not Found');
    include '404.php';
    exit;
}

// Get article by slug
$article = getArticleBySlug($slug);

if (!$article) {
    header('HTTP/1.0 404 Not Found');
    include '404.php';
    exit;
}

// Update view count
if ($article) {
    $stmt = $pdo->prepare("UPDATE articles SET views = views + 1 WHERE id = ?");
    $stmt->execute([$article['id']]);
}

$pageTitle = $article['title'];
include 'includes/header.php';
?>

<div class="container my-5">
    <div class="row">
        <!-- Main Content -->
        <div class="col-lg-8">
            <article>
                <!-- Article Header -->
                <header class="mb-4">
                    <?php if ($article['category_name']): ?>
                    <div class="mb-2">
                        <a href="category.php?slug=<?php echo getCategories()[0]['slug']; ?>" class="badge bg-primary text-decoration-none">
                            <?php echo htmlspecialchars($article['category_name']); ?>
                        </a>
                    </div>
                    <?php endif; ?>
                    
                    <h1 class="display-5 fw-bold mb-3"><?php echo htmlspecialchars($article['title']); ?></h1>
                    
                    <div class="text-muted mb-3">
                        <i class="fas fa-user me-2"></i>By <?php echo htmlspecialchars($article['author_name']); ?>
                        <span class="mx-2">•</span>
                        <i class="fas fa-calendar me-2"></i><?php echo formatDate($article['published_at']); ?>
                        <span class="mx-2">•</span>
                        <i class="fas fa-eye me-2"></i><?php echo number_format($article['views']); ?> views
                    </div>
                    
                    <?php if ($article['excerpt']): ?>
                    <div class="lead mb-4">
                        <?php echo htmlspecialchars($article['excerpt']); ?>
                    </div>
                    <?php endif; ?>
                </header>
                
                <!-- Featured Image -->
                <?php if ($article['featured_image']): ?>
                <div class="mb-4">
                    <img src="<?php echo htmlspecialchars($article['featured_image']); ?>" 
                         class="img-fluid rounded" 
                         alt="<?php echo htmlspecialchars($article['title']); ?>">
                </div>
                <?php endif; ?>
                
                <!-- Article Content -->
                <div class="article-content">
                    <?php echo $article['content']; ?>
                </div>
                
                <!-- Article Footer -->
                <footer class="mt-5 pt-4 border-top">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Share this article:</h6>
                            <a href="https://www.facebook.com/sharer/sharer.php?u=<?php echo urlencode(SITE_URL . '/article.php?slug=' . $article['slug']); ?>" 
                               class="btn btn-outline-primary btn-sm me-2" target="_blank">
                                <i class="fab fa-facebook-f"></i> Facebook
                            </a>
                            <a href="https://twitter.com/intent/tweet?url=<?php echo urlencode(SITE_URL . '/article.php?slug=' . $article['slug']); ?>&text=<?php echo urlencode($article['title']); ?>" 
                               class="btn btn-outline-info btn-sm me-2" target="_blank">
                                <i class="fab fa-twitter"></i> Twitter
                            </a>
                            <a href="https://www.linkedin.com/sharing/share-offsite/?url=<?php echo urlencode(SITE_URL . '/article.php?slug=' . $article['slug']); ?>" 
                               class="btn btn-outline-primary btn-sm" target="_blank">
                                <i class="fab fa-linkedin-in"></i> LinkedIn
                            </a>
                        </div>
                        <div class="col-md-6 text-md-end">
                            <small class="text-muted">
                                Last updated: <?php echo formatDate($article['updated_at']); ?>
                            </small>
                        </div>
                    </div>
                </footer>
            </article>
        </div>
        
        <!-- Sidebar -->
        <div class="col-lg-4">
            <div class="sticky-top" style="top: 2rem;">
                <!-- Related Articles -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Related Articles</h5>
                    </div>
                    <div class="card-body">
                        <?php
                        $relatedArticles = getArticles(5, 0, 'published', $article['category_id']);
                        $relatedArticles = array_filter($relatedArticles, function($a) use ($article) {
                            return $a['id'] != $article['id'];
                        });
                        $relatedArticles = array_slice($relatedArticles, 0, 4);
                        
                        if (empty($relatedArticles)):
                        ?>
                        <p class="text-muted">No related articles found.</p>
                        <?php else: ?>
                        <?php foreach ($relatedArticles as $related): ?>
                        <div class="mb-3 pb-3 border-bottom">
                            <h6 class="mb-1">
                                <a href="article.php?slug=<?php echo $related['slug']; ?>" class="text-decoration-none">
                                    <?php echo htmlspecialchars($related['title']); ?>
                                </a>
                            </h6>
                            <small class="text-muted">
                                <?php echo formatDate($related['published_at']); ?>
                            </small>
                        </div>
                        <?php endforeach; ?>
                        <?php endif; ?>
                    </div>
                </div>
                
                <!-- Categories -->
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Categories</h5>
                    </div>
                    <div class="card-body">
                        <?php
                        $categories = getCategories();
                        foreach ($categories as $category):
                        ?>
                        <a href="category.php?slug=<?php echo $category['slug']; ?>" class="badge bg-secondary text-decoration-none me-2 mb-2">
                            <?php echo htmlspecialchars($category['name']); ?>
                        </a>
                        <?php endforeach; ?>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<?php include 'includes/footer.php'; ?>