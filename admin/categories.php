<?php
require_once '../config/config.php';
requireAuth();

$pageTitle = 'Category Management';

// Handle category operations
if ($_POST) {
    if (isset($_POST['create_category'])) {
        $name = sanitize($_POST['name']);
        $description = sanitize($_POST['description']);
        $slug = generateSlug($name);
        $parentId = intval($_POST['parent_id']) ?: null;
        
        $stmt = $pdo->prepare("INSERT INTO categories (name, slug, description, parent_id) VALUES (?, ?, ?, ?)");
        if ($stmt->execute([$name, $slug, $description, $parentId])) {
            $success = 'Category created successfully!';
        } else {
            $error = 'Failed to create category.';
        }
    } elseif (isset($_POST['update_category'])) {
        $id = intval($_POST['category_id']);
        $name = sanitize($_POST['name']);
        $description = sanitize($_POST['description']);
        $slug = sanitize($_POST['slug']);
        $parentId = intval($_POST['parent_id']) ?: null;
        
        $stmt = $pdo->prepare("UPDATE categories SET name = ?, slug = ?, description = ?, parent_id = ? WHERE id = ?");
        if ($stmt->execute([$name, $slug, $description, $parentId, $id])) {
            $success = 'Category updated successfully!';
        } else {
            $error = 'Failed to update category.';
        }
    }
}

// Handle category deletion
if (isset($_GET['delete'])) {
    $categoryId = intval($_GET['delete']);
    $stmt = $pdo->prepare("DELETE FROM categories WHERE id = ?");
    if ($stmt->execute([$categoryId])) {
        $success = 'Category deleted successfully!';
    } else {
        $error = 'Failed to delete category.';
    }
}

