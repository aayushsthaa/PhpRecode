<?php
// Echhapa CMS Installation Script

// Check if already installed
if (file_exists('config/installed.lock')) {
    die('<h1>Already Installed</h1><p>Echhapa CMS is already installed. Delete config/installed.lock to reinstall.</p>');
}

$step = isset($_GET['step']) ? intval($_GET['step']) : 1;
$errors = [];
$success = [];

// Handle form submissions
if ($_POST) {
    if ($step == 2) {
        // Database configuration
        $dbHost = $_POST['db_host'] ?? 'localhost';
        $dbName = $_POST['db_name'] ?? 'echhapa_cms';
        $dbUser = $_POST['db_user'] ?? 'root';
        $dbPass = $_POST['db_pass'] ?? '';
        
        try {
            // Test database connection
            $pdo = new PDO("mysql:host=$dbHost;dbname=$dbName;charset=utf8mb4", $dbUser, $dbPass);
            $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            
            // Store database config
            $_SESSION['db_config'] = [
                'host' => $dbHost,
                'name' => $dbName,
                'user' => $dbUser,
                'pass' => $dbPass
            ];
            
            $success[] = 'Database connection successful!';
            $step = 3;
        } catch (PDOException $e) {
            $errors[] = 'Database connection failed: ' . $e->getMessage();
        }
    } elseif ($step == 3) {
        // Admin user creation
        $adminUser = $_POST['admin_user'] ?? '';
        $adminEmail = $_POST['admin_email'] ?? '';
        $adminPass = $_POST['admin_pass'] ?? '';
        $siteName = $_POST['site_name'] ?? 'Echhapa News';
        
        if (empty($adminUser) || empty($adminEmail) || empty($adminPass)) {
            $errors[] = 'All fields are required';
        } elseif (strlen($adminPass) < 6) {
            $errors[] = 'Password must be at least 6 characters';
        } else {
            try {
                session_start();
                $dbConfig = $_SESSION['db_config'];
                
                // Connect to database
                $pdo = new PDO("mysql:host={$dbConfig['host']};dbname={$dbConfig['name']};charset=utf8mb4", 
                               $dbConfig['user'], $dbConfig['pass']);
                $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
                
                // Create tables using the database schema
                require_once 'config/database.php';
                createTables($pdo);
                
                // Create admin user
                $hashedPassword = password_hash($adminPass, PASSWORD_DEFAULT);
                $stmt = $pdo->prepare("INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, 'admin')");
                $stmt->execute([$adminUser, $adminEmail, $hashedPassword]);
                
                // Set site name
                $stmt = $pdo->prepare("INSERT INTO site_settings (setting_key, setting_value, setting_type) VALUES ('site_name', ?, 'text') ON DUPLICATE KEY UPDATE setting_value = ?");
                $stmt->execute([$siteName, $siteName]);
                
                // Create installed lock file
                file_put_contents('config/installed.lock', date('Y-m-d H:i:s'));
                
                $success[] = 'Installation completed successfully!';
                $step = 4;
            } catch (Exception $e) {
                $errors[] = 'Installation failed: ' . $e->getMessage();
            }
        }
    }
}

if ($step == 1) {
    session_start();
}
?>
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Echhapa CMS Installation</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-dark">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-8 col-lg-6">
                <div class="card mt-5 shadow">
                    <div class="card-header text-center py-4">
                        <h2 class="fw-bold mb-0">Echhapa CMS</h2>
                        <p class="text-muted mb-0">Installation Wizard</p>
                    </div>
                    <div class="card-body p-5">
                        <!-- Progress Bar -->
                        <div class="progress mb-4">
                            <div class="progress-bar" style="width: <?php echo ($step / 4) * 100; ?>%"></div>
                        </div>
                        
                        <?php foreach ($errors as $error): ?>
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle me-2"></i><?php echo htmlspecialchars($error); ?>
                        </div>
                        <?php endforeach; ?>
                        
                        <?php foreach ($success as $message): ?>
                        <div class="alert alert-success">
                            <i class="fas fa-check-circle me-2"></i><?php echo htmlspecialchars($message); ?>
                        </div>
                        <?php endforeach; ?>
                        
                        <?php if ($step == 1): ?>
                        <!-- Step 1: Welcome -->
                        <div class="text-center mb-4">
                            <i class="fas fa-rocket fa-3x text-primary mb-3"></i>
                            <h4>Welcome to Echhapa CMS</h4>
                            <p class="text-muted">This installer will help you set up your news portal in just a few steps.</p>
                        </div>
                        
                        <div class="mb-4">
                            <h6>System Requirements Check:</h6>
                            <ul class="list-group">
                                <li class="list-group-item d-flex justify-content-between">
                                    PHP Version (>= 7.4)
                                    <?php if (version_compare(PHP_VERSION, '7.4.0', '>=')): ?>
                                    <span class="text-success"><i class="fas fa-check"></i> <?php echo PHP_VERSION; ?></span>
                                    <?php else: ?>
                                    <span class="text-danger"><i class="fas fa-times"></i> <?php echo PHP_VERSION; ?></span>
                                    <?php endif; ?>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    PDO Extension
                                    <?php if (extension_loaded('pdo')): ?>
                                    <span class="text-success"><i class="fas fa-check"></i> Enabled</span>
                                    <?php else: ?>
                                    <span class="text-danger"><i class="fas fa-times"></i> Not Found</span>
                                    <?php endif; ?>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    MySQL Extension
                                    <?php if (extension_loaded('pdo_mysql')): ?>
                                    <span class="text-success"><i class="fas fa-check"></i> Enabled</span>
                                    <?php else: ?>
                                    <span class="text-danger"><i class="fas fa-times"></i> Not Found</span>
                                    <?php endif; ?>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    Uploads Directory
                                    <?php if (is_writable('uploads') || mkdir('uploads', 0777, true)): ?>
                                    <span class="text-success"><i class="fas fa-check"></i> Writable</span>
                                    <?php else: ?>
                                    <span class="text-danger"><i class="fas fa-times"></i> Not Writable</span>
                                    <?php endif; ?>
                                </li>
                            </ul>
                        </div>
                        
                        <div class="d-grid">
                            <a href="?step=2" class="btn btn-primary btn-lg">
                                <i class="fas fa-arrow-right me-2"></i>Continue to Database Setup
                            </a>
                        </div>
                        
                        <?php elseif ($step == 2): ?>
                        <!-- Step 2: Database Configuration -->
                        <div class="text-center mb-4">
                            <i class="fas fa-database fa-3x text-primary mb-3"></i>
                            <h4>Database Configuration</h4>
                            <p class="text-muted">Please provide your database connection details.</p>
                        </div>
                        
                        <form method="POST">
                            <div class="mb-3">
                                <label class="form-label">Database Host</label>
                                <input type="text" class="form-control" name="db_host" value="localhost" required>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Database Name</label>
                                <input type="text" class="form-control" name="db_name" value="echhapa_cms" required>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Database Username</label>
                                <input type="text" class="form-control" name="db_user" value="root" required>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Database Password</label>
                                <input type="password" class="form-control" name="db_pass">
                            </div>
                            
                            <div class="d-grid gap-2">
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-check me-2"></i>Test Database Connection
                                </button>
                                <a href="?step=1" class="btn btn-outline-secondary">
                                    <i class="fas fa-arrow-left me-2"></i>Back
                                </a>
                            </div>
                        </form>
                        
                        <?php elseif ($step == 3): ?>
                        <!-- Step 3: Admin User Creation -->
                        <div class="text-center mb-4">
                            <i class="fas fa-user-shield fa-3x text-primary mb-3"></i>
                            <h4>Admin Account Setup</h4>
                            <p class="text-muted">Create your administrator account and configure basic site settings.</p>
                        </div>
                        
                        <form method="POST">
                            <div class="mb-3">
                                <label class="form-label">Site Name</label>
                                <input type="text" class="form-control" name="site_name" value="Echhapa News" required>
                            </div>
                            
                            <hr>
                            
                            <div class="mb-3">
                                <label class="form-label">Admin Username</label>
                                <input type="text" class="form-control" name="admin_user" required>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Admin Email</label>
                                <input type="email" class="form-control" name="admin_email" required>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Admin Password</label>
                                <input type="password" class="form-control" name="admin_pass" required minlength="6">
                                <div class="form-text">Minimum 6 characters required.</div>
                            </div>
                            
                            <div class="d-grid gap-2">
                                <button type="submit" class="btn btn-success">
                                    <i class="fas fa-rocket me-2"></i>Complete Installation
                                </button>
                                <a href="?step=2" class="btn btn-outline-secondary">
                                    <i class="fas fa-arrow-left me-2"></i>Back
                                </a>
                            </div>
                        </form>
                        
                        <?php elseif ($step == 4): ?>
                        <!-- Step 4: Installation Complete -->
                        <div class="text-center">
                            <i class="fas fa-check-circle fa-4x text-success mb-4"></i>
                            <h4 class="text-success mb-3">Installation Complete!</h4>
                            <p class="text-muted mb-4">Echhapa CMS has been successfully installed and configured.</p>
                            
                            <div class="alert alert-warning">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                <strong>Important:</strong> For security reasons, please delete this installation file (install.php) from your server.
                            </div>
                            
                            <div class="d-grid gap-2">
                                <a href="/admin/" class="btn btn-primary btn-lg">
                                    <i class="fas fa-tachometer-alt me-2"></i>Go to Admin Dashboard
                                </a>
                                <a href="/" class="btn btn-outline-secondary">
                                    <i class="fas fa-eye me-2"></i>View Website
                                </a>
                            </div>
                        </div>
                        <?php endif; ?>
                        
                    </div>
                    <div class="card-footer text-center text-muted">
                        <small>Echhapa CMS v1.0 - Powered by PHP & MySQL</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
