<?php
require_once '../config/config.php';
requireAuth();

$pageTitle = 'Dashboard';

// Get dashboard statistics
global $pdo;
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

<!-- Modern Stats Dashboard -->
<div class="row g-4 mb-5">
    <div class="col-xl-3 col-sm-6">
        <div class="stats-card primary">
            <div class="d-flex align-items-center justify-content-between">
                <div>
                    <div class="stats-label">Published Articles</div>
                    <div class="stats-number"><?php echo $publishedArticles; ?></div>
                    <div class="stats-change text-success"><i class="fas fa-arrow-up"></i> +12% from last month</div>
                </div>
                <div class="stats-icon">
                    <i class="fas fa-newspaper"></i>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-xl-3 col-sm-6">
        <div class="stats-card warning">
            <div class="d-flex align-items-center justify-content-between">
                <div>
                    <div class="stats-label">Draft Articles</div>
                    <div class="stats-number"><?php echo $draftArticles; ?></div>
                    <div class="stats-change text-muted"><i class="fas fa-edit"></i> Ready for review</div>
                </div>
                <div class="stats-icon">
                    <i class="fas fa-file-alt"></i>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-xl-3 col-sm-6">
        <div class="stats-card info">
            <div class="d-flex align-items-center justify-content-between">
                <div>
                    <div class="stats-label">Total Users</div>
                    <div class="stats-number"><?php echo $totalUsers; ?></div>
                    <div class="stats-change text-info"><i class="fas fa-users"></i> Active authors</div>
                </div>
                <div class="stats-icon">
                    <i class="fas fa-user-friends"></i>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-xl-3 col-sm-6">
        <div class="stats-card success">
            <div class="d-flex align-items-center justify-content-between">
                <div>
                    <div class="stats-label">Categories</div>
                    <div class="stats-number"><?php echo $totalCategories; ?></div>
                    <div class="stats-change text-success"><i class="fas fa-tags"></i> Content organized</div>
                </div>
                <div class="stats-icon">
                    <i class="fas fa-layer-group"></i>
                </div>
            </div>
        </div>
    </div>
</div>
    
<!-- Quick Actions Grid -->
<div class="row g-4 mb-5">
    <div class="col-12">
        <h3 class="section-title">Quick Actions</h3>
        <div class="quick-actions-grid">
            <a href="<?php echo adminUrl('article-edit.php'); ?>" class="quick-action-card primary">
                <div class="quick-action-icon">
                    <i class="fas fa-plus"></i>
                </div>
                <div class="quick-action-content">
                    <h4>New Article</h4>
                    <p>Create and publish new content</p>
                </div>
            </a>
            
            <a href="<?php echo adminUrl('layouts.php'); ?>" class="quick-action-card info">
                <div class="quick-action-icon">
                    <i class="fas fa-th-large"></i>
                </div>
                <div class="quick-action-content">
                    <h4>Layout Manager</h4>
                    <p>Customize homepage layout</p>
                </div>
            </a>
            
            <a href="<?php echo adminUrl('categories.php'); ?>" class="quick-action-card success">
                <div class="quick-action-icon">
                    <i class="fas fa-tags"></i>
                </div>
                <div class="quick-action-content">
                    <h4>Categories</h4>
                    <p>Organize your content</p>
                </div>
            </a>
            
            <a href="<?php echo adminUrl('media.php'); ?>" class="quick-action-card warning">
                <div class="quick-action-icon">
                    <i class="fas fa-images"></i>
                </div>
                <div class="quick-action-content">
                    <h4>Media Library</h4>
                    <p>Upload and manage files</p>
                </div>
            </a>
            
            <a href="<?php echo adminUrl('users.php'); ?>" class="quick-action-card secondary">
                <div class="quick-action-icon">
                    <i class="fas fa-users"></i>
                </div>
                <div class="quick-action-content">
                    <h4>User Management</h4>
                    <p>Manage authors and admins</p>
                </div>
            </a>
            
            <a href="<?php echo adminUrl('settings.php'); ?>" class="quick-action-card dark">
                <div class="quick-action-icon">
                    <i class="fas fa-cog"></i>
                </div>
                <div class="quick-action-content">
                    <h4>Settings</h4>
                    <p>Configure site preferences</p>
                </div>
            </a>
        </div>
    </div>
</div>
    
<!-- Recent Articles Section -->
<div class="row g-4">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h3 class="section-title mb-0">Recent Articles</h3>
            <a href="<?php echo adminUrl('articles.php'); ?>" class="btn btn-primary">
                <i class="fas fa-list me-2"></i>View All Articles
            </a>
        </div>
        
        <?php if (empty($recentArticles)): ?>
        <div class="empty-state">
            <div class="empty-state-icon">
                <i class="fas fa-newspaper"></i>
            </div>
            <h4>No Articles Yet</h4>
            <p class="text-muted">Get started by creating your first article.</p>
            <a href="<?php echo adminUrl('article-edit.php'); ?>" class="btn btn-primary">
                <i class="fas fa-plus me-2"></i>Create Article
            </a>
        </div>
        <?php else: ?>
        <div class="modern-table">
            <table class="table table-borderless">
                <thead>
                    <tr>
                        <th>Article</th>
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
                            <div class="article-preview">
                                <h6 class="mb-1"><?php echo htmlspecialchars($article['title']); ?></h6>
                                <p class="text-muted small mb-0"><?php echo truncateText(strip_tags($article['content']), 80); ?></p>
                            </div>
                        </td>
                        <td>
                            <div class="author-info">
                                <i class="fas fa-user-circle me-2 text-muted"></i>
                                <?php echo $article['author_name']; ?>
                            </div>
                        </td>
                        <td>
                            <span class="badge bg-light text-dark"><?php echo $article['category_name'] ?: 'Uncategorized'; ?></span>
                        </td>
                        <td>
                            <small class="text-muted"><?php echo formatDate($article['published_at'] ?: $article['created_at']); ?></small>
                        </td>
                        <td>
                            <div class="btn-group btn-group-sm" role="group">
                                <a href="<?php echo adminUrl('article-edit.php?id=' . $article['id']); ?>" class="btn btn-outline-primary" title="Edit">
                                    <i class="fas fa-edit"></i>
                                </a>
                                <a href="<?php echo url('article.php?slug=' . $article['slug']); ?>" class="btn btn-outline-secondary" target="_blank" title="View">
                                    <i class="fas fa-external-link-alt"></i>
                                </a>
                            </div>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
        <?php endif; ?>
    </div>
</div>

<?php include '../includes/admin-footer.php'; ?>
