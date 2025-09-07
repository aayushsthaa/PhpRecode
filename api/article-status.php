<?php
require_once '../config/config.php';
requireAuth();

header('Content-Type: application/json');

try {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!$input || !isset($input['article_id']) || !isset($input['status'])) {
        throw new Exception('Missing required parameters');
    }
    
    $articleId = intval($input['article_id']);
    $status = sanitize($input['status']);
    
    // Validate status
    $validStatuses = ['draft', 'published', 'scheduled'];
    if (!in_array($status, $validStatuses)) {
        throw new Exception('Invalid status');
    }
    
    // Check if user has permission to edit this article
    $stmt = $pdo->prepare("SELECT author_id FROM articles WHERE id = ?");
    $stmt->execute([$articleId]);
    $article = $stmt->fetch();
    
    if (!$article) {
        throw new Exception('Article not found');
    }
    
    // Check permissions
    if ($article['author_id'] != $_SESSION['user_id'] && !hasPermission('editor')) {
        throw new Exception('Insufficient permissions');
    }
    
    $publishedAt = null;
    if ($status === 'published') {
        $publishedAt = date('Y-m-d H:i:s');
    } elseif ($status === 'scheduled' && isset($input['publish_date'])) {
        $publishedAt = $input['publish_date'];
    }
    
    $stmt = $pdo->prepare("UPDATE articles SET status = ?, published_at = ?, updated_at = NOW() WHERE id = ?");
    $stmt->execute([$status, $publishedAt, $articleId]);
    
    echo json_encode([
        'success' => true,
        'message' => 'Article status updated successfully',
        'status' => $status,
        'published_at' => $publishedAt
    ]);
    
} catch (Exception $e) {
    http_response_code(400);
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage()
    ]);
}
?>
