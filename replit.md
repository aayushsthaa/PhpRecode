# Overview

Echhapa is a news portal application built with a traditional web architecture using HTML, CSS, and JavaScript. The application features a public-facing news website with an administrative dashboard for content management. The system includes article publishing, layout management, image handling, and user engagement features like newsletter subscriptions and social sharing.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Traditional Web Stack**: Built using vanilla HTML, CSS, and JavaScript without modern frontend frameworks
- **Responsive Design**: Uses Bootstrap framework for responsive layouts and components
- **Component-Based Structure**: Modular JavaScript files for different functionality areas (admin, layout management, frontend)
- **CSS Organization**: Separate stylesheets for admin dashboard and public site styling

## Content Management System
- **Admin Dashboard**: Fixed sidebar navigation with content management interface
- **Rich Text Editor**: TinyMCE integration for article content editing
- **File Upload System**: Drag-and-drop file upload functionality for media management
- **Layout Manager**: Dynamic homepage layout management with sortable sections and drag-and-drop article placement

## User Interface Features
- **Lazy Loading**: Intersection Observer API for optimized image loading
- **Data Tables**: Enhanced table functionality for admin data management
- **Form Validation**: Client-side validation for user inputs
- **Social Sharing**: Built-in social media sharing capabilities
- **Newsletter System**: Email subscription functionality with validation
- **Reading Progress**: Progress tracking for article reading
- **Mobile Optimization**: Responsive mobile menu and layout

## Design Patterns
- **Progressive Enhancement**: Base functionality works without JavaScript, enhanced with interactive features
- **Event-Driven Architecture**: DOM event handling for user interactions
- **Modular JavaScript**: Separate initialization functions for different components
- **CSS Utility Classes**: Bootstrap integration with custom utility classes

# External Dependencies

## Frontend Libraries
- **Bootstrap**: UI framework for responsive design and components
- **TinyMCE**: Rich text editor for content creation
- **Sortable.js**: Drag-and-drop functionality for layout management
- **DataTables**: Enhanced table functionality for admin interface
- **Feather Icons**: Icon library for UI elements

## Browser APIs
- **Intersection Observer**: For lazy loading and scroll-based interactions
- **File API**: For drag-and-drop file uploads
- **Fetch API**: For AJAX requests and form submissions

## Third-Party Services
- **Social Media APIs**: Integration for social sharing functionality
- **Email Services**: Newsletter subscription handling (implementation pending)
- **Analytics**: Potential integration for tracking user engagement

## Development Tools
- **CSS Preprocessors**: Potential SASS/LESS support for advanced styling
- **Image Optimization**: Client-side image processing for uploads
- **Form Libraries**: Enhanced form validation and submission handling