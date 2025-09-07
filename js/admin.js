// Admin Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeAdminComponents();
    initializeFileUpload();
    initializeTinyMCE();
    initializeFormValidation();
    initializeDataTables();
    initializeTooltips();
});

// Initialize all admin components
function initializeAdminComponents() {
    // Auto-hide alerts after 5 seconds
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// File upload functionality
function initializeFileUpload() {
    const uploadAreas = document.querySelectorAll('.upload-area');
    
    uploadAreas.forEach(area => {
        const fileInput = area.querySelector('input[type="file"]');
        const dropZone = area.querySelector('.drop-zone');
        
        if (!fileInput || !dropZone) return;
        
        // Drag and drop handlers
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });
        
        dropZone.addEventListener('drop', handleDrop, false);
        dropZone.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', handleFileSelect);
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        function highlight() {
            dropZone.classList.add('dragover');
        }
        
        function unhighlight() {
            dropZone.classList.remove('dragover');
        }
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files);
        }
        
        function handleFileSelect(e) {
            const files = e.target.files;
            handleFiles(files);
        }
        
        function handleFiles(files) {
            ([...files]).forEach(uploadFile);
        }
        
        function uploadFile(file) {
            const formData = new FormData();
            formData.append('file', file);
            
            // Create progress bar
            const progressContainer = document.createElement('div');
            progressContainer.className = 'upload-progress mb-3';
            progressContainer.innerHTML = `
                <div class="d-flex justify-content-between mb-1">
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${formatFileSize(file.size)}</span>
                </div>
                <div class="progress">
                    <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                </div>
            `;
            
            area.appendChild(progressContainer);
            const progressBar = progressContainer.querySelector('.progress-bar');
            
            // Upload file
            fetch('/api/upload.php', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                progressBar.style.width = '100%';
                progressBar.classList.add('bg-success');
                
                if (data.success) {
                    setTimeout(() => {
                        progressContainer.innerHTML = `
                            <div class="alert alert-success">
                                <i class="fas fa-check me-2"></i>
                                File uploaded successfully: ${data.filename}
                            </div>
                        `;
                    }, 500);
                } else {
                    progressBar.classList.remove('bg-success');
                    progressBar.classList.add('bg-danger');
                    progressContainer.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Upload failed: ${data.error}
                        </div>
                    `;
                }
            })
            .catch(error => {
                progressBar.classList.add('bg-danger');
                progressContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Upload failed: ${error.message}
                    </div>
                `;
            });
        }
    });
}

// Initialize TinyMCE editor
function initializeTinyMCE() {
    if (typeof tinymce !== 'undefined') {
        tinymce.init({
            selector: '.rich-editor',
            height: 400,
            menubar: false,
            plugins: [
                'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
                'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
                'insertdatetime', 'media', 'table', 'help', 'wordcount'
            ],
            toolbar: 'undo redo | blocks | ' +
                'bold italic backcolor | alignleft aligncenter ' +
                'alignright alignjustify | bullist numlist outdent indent | ' +
                'removeformat | help',
            content_style: 'body { font-family: -apple-system, BlinkMacSystemFont, San Francisco, Segoe UI, Roboto, Helvetica Neue, sans-serif; font-size: 14px; }',
            setup: function(editor) {
                editor.on('change', function() {
                    editor.save();
                });
            }
        });
    }
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Real-time slug generation
    const titleInput = document.querySelector('#article-title');
    const slugInput = document.querySelector('#article-slug');
    
    if (titleInput && slugInput) {
        titleInput.addEventListener('input', function() {
            const slug = generateSlug(this.value);
            slugInput.value = slug;
        });
    }
}

// Initialize DataTables
function initializeDataTables() {
    const tables = document.querySelectorAll('.data-table');
    
    tables.forEach(table => {
        if (typeof $ !== 'undefined' && $.fn.DataTable) {
            $(table).DataTable({
                responsive: true,
                pageLength: 25,
                language: {
                    search: "_INPUT_",
                    searchPlaceholder: "Search..."
                }
            });
        }
    });
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Article status management
function updateArticleStatus(articleId, status) {
    fetch('/api/article-status.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            article_id: articleId,
            status: status
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Article status updated successfully!', 'success');
            // Refresh the page or update the UI
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('Failed to update article status: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        showNotification('Error updating article status: ' + error.message, 'danger');
    });
}

// Schedule article publication
function scheduleArticle(articleId, publishDate) {
    fetch('/api/schedule-article.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            article_id: articleId,
            publish_date: publishDate
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Article scheduled successfully!', 'success');
        } else {
            showNotification('Failed to schedule article: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        showNotification('Error scheduling article: ' + error.message, 'danger');
    });
}

// Delete confirmation
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

// Utility functions
function generateSlug(text) {
    return text
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .trim();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Auto-save functionality for forms
function initializeAutoSave() {
    const autoSaveForms = document.querySelectorAll('[data-autosave]');
    
    autoSaveForms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        let autoSaveTimeout;
        
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                clearTimeout(autoSaveTimeout);
                autoSaveTimeout = setTimeout(() => {
                    autoSaveForm(form);
                }, 2000);
            });
        });
    });
}

function autoSaveForm(form) {
    const formData = new FormData(form);
    formData.append('auto_save', '1');
    
    fetch(form.action || window.location.href, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const saveIndicator = document.querySelector('.auto-save-indicator');
            if (saveIndicator) {
                saveIndicator.textContent = 'Draft saved';
                saveIndicator.classList.remove('text-danger');
                saveIndicator.classList.add('text-success');
            }
        }
    })
    .catch(error => {
        console.error('Auto-save failed:', error);
    });
}

// Initialize auto-save
initializeAutoSave();

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+S to save
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        const saveButton = document.querySelector('button[type="submit"]');
        if (saveButton) {
            saveButton.click();
        }
    }
    
    // Ctrl+P to preview
    if (e.ctrlKey && e.key === 'p') {
        e.preventDefault();
        const previewButton = document.querySelector('.preview-button');
        if (previewButton) {
            previewButton.click();
        }
    }
});

// Initialize advanced features on page load
window.addEventListener('load', function() {
    initializeCharts();
    initializeAdvancedComponents();
});

function initializeCharts() {
    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        const chartElements = document.querySelectorAll('.chart');
        chartElements.forEach(element => {
            // Chart initialization would go here
        });
    }
}

function initializeAdvancedComponents() {
    // Initialize any advanced components
    console.log('Advanced admin components initialized');
}