// Get all categories with article counts
$stmt = $pdo->query("SELECT c.*, COUNT(a.id) as article_count, pc.name as parent_name
                    FROM categories c 
                    LEFT JOIN articles a ON c.id = a.category_id 
                    LEFT JOIN categories pc ON c.parent_id = pc.id
                    GROUP BY c.id 
                    ORDER BY c.name");
$categories = $stmt->fetchAll();

// Get parent categories for form
$parentCategories = array_filter($categories, function($cat) { return $cat['parent_id'] === null; });

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

    <div class="row">
        <!-- Categories List -->
        <div class="col-lg-8">
            <div class="card shadow">
                <div class="card-header">
                    <h6 class="m-0 font-weight-bold text-primary">Categories</h6>
                </div>
                <div class="card-body">
                    <?php if (empty($categories)): ?>
                    <div class="text-center py-4">
                        <i class="fas fa-tags fa-3x text-muted mb-3"></i>
                        <h5 class="text-muted">No categories found</h5>
                        <p class="text-muted">Create your first category to organize your articles.</p>
                    </div>
                    <?php else: ?>
                    <div class="table-responsive">
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Slug</th>
                                    <th>Parent</th>
                                    <th>Articles</th>
                                    <th>Created</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($categories as $category): ?>
                                <tr>
                                    <td>
                                        <strong><?php echo htmlspecialchars($category['name']); ?></strong>
                                        <?php if ($category['description']): ?>
                                        <br><small class="text-muted"><?php echo htmlspecialchars($category['description']); ?></small>
                                        <?php endif; ?>
                                    </td>
                                    <td><code><?php echo $category['slug']; ?></code></td>
                                    <td><?php echo $category['parent_name'] ? htmlspecialchars($category['parent_name']) : '—'; ?></td>
                                    <td>
                                        <?php if ($category['article_count'] > 0): ?>
                                        <a href="<?php echo adminUrl('articles.php?category=' . $category['id']); ?>" class="text-decoration-none">
                                            <?php echo $category['article_count']; ?>
                                        </a>
                                        <?php else: ?>
                                        0
                                        <?php endif; ?>
                                    </td>
                                    <td><?php echo formatDate($category['created_at']); ?></td>
                                    <td>
                                        <div class="btn-group btn-group-sm">
                                            <button class="btn btn-outline-primary" onclick="editCategory(<?php echo htmlspecialchars(json_encode($category)); ?>)">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                            <a href="<?php echo url('category.php?slug=' . $category['slug']); ?>" class="btn btn-outline-secondary" target="_blank">
                                                <i class="fas fa-eye"></i>
                                            </a>
                                            <a href="?delete=<?php echo $category['id']; ?>" class="btn btn-outline-danger" 
                                               onclick="return confirm('Are you sure you want to delete this category? This will uncategorize all articles in this category.')">
                                                <i class="fas fa-trash"></i>
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
        </div>

        <!-- Add/Edit Category Form -->
        <div class="col-lg-4">
            <div class="card shadow">
                <div class="card-header">
                    <h6 class="m-0 font-weight-bold text-primary" id="formTitle">Add New Category</h6>
                </div>
                <div class="card-body">
                    <form method="POST" id="categoryForm">
                        <input type="hidden" name="category_id" id="categoryId">
                        
                        <div class="mb-3">
                            <label class="form-label">Name *</label>
                            <input type="text" class="form-control" name="name" id="categoryName" required>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Slug</label>
                            <input type="text" class="form-control" name="slug" id="categorySlug">
                            <div class="form-text">Leave blank to auto-generate from name.</div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Parent Category</label>
                            <select class="form-select" name="parent_id" id="parentId">
                                <option value="">None (Top Level)</option>
                                <?php foreach ($parentCategories as $parent): ?>
                                <option value="<?php echo $parent['id']; ?>">
                                    <?php echo htmlspecialchars($parent['name']); ?>
                                </option>
                                <?php endforeach; ?>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Description</label>
                            <textarea class="form-control" name="description" id="categoryDescription" rows="3"></textarea>
                        </div>

                        <div class="d-grid gap-2">
                            <button type="submit" name="create_category" id="submitBtn" class="btn btn-primary">
                                <i class="fas fa-plus me-1"></i>Create Category
                            </button>
                            <button type="button" class="btn btn-secondary" id="cancelBtn" onclick="resetForm()" style="display: none;">
                                <i class="fas fa-times me-1"></i>Cancel Edit
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <!-- Category Stats -->
            <div class="card shadow mt-4">
                <div class="card-header">
                    <h6 class="m-0 font-weight-bold text-primary">Category Statistics</h6>
                </div>
                <div class="card-body">
                    <div class="row text-center">
                        <div class="col-6">
                            <div class="border-end">
                                <h4 class="text-primary"><?php echo count($categories); ?></h4>
                                <small class="text-muted">Total Categories</small>
                            </div>
                        </div>
                        <div class="col-6">
                            <h4 class="text-success"><?php echo count($parentCategories); ?></h4>
                            <small class="text-muted">Parent Categories</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
// Auto-generate slug from name
document.getElementById('categoryName').addEventListener('input', function() {
    const slug = generateSlug(this.value);
    document.getElementById('categorySlug').value = slug;
});

function editCategory(category) {
    document.getElementById('formTitle').textContent = 'Edit Category';
    document.getElementById('categoryId').value = category.id;
    document.getElementById('categoryName').value = category.name;
    document.getElementById('categorySlug').value = category.slug;
    document.getElementById('categoryDescription').value = category.description || '';
    document.getElementById('parentId').value = category.parent_id || '';
    
    document.getElementById('submitBtn').innerHTML = '<i class="fas fa-save me-1"></i>Update Category';
    document.getElementById('submitBtn').name = 'update_category';
    document.getElementById('cancelBtn').style.display = 'block';
}

function resetForm() {
    document.getElementById('formTitle').textContent = 'Add New Category';
    document.getElementById('categoryForm').reset();
    document.getElementById('categoryId').value = '';
    document.getElementById('submitBtn').innerHTML = '<i class="fas fa-plus me-1"></i>Create Category';
    document.getElementById('submitBtn').name = 'create_category';
    document.getElementById('cancelBtn').style.display = 'none';
}

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
