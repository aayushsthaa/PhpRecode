<?php
require_once '../config/config.php';
requireAuth();

header('Content-Type: application/json');

try {
    if (!isset($_FILES['file'])) {
        throw new Exception('No file uploaded');
    }
    
    $file = $_FILES['file'];
    $uploadPath = uploadFile($file);
    
    if (!$uploadPath) {
        throw new Exception('File upload failed');
    }
    
    // Store file info in database
    $stmt = $pdo->prepare("INSERT INTO media (filename, original_name, file_path, file_type, file_size, uploaded_by) VALUES (?, ?, ?, ?, ?, ?)");
    $stmt->execute([
        basename($uploadPath),
        $file['name'],
        $uploadPath,
        $file['type'],
        $file['size'],
        $_SESSION['user_id']
    ]);
    
    $fileId = $pdo->lastInsertId();
    
    echo json_encode([
        'success' => true,
        'file_id' => $fileId,
        'filename' => basename($uploadPath),
        'file_path' => $uploadPath,
        'file_url' => '/' . $uploadPath
    ]);
    
} catch (Exception $e) {
    http_response_code(400);
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage()
    ]);
}
?>
