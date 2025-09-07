/**
 * Custom Rich Text Editor
 * A lightweight, feature-rich alternative to TinyMCE
 */

class CustomEditor {
    constructor(selector, options = {}) {
        this.selector = selector;
        this.options = {
            height: '400px',
            placeholder: 'Start writing...',
            toolbar: [
                'bold', 'italic', 'underline', 'strikethrough', '|',
                'h1', 'h2', 'h3', '|',
                'ul', 'ol', '|',
                'link', 'image', '|',
                'align-left', 'align-center', 'align-right', '|',
                'undo', 'redo', '|',
                'code', 'fullscreen'
            ],
            ...options
        };
        this.init();
    }

    init() {
        const element = document.querySelector(this.selector);
        if (!element) return;

        // Create editor container
        this.container = document.createElement('div');
        this.container.className = 'custom-editor';
        
        // Create toolbar
        this.toolbar = this.createToolbar();
        
        // Create editor area
        this.editor = document.createElement('div');
        this.editor.className = 'editor-content';
        this.editor.contentEditable = true;
        this.editor.style.height = this.options.height;
        this.editor.setAttribute('data-placeholder', this.options.placeholder);
        
        // Create status bar
        this.statusBar = document.createElement('div');
        this.statusBar.className = 'editor-status';
        this.statusBar.innerHTML = '<span class="word-count">Words: 0</span> <span class="char-count">Characters: 0</span>';

        // Assemble editor
        this.container.appendChild(this.toolbar);
        this.container.appendChild(this.editor);
        this.container.appendChild(this.statusBar);
        
        // Replace original element
        element.parentNode.insertBefore(this.container, element);
        element.style.display = 'none';
        
        // Store reference to original element
        this.originalElement = element;
        
        // Bind events
        this.bindEvents();
        
        // Load existing content
        if (element.value) {
            this.editor.innerHTML = element.value;
        }
    }

    createToolbar() {
        const toolbar = document.createElement('div');
        toolbar.className = 'editor-toolbar';
        
        this.options.toolbar.forEach(item => {
            if (item === '|') {
                const separator = document.createElement('div');
                separator.className = 'toolbar-separator';
                toolbar.appendChild(separator);
            } else {
                const button = this.createToolbarButton(item);
                toolbar.appendChild(button);
            }
        });
        
        return toolbar;
    }

    createToolbarButton(action) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'toolbar-btn';
        button.setAttribute('data-action', action);
        
        const icons = {
            'bold': '<i class="fas fa-bold"></i>',
            'italic': '<i class="fas fa-italic"></i>',
            'underline': '<i class="fas fa-underline"></i>',
            'strikethrough': '<i class="fas fa-strikethrough"></i>',
            'h1': 'H1',
            'h2': 'H2',
            'h3': 'H3',
            'ul': '<i class="fas fa-list-ul"></i>',
            'ol': '<i class="fas fa-list-ol"></i>',
            'link': '<i class="fas fa-link"></i>',
            'image': '<i class="fas fa-image"></i>',
            'align-left': '<i class="fas fa-align-left"></i>',
            'align-center': '<i class="fas fa-align-center"></i>',
            'align-right': '<i class="fas fa-align-right"></i>',
            'undo': '<i class="fas fa-undo"></i>',
            'redo': '<i class="fas fa-redo"></i>',
            'code': '<i class="fas fa-code"></i>',
            'fullscreen': '<i class="fas fa-expand"></i>'
        };
        
        button.innerHTML = icons[action] || action.toUpperCase();
        button.title = this.getButtonTitle(action);
        
        button.addEventListener('click', (e) => {
            e.preventDefault();
            this.executeCommand(action);
        });
        
