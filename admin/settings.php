<?php
require_once '../config/config.php';
requireAuth();
if (!hasPermission('admin')) {
    die('Access denied. Admin privileges required.');
}

$pageTitle = 'Site Settings';

// Handle settings update
if ($_POST) {
    foreach ($_POST as $key => $value) {
        if ($key !== 'submit') {
            setSetting($key, $value);
        }
    }
    $success = 'Settings updated successfully!';
}

// Get current settings
$settings = [
    'site_name' => getSetting('site_name', 'Echhapa News'),
    'site_description' => getSetting('site_description', 'Your trusted source for news and information'),
    'site_keywords' => getSetting('site_keywords', 'news, breaking news, world news, politics, business'),
    'contact_email' => getSetting('contact_email', 'contact@echhapa.com'),
    'social_facebook' => getSetting('social_facebook'),
    'social_twitter' => getSetting('social_twitter'),
    'social_instagram' => getSetting('social_instagram'),
    'analytics_code' => getSetting('analytics_code'),
    'header_code' => getSetting('header_code'),
    'footer_code' => getSetting('footer_code'),
];

include '../includes/admin-header.php';
?>

<div class="container-fluid">
    <?php if (isset($success)): ?>
    <div class="alert alert-success alert-dismissible fade show">
        <i class="fas fa-check-circle me-2"></i><?php echo $success; ?>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
    <?php endif; ?>

    <form method="POST">
        <div class="row">
            <!-- General Settings -->
            <div class="col-lg-6 mb-4">
                <div class="card shadow">
                    <div class="card-header">
                        <h6 class="m-0 font-weight-bold text-primary">General Settings</h6>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label">Site Name</label>
                            <input type="text" class="form-control" name="site_name" 
                                   value="<?php echo htmlspecialchars($settings['site_name']); ?>" required>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Site Description</label>
                            <textarea class="form-control" name="site_description" rows="3"><?php echo htmlspecialchars($settings['site_description']); ?></textarea>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Site Keywords</label>
                            <textarea class="form-control" name="site_keywords" rows="2"><?php echo htmlspecialchars($settings['site_keywords']); ?></textarea>
                            <div class="form-text">Separate keywords with commas.</div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Contact Email</label>
                            <input type="email" class="form-control" name="contact_email" 
                                   value="<?php echo htmlspecialchars($settings['contact_email']); ?>">
                        </div>
                    </div>
                </div>
            </div>

            <!-- Social Media Settings -->
            <div class="col-lg-6 mb-4">
                <div class="card shadow">
                    <div class="card-header">
                        <h6 class="m-0 font-weight-bold text-primary">Social Media</h6>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label">Facebook URL</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fab fa-facebook-f"></i></span>
                                <input type="url" class="form-control" name="social_facebook" 
                                       value="<?php echo htmlspecialchars($settings['social_facebook']); ?>"
                                       placeholder="https://facebook.com/yourpage">
                            </div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Twitter URL</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fab fa-twitter"></i></span>
                                <input type="url" class="form-control" name="social_twitter" 
                                       value="<?php echo htmlspecialchars($settings['social_twitter']); ?>"
                                       placeholder="https://twitter.com/youraccount">
                            </div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Instagram URL</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fab fa-instagram"></i></span>
                                <input type="url" class="form-control" name="social_instagram" 
                                       value="<?php echo htmlspecialchars($settings['social_instagram']); ?>"
                                       placeholder="https://instagram.com/youraccount">
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Advanced Settings -->
            <div class="col-12">
                <div class="card shadow">
                    <div class="card-header">
                        <h6 class="m-0 font-weight-bold text-primary">Advanced Settings</h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-lg-4 mb-3">
                                <label class="form-label">Analytics Code</label>
                                <textarea class="form-control" name="analytics_code" rows="5" placeholder="Google Analytics or other tracking code"><?php echo htmlspecialchars($settings['analytics_code']); ?></textarea>
                                <div class="form-text">HTML code for analytics tracking.</div>
                            </div>

                            <div class="col-lg-4 mb-3">
                                <label class="form-label">Header Code</label>
                                <textarea class="form-control" name="header_code" rows="5" placeholder="Custom HTML for &lt;head&gt; section"><?php echo htmlspecialchars($settings['header_code']); ?></textarea>
                                <div class="form-text">Custom HTML inserted before closing &lt;/head&gt; tag.</div>
                            </div>

                            <div class="col-lg-4 mb-3">
                                <label class="form-label">Footer Code</label>
                                <textarea class="form-control" name="footer_code" rows="5" placeholder="Custom HTML for footer"><?php echo htmlspecialchars($settings['footer_code']); ?></textarea>
                                <div class="form-text">Custom HTML inserted before closing &lt;/body&gt; tag.</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- System Information -->
            <div class="col-lg-6 mt-4">
                <div class="card shadow">
                    <div class="card-header">
                        <h6 class="m-0 font-weight-bold text-primary">System Information</h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-6">
                                <strong>PHP Version:</strong>
                            </div>
                            <div class="col-6">
                                <?php echo PHP_VERSION; ?>
                            </div>
                        </div>
                        <hr>
                        <div class="row">
                            <div class="col-6">
                                <strong>Database:</strong>
                            </div>
                            <div class="col-6">
                                MySQL <?php echo $pdo->query('SELECT VERSION()')->fetchColumn(); ?>
                            </div>
                        </div>
                        <hr>
                        <div class="row">
                            <div class="col-6">
                                <strong>Upload Dir:</strong>
                            </div>
                            <div class="col-6">
                                <?php echo is_writable(UPLOAD_DIR) ? '<span class="text-success">Writable</span>' : '<span class="text-danger">Not Writable</span>'; ?>
                            </div>
                        </div>
                        <hr>
                        <div class="row">
                            <div class="col-6">
                                <strong>Max Upload:</strong>
                            </div>
                            <div class="col-6">
                                <?php echo ini_get('upload_max_filesize'); ?>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="col-lg-6 mt-4">
                <div class="card shadow">
                    <div class="card-header">
                        <h6 class="m-0 font-weight-bold text-primary">Quick Actions</h6>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-2">
                            <a href="/" class="btn btn-outline-primary" target="_blank">
                                <i class="fas fa-external-link-alt me-1"></i>View Website
                            </a>
                            <button type="button" class="btn btn-outline-info" onclick="clearCache()">
                                <i class="fas fa-broom me-1"></i>Clear Cache
                            </button>
                            <button type="button" class="btn btn-outline-warning" onclick="exportSettings()">
                                <i class="fas fa-download me-1"></i>Export Settings
                            </button>
                            <button type="button" class="btn btn-outline-secondary" onclick="backupDatabase()">
                                <i class="fas fa-database me-1"></i>Backup Database
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-12">
                <div class="card shadow">
                    <div class="card-body text-center">
                        <button type="submit" name="submit" class="btn btn-primary btn-lg">
                            <i class="fas fa-save me-2"></i>Save All Settings
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </form>
</div>

<script>
function clearCache() {
    if (confirm('Are you sure you want to clear the cache?')) {
        fetch('/api/clear-cache.php', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Cache cleared successfully!', 'success');
                } else {
                    showNotification('Error clearing cache', 'danger');
                }
            });
    }
}

function exportSettings() {
    window.location.href = '/api/export-settings.php';
}

function backupDatabase() {
    if (confirm('This will create a database backup. Continue?')) {
        window.location.href = '/api/backup-database.php';
    }
}
</script>

<?php include '../includes/admin-footer.php'; ?>
