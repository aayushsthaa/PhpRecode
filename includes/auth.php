<?php
// Authentication functions

function login($username, $password) {
    global $pdo;
    
    $stmt = $pdo->prepare("SELECT * FROM users WHERE username = ? OR email = ?");
    $stmt->execute([$username, $username]);
    $user = $stmt->fetch();
    
    if ($user && password_verify($password, $user['password_hash'])) {
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['role'] = $user['role'];
        return true;
    }
    
    return false;
}

function logout() {
    session_destroy();
    header('Location: /admin/login.php');
    exit;
}

function register($username, $email, $password, $role = 'author') {
    global $pdo;
    
    // Check if username or email already exists
    $stmt = $pdo->prepare("SELECT COUNT(*) FROM users WHERE username = ? OR email = ?");
    $stmt->execute([$username, $email]);
    
    if ($stmt->fetchColumn() > 0) {
        return false;
    }
    
    $passwordHash = password_hash($password, PASSWORD_DEFAULT);
    
    $stmt = $pdo->prepare("INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)");
    return $stmt->execute([$username, $email, $passwordHash, $role]);
}
?>
