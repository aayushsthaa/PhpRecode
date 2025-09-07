<nav id="sidebarMenu" class="col-md-3 col-lg-2 d-md-block bg-dark sidebar collapse">
    <div class="position-sticky pt-3">
        <div class="text-center mb-4">
            <h4 class="text-light">Echhapa CMS</h4>
            <small class="text-muted">Admin Dashboard</small>
        </div>
        
        <ul class="nav flex-column">
            <li class="nav-item">
                <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'dashboard.php' ? 'active' : ''; ?>" href="<?php echo adminUrl('dashboard.php'); ?>">
                    <i class="fas fa-tachometer-alt me-2"></i>Dashboard
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'articles.php' ? 'active' : ''; ?>" href="<?php echo adminUrl('articles.php'); ?>">
                    <i class="fas fa-newspaper me-2"></i>Articles
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'layouts.php' ? 'active' : ''; ?>" href="<?php echo adminUrl('layouts.php'); ?>">
                    <i class="fas fa-th-large me-2"></i>Layout Management
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'categories.php' ? 'active' : ''; ?>" href="<?php echo adminUrl('categories.php'); ?>">
                    <i class="fas fa-tags me-2"></i>Categories
                </a>
            </li>
            <?php if (hasPermission('admin')): ?>
            <li class="nav-item">
                <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'users.php' ? 'active' : ''; ?>" href="<?php echo adminUrl('users.php'); ?>">
                    <i class="fas fa-users me-2"></i>Users
                </a>
            </li>
            <?php endif; ?>
            <li class="nav-item">
                <a class="nav-link" href="#" data-bs-toggle="collapse" data-bs-target="#mediaSubmenu">
                    <i class="fas fa-images me-2"></i>Media
                    <i class="fas fa-chevron-down ms-auto"></i>
                </a>
                <div class="collapse" id="mediaSubmenu">
                    <ul class="nav flex-column ms-3">
                        <li class="nav-item">
                            <a class="nav-link text-muted" href="<?php echo adminUrl('media.php'); ?>">
                                <i class="fas fa-folder me-2"></i>Media Library
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link text-muted" href="<?php echo adminUrl('upload.php'); ?>">
                                <i class="fas fa-upload me-2"></i>Upload Files
                            </a>
                        </li>
                    </ul>
                </div>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="#" data-bs-toggle="collapse" data-bs-target="#appearanceSubmenu">
                    <i class="fas fa-paint-brush me-2"></i>Appearance
                    <i class="fas fa-chevron-down ms-auto"></i>
                </a>
                <div class="collapse" id="appearanceSubmenu">
                    <ul class="nav flex-column ms-3">
                        <li class="nav-item">
                            <a class="nav-link text-muted" href="<?php echo adminUrl('homepage.php'); ?>">
                                <i class="fas fa-home me-2"></i>Homepage
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link text-muted" href="<?php echo adminUrl('sidebar.php'); ?>">
                                <i class="fas fa-columns me-2"></i>Sidebar
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link text-muted" href="<?php echo adminUrl('menus.php'); ?>">
                                <i class="fas fa-bars me-2"></i>Menus
                            </a>
                        </li>
                    </ul>
                </div>
            </li>
            <?php if (hasPermission('admin')): ?>
            <li class="nav-item">
                <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'settings.php' ? 'active' : ''; ?>" href="/admin/settings.php">
                    <i class="fas fa-cog me-2"></i>Settings
                </a>
            </li>
            <?php endif; ?>
        </ul>
        
        <hr class="my-3">
        
        <ul class="nav flex-column">
            <li class="nav-item">
                <a class="nav-link text-muted" href="/" target="_blank">
                    <i class="fas fa-external-link-alt me-2"></i>View Website
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link text-muted" href="/admin/logout.php">
                    <i class="fas fa-sign-out-alt me-2"></i>Logout
                </a>
            </li>
        </ul>
    </div>
</nav>
