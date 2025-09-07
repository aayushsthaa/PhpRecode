<?php
echo "PHP Test Page\n";
echo "Current time: " . date('Y-m-d H:i:s') . "\n";
echo "PHP Version: " . phpversion() . "\n";

// Check database
try {
    $dsn = 'pgsql:host=' . ($_ENV['PGHOST'] ?? 'localhost') . ';port=' . ($_ENV['PGPORT'] ?? '5432') . ';dbname=' . ($_ENV['PGDATABASE'] ?? 'test');
    $user = $_ENV['PGUSER'] ?? 'postgres';
    $pass = $_ENV['PGPASSWORD'] ?? '';
    $pdo = new PDO($dsn, $user, $pass);
    echo "Database connection: OK\n";
} catch (PDOException $e) {
    echo "Database connection failed: " . $e->getMessage() . "\n";
}
?>