<?php
require_once '../config/config.php';
requireAuth();

$isEdit = isset($_GET['id']);
$articleId = $isEdit ? intval($_GET['id']) : 0;
$article = null;

if ($isEdit) {
    $stmt = $pdo->prepare("SELECT * FROM articles WHERE id = ?");
    $stmt->execute([$articleId]);
    $article = $stmt->fetch();
    
    if (!$article) {
        header('Location: ' . adminUrl('articles.php?error=Article not found'));
        exit;
    }
}

$pageTitle = $isEdit ? 'Edit Article' : 'Create New Article';

// Handle form submission
if ($_POST) {
    $title = sanitize($_POST['title']);
    $slug = sanitize($_POST['slug']) ?: generateSlug($title);
    $excerpt = sanitize($_POST['excerpt']);
    $content = $_POST['content']; // Don't sanitize content as it may contain HTML
    $categoryId = intval($_POST['category_id']) ?: null;
    $status = sanitize($_POST['status']);
    $publishedAt = null;
    
    if ($status === 'published') {
        $publishedAt = date('Y-m-d H:i:s');
    } elseif ($status === 'scheduled' && !empty($_POST['scheduled_date'])) {
        $publishedAt = sanitize($_POST['scheduled_date']);
    }
    
    // Handle featured image upload
    $featuredImage = $article['featured_image'] ?? null;
    if (isset($_FILES['featured_image']) && $_FILES['featured_image']['error'] === UPLOAD_ERR_OK) {
        $uploadedFile = uploadFile($_FILES['featured_image']);
        if ($uploadedFile) {
            $featuredImage = $uploadedFile;
        }
    }
    
    try {
        if ($isEdit) {
            $stmt = $pdo->prepare("UPDATE articles SET title = ?, slug = ?, excerpt = ?, content = ?, featured_image = ?, category_id = ?, status = ?, published_at = ?, updated_at = NOW() WHERE id = ?");
            $stmt->execute([$title, $slug, $excerpt, $content, $featuredImage, $categoryId, $status, $publishedAt, $articleId]);
            $success = 'Article updated successfully!';
        } else {
            $stmt = $pdo->prepare("INSERT INTO articles (title, slug, excerpt, content, featured_image, author_id, category_id, status, published_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)");
            $stmt->execute([$title, $slug, $excerpt, $content, $featuredImage, $_SESSION['user_id'], $categoryId, $status, $publishedAt]);
            $articleId = $pdo->lastInsertId();
            $success = 'Article created successfully!';
            $isEdit = true;
            
            // Reload article data
            $stmt = $pdo->prepare("SELECT * FROM articles WHERE id = ?");
            $stmt->execute([$articleId]);
            $article = $stmt->fetch();
        }
        
        // Handle tags
        if (isset($_POST['tags'])) {
            // Delete existing tags
            $stmt = $pdo->prepare("DELETE FROM article_tags WHERE article_id = ?");
            $stmt->execute([$articleId]);
            
            $tags = array_filter(array_map('trim', explode(',', $_POST['tags'])));
            foreach ($tags as $tagName) {
                if (empty($tagName)) continue;
                
                // Insert or get tag
                $tagSlug = generateSlug($tagName);
                $stmt = $pdo->prepare("INSERT IGNORE INTO tags (name, slug) VALUES (?, ?)");
                $stmt->execute([$tagName, $tagSlug]);
                
                $stmt = $pdo->prepare("SELECT id FROM tags WHERE slug = ?");
                $stmt->execute([$tagSlug]);
                $tagId = $stmt->fetchColumn();
                
                // Link tag to article
                $stmt = $pdo->prepare("INSERT IGNORE INTO article_tags (article_id, tag_id) VALUES (?, ?)");
                $stmt->execute([$articleId, $tagId]);
            }
        }
        
    } catch (PDOException $e) {
        $error = 'Error saving article: ' . $e->getMessage();
    }
}

// Get categories
$categories = getCategories();

// Get article tags if editing
$articleTags = [];
if ($isEdit && $article) {
    $stmt = $pdo->prepare("SELECT t.name FROM tags t JOIN article_tags at ON t.id = at.tag_id WHERE at.article_id = ?");
    $stmt->execute([$articleId]);
    $articleTags = $stmt->fetchAll(PDO::FETCH_COLUMN);
}

include '../includes/admin-header.php';
?>

