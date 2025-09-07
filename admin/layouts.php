<?php
require_once '../config/config.php';
requireAuth();
requireAuth();
if (!hasPermission('editor')) {
    die('Access denied. Editor privileges required.');
}

$pageTitle = 'Layout Management';

// Handle section creation
if ($_POST && isset($_POST['create_section'])) {
    $name = sanitize($_POST['section_name']);
    $slug = generateSlug($name);
    $layoutType = sanitize($_POST['layout_type']);
    $maxArticles = intval($_POST['max_articles']);
    
    $stmt = $pdo->prepare("INSERT INTO homepage_sections (name, slug, layout_type, max_articles, sort_order) 
                          SELECT ?, ?, ?, ?, COALESCE(MAX(sort_order), 0) + 1 FROM homepage_sections");
    $stmt->execute([$name, $slug, $layoutType, $maxArticles]);
    $success = 'New section created successfully!';
}

// Get all homepage sections
$stmt = $pdo->query("SELECT * FROM homepage_sections ORDER BY sort_order ASC");
$sections = $stmt->fetchAll();

// Get available articles for assignment
$availableArticles = getArticles(50, 0, 'published');

include '../includes/admin-header.php';
?>

<div class="container-fluid">
    <?php if (isset($success)): ?>
    <div class="alert alert-success alert-dismissible fade show">
        <i class="fas fa-check-circle me-2"></i><?php echo $success; ?>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
    <?php endif; ?>

    <!-- Layout Actions -->
    <div class="card shadow mb-4">
        <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="m-0 font-weight-bold text-primary">Layout Management</h6>
            <div class="layout-actions">
                <button class="btn btn-outline-primary me-2" data-bs-toggle="modal" data-bs-target="#newSectionModal">
                    <i class="fas fa-plus me-1"></i>New Section
                </button>
                <button class="btn btn-outline-secondary me-2 preview-layout">
                    <i class="fas fa-eye me-1"></i>Preview Layout
                </button>
            </div>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-md-8">
                    <h6 class="mb-3">Homepage Sections</h6>
                    <div class="sections-list" id="sectionsList">
                        <?php foreach ($sections as $section): ?>
                        <div class="section-item card mb-3" data-section-id="<?php echo $section['id']; ?>">
                            <div class="card-body">
                                <div class="row align-items-center">
                                    <div class="col-1">
                                        <div class="section-drag-handle text-muted" style="cursor: grab;">
                                            <i class="fas fa-grip-vertical"></i>
                                        </div>
                                    </div>
                                    <div class="col-6">
                                        <h6 class="mb-1"><?php echo htmlspecialchars($section['name']); ?></h6>
                                        <small class="text-muted">
                                            <?php echo ucfirst($section['layout_type']); ?> layout • 
                                            Max <?php echo $section['max_articles']; ?> articles •
                                            <span class="badge bg-<?php echo $section['is_active'] ? 'success' : 'secondary'; ?>">
                                                <?php echo $section['is_active'] ? 'Active' : 'Inactive'; ?>
                                            </span>
                                        </small>
                                    </div>
                                    <div class="col-5 text-end">
                                        <div class="btn-group btn-group-sm">
                                            <button class="btn btn-outline-primary" onclick="editSection(<?php echo $section['id']; ?>)">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                            <button class="btn btn-outline-info" onclick="manageArticles(<?php echo $section['id']; ?>)">
                                                <i class="fas fa-newspaper"></i>
                                            </button>
                                            <button class="btn btn-outline-secondary" onclick="toggleSection(<?php echo $section['id']; ?>, <?php echo $section['is_active'] ? 'false' : 'true'; ?>)">
                                                <i class="fas fa-<?php echo $section['is_active'] ? 'eye-slash' : 'eye'; ?>"></i>
                                            </button>
                                            <button class="btn btn-outline-danger" onclick="deleteSection(<?php echo $section['id']; ?>)">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Article assignment area -->
                                <div class="article-assignment mt-3" style="display: none;" id="articles-<?php echo $section['id']; ?>">
                                    <hr>
                                    <h6>Assigned Articles</h6>
                                    <div class="article-list" data-section-id="<?php echo $section['id']; ?>" style="min-height: 100px; border: 2px dashed #dee2e6; border-radius: 0.375rem; padding: 1rem;">
                                        <?php
                                        $sectionArticles = getSectionArticles($section['id']);
                                        foreach ($sectionArticles as $article):
                                        ?>
                                        <div class="article-item card mb-2" data-article-id="<?php echo $article['id']; ?>">
                                            <div class="card-body p-2">
                                                <div class="row align-items-center">
                                                    <div class="col-1">
                                                        <i class="fas fa-grip-vertical text-muted" style="cursor: grab;"></i>
                                                    </div>
                                                    <div class="col-8">
                                                        <h6 class="mb-0"><?php echo htmlspecialchars($article['title']); ?></h6>
                                                        <small class="text-muted">By <?php echo $article['author_name']; ?></small>
                                                    </div>
                                                    <div class="col-3">
                                                        <div class="form-check">
                                                            <input class="form-check-input" type="checkbox" <?php echo $article['is_featured'] ? 'checked' : ''; ?> 
                                                                   onchange="toggleFeatured(<?php echo $article['id']; ?>, <?php echo $section['id']; ?>, this.checked)">
                                                            <label class="form-check-label">Featured</label>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <?php endforeach; ?>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <?php endforeach; ?>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <h6 class="mb-3">Available Articles</h6>
                    <div class="available-articles" style="max-height: 600px; overflow-y: auto;">
                        <?php foreach ($availableArticles as $article): ?>
                        <div class="article-item card mb-2" data-article-id="<?php echo $article['id']; ?>" style="cursor: grab;">
                            <div class="card-body p-2">
                                <h6 class="mb-1"><?php echo htmlspecialchars($article['title']); ?></h6>
                                <small class="text-muted">
                                    By <?php echo $article['author_name']; ?> • 
                                    <?php echo formatDate($article['published_at']); ?>
                                </small>
                            </div>
                        </div>
                        <?php endforeach; ?>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Live Preview -->
    <div class="card shadow">
        <div class="card-header">
            <h6 class="m-0 font-weight-bold text-primary">Live Preview</h6>
        </div>
        <div class="card-body">
            <div class="text-center">
                <iframe src="/?preview=1" class="layout-preview-frame w-100" style="height: 600px; border: 1px solid #dee2e6; border-radius: 0.375rem;"></iframe>
            </div>
        </div>
    </div>
</div>

<!-- New Section Modal -->
<div class="modal fade" id="newSectionModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Create New Section</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form method="POST">
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Section Name</label>
                        <input type="text" class="form-control" name="section_name" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Layout Type</label>
                        <select class="form-select" name="layout_type">
                            <option value="featured">Featured (Main + Side articles)</option>
                            <option value="grid" selected>Grid (Equal sized cards)</option>
                            <option value="list">List (Horizontal layout)</option>
                            <option value="carousel">Carousel (Rotating display)</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Maximum Articles</label>
                        <input type="number" class="form-control" name="max_articles" value="6" min="1" max="20">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" name="create_section" class="btn btn-primary">Create Section</button>
                </div>
            </form>
        </div>
    </div>
</div>

<script>
// Initialize sortable sections
document.addEventListener('DOMContentLoaded', function() {
    // Initialize sortable for sections list
    if (typeof Sortable !== 'undefined') {
        new Sortable(document.getElementById('sectionsList'), {
            handle: '.section-drag-handle',
            animation: 150,
            ghostClass: 'sortable-ghost',
            onEnd: function(evt) {
                updateSectionOrder();
            }
        });
        
        // Initialize sortable for each article list
        document.querySelectorAll('.article-list').forEach(list => {
            new Sortable(list, {
                group: 'articles',
                animation: 150,
                ghostClass: 'article-ghost',
                onAdd: function(evt) {
                    handleArticleMove(evt);
                }
            });
        });
        
        // Initialize sortable for available articles
        new Sortable(document.querySelector('.available-articles'), {
            group: {
                name: 'articles',
                pull: 'clone',
                put: false
            },
            sort: false,
            animation: 150
        });
    }
});

function editSection(sectionId) {
    // Open section editing modal (implement as needed)
    window.location.href = `section-edit.php?id=${sectionId}`;
}

function manageArticles(sectionId) {
    const articleArea = document.getElementById(`articles-${sectionId}`);
    if (articleArea.style.display === 'none') {
        articleArea.style.display = 'block';
    } else {
        articleArea.style.display = 'none';
    }
}

function toggleSection(sectionId, active) {
    fetch('/api/toggle-section.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ section_id: sectionId, is_active: active })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error updating section status');
        }
    });
}

