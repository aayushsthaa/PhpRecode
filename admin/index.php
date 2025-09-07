<?php
// Redirect to dashboard
require_once '../config/config.php';
header('Location: ' . adminUrl('dashboard.php'));
exit;
?>
