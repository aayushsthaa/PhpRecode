<?php
require_once '../config/config.php';
requireAuth();

$pageTitle = 'Dashboard';

// Get dashboard statistics
$stmt = $pdo->query("SELECT COUNT(*) FROM articles WHERE status = 'published'");
$publishedArticles = $stmt->fetchColumn();

$stmt = $pdo->query("SELECT COUNT(*) FROM articles WHERE status = 'draft'");
$draftArticles = $stmt->fetchColumn();

$stmt = $pdo->query("SELECT COUNT(*) FROM users");
$totalUsers = $stmt->fetchColumn();

$stmt = $pdo->query("SELECT COUNT(*) FROM categories");
$totalCategories = $stmt->fetchColumn();

// Get recent articles
$recentArticles = getArticles(5, 0, 'published');

include '../includes/admin-header.php';
?>

<div class="container-fluid">
    <!-- Stats Cards -->
    <div class="row mb-4">
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-primary shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">Published Articles</div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800"><?php echo $publishedArticles; ?></div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-newspaper fa-2x text-primary"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-warning shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">Draft Articles</div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800"><?php echo $draftArticles; ?></div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-edit fa-2x text-warning"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-info shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-info text-uppercase mb-1">Total Users</div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800"><?php echo $totalUsers; ?></div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-users fa-2x text-info"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-success shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-success text-uppercase mb-1">Categories</div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800"><?php echo $totalCategories; ?></div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-tags fa-2x text-success"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Quick Actions -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card shadow">
                <div class="card-header">
                    <h6 class="m-0 font-weight-bold text-primary">Quick Actions</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3 mb-3">
                            <a href="/admin/article-edit.php" class="btn btn-primary btn-block">
                                <i class="fas fa-plus me-2"></i>New Article
                            </a>
                        </div>
                        <div class="col-md-3 mb-3">
                            <a href="/admin/layouts.php" class="btn btn-info btn-block">
                                <i class="fas fa-th-large me-2"></i>Manage Layouts
                            </a>
                        </div>
                        <div class="col-md-3 mb-3">
                            <a href="/admin/categories.php" class="btn btn-success btn-block">
                                <i class="fas fa-tags me-2"></i>Manage Categories
                            </a>
                        </div>
                        <div class="col-md-3 mb-3">
                            <a href="/admin/settings.php" class="btn btn-warning btn-block">
                                <i class="fas fa-cog me-2"></i>Site Settings
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Recent Articles -->
    <div class="row">
        <div class="col-12">
            <div class="card shadow">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h6 class="m-0 font-weight-bold text-primary">Recent Articles</h6>
                    <a href="/admin/articles.php" class="btn btn-sm btn-primary">View All</a>
                </div>
                <div class="card-body">
                    <?php if (empty($recentArticles)): ?>
                    <div class="text-center py-4">
                        <i class="fas fa-newspaper fa-3x text-muted mb-3"></i>
                        <p class="text-muted">No articles found. <a href="/admin/article-edit.php">Create your first article</a>.</p>
                    </div>
                    <?php else: ?>
                    <div class="table-responsive">
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Title</th>
                                    <th>Author</th>
                                    <th>Category</th>
                                    <th>Published</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($recentArticles as $article): ?>
                                <tr>
                                    <td>
                                        <strong><?php echo htmlspecialchars($article['title']); ?></strong>
                                        <br><small class="text-muted"><?php echo truncateText(strip_tags($article['content']), 50); ?></small>
                                    </td>
                                    <td><?php echo $article['author_name']; ?></td>
                                    <td><?php echo $article['category_name'] ?: 'Uncategorized'; ?></td>
                                    <td><?php echo formatDate($article['published_at'] ?: $article['created_at']); ?></td>
                                    <td>
                                        <a href="/admin/article-edit.php?id=<?php echo $article['id']; ?>" class="btn btn-sm btn-outline-primary">Edit</a>
                                        <a href="/article.php?slug=<?php echo $article['slug']; ?>" class="btn btn-sm btn-outline-secondary" target="_blank">View</a>
                                    </td>
                                </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </div>
</div>

<?php include '../includes/admin-footer.php'; ?>
