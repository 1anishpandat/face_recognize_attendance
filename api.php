<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE');
header('Access-Control-Allow-Headers: Content-Type');

require_once 'config.php';
require_once 'AttendanceController.php';

$database = new DatabaseConfig();
$db = $database->connection;
$controller = new AttendanceController($db);

$method = $_SERVER['REQUEST_METHOD'];
$input = json_decode(file_get_contents('php://input'), true);

switch($method) {
    case 'GET':
        if(isset($_GET['action'])) {
            switch($_GET['action']) {
                case 'get_attendance':
                    $date = $_GET['date'] ?? date('Y-m-d');
                    echo $controller->getTodaysAttendance($date);
                    break;
                case 'get_employees':
                    echo $controller->getAllEmployees();
                    break;
                default:
                    http_response_code(400);
                    echo json_encode(['error' => 'Invalid action']);
            }
        }
        break;
        
    case 'POST':
        if(isset($input['action'])) {
            switch($input['action']) {
                case 'register_employee':
                    echo $controller->registerEmployee($input);
                    break;
                case 'mark_attendance':
                    echo $controller->markAttendance($input);
                    break;
                case 'recognize_face':
                    echo $controller->recognizeFace($input);
                    break;
                default:
                    http_response_code(400);
                    echo json_encode(['error' => 'Invalid action']);
            }
        }
        break;
        
    default:
        http_response_code(405);
        echo json_encode(['error' => 'Method not allowed']);
        break;
}