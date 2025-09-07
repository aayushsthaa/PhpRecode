// Layout Management JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeLayoutManager();
    initializeSectionSorting();
    initializeArticleDragDrop();
    initializeLayoutPreview();
});

// Main layout manager initialization
function initializeLayoutManager() {
    const layoutContainer = document.querySelector('.layout-container');
    if (!layoutContainer) return;
    
    // Initialize sortable sections
    if (typeof Sortable !== 'undefined') {
        new Sortable(layoutContainer, {
            handle: '.drag-handle',
            animation: 150,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            onEnd: function(evt) {
                updateSectionOrder();
            }
        });
    }
    
    // Add section controls
    addSectionControls();
    
    // Initialize section editing
    initializeSectionEditing();
}

// Initialize section sorting
function initializeSectionSorting() {
    const sectionsList = document.querySelector('.sections-list');
    if (!sectionsList) return;
    
    if (typeof Sortable !== 'undefined') {
        new Sortable(sectionsList, {
            handle: '.section-drag-handle',
            animation: 150,
            ghostClass: 'section-ghost',
            onEnd: function(evt) {
                updateHomepageSectionOrder();
            }
        });
    }
}

// Initialize article drag and drop
function initializeArticleDragDrop() {
    const articleLists = document.querySelectorAll('.article-list');
    
    articleLists.forEach(list => {
        if (typeof Sortable !== 'undefined') {
            new Sortable(list, {
                group: 'articles',
                animation: 150,
                ghostClass: 'article-ghost',
                onAdd: function(evt) {
                    handleArticleMove(evt);
                },
                onUpdate: function(evt) {
                    updateArticleOrder(evt.target);
                }
            });
        }
    });
}

