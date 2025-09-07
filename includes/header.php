<!DOCTYPE html>
<html lang="en" data-bs-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo isset($pageTitle) ? $pageTitle . ' - ' : ''; ?><?php echo getSetting('site_name', 'Echhapa News'); ?></title>
    <meta name="description" content="<?php echo getSetting('site_description', 'Your trusted source for news and information'); ?>">
    <meta name="keywords" content="<?php echo getSetting('site_keywords', 'news, breaking news, world news, politics, business'); ?>">
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <!-- Custom CSS -->
    <link href="/css/style.css" rel="stylesheet">
    
    <?php echo getSetting('header_code', ''); ?>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom">
        <div class="container">
            <a class="navbar-brand fw-bold fs-2" href="/"><?php echo getSetting('site_name', 'Echhapa News'); ?></a>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <?php
                    $categories = getCategories();
                    foreach (array_slice($categories, 0, 6) as $category):
                    ?>
                    <li class="nav-item">
                        <a class="nav-link" href="/category.php?slug=<?php echo $category['slug']; ?>"><?php echo $category['name']; ?></a>
                    </li>
                    <?php endforeach; ?>
                    <li class="nav-item">
                        <a class="nav-link" href="/contact.php">Contact</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    
    <!-- Breaking News Bar -->
    <div class="bg-danger text-white py-2">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-auto">
                    <strong><i class="fas fa-bolt me-2"></i>BREAKING NEWS</strong>
                </div>
                <div class="col">
                    <marquee class="mb-0">Latest breaking news updates will appear here...</marquee>
                </div>
            </div>
        </div>
    </div>
