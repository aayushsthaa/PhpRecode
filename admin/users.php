<?php
require_once '../config/config.php';
requireAuth();
if (!hasPermission('admin')) {
    die('Access denied. Admin privileges required.');
}

$pageTitle = 'User Management';

// Handle user creation/editing
if ($_POST && isset($_POST['action'])) {
    $action = $_POST['action'];
    $username = sanitize($_POST['username']);
    $email = sanitize($_POST['email']);
    $role = sanitize($_POST['role']);
    
    if ($action === 'create') {
        $password = $_POST['password'];
        if (register($username, $email, $password, $role)) {
            $success = 'User created successfully!';
        } else {
            $error = 'Failed to create user. Username or email might already exist.';
        }
    } elseif ($action === 'update') {
        $userId = intval($_POST['user_id']);
        $stmt = $pdo->prepare("UPDATE users SET username = ?, email = ?, role = ? WHERE id = ?");
        if ($stmt->execute([$username, $email, $role, $userId])) {
            $success = 'User updated successfully!';
        } else {
            $error = 'Failed to update user.';
        }
    }
}

// Handle user deletion
if (isset($_GET['delete'])) {
    $userId = intval($_GET['delete']);
    if ($userId != $_SESSION['user_id']) { // Prevent self-deletion
        $stmt = $pdo->prepare("DELETE FROM users WHERE id = ?");
        if ($stmt->execute([$userId])) {
            $success = 'User deleted successfully!';
        } else {
            $error = 'Failed to delete user.';
        }
    } else {
        $error = 'Cannot delete your own account.';
    }
}

// Get all users
$stmt = $pdo->query("SELECT u.*, COUNT(a.id) as article_count 
                    FROM users u 
                    LEFT JOIN articles a ON u.id = a.author_id 
                    GROUP BY u.id 
                    ORDER BY u.created_at DESC");
$users = $stmt->fetchAll();

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

    <div class="card shadow">
        <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="m-0 font-weight-bold text-primary">User Management</h6>
            <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#userModal">
                <i class="fas fa-plus me-1"></i>Add New User
            </button>
        </div>
        <div class="card-body">
            <div class="table-responsive">
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Role</th>
                            <th>Articles</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($users as $user): ?>
                        <tr>
                            <td><?php echo $user['id']; ?></td>
                            <td>
                                <strong><?php echo htmlspecialchars($user['username']); ?></strong>
                                <?php if ($user['id'] == $_SESSION['user_id']): ?>
                                <span class="badge bg-info">You</span>
                                <?php endif; ?>
                            </td>
                            <td><?php echo htmlspecialchars($user['email']); ?></td>
                            <td>
                                <?php
                                $roleClasses = [
                                    'admin' => 'danger',
                                    'editor' => 'warning',
                                    'author' => 'success'
                                ];
                                ?>
                                <span class="badge bg-<?php echo $roleClasses[$user['role']] ?? 'secondary'; ?>">
                                    <?php echo ucfirst($user['role']); ?>
                                </span>
                            </td>
                            <td><?php echo $user['article_count']; ?></td>
                            <td><?php echo formatDate($user['created_at']); ?></td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-outline-primary" onclick="editUser(<?php echo htmlspecialchars(json_encode($user)); ?>)">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <?php if ($user['id'] != $_SESSION['user_id']): ?>
                                    <a href="?delete=<?php echo $user['id']; ?>" class="btn btn-outline-danger" 
                                       onclick="return confirm('Are you sure you want to delete this user?')">
                                        <i class="fas fa-trash"></i>
                                    </a>
                                    <?php endif; ?>
                                </div>
                            </td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<!-- User Modal -->
<div class="modal fade" id="userModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="userModalTitle">Add New User</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form method="POST" id="userForm">
                <input type="hidden" name="action" id="formAction" value="create">
                <input type="hidden" name="user_id" id="userId">
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Username *</label>
                        <input type="text" class="form-control" name="username" id="username" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Email *</label>
                        <input type="email" class="form-control" name="email" id="email" required>
                    </div>
                    <div class="mb-3" id="passwordField">
                        <label class="form-label">Password *</label>
                        <input type="password" class="form-control" name="password" id="password">
                        <div class="form-text">Minimum 6 characters required.</div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Role</label>
                        <select class="form-select" name="role" id="role">
                            <option value="author">Author</option>
                            <option value="editor">Editor</option>
                            <option value="admin">Administrator</option>
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary" id="submitBtn">Create User</button>
                </div>
            </form>
        </div>
    </div>
</div>

<script>
function editUser(user) {
    document.getElementById('userModalTitle').textContent = 'Edit User';
    document.getElementById('formAction').value = 'update';
    document.getElementById('userId').value = user.id;
    document.getElementById('username').value = user.username;
    document.getElementById('email').value = user.email;
    document.getElementById('role').value = user.role;
    document.getElementById('submitBtn').textContent = 'Update User';
    
    // Hide password field for editing
    const passwordField = document.getElementById('passwordField');
    passwordField.style.display = 'none';
    document.getElementById('password').required = false;
    
    new bootstrap.Modal(document.getElementById('userModal')).show();
}

// Reset form when modal is closed
document.getElementById('userModal').addEventListener('hidden.bs.modal', function() {
    document.getElementById('userModalTitle').textContent = 'Add New User';
    document.getElementById('formAction').value = 'create';
    document.getElementById('userId').value = '';
    document.getElementById('userForm').reset();
    document.getElementById('submitBtn').textContent = 'Create User';
    
    // Show password field for new user
    const passwordField = document.getElementById('passwordField');
    passwordField.style.display = 'block';
    document.getElementById('password').required = true;
});
</script>

<?php include '../includes/admin-footer.php'; ?>