// Add controls to each section
function addSectionControls() {
    const sections = document.querySelectorAll('.layout-section');
    
    sections.forEach(section => {
        if (section.querySelector('.section-controls')) return;
        
        const controls = document.createElement('div');
        controls.className = 'section-controls position-absolute top-0 end-0 p-2';
        controls.innerHTML = `
            <div class="btn-group btn-group-sm">
                <button class="btn btn-outline-secondary drag-handle" type="button" title="Drag to reorder">
                    <i class="fas fa-grip-vertical"></i>
                </button>
                <button class="btn btn-outline-primary edit-section" type="button" title="Edit section">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-outline-info preview-section" type="button" title="Preview section">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-outline-danger delete-section" type="button" title="Delete section">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        section.style.position = 'relative';
        section.appendChild(controls);
        
        // Attach event listeners
        controls.querySelector('.edit-section').addEventListener('click', () => editSection(section));
        controls.querySelector('.preview-section').addEventListener('click', () => previewSection(section));
        controls.querySelector('.delete-section').addEventListener('click', () => deleteSection(section));
    });
}

// Initialize section editing
function initializeSectionEditing() {
    // Section settings modal
    const sectionModal = createSectionModal();
    document.body.appendChild(sectionModal);
    
    // Layout type changes
    document.addEventListener('change', function(e) {
        if (e.target.matches('.layout-type-select')) {
            handleLayoutTypeChange(e.target);
        }
    });
}

// Create section editing modal
function createSectionModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'sectionModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Edit Section</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="sectionForm">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Section Name</label>
                                    <input type="text" class="form-control" name="section_name" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Layout Type</label>
                                    <select class="form-select layout-type-select" name="layout_type">
                                        <option value="featured">Featured</option>
                                        <option value="grid">Grid</option>
                                        <option value="list">List</option>
                                        <option value="carousel">Carousel</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Max Articles</label>
                                    <input type="number" class="form-control" name="max_articles" min="1" max="20" value="6">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Category Filter</label>
                                    <select class="form-select" name="category_filter">
                                        <option value="">All Categories</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="is_active" id="sectionActive" checked>
                                <label class="form-check-label" for="sectionActive">
                                    Active (show on homepage)
                                </label>
                            </div>
                        </div>
                        <div id="layoutPreview" class="mt-4">
                            <h6>Layout Preview</h6>
                            <div class="preview-container border rounded p-3"></div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="saveSectionSettings()">Save Changes</button>
                </div>
            </div>
        </div>
    `;
    
    return modal;
}

// Edit section function
function editSection(sectionElement) {
    const sectionId = sectionElement.dataset.sectionId;
    const modal = new bootstrap.Modal(document.getElementById('sectionModal'));
    
    // Load section data
    if (sectionId) {
        fetch(`/api/get-section.php?id=${sectionId}`)
            .then(response => response.json())
            .then(data => {
                populateSectionForm(data);
                modal.show();
            })
            .catch(error => {
                console.error('Error loading section data:', error);
                showNotification('Error loading section data', 'danger');
            });
    } else {
        // New section
        resetSectionForm();
        modal.show();
    }
}

// Populate section form with data
function populateSectionForm(data) {
    const form = document.getElementById('sectionForm');
    
    form.querySelector('[name="section_name"]').value = data.name || '';
    form.querySelector('[name="layout_type"]').value = data.layout_type || 'grid';
    form.querySelector('[name="max_articles"]').value = data.max_articles || 6;
    form.querySelector('[name="category_filter"]').value = data.category_filter || '';
    form.querySelector('[name="is_active"]').checked = data.is_active || false;
    
    // Update layout preview
    updateLayoutPreview(data.layout_type);
}

// Reset section form
function resetSectionForm() {
    const form = document.getElementById('sectionForm');
    form.reset();
    updateLayoutPreview('grid');
}

// Handle layout type changes
function handleLayoutTypeChange(select) {
    const layoutType = select.value;
    updateLayoutPreview(layoutType);
}

// Update layout preview
function updateLayoutPreview(layoutType) {
    const previewContainer = document.querySelector('.preview-container');
    if (!previewContainer) return;
    
    let previewHTML = '';
    
    switch (layoutType) {
        case 'featured':
            previewHTML = `
                <div class="row">
                    <div class="col-8">
                        <div class="bg-primary text-white p-3 rounded mb-2">Main Featured Article</div>
                    </div>
                    <div class="col-4">
                        <div class="bg-secondary text-white p-2 rounded mb-1">Side Article 1</div>
                        <div class="bg-secondary text-white p-2 rounded mb-1">Side Article 2</div>
                        <div class="bg-secondary text-white p-2 rounded">Side Article 3</div>
                    </div>
                </div>
            `;
            break;
        case 'grid':
            previewHTML = `
                <div class="row">
                    <div class="col-4 mb-2"><div class="bg-info text-white p-3 rounded">Article 1</div></div>
                    <div class="col-4 mb-2"><div class="bg-info text-white p-3 rounded">Article 2</div></div>
                    <div class="col-4 mb-2"><div class="bg-info text-white p-3 rounded">Article 3</div></div>
                    <div class="col-4"><div class="bg-info text-white p-3 rounded">Article 4</div></div>
                    <div class="col-4"><div class="bg-info text-white p-3 rounded">Article 5</div></div>
                    <div class="col-4"><div class="bg-info text-white p-3 rounded">Article 6</div></div>
                </div>
            `;
            break;
        case 'list':
            previewHTML = `
                <div class="bg-success text-white p-2 rounded mb-1">Article 1 - List Style</div>
                <div class="bg-success text-white p-2 rounded mb-1">Article 2 - List Style</div>
                <div class="bg-success text-white p-2 rounded mb-1">Article 3 - List Style</div>
                <div class="bg-success text-white p-2 rounded">Article 4 - List Style</div>
            `;
            break;
        case 'carousel':
            previewHTML = `
                <div class="bg-warning text-dark p-3 rounded text-center">
                    <div>← Article Carousel →</div>
                    <small>Rotating article display</small>
                </div>
            `;
            break;
    }
    
    previewContainer.innerHTML = previewHTML;
}

// Save section settings
function saveSectionSettings() {
    const form = document.getElementById('sectionForm');
    const formData = new FormData(form);
    
    fetch('/api/save-section.php', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Section saved successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('sectionModal')).hide();
            // Refresh the layout
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('Error saving section: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        showNotification('Error saving section: ' + error.message, 'danger');
    });
}

// Update section order
function updateSectionOrder() {
    const sections = document.querySelectorAll('.layout-section');
    const order = Array.from(sections).map((section, index) => ({
        id: section.dataset.sectionId,
        order: index + 1
    }));
    
    fetch('/api/update-section-order.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ order })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Section order updated!', 'success');
        }
    })
    .catch(error => {
        console.error('Error updating section order:', error);
    });
}

// Update homepage section order
function updateHomepageSectionOrder() {
    const sections = document.querySelectorAll('.section-item');
    const order = Array.from(sections).map((section, index) => ({
        id: section.dataset.sectionId,
        order: index + 1
    }));
    
    fetch('/api/update-homepage-order.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ order })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Homepage layout updated!', 'success');
        }
    })
    .catch(error => {
        console.error('Error updating homepage order:', error);
    });
}