        return button;
    }

    getButtonTitle(action) {
        const titles = {
            'bold': 'Bold (Ctrl+B)',
            'italic': 'Italic (Ctrl+I)',
            'underline': 'Underline (Ctrl+U)',
            'strikethrough': 'Strikethrough',
            'h1': 'Heading 1',
            'h2': 'Heading 2',
            'h3': 'Heading 3',
            'ul': 'Bullet List',
            'ol': 'Numbered List',
            'link': 'Insert Link',
            'image': 'Insert Image',
            'align-left': 'Align Left',
            'align-center': 'Align Center',
            'align-right': 'Align Right',
            'undo': 'Undo (Ctrl+Z)',
            'redo': 'Redo (Ctrl+Y)',
            'code': 'View HTML',
            'fullscreen': 'Full Screen'
        };
        return titles[action] || action;
    }

    executeCommand(action) {
        this.editor.focus();
        
        switch(action) {
            case 'bold':
                document.execCommand('bold', false, null);
                break;
            case 'italic':
                document.execCommand('italic', false, null);
                break;
            case 'underline':
                document.execCommand('underline', false, null);
                break;
            case 'strikethrough':
                document.execCommand('strikeThrough', false, null);
                break;
            case 'h1':
            case 'h2':
            case 'h3':
                document.execCommand('formatBlock', false, action.toUpperCase());
                break;
            case 'ul':
                document.execCommand('insertUnorderedList', false, null);
                break;
            case 'ol':
                document.execCommand('insertOrderedList', false, null);
                break;
            case 'link':
                this.insertLink();
                break;
            case 'image':
                this.insertImage();
                break;
            case 'align-left':
                document.execCommand('justifyLeft', false, null);
                break;
            case 'align-center':
                document.execCommand('justifyCenter', false, null);
                break;
            case 'align-right':
                document.execCommand('justifyRight', false, null);
                break;
            case 'undo':
                document.execCommand('undo', false, null);
                break;
            case 'redo':
                document.execCommand('redo', false, null);
                break;
            case 'code':
                this.toggleCodeView();
                break;
            case 'fullscreen':
                this.toggleFullscreen();
                break;
        }
        
        this.updateToolbarState();
        this.updateWordCount();
        this.syncContent();
    }

    insertLink() {
        const url = prompt('Enter URL:');
        if (url) {
            const selection = window.getSelection();
            if (selection.rangeCount) {
                const range = selection.getRangeAt(0);
                const selectedText = range.toString();
                const linkText = selectedText || url;
                
                const link = document.createElement('a');
                link.href = url;
                link.textContent = linkText;
                link.target = '_blank';
                
                range.deleteContents();
                range.insertNode(link);
                
                // Move cursor after the link
                range.setStartAfter(link);
                range.collapse(true);
                selection.removeAllRanges();
                selection.addRange(range);
            }
        }
    }

    insertImage() {
        const url = prompt('Enter image URL:');
        if (url) {
            const img = document.createElement('img');
            img.src = url;
            img.style.maxWidth = '100%';
            img.style.height = 'auto';
            
            const selection = window.getSelection();
            if (selection.rangeCount) {
                const range = selection.getRangeAt(0);
                range.insertNode(img);
                range.setStartAfter(img);
                range.collapse(true);
                selection.removeAllRanges();
                selection.addRange(range);
            }
        }
    }

    toggleCodeView() {
        const codeBtn = this.toolbar.querySelector('[data-action="code"]');
        
        if (this.editor.style.display === 'none') {
            // Switch back to WYSIWYG
            this.editor.innerHTML = this.codeEditor.value;
            this.editor.style.display = 'block';
            this.codeEditor.style.display = 'none';
            codeBtn.classList.remove('active');
        } else {
            // Switch to HTML code view
            if (!this.codeEditor) {
                this.codeEditor = document.createElement('textarea');
                this.codeEditor.className = 'editor-code';
                this.codeEditor.style.height = this.options.height;
                this.editor.parentNode.insertBefore(this.codeEditor, this.editor.nextSibling);
            }
            
            this.codeEditor.value = this.editor.innerHTML;
            this.editor.style.display = 'none';
            this.codeEditor.style.display = 'block';
            this.codeEditor.focus();
            codeBtn.classList.add('active');
        }
    }

    toggleFullscreen() {
        this.container.classList.toggle('fullscreen');
        const fullscreenBtn = this.toolbar.querySelector('[data-action="fullscreen"]');
        
        if (this.container.classList.contains('fullscreen')) {
            fullscreenBtn.innerHTML = '<i class="fas fa-compress"></i>';
            fullscreenBtn.title = 'Exit Fullscreen';
        } else {
            fullscreenBtn.innerHTML = '<i class="fas fa-expand"></i>';
            fullscreenBtn.title = 'Full Screen';
        }
    }

    updateToolbarState() {
        // Update button states based on current selection
        const commands = ['bold', 'italic', 'underline', 'strikethrough'];
        
        commands.forEach(cmd => {
            const btn = this.toolbar.querySelector(`[data-action="${cmd}"]`);
            if (btn) {
                if (document.queryCommandState(cmd)) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            }
        });
    }

    updateWordCount() {
        const text = this.editor.textContent || '';
        const words = text.trim() ? text.trim().split(/\s+/).length : 0;
        const chars = text.length;
        
        const wordCountEl = this.statusBar.querySelector('.word-count');
        const charCountEl = this.statusBar.querySelector('.char-count');
        
        if (wordCountEl) wordCountEl.textContent = `Words: ${words}`;
        if (charCountEl) charCountEl.textContent = `Characters: ${chars}`;
    }

    syncContent() {
        // Sync content with original element
        if (this.originalElement) {
            this.originalElement.value = this.editor.innerHTML;
        }
    }

    bindEvents() {
        // Editor events
        this.editor.addEventListener('input', () => {
            this.updateWordCount();
            this.syncContent();
        });
        
        this.editor.addEventListener('keyup', () => {
            this.updateToolbarState();
        });
        
        this.editor.addEventListener('mouseup', () => {
            this.updateToolbarState();
        });
        
        // Keyboard shortcuts
        this.editor.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key.toLowerCase()) {
                    case 'b':
                        e.preventDefault();
                        this.executeCommand('bold');
                        break;
                    case 'i':
                        e.preventDefault();
                        this.executeCommand('italic');
                        break;
                    case 'u':
                        e.preventDefault();
                        this.executeCommand('underline');
                        break;
                    case 'z':
                        if (e.shiftKey) {
                            e.preventDefault();
                            this.executeCommand('redo');
                        } else {
                            e.preventDefault();
                            this.executeCommand('undo');
                        }
                        break;
                    case 'y':
                        e.preventDefault();
                        this.executeCommand('redo');
                        break;
                }
            }
        });
        
        // Paste cleanup
        this.editor.addEventListener('paste', (e) => {
            e.preventDefault();
            const text = (e.clipboardData || window.clipboardData).getData('text/plain');
            document.execCommand('insertText', false, text);
        });
        
        // Initial updates
        this.updateWordCount();
        this.updateToolbarState();
    }

    // Public API methods
    getContent() {
        return this.editor.innerHTML;
    }

    setContent(html) {
        this.editor.innerHTML = html;
        this.syncContent();
        this.updateWordCount();
    }

    focus() {
        this.editor.focus();
    }

    destroy() {
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
        if (this.originalElement) {
            this.originalElement.style.display = '';
        }
    }
}

// Global function to initialize custom editors
function initializeCustomEditors() {
    document.querySelectorAll('.rich-editor, #articleContent, .custom-editor-target').forEach(element => {
        if (!element.dataset.editorInitialized) {
            new CustomEditor(`#${element.id}`, {
                height: element.dataset.height || '400px'
            });
            element.dataset.editorInitialized = 'true';
        }
    });
}

// Auto-initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', initializeCustomEditors);

// Export for use in other scripts
window.CustomEditor = CustomEditor;
window.initializeCustomEditors = initializeCustomEditors;