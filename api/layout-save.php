<?php
require_once '../config/config.php';
requireAuth();
if (!hasPermission('editor')) {
    die(json_encode(['success' => false, 'error' => 'Insufficient permissions']));
}

header('Content-Type: application/json');

try {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!$input) {
        throw new Exception('Invalid JSON data');
    }
    
    $action = $input['action'] ?? '';
    
    switch ($action) {
        case 'update_section_order':
            $order = $input['order'] ?? [];
            foreach ($order as $item) {
                $stmt = $pdo->prepare("UPDATE homepage_sections SET sort_order = ? WHERE id = ?");
                $stmt->execute([$item['order'], $item['id']]);
            }
            echo json_encode(['success' => true, 'message' => 'Section order updated']);
            break;
            
        case 'assign_article':
            $articleId = intval($input['article_id']);
            $sectionId = intval($input['section_id']);
            
            // Remove existing assignment
            $stmt = $pdo->prepare("DELETE FROM section_articles WHERE article_id = ?");
            $stmt->execute([$articleId]);
            
            // Add new assignment
            $stmt = $pdo->prepare("INSERT INTO section_articles (section_id, article_id, position) VALUES (?, ?, 0)");
            $stmt->execute([$sectionId, $articleId]);
            
            echo json_encode(['success' => true, 'message' => 'Article assigned']);
            break;
            
        case 'toggle_section':
            $sectionId = intval($input['section_id']);
            $isActive = $input['is_active'] ? 1 : 0;
            
            $stmt = $pdo->prepare("UPDATE homepage_sections SET is_active = ? WHERE id = ?");
            $stmt->execute([$isActive, $sectionId]);
            
            echo json_encode(['success' => true, 'message' => 'Section status updated']);
            break;
            
        case 'delete_section':
            $sectionId = intval($input['section_id']);
            
            // Delete section and its assignments
            $stmt = $pdo->prepare("DELETE FROM section_articles WHERE section_id = ?");
            $stmt->execute([$sectionId]);
            
            $stmt = $pdo->prepare("DELETE FROM homepage_sections WHERE id = ?");
            $stmt->execute([$sectionId]);
            
            echo json_encode(['success' => true, 'message' => 'Section deleted']);
            break;
            
        case 'toggle_featured':
            $articleId = intval($input['article_id']);
            $sectionId = intval($input['section_id']);
            $isFeatured = $input['is_featured'] ? 1 : 0;
            
            $stmt = $pdo->prepare("UPDATE section_articles SET is_featured = ? WHERE article_id = ? AND section_id = ?");
            $stmt->execute([$isFeatured, $articleId, $sectionId]);
            
            echo json_encode(['success' => true, 'message' => 'Featured status updated']);
            break;
            
        default:
            throw new Exception('Invalid action');
    }
    
} catch (Exception $e) {
    http_response_code(400);
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage()
    ]);
}
?>
