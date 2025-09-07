<?php
require_once 'config/config.php';

// Get category slug from URL parameter
$slug = $_GET['slug'] ?? '';

if (empty($slug)) {
    header('HTTP/1.0 404 Not Found');
    include '404.php';
    exit;
}

// Get category by slug
$category = null;
$categories = getCategories();
foreach ($categories as $cat) {
    if ($cat['slug'] === $slug) {
        $category = $cat;
        break;
    }
}

if (!$category) {
    header('HTTP/1.0 404 Not Found');
    include '404.php';
    exit;
}

// Get articles for this category
$page = isset($_GET['page']) ? max(1, intval($_GET['page'])) : 1;
$perPage = 12;
$offset = ($page - 1) * $perPage;

$articles = getArticles($perPage, $offset, 'published', $category['id']);

// Get total count for pagination
$stmt = $pdo->prepare("SELECT COUNT(*) FROM articles WHERE category_id = ? AND status = 'published'");
$stmt->execute([$category['id']]);
$totalArticles = $stmt->fetchColumn();
$totalPages = ceil($totalArticles / $perPage);

$pageTitle = $category['name'];
include 'includes/header.php';
?>

<div class="container my-5">
    <!-- Category Header -->
    <div class="row mb-5">
        <div class="col-12">
            <div class="text-center">
                <h1 class="display-4 fw-bold mb-3"><?php echo htmlspecialchars($category['name']); ?></h1>
                <?php if ($category['description']): ?>
                <p class="lead text-muted"><?php echo htmlspecialchars($category['description']); ?></p>
                <?php endif; ?>
                <div class="text-muted">
                    <i class="fas fa-newspaper me-2"></i><?php echo number_format($totalArticles); ?> articles
                </div>
            </div>
        </div>
    </div>
    
    <!-- Articles Grid -->
    <?php if (empty($articles)): ?>
    <div class="row">
        <div class="col-12">
            <div class="text-center py-5">
                <i class="fas fa-newspaper fa-4x text-muted mb-3"></i>
                <h3>No articles found</h3>
                <p class="text-muted">There are no published articles in this category yet.</p>
                <a href="index.php" class="btn btn-primary">Browse All Articles</a>
            </div>
        </div>
    </div>
    <?php else: ?>
    <div class="row">
        <?php foreach ($articles as $article): ?>
        <div class="col-lg-4 col-md-6 mb-4">
            <div class="card h-100 border-0 shadow-sm">
                <?php if ($article['featured_image']): ?>
                <img src="<?php echo htmlspecialchars($article['featured_image']); ?>" 
                     class="card-img-top" 
                     alt="<?php echo htmlspecialchars($article['title']); ?>">
                <?php endif; ?>
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title">
                        <a href="article.php?slug=<?php echo $article['slug']; ?>" 
                           class="text-decoration-none text-dark">
                            <?php echo htmlspecialchars($article['title']); ?>
                        </a>
                    </h5>
                    <p class="card-text text-muted mb-3">
                        <?php echo truncateText($article['excerpt'] ?: strip_tags($article['content']), 120); ?>
                    </p>
                    <div class="mt-auto">
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="fas fa-user me-1"></i>
                                <?php echo htmlspecialchars($article['author_name']); ?>
                            </small>
                            <small class="text-muted">
                                <i class="fas fa-calendar me-1"></i>
                                <?php echo formatDate($article['published_at']); ?>
                            </small>
                        </div>
                        <div class="mt-2">
                            <small class="text-muted">
                                <i class="fas fa-eye me-1"></i>
                                <?php echo number_format($article['views']); ?> views
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <?php endforeach; ?>
    </div>
    
    <!-- Pagination -->
    <?php if ($totalPages > 1): ?>
    <div class="row mt-5">
        <div class="col-12">
            <nav aria-label="Category pagination">
                <ul class="pagination justify-content-center">
                    <?php if ($page > 1): ?>
                    <li class="page-item">
                        <a class="page-link" href="category.php?slug=<?php echo $slug; ?>&page=<?php echo $page - 1; ?>">
                            <i class="fas fa-chevron-left"></i> Previous
                        </a>
                    </li>
                    <?php endif; ?>
                    
                    <?php
                    $startPage = max(1, $page - 2);
                    $endPage = min($totalPages, $page + 2);
                    
                    for ($i = $startPage; $i <= $endPage; $i++):
                    ?>
                    <li class="page-item <?php echo $i == $page ? 'active' : ''; ?>">
                        <a class="page-link" href="category.php?slug=<?php echo $slug; ?>&page=<?php echo $i; ?>">
                            <?php echo $i; ?>
                        </a>
                    </li>
                    <?php endfor; ?>
                    
                    <?php if ($page < $totalPages): ?>
                    <li class="page-item">
                        <a class="page-link" href="category.php?slug=<?php echo $slug; ?>&page=<?php echo $page + 1; ?>">
                            Next <i class="fas fa-chevron-right"></i>
                        </a>
                    </li>
                    <?php endif; ?>
                </ul>
            </nav>
        </div>
    </div>
    <?php endif; ?>
    <?php endif; ?>
</div>

<!-- Other Categories -->
<div class="bg-light py-5">
    <div class="container">
        <div class="row">
            <div class="col-12">
                <h3 class="mb-4 text-center">Other Categories</h3>
                <div class="text-center">
                    <?php foreach ($categories as $cat): ?>
                        <?php if ($cat['id'] != $category['id']): ?>
                        <a href="category.php?slug=<?php echo $cat['slug']; ?>" 
                           class="badge bg-primary text-decoration-none fs-6 me-3 mb-2 py-2 px-3">
                            <?php echo htmlspecialchars($cat['name']); ?>
                        </a>
                        <?php endif; ?>
                    <?php endforeach; ?>
                </div>
            </div>
        </div>
    </div>
</div>

<?php include 'includes/footer.php'; ?>