<?php
require_once 'config/config.php';

$pageTitle = 'Contact Us';
$success = '';
$error = '';

if ($_POST) {
    $name = sanitize($_POST['name'] ?? '');
    $email = sanitize($_POST['email'] ?? '');
    $subject = sanitize($_POST['subject'] ?? '');
    $message = sanitize($_POST['message'] ?? '');
    
    if (empty($name) || empty($email) || empty($subject) || empty($message)) {
        $error = 'All fields are required.';
    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $error = 'Please enter a valid email address.';
    } else {
        // Here you would normally send the email or save to database
        // For now, we'll just show a success message
        $success = 'Thank you for your message! We will get back to you soon.';
        
        // Clear form data
        $name = $email = $subject = $message = '';
    }
}

include 'includes/header.php';
?>

<div class="container my-5">
    <div class="row">
        <div class="col-lg-8 mx-auto">
            <!-- Contact Header -->
            <div class="text-center mb-5">
                <h1 class="display-4 fw-bold mb-3">Contact Us</h1>
                <p class="lead text-muted">
                    Have a question, suggestion, or want to share your story? We'd love to hear from you.
                </p>
            </div>
            
            <!-- Contact Form -->
            <div class="card shadow">
                <div class="card-body p-5">
                    <?php if ($success): ?>
                    <div class="alert alert-success">
                        <i class="fas fa-check-circle me-2"></i><?php echo $success; ?>
                    </div>
                    <?php endif; ?>
                    
                    <?php if ($error): ?>
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i><?php echo $error; ?>
                    </div>
                    <?php endif; ?>
                    
                    <form method="POST">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="name" class="form-label">Full Name *</label>
                                <input type="text" class="form-control" id="name" name="name" 
                                       value="<?php echo htmlspecialchars($name ?? ''); ?>" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="email" class="form-label">Email Address *</label>
                                <input type="email" class="form-control" id="email" name="email" 
                                       value="<?php echo htmlspecialchars($email ?? ''); ?>" required>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="subject" class="form-label">Subject *</label>
                            <input type="text" class="form-control" id="subject" name="subject" 
                                   value="<?php echo htmlspecialchars($subject ?? ''); ?>" required>
                        </div>
                        
                        <div class="mb-4">
                            <label for="message" class="form-label">Message *</label>
                            <textarea class="form-control" id="message" name="message" rows="6" required><?php echo htmlspecialchars($message ?? ''); ?></textarea>
                        </div>
                        
                        <div class="text-center">
                            <button type="submit" class="btn btn-primary btn-lg px-5">
                                <i class="fas fa-paper-plane me-2"></i>Send Message
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Contact Information -->
    <div class="row mt-5">
        <div class="col-md-4 text-center mb-4">
            <div class="card h-100 border-0">
                <div class="card-body">
                    <i class="fas fa-envelope fa-3x text-primary mb-3"></i>
                    <h5>Email Us</h5>
                    <p class="text-muted">
                        <?php echo getSetting('contact_email', 'contact@echhapa.com'); ?>
                    </p>
                </div>
            </div>
        </div>
        
        <div class="col-md-4 text-center mb-4">
            <div class="card h-100 border-0">
                <div class="card-body">
                    <i class="fas fa-newspaper fa-3x text-primary mb-3"></i>
                    <h5>News Tips</h5>
                    <p class="text-muted">
                        Have a story? Share your news tips with our editorial team.
                    </p>
                </div>
            </div>
        </div>
        
        <div class="col-md-4 text-center mb-4">
            <div class="card h-100 border-0">
                <div class="card-body">
                    <i class="fas fa-users fa-3x text-primary mb-3"></i>
                    <h5>Media Inquiries</h5>
                    <p class="text-muted">
                        Press inquiries and partnership opportunities welcome.
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>

<?php include 'includes/footer.php'; ?>