// Handle article move between sections
function handleArticleMove(evt) {
    const articleId = evt.item.dataset.articleId;
    const newSectionId = evt.to.dataset.sectionId;
    const position = evt.newIndex;
    
    fetch('/api/move-article.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            article_id: articleId,
            section_id: newSectionId,
            position: position
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Article moved successfully!', 'success');
        } else {
            showNotification('Error moving article: ' + data.error, 'danger');
            // Revert the move
            evt.from.insertBefore(evt.item, evt.from.children[evt.oldIndex]);
        }
    })
    .catch(error => {
        showNotification('Error moving article: ' + error.message, 'danger');
        // Revert the move
        evt.from.insertBefore(evt.item, evt.from.children[evt.oldIndex]);
    });
}

// Update article order within a section
function updateArticleOrder(list) {
    const sectionId = list.dataset.sectionId;
    const articles = Array.from(list.children).map((item, index) => ({
        id: item.dataset.articleId,
        position: index
    }));
    
    fetch('/api/update-article-order.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            section_id: sectionId,
            articles: articles
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            console.error('Error updating article order:', data.error);
        }
    })
    .catch(error => {
        console.error('Error updating article order:', error);
    });
}

// Preview section
function previewSection(sectionElement) {
    const sectionId = sectionElement.dataset.sectionId;
    window.open(`/preview-section.php?id=${sectionId}`, '_blank');
}

// Delete section
function deleteSection(sectionElement) {
    if (!confirm('Are you sure you want to delete this section? This action cannot be undone.')) {
        return;
    }
    
    const sectionId = sectionElement.dataset.sectionId;
    
    fetch('/api/delete-section.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ section_id: sectionId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            sectionElement.remove();
            showNotification('Section deleted successfully!', 'success');
        } else {
            showNotification('Error deleting section: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        showNotification('Error deleting section: ' + error.message, 'danger');
    });
}

// Initialize layout preview
function initializeLayoutPreview() {
    const previewButton = document.querySelector('.preview-layout');
    if (previewButton) {
        previewButton.addEventListener('click', function() {
            window.open('/', '_blank');
        });
    }
    
    // Live preview updates
    const previewFrame = document.querySelector('.layout-preview-frame');
    if (previewFrame) {
        // Initialize iframe preview
        updateLivePreview();
    }
}

// Update live preview
function updateLivePreview() {
    const previewFrame = document.querySelector('.layout-preview-frame');
    if (previewFrame) {
        previewFrame.src = '/?preview=1&t=' + Date.now();
    }
}

// Export/Import layout functions
function exportLayout() {
    fetch('/api/export-layout.php')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const dataStr = JSON.stringify(data.layout, null, 2);
                const dataBlob = new Blob([dataStr], {type: 'application/json'});
                
                const link = document.createElement('a');
                link.href = URL.createObjectURL(dataBlob);
                link.download = 'echhapa-layout-' + new Date().toISOString().split('T')[0] + '.json';
                link.click();
                
                showNotification('Layout exported successfully!', 'success');
            }
        })
        .catch(error => {
            showNotification('Error exporting layout: ' + error.message, 'danger');
        });
}

function importLayout() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const layout = JSON.parse(e.target.result);
                
                fetch('/api/import-layout.php', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ layout })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification('Layout imported successfully!', 'success');
                        setTimeout(() => location.reload(), 1000);
                    } else {
                        showNotification('Error importing layout: ' + data.error, 'danger');
                    }
                })
                .catch(error => {
                    showNotification('Error importing layout: ' + error.message, 'danger');
                });
            } catch (error) {
                showNotification('Invalid layout file', 'danger');
            }
        };
        reader.readAsText(file);
    };
    
    input.click();
}

// Add export/import buttons to layout page
document.addEventListener('DOMContentLoaded', function() {
    const layoutActions = document.querySelector('.layout-actions');
    if (layoutActions) {
        const exportBtn = document.createElement('button');
        exportBtn.className = 'btn btn-outline-secondary me-2';
        exportBtn.innerHTML = '<i class="fas fa-download me-1"></i>Export Layout';
        exportBtn.onclick = exportLayout;
        
        const importBtn = document.createElement('button');
        importBtn.className = 'btn btn-outline-secondary';
        importBtn.innerHTML = '<i class="fas fa-upload me-1"></i>Import Layout';
        importBtn.onclick = importLayout;
        
        layoutActions.appendChild(exportBtn);
        layoutActions.appendChild(importBtn);
    }
});
