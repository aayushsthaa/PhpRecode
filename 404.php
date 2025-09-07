<?php
require_once 'config/config.php';

$pageTitle = '404 - Page Not Found';
include 'includes/header.php';
?>

<div class="container my-5">
    <div class="row">
        <div class="col-12">
            <div class="text-center py-5">
                <div class="mb-4">
                    <i class="fas fa-exclamation-triangle fa-5x text-warning"></i>
                </div>
                <h1 class="display-1 fw-bold text-primary">404</h1>
                <h2 class="h3 mb-3">Page Not Found</h2>
                <p class="lead text-muted mb-4">
                    Sorry, the page you are looking for doesn't exist or has been moved.
                </p>
                
                <div class="d-flex gap-3 justify-content-center">
                    <a href="index.php" class="btn btn-primary btn-lg">
                        <i class="fas fa-home me-2"></i>Go Home
                    </a>
                    <button class="btn btn-outline-secondary btn-lg" onclick="history.back()">
                        <i class="fas fa-arrow-left me-2"></i>Go Back
                    </button>
                </div>
                
                <!-- Popular Articles -->
                <div class="mt-5">
                    <h4 class="mb-4">Popular Articles</h4>
                    <div class="row">
                        <?php
                        $popularArticles = getArticles(3, 0, 'published');
                        foreach ($popularArticles as $article):
                        ?>
                        <div class="col-md-4 mb-3">
                            <div class="card h-100">
                                <?php if ($article['featured_image']): ?>
                                <img src="<?php echo htmlspecialchars($article['featured_image']); ?>" 
                                     class="card-img-top" 
                                     alt="<?php echo htmlspecialchars($article['title']); ?>">
                                <?php endif; ?>
                                <div class="card-body">
                                    <h6 class="card-title">
                                        <a href="article.php?slug=<?php echo $article['slug']; ?>" 
                                           class="text-decoration-none">
                                            <?php echo htmlspecialchars($article['title']); ?>
                                        </a>
                                    </h6>
                                    <small class="text-muted">
                                        <?php echo formatDate($article['published_at']); ?>
                                    </small>
                                </div>
                            </div>
                        </div>
                        <?php endforeach; ?>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<?php include 'includes/footer.php'; ?>