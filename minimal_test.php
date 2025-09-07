<?php
echo "<!DOCTYPE html>\n";
echo "<html><head><title>Echhapa CMS Test</title></head><body>\n";
echo "<h1>Echhapa CMS is Working!</h1>\n";
echo "<p>Current time: " . date('Y-m-d H:i:s') . "</p>\n";
echo "<p>PHP Version: " . phpversion() . "</p>\n";

// Test database connection
try {
    $dsn = 'pgsql:host=' . ($_ENV['PGHOST'] ?? 'localhost') . ';port=' . ($_ENV['PGPORT'] ?? '5432') . ';dbname=' . ($_ENV['PGDATABASE'] ?? 'test');
    $user = $_ENV['PGUSER'] ?? 'postgres';
    $pass = $_ENV['PGPASSWORD'] ?? '';
    $pdo = new PDO($dsn, $user, $pass);
    echo "<p style='color: green;'>✓ Database connection: SUCCESS</p>\n";
    
    // Test if tables exist
    try {
        $stmt = $pdo->query("SELECT COUNT(*) FROM users");
        $count = $stmt->fetchColumn();
        echo "<p style='color: green;'>✓ Found $count users in database</p>\n";
        echo "<p><a href='/admin/'>Go to Admin Dashboard</a></p>\n";
    } catch (Exception $e) {
        echo "<p style='color: orange;'>⚠ Database connected but tables not found. <a href='install.php'>Run Installation</a></p>\n";
    }
    
} catch (PDOException $e) {
    echo "<p style='color: red;'>✗ Database connection failed: " . htmlspecialchars($e->getMessage()) . "</p>\n";
}

echo "<hr>\n";
echo "<p>Available Pages:</p>\n";
echo "<ul>\n";
echo "<li><a href='/'>Homepage</a></li>\n";
echo "<li><a href='/admin/'>Admin Dashboard</a></li>\n";
echo "<li><a href='/install.php'>Installation</a></li>\n";
echo "</ul>\n";
echo "</body></html>\n";
?>