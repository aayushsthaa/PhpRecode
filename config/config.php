<?php
// Application configuration
session_start();

// Site configuration
define('SITE_URL', $_ENV['SITE_URL'] ?? 'http://localhost:5000');
define('UPLOAD_DIR', 'uploads/');
define('MAX_FILE_SIZE', 10 * 1024 * 1024); // 10MB
define('ALLOWED_FILE_TYPES', ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx']);

// Include database connection
require_once 'database.php';

// Include helper functions
require_once dirname(__DIR__) . '/includes/functions.php';

// Include authentication functions
require_once dirname(__DIR__) . '/includes/auth.php';

// Set timezone
date_default_timezone_set('UTC');

// Error reporting (disable in production)
error_reporting(E_ALL);
ini_set('display_errors', 1);
?>
