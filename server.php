<?php
// Simple PHP development server
// This file serves as the entry point for the PHP application

// Set the document root to current directory
$documentRoot = __DIR__;

// Get the requested URI
$requestUri = $_SERVER['REQUEST_URI'];
$requestMethod = $_SERVER['REQUEST_METHOD'];

// Parse the URL
$parsedUrl = parse_url($requestUri);
$path = $parsedUrl['path'];

// Remove query string from path
$path = strtok($path, '?');

// If it's a file request (CSS, JS, images), serve it directly
if ($path !== '/' && file_exists($documentRoot . $path)) {
    $extension = pathinfo($path, PATHINFO_EXTENSION);
    
    // Set appropriate content type
    $contentTypes = [
        'css' => 'text/css',
        'js' => 'application/javascript',
        'png' => 'image/png',
        'jpg' => 'image/jpeg',
        'jpeg' => 'image/jpeg',
        'gif' => 'image/gif',
        'svg' => 'image/svg+xml',
        'ico' => 'image/x-icon',
        'woff' => 'font/woff',
        'woff2' => 'font/woff2',
        'ttf' => 'font/ttf',
        'eot' => 'application/vnd.ms-fontobject'
    ];
    
    if (isset($contentTypes[$extension])) {
        header('Content-Type: ' . $contentTypes[$extension]);
    }
    
    readfile($documentRoot . $path);
    return;
}

// Route to appropriate PHP file
$route = $path;

// Handle admin routes
if (strpos($route, '/admin') === 0) {
    $adminPath = substr($route, 6); // Remove '/admin'
    
    if ($adminPath === '' || $adminPath === '/') {
        $route = '/admin/index.php';
    } elseif (file_exists($documentRoot . '/admin' . $adminPath . '.php')) {
        $route = '/admin' . $adminPath . '.php';
    } elseif (file_exists($documentRoot . '/admin' . $adminPath)) {
        $route = '/admin' . $adminPath;
    } else {
        $route = '/admin/index.php';
    }
}

// Handle API routes
elseif (strpos($route, '/api') === 0) {
    $apiPath = substr($route, 4); // Remove '/api'
    
    if ($apiPath === '' || $apiPath === '/') {
        http_response_code(404);
        echo json_encode(['error' => 'API endpoint not found']);
        return;
    } elseif (file_exists($documentRoot . '/api' . $apiPath . '.php')) {
        $route = '/api' . $apiPath . '.php';
    } elseif (file_exists($documentRoot . '/api' . $apiPath)) {
        $route = '/api' . $apiPath;
    } else {
        http_response_code(404);
        echo json_encode(['error' => 'API endpoint not found']);
        return;
    }
}

// Handle other routes
else {
    if ($route === '/' || $route === '') {
        $route = '/index.php';
    } elseif (file_exists($documentRoot . $route . '.php')) {
        $route = $route . '.php';
    } elseif (!file_exists($documentRoot . $route)) {
        // Check if it's an article or category slug
        if (preg_match('/^\/article\/([^\/]+)$/', $route, $matches)) {
            $_GET['slug'] = $matches[1];
            $route = '/article.php';
        } elseif (preg_match('/^\/category\/([^\/]+)$/', $route, $matches)) {
            $_GET['slug'] = $matches[1];
            $route = '/category.php';
        } else {
            http_response_code(404);
            echo "404 - Page not found";
            return;
        }
    }
}

// Include the appropriate PHP file
$file = $documentRoot . $route;

if (file_exists($file)) {
    include $file;
} else {
    http_response_code(404);
    echo "404 - Page not found";
}
?>