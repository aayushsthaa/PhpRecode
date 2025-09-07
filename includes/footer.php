    <!-- Footer -->
    <footer class="bg-dark text-light py-5 mt-5">
        <div class="container">
            <div class="row">
                <div class="col-lg-4 mb-4">
                    <h5 class="fw-bold"><?php echo getSetting('site_name', 'Echhapa News'); ?></h5>
                    <p class="text-muted"><?php echo getSetting('site_description', 'Your trusted source for news and information'); ?></p>
                    <div class="social-links">
                        <?php if (getSetting('social_facebook')): ?>
                        <a href="<?php echo getSetting('social_facebook'); ?>" class="text-light me-3"><i class="fab fa-facebook-f"></i></a>
                        <?php endif; ?>
                        <?php if (getSetting('social_twitter')): ?>
                        <a href="<?php echo getSetting('social_twitter'); ?>" class="text-light me-3"><i class="fab fa-twitter"></i></a>
                        <?php endif; ?>
                        <?php if (getSetting('social_instagram')): ?>
                        <a href="<?php echo getSetting('social_instagram'); ?>" class="text-light me-3"><i class="fab fa-instagram"></i></a>
                        <?php endif; ?>
                    </div>
                </div>
                <div class="col-lg-2 mb-4">
                    <h6 class="fw-bold">Categories</h6>
                    <ul class="list-unstyled">
                        <?php
                        $categories = getCategories();
                        foreach (array_slice($categories, 0, 5) as $category):
                        ?>
                        <li><a href="/category.php?slug=<?php echo $category['slug']; ?>" class="text-muted text-decoration-none"><?php echo $category['name']; ?></a></li>
                        <?php endforeach; ?>
                    </ul>
                </div>
                <div class="col-lg-3 mb-4">
                    <h6 class="fw-bold">Quick Links</h6>
                    <ul class="list-unstyled">
                        <li><a href="/about.php" class="text-muted text-decoration-none">About Us</a></li>
                        <li><a href="/contact.php" class="text-muted text-decoration-none">Contact</a></li>
                        <li><a href="/privacy.php" class="text-muted text-decoration-none">Privacy Policy</a></li>
                        <li><a href="/terms.php" class="text-muted text-decoration-none">Terms of Service</a></li>
                        <li><a href="/admin/" class="text-muted text-decoration-none">Admin Login</a></li>
                    </ul>
                </div>
                <div class="col-lg-3 mb-4">
                    <h6 class="fw-bold">Contact Info</h6>
                    <p class="text-muted mb-2"><i class="fas fa-envelope me-2"></i><?php echo getSetting('contact_email', 'contact@echhapa.com'); ?></p>
                    <p class="text-muted mb-2"><i class="fas fa-phone me-2"></i>+1 (555) 123-4567</p>
                    <p class="text-muted"><i class="fas fa-map-marker-alt me-2"></i>123 News Street, Media City</p>
                </div>
            </div>
            <hr class="my-4">
            <div class="row align-items-center">
                <div class="col-md-6">
                    <p class="text-muted mb-0">&copy; <?php echo date('Y'); ?> <?php echo getSetting('site_name', 'Echhapa News'); ?>. All rights reserved.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <p class="text-muted mb-0">Powered by Echhapa CMS</p>
                </div>
            </div>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Custom JS -->
    <script src="/js/script.js"></script>
    
    <?php echo getSetting('footer_code', ''); ?>
    <?php echo getSetting('analytics_code', ''); ?>
</body>
</html>
