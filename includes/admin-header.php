<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo isset($pageTitle) ? $pageTitle . ' - ' : ''; ?>Admin Dashboard - <?php echo getSetting('site_name', 'Echhapa News'); ?></title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <!-- SortableJS for drag and drop -->
    <script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>
    <!-- TinyMCE for rich text editing -->
    <script src="https://cdn.tiny.cloud/1/no-api-key/tinymce/6/tinymce.min.js" referrerpolicy="origin"></script>
    <!-- Custom Admin CSS -->
    <link href="<?php echo asset('css/admin.css'); ?>" rel="stylesheet">
</head>
<body>
    <?php include 'admin-sidebar.php'; ?>
    
    <div class="main-content">
        <!-- Top Header -->
        <header class="content-header">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1><?php echo isset($pageTitle) ? $pageTitle : 'Dashboard'; ?></h1>
                    <nav aria-label="breadcrumb">
                        <ol class="breadcrumb">
                            <li class="breadcrumb-item"><a href="<?php echo adminUrl('dashboard.php'); ?>">Home</a></li>
                            <?php if(isset($pageTitle) && $pageTitle != 'Dashboard'): ?>
                            <li class="breadcrumb-item active"><?php echo $pageTitle; ?></li>
                            <?php endif; ?>
                        </ol>
                    </nav>
                </div>
                <div class="d-flex align-items-center gap-3">
                    <a href="<?php echo url(); ?>" class="btn btn-outline-primary btn-sm" target="_blank">
                        <i class="fas fa-external-link-alt me-1"></i>View Site
                    </a>
                    <div class="dropdown">
                        <button class="btn btn-outline-secondary btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown">
                            <i class="fas fa-user-circle me-1"></i><?php echo $_SESSION['username']; ?>
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><a class="dropdown-item" href="<?php echo adminUrl('profile.php'); ?>"><i class="fas fa-user-edit me-2"></i>Profile</a></li>
                            <li><a class="dropdown-item" href="<?php echo adminUrl('settings.php'); ?>"><i class="fas fa-cog me-2"></i>Settings</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="<?php echo adminUrl('logout.php'); ?>"><i class="fas fa-sign-out-alt me-2"></i>Logout</a></li>
                        </ul>
                    </div>
                    <button class="btn btn-outline-secondary btn-sm d-md-none" id="sidebar-toggle">
                        <i class="fas fa-bars"></i>
                    </button>
                </div>
            </div>
        </header>
        
        <div class="content-body">