function deleteSection(sectionId) {
    if (confirm('Are you sure you want to delete this section? This action cannot be undone.')) {
        fetch('/api/delete-section.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ section_id: sectionId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error deleting section: ' + data.error);
            }
        });
    }
}

function toggleFeatured(articleId, sectionId, isFeatured) {
    fetch('/api/toggle-featured.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            article_id: articleId, 
            section_id: sectionId, 
            is_featured: isFeatured 
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Featured status updated!', 'success');
        } else {
            alert('Error updating featured status');
        }
    });
}

function updateSectionOrder() {
    const sections = Array.from(document.querySelectorAll('.section-item')).map((section, index) => ({
        id: section.dataset.sectionId,
        order: index + 1
    }));
    
    fetch('/api/update-section-order.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ order: sections })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Section order updated!', 'success');
        }
    });
}

function handleArticleMove(evt) {
    const articleId = evt.item.dataset.articleId;
    const newSectionId = evt.to.dataset.sectionId;
    
    fetch('/api/assign-article.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            article_id: articleId, 
            section_id: newSectionId 
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Article assigned successfully!', 'success');
        } else {
            alert('Error assigning article: ' + data.error);
            evt.item.remove(); // Remove the item if assignment failed
        }
    });
}
</script>

<?php include '../includes/admin-footer.php'; ?>
