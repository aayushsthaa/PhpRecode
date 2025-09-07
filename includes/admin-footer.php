        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Custom Admin JS -->
    <script src="<?php echo asset('js/admin.js'); ?>"></script>
    <!-- Layout Manager JS -->
    <script src="<?php echo asset('js/layout-manager.js'); ?>"></script>
    
    <script>
    // Sidebar toggle for mobile
    document.getElementById('sidebar-toggle')?.addEventListener('click', function() {
        document.querySelector('.sidebar').classList.toggle('show');
    });
    
    // Auto-hide mobile sidebar when clicking outside
    document.addEventListener('click', function(e) {
        const sidebar = document.querySelector('.sidebar');
        const toggle = document.getElementById('sidebar-toggle');
        if (window.innerWidth <= 768 && !sidebar.contains(e.target) && e.target !== toggle) {
            sidebar.classList.remove('show');
        }
    });
    </script>
</body>
</html>
