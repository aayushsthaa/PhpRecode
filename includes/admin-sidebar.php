<aside class="sidebar">
    <!-- Brand Section -->
    <div class="sidebar-brand">
        <h4>Echhapa</h4>
        <small>Content Management</small>
    </div>
    
    <!-- Navigation Menu -->
    <nav class="sidebar-nav">
        <ul class="nav flex-column">
            <!-- Main Dashboard -->
            <li class="nav-item">
                <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'dashboard.php' ? 'active' : ''; ?>" href="<?php echo adminUrl('dashboard.php'); ?>">
                    <i class="fas fa-tachometer-alt"></i>
                    <span>Dashboard</span>
                </a>
            </li>
            
            <!-- Content Management Section -->
            <div class="sidebar-heading">Content</div>
            
            <li class="nav-item">
                <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'articles.php' || basename($_SERVER['PHP_SELF']) == 'article-edit.php' ? 'active' : ''; ?>" href="<?php echo adminUrl('articles.php'); ?>">
                    <i class="fas fa-newspaper"></i>
                    <span>Articles</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'categories.php' ? 'active' : ''; ?>" href="<?php echo adminUrl('categories.php'); ?>">
                    <i class="fas fa-tags"></i>
                    <span>Categories</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'media.php' || basename($_SERVER['PHP_SELF']) == 'upload.php' ? 'active' : ''; ?>" href="<?php echo adminUrl('media.php'); ?>">
                    <i class="fas fa-images"></i>
                    <span>Media Library</span>
                </a>
            </li>
            
            <!-- Website Management Section -->
            <div class="sidebar-heading">Website</div>
            
            <li class="nav-item">
                <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'layouts.php' || basename($_SERVER['PHP_SELF']) == 'homepage.php' ? 'active' : ''; ?>" href="<?php echo adminUrl('layouts.php'); ?>">
                    <i class="fas fa-th-large"></i>
                    <span>Layout Manager</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'menus.php' ? 'active' : ''; ?>" href="<?php echo adminUrl('menus.php'); ?>">
                    <i class="fas fa-bars"></i>
                    <span>Navigation Menus</span>
                </a>
            </li>
            
            <!-- System Management Section -->
            <?php if (hasPermission('admin')): ?>
            <div class="sidebar-heading">System</div>
            
            <li class="nav-item">
                <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'users.php' ? 'active' : ''; ?>" href="<?php echo adminUrl('users.php'); ?>">
                    <i class="fas fa-users"></i>
                    <span>Users</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'settings.php' ? 'active' : ''; ?>" href="<?php echo adminUrl('settings.php'); ?>">
                    <i class="fas fa-cog"></i>
                    <span>Settings</span>
                </a>
            </li>
            
            <li class="nav-item">
                <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'analytics.php' ? 'active' : ''; ?>" href="<?php echo adminUrl('analytics.php'); ?>">
                    <i class="fas fa-chart-bar"></i>
                    <span>Analytics</span>
                </a>
            </li>
            <?php endif; ?>
        </ul>
    </nav>
    
    <!-- Footer Section -->
    <div class="sidebar-footer">
        <div class="d-flex align-items-center p-3 border-top">
            <div class="flex-shrink-0">
                <i class="fas fa-user-circle fa-2x text-muted"></i>
            </div>
            <div class="flex-grow-1 ms-2">
                <div class="fw-semibold text-light small"><?php echo $_SESSION['username']; ?></div>
                <div class="text-muted small">Administrator</div>
            </div>
        </div>
    </div>
</aside>