<div class="container-fluid">
    <?php if (isset($success)): ?>
    <div class="alert alert-success alert-dismissible fade show">
        <i class="fas fa-check-circle me-2"></i><?php echo $success; ?>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
    <?php endif; ?>
    
    <?php if (isset($error)): ?>
    <div class="alert alert-danger alert-dismissible fade show">
        <i class="fas fa-exclamation-triangle me-2"></i><?php echo $error; ?>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
    <?php endif; ?>

    <form method="POST" enctype="multipart/form-data" class="needs-validation" novalidate>
        <div class="row">
            <!-- Main Content -->
            <div class="col-lg-8">
                <div class="card shadow mb-4">
                    <div class="card-header">
                        <h6 class="m-0 font-weight-bold text-primary">Article Content</h6>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label for="title" class="form-label">Title *</label>
                            <input type="text" class="form-control" id="title" name="title" 
                                   value="<?php echo htmlspecialchars($article['title'] ?? ''); ?>" required>
                            <div class="invalid-feedback">Please provide a title.</div>
                        </div>

                        <div class="mb-3">
                            <label for="slug" class="form-label">URL Slug</label>
                            <input type="text" class="form-control" id="slug" name="slug" 
                                   value="<?php echo htmlspecialchars($article['slug'] ?? ''); ?>">
                            <div class="form-text">Leave blank to auto-generate from title.</div>
                        </div>

                        <div class="mb-3">
                            <label for="excerpt" class="form-label">Excerpt</label>
                            <textarea class="form-control" id="excerpt" name="excerpt" rows="3"><?php echo htmlspecialchars($article['excerpt'] ?? ''); ?></textarea>
                            <div class="form-text">Brief summary of the article (optional).</div>
                        </div>

                        <div class="mb-3">
                            <label for="content" class="form-label">Content *</label>
                            <textarea class="form-control rich-editor" id="content" name="content" rows="15" required><?php echo htmlspecialchars($article['content'] ?? ''); ?></textarea>
                            <div class="invalid-feedback">Please provide article content.</div>
                        </div>
                    </div>
                </div>

                <!-- SEO Settings -->
                <div class="card shadow mb-4">
                    <div class="card-header">
                        <h6 class="m-0 font-weight-bold text-primary">SEO & Meta</h6>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label for="tags" class="form-label">Tags</label>
                            <input type="text" class="form-control" id="tags" name="tags" 
                                   value="<?php echo htmlspecialchars(implode(', ', $articleTags)); ?>">
                            <div class="form-text">Separate tags with commas (e.g., breaking news, politics, world).</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Sidebar -->
            <div class="col-lg-4">
                <!-- Publish Settings -->
                <div class="card shadow mb-4">
                    <div class="card-header">
                        <h6 class="m-0 font-weight-bold text-primary">Publish Settings</h6>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label for="status" class="form-label">Status</label>
                            <select class="form-select" id="status" name="status">
                                <option value="draft" <?php echo ($article['status'] ?? 'draft') === 'draft' ? 'selected' : ''; ?>>Draft</option>
                                <option value="published" <?php echo ($article['status'] ?? '') === 'published' ? 'selected' : ''; ?>>Published</option>
                                <option value="scheduled" <?php echo ($article['status'] ?? '') === 'scheduled' ? 'selected' : ''; ?>>Scheduled</option>
                            </select>
                        </div>

                        <div class="mb-3" id="scheduledDateDiv" style="display: none;">
                            <label for="scheduled_date" class="form-label">Publish Date & Time</label>
                            <input type="datetime-local" class="form-control" id="scheduled_date" name="scheduled_date" 
                                   value="<?php echo $article['published_at'] ? date('Y-m-d\TH:i', strtotime($article['published_at'])) : ''; ?>">
                        </div>

                        <div class="mb-3">
                            <label for="category_id" class="form-label">Category</label>
                            <select class="form-select" id="category_id" name="category_id">
                                <option value="">Uncategorized</option>
                                <?php foreach ($categories as $category): ?>
                                <option value="<?php echo $category['id']; ?>" 
                                        <?php echo ($article['category_id'] ?? 0) == $category['id'] ? 'selected' : ''; ?>>
                                    <?php echo htmlspecialchars($category['name']); ?>
                                </option>
                                <?php endforeach; ?>
                            </select>
                        </div>

                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save me-1"></i><?php echo $isEdit ? 'Update Article' : 'Create Article'; ?>
                            </button>
                            <?php if ($isEdit && $article['status'] === 'published'): ?>
                            <a href="/article.php?slug=<?php echo $article['slug']; ?>" class="btn btn-outline-secondary" target="_blank">
                                <i class="fas fa-eye me-1"></i>View Article
                            </a>
                            <?php endif; ?>
                            <a href="/admin/articles.php" class="btn btn-outline-secondary">
                                <i class="fas fa-arrow-left me-1"></i>Back to Articles
                            </a>
                        </div>
                    </div>
                </div>

                <!-- Featured Image -->
                <div class="card shadow mb-4">
                    <div class="card-header">
                        <h6 class="m-0 font-weight-bold text-primary">Featured Image</h6>
                    </div>
                    <div class="card-body">
                        <?php if (!empty($article['featured_image'])): ?>
                        <div class="current-image mb-3">
                            <img src="/<?php echo $article['featured_image']; ?>" class="img-fluid rounded" alt="Current featured image">
                            <div class="form-text mt-1">Current featured image</div>
                        </div>
                        <?php endif; ?>
                        
                        <div class="mb-3">
                            <input type="file" class="form-control" name="featured_image" accept="image/*">
                            <div class="form-text">Upload a new featured image (JPG, PNG, GIF).</div>
                        </div>
                    </div>
                </div>

                <!-- Auto-save indicator -->
                <div class="card shadow">
                    <div class="card-body text-center">
                        <span class="auto-save-indicator text-muted">
                            <i class="fas fa-clock me-1"></i>Auto-saving...
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </form>
</div>

<script>
// Auto-generate slug from title
document.getElementById('title').addEventListener('input', function() {
    const slug = generateSlug(this.value);
    document.getElementById('slug').value = slug;
});

// Show/hide scheduled date based on status
document.getElementById('status').addEventListener('change', function() {
    const scheduledDiv = document.getElementById('scheduledDateDiv');
    if (this.value === 'scheduled') {
        scheduledDiv.style.display = 'block';
        document.getElementById('scheduled_date').required = true;
    } else {
        scheduledDiv.style.display = 'none';
        document.getElementById('scheduled_date').required = false;
    }
});

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
    const statusSelect = document.getElementById('status');
    if (statusSelect.value === 'scheduled') {
        document.getElementById('scheduledDateDiv').style.display = 'block';
    }
});

function generateSlug(text) {
    return text
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .trim();
}
</script>

<?php include '../includes/admin-footer.php'; ?>
