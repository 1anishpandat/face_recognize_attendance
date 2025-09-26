<?php
// config.php - Database configuration
class DatabaseConfig {
    private $host = "localhost";
    private $username = "root";
    private $password = "";
    private $database = "attendance_system";
    public $connection;

    public function __construct() {
        $this->connection = null;
        try {
            $this->connection = new PDO(
                "mysql:host=" . $this->host . ";dbname=" . $this->database,
                $this->username,
                $this->password
            );
            $this->connection->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        } catch(PDOException $exception) {
            echo "Connection error: " . $exception->getMessage();
        }
    }
}