<?php
require_once '../config/config.php';
requireAuth();

$pageTitle = 'Articles Management';

// Handle bulk actions
if ($_POST && isset($_POST['bulk_action']) && !empty($_POST['selected_articles'])) {
    $action = sanitize($_POST['bulk_action']);
    $articleIds = array_map('intval', $_POST['selected_articles']);
    
    if ($action === 'delete') {
        foreach ($articleIds as $id) {
            $stmt = $pdo->prepare("DELETE FROM articles WHERE id = ?");
            $stmt->execute([$id]);
        }
        $success = 'Selected articles have been deleted.';
    } elseif ($action === 'publish') {
        foreach ($articleIds as $id) {
            $stmt = $pdo->prepare("UPDATE articles SET status = 'published', published_at = NOW() WHERE id = ?");
            $stmt->execute([$id]);
        }
        $success = 'Selected articles have been published.';
    } elseif ($action === 'draft') {
        foreach ($articleIds as $id) {
            $stmt = $pdo->prepare("UPDATE articles SET status = 'draft', published_at = NULL WHERE id = ?");
            $stmt->execute([$id]);
        }
        $success = 'Selected articles have been moved to draft.';
    }
}

// Get filter parameters
$status = isset($_GET['status']) ? sanitize($_GET['status']) : '';
$category = isset($_GET['category']) ? intval($_GET['category']) : 0;
$search = isset($_GET['search']) ? sanitize($_GET['search']) : '';
$page = isset($_GET['page']) ? max(1, intval($_GET['page'])) : 1;
$limit = 20;
$offset = ($page - 1) * $limit;

// Build query
$sql = "SELECT a.*, u.username as author_name, c.name as category_name 
        FROM articles a 
        LEFT JOIN users u ON a.author_id = u.id 
        LEFT JOIN categories c ON a.category_id = c.id 
        WHERE 1=1";

$params = [];

if ($status) {
    $sql .= " AND a.status = ?";
    $params[] = $status;
}

if ($category) {
    $sql .= " AND a.category_id = ?";
    $params[] = $category;
}

if ($search) {
    $sql .= " AND (a.title LIKE ? OR a.content LIKE ?)";
    $params[] = "%$search%";
    $params[] = "%$search%";
}

// Count total articles
$countSql = "SELECT COUNT(*) FROM ($sql) as count_query";
$countStmt = $pdo->prepare($countSql);
$countStmt->execute($params);
$totalArticles = $countStmt->fetchColumn();
$totalPages = ceil($totalArticles / $limit);

// Get articles for current page
$sql .= " ORDER BY a.created_at DESC LIMIT ? OFFSET ?";
$params[] = $limit;
$params[] = $offset;

$stmt = $pdo->prepare($sql);
$stmt->execute($params);
$articles = $stmt->fetchAll();

// Get categories for filter
$categories = getCategories();

include '../includes/admin-header.php';
?>

<div class="container-fluid">
    <?php if (isset($success)): ?>
    <div class="alert alert-success alert-dismissible fade show">
        <i class="fas fa-check-circle me-2"></i><?php echo $success; ?>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
    <?php endif; ?>

    <!-- Filters and Actions -->
    <div class="card shadow mb-4">
        <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="m-0 font-weight-bold text-primary">Articles Filter & Actions</h6>
            <a href="/admin/article-edit.php" class="btn btn-primary">
                <i class="fas fa-plus me-1"></i>New Article
            </a>
        </div>
        <div class="card-body">
            <form method="GET" class="row align-items-end">
                <div class="col-md-3 mb-3">
                    <label class="form-label">Status</label>
                    <select name="status" class="form-select">
                        <option value="">All Statuses</option>
                        <option value="published" <?php echo $status === 'published' ? 'selected' : ''; ?>>Published</option>
                        <option value="draft" <?php echo $status === 'draft' ? 'selected' : ''; ?>>Draft</option>
                        <option value="scheduled" <?php echo $status === 'scheduled' ? 'selected' : ''; ?>>Scheduled</option>
                    </select>
                </div>
                <div class="col-md-3 mb-3">
                    <label class="form-label">Category</label>
                    <select name="category" class="form-select">
                        <option value="">All Categories</option>
                        <?php foreach ($categories as $cat): ?>
                        <option value="<?php echo $cat['id']; ?>" <?php echo $category == $cat['id'] ? 'selected' : ''; ?>>
                            <?php echo htmlspecialchars($cat['name']); ?>
                        </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="col-md-4 mb-3">
                    <label class="form-label">Search</label>
                    <input type="text" name="search" class="form-control" placeholder="Search articles..." value="<?php echo htmlspecialchars($search); ?>">
                </div>
                <div class="col-md-2 mb-3">
                    <button type="submit" class="btn btn-secondary w-100">
                        <i class="fas fa-search me-1"></i>Filter
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- Articles Table -->
    <div class="card shadow">
        <div class="card-header">
            <h6 class="m-0 font-weight-bold text-primary">
                Articles (<?php echo $totalArticles; ?> total)
            </h6>
        </div>
        <div class="card-body">
            <?php if (empty($articles)): ?>
            <div class="text-center py-5">
                <i class="fas fa-newspaper fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No articles found</h5>
                <p class="text-muted">
                    <?php if ($search || $status || $category): ?>
                    Try adjusting your filters or <a href="/admin/articles.php">view all articles</a>.
                    <?php else: ?>
                    Get started by <a href="/admin/article-edit.php">creating your first article</a>.
                    <?php endif; ?>
                </p>
            </div>
            <?php else: ?>
            <form method="POST" id="articlesForm">
                <div class="table-responsive">
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th width="40">
                                    <input type="checkbox" id="selectAll" class="form-check-input">
                                </th>
                                <th>Title</th>
                                <th>Author</th>
                                <th>Category</th>
                                <th>Status</th>
                                <th>Date</th>
                                <th width="150">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($articles as $article): ?>
                            <tr>
                                <td>
                                    <input type="checkbox" name="selected_articles[]" value="<?php echo $article['id']; ?>" class="form-check-input article-checkbox">
                                </td>
                                <td>
                                    <strong><?php echo htmlspecialchars($article['title']); ?></strong>
                                    <br>
                                    <small class="text-muted">
                                        <?php echo truncateText(strip_tags($article['content']), 80); ?>
                                    </small>
                                </td>
                                <td><?php echo htmlspecialchars($article['author_name']); ?></td>
                                <td><?php echo htmlspecialchars($article['category_name'] ?: 'Uncategorized'); ?></td>
                                <td>
                                    <?php
                                    $statusClass = [
                                        'published' => 'success',
                                        'draft' => 'secondary',
                                        'scheduled' => 'warning'
                                    ];
                                    ?>
                                    <span class="badge bg-<?php echo $statusClass[$article['status']] ?? 'secondary'; ?>">
                                        <?php echo ucfirst($article['status']); ?>
                                    </span>
                                </td>
                                <td>
                                    <?php if ($article['published_at']): ?>
                                        <?php echo formatDate($article['published_at'], 'M j, Y g:i A'); ?>
                                    <?php else: ?>
                                        <?php echo formatDate($article['created_at'], 'M j, Y g:i A'); ?>
                                        <br><small class="text-muted">Created</small>
                                    <?php endif; ?>
                                </td>
                                <td>
                                    <div class="btn-group btn-group-sm">
                                        <a href="/admin/article-edit.php?id=<?php echo $article['id']; ?>" class="btn btn-outline-primary" title="Edit">
                                            <i class="fas fa-edit"></i>
                                        </a>
                                        <?php if ($article['status'] === 'published'): ?>
                                        <a href="/article.php?slug=<?php echo $article['slug']; ?>" class="btn btn-outline-secondary" target="_blank" title="View">
                                            <i class="fas fa-eye"></i>
                                        </a>
                                        <?php endif; ?>
                                        <button type="button" class="btn btn-outline-danger" onclick="deleteArticle(<?php echo $article['id']; ?>)" title="Delete">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>

                <!-- Bulk Actions -->
                <div class="row align-items-center mt-3">
                    <div class="col-md-6">
                        <div class="input-group">
                            <select name="bulk_action" class="form-select" required>
                                <option value="">Bulk Actions</option>
                                <option value="publish">Publish Selected</option>
                                <option value="draft">Move to Draft</option>
                                <option value="delete">Delete Selected</option>
                            </select>
                            <button type="submit" class="btn btn-secondary" onclick="return confirmBulkAction()">Apply</button>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <!-- Pagination -->
                        <?php if ($totalPages > 1): ?>
                        <nav>
                            <ul class="pagination justify-content-end mb-0">
                                <?php if ($page > 1): ?>
                                <li class="page-item">
                                    <a class="page-link" href="?<?php echo http_build_query(array_merge($_GET, ['page' => $page - 1])); ?>">&laquo; Previous</a>
                                </li>
                                <?php endif; ?>
                                
                                <?php
                                $start = max(1, $page - 2);
                                $end = min($totalPages, $page + 2);
                                
                                for ($i = $start; $i <= $end; $i++):
                                ?>
                                <li class="page-item <?php echo $i == $page ? 'active' : ''; ?>">
                                    <a class="page-link" href="?<?php echo http_build_query(array_merge($_GET, ['page' => $i])); ?>"><?php echo $i; ?></a>
                                </li>
                                <?php endfor; ?>
                                
                                <?php if ($page < $totalPages): ?>
                                <li class="page-item">
                                    <a class="page-link" href="?<?php echo http_build_query(array_merge($_GET, ['page' => $page + 1])); ?>">Next &raquo;</a>
                                </li>
                                <?php endif; ?>
                            </ul>
                        </nav>
                        <?php endif; ?>
                    </div>
                </div>
            </form>
            <?php endif; ?>
        </div>
    </div>
</div>

<script>
// Select all checkbox functionality
document.getElementById('selectAll').addEventListener('change', function() {
    const checkboxes = document.querySelectorAll('.article-checkbox');
    checkboxes.forEach(cb => cb.checked = this.checked);
});

// Individual checkbox change
document.querySelectorAll('.article-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const allCheckboxes = document.querySelectorAll('.article-checkbox');
        const checkedCheckboxes = document.querySelectorAll('.article-checkbox:checked');
        document.getElementById('selectAll').checked = allCheckboxes.length === checkedCheckboxes.length;
    });
});

// Confirm bulk actions
function confirmBulkAction() {
    const selected = document.querySelectorAll('.article-checkbox:checked');
    if (selected.length === 0) {
        alert('Please select at least one article.');
        return false;
    }
    
    const action = document.querySelector('[name="bulk_action"]').value;
    if (action === 'delete') {
        return confirm(`Are you sure you want to delete ${selected.length} selected article(s)? This action cannot be undone.`);
    }
    
    return confirm(`Are you sure you want to apply this action to ${selected.length} selected article(s)?`);
}

// Delete individual article
function deleteArticle(id) {
    if (confirm('Are you sure you want to delete this article? This action cannot be undone.')) {
        window.location.href = `article-delete.php?id=${id}`;
    }
}
</script>

<?php include '../includes/admin-footer.php'; ?>
