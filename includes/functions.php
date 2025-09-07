<?php
// Helper functions

function sanitize($data) {
    return htmlspecialchars(strip_tags($data), ENT_QUOTES, 'UTF-8');
}

function generateSlug($text) {
    $text = strtolower($text);
    $text = preg_replace('/[^a-z0-9\s-]/', '', $text);
    $text = preg_replace('/[\s-]+/', '-', $text);
    return trim($text, '-');
}

function uploadFile($file, $uploadDir = 'uploads/') {
    if (!isset($file['error']) || $file['error'] !== UPLOAD_ERR_OK) {
        return false;
    }
    
    $fileSize = $file['size'];
    $fileName = $file['name'];
    $fileTmpName = $file['tmp_name'];
    $fileType = strtolower(pathinfo($fileName, PATHINFO_EXTENSION));
    
    // Check file size
    if ($fileSize > MAX_FILE_SIZE) {
        return false;
    }
    
    // Check file type
    if (!in_array($fileType, ALLOWED_FILE_TYPES)) {
        return false;
    }
    
    // Generate unique filename
    $newFileName = uniqid() . '.' . $fileType;
    $uploadPath = $uploadDir . $newFileName;
    
    // Create upload directory if it doesn't exist
    if (!file_exists($uploadDir)) {
        mkdir($uploadDir, 0777, true);
    }
    
    // Move uploaded file
    if (move_uploaded_file($fileTmpName, $uploadPath)) {
        return $uploadPath;
    }
    
    return false;
}

function formatDate($date, $format = 'M j, Y') {
    return date($format, strtotime($date));
}

function truncateText($text, $length = 150) {
    if (strlen($text) <= $length) {
        return $text;
    }
    return substr($text, 0, $length) . '...';
}

function getSetting($key, $default = '') {
    global $pdo;
    $stmt = $pdo->prepare("SELECT setting_value FROM site_settings WHERE setting_key = ?");
    $stmt->execute([$key]);
    $result = $stmt->fetch();
    return $result ? $result['setting_value'] : $default;
}

function setSetting($key, $value, $type = 'text') {
    global $pdo;
    $stmt = $pdo->prepare("INSERT INTO site_settings (setting_key, setting_value, setting_type) VALUES (?, ?, ?) ON DUPLICATE KEY UPDATE setting_value = ?, updated_at = NOW()");
    $stmt->execute([$key, $value, $type, $value]);
}

function getArticles($limit = 10, $offset = 0, $status = 'published', $categoryId = null) {
    global $pdo;
    
    $sql = "SELECT a.*, u.username as author_name, c.name as category_name 
            FROM articles a 
            LEFT JOIN users u ON a.author_id = u.id 
            LEFT JOIN categories c ON a.category_id = c.id 
            WHERE a.status = ?";
    
    $params = [$status];
    
    if ($categoryId) {
        $sql .= " AND a.category_id = ?";
        $params[] = $categoryId;
    }
    
    $sql .= " ORDER BY a.published_at DESC, a.created_at DESC LIMIT " . intval($limit) . " OFFSET " . intval($offset);
    
    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);
    return $stmt->fetchAll();
}

function getArticleBySlug($slug) {
    global $pdo;
    $stmt = $pdo->prepare("SELECT a.*, u.username as author_name, c.name as category_name 
                          FROM articles a 
                          LEFT JOIN users u ON a.author_id = u.id 
                          LEFT JOIN categories c ON a.category_id = c.id 
                          WHERE a.slug = ? AND a.status = 'published'");
    $stmt->execute([$slug]);
    return $stmt->fetch();
}

function getCategories() {
    global $pdo;
    $stmt = $pdo->query("SELECT * FROM categories ORDER BY name");
    return $stmt->fetchAll();
}

function getHomepageSections() {
    global $pdo;
    $stmt = $pdo->query("SELECT * FROM homepage_sections WHERE is_active = 1 ORDER BY sort_order");
    return $stmt->fetchAll();
}

function getSectionArticles($sectionId, $limit = null) {
    global $pdo;
    
    $sql = "SELECT a.*, u.username as author_name, c.name as category_name, sa.is_featured, sa.position
            FROM section_articles sa
            JOIN articles a ON sa.article_id = a.id
            LEFT JOIN users u ON a.author_id = u.id
            LEFT JOIN categories c ON a.category_id = c.id
            WHERE sa.section_id = ? AND a.status = 'published'
            ORDER BY sa.is_featured DESC, sa.position ASC, a.published_at DESC";
    
    if ($limit) {
        $sql .= " LIMIT " . intval($limit);
    }
    
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$sectionId]);
    return $stmt->fetchAll();
}

function getSidebarWidgets() {
    global $pdo;
    $stmt = $pdo->query("SELECT * FROM sidebar_widgets WHERE is_active = 1 ORDER BY position");
    return $stmt->fetchAll();
}

function isLoggedIn() {
    return isset($_SESSION['user_id']);
}

function requireAuth() {
    if (!isLoggedIn()) {
        header('Location: /admin/login.php');
        exit;
    }
}

function getCurrentUser() {
    global $pdo;
    if (!isLoggedIn()) {
        return null;
    }
    
    $stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
    $stmt->execute([$_SESSION['user_id']]);
    return $stmt->fetch();
}

function hasPermission($requiredRole = 'author') {
    $user = getCurrentUser();
    if (!$user) return false;
    
    $roles = ['author' => 1, 'editor' => 2, 'admin' => 3];
    $userLevel = $roles[$user['role']] ?? 0;
    $requiredLevel = $roles[$requiredRole] ?? 0;
    
    return $userLevel >= $requiredLevel;
}
?>
