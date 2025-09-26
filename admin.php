<?php
require_once 'config.php';
require_once 'AttendanceController.php';

$database = new DatabaseConfig();
$db = $database->connection;
$controller = new AttendanceController($db);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Attendance System - Admin Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f4;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: #333;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-card h3 {
            margin: 0 0 10px 0;
            font-size: 2em;
        }
        .stat-card p {
            margin: 0;
            opacity: 0.9;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f8f9fa;
            font-weight: 600;
        }
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        .btn-primary {
            background-color: #007bff;
            color: white;
        }
        .btn-danger {
            background-color: #dc3545;
            color: white;
        }
        .status-present { color: #28a745; font-weight: bold; }
        .status-late { color: #ffc107; font-weight: bold; }
        .status-absent { color: #dc3545; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Attendance System Admin Dashboard</h1>
            <p>Manage employees and view attendance records</p>
        </div>
        
        <div class="stats">
            <?php
            // Get statistics
            $todayDate = date('Y-m-d');
            
            // Total employees
            $empStmt = $db->prepare("SELECT COUNT(*) as count FROM employees");
            $empStmt->execute();
            $totalEmployees = $empStmt->fetch(PDO::FETCH_ASSOC)['count'];
            
            // Today's present
            $presentStmt = $db->prepare("SELECT COUNT(*) as count FROM attendance WHERE date = ? AND status IN ('Present', 'Late')");
            $presentStmt->execute([$todayDate]);
            $todayPresent = $presentStmt->fetch(PDO::FETCH_ASSOC)['count'];
            
            // Today's absent
            $todayAbsent = $totalEmployees - $todayPresent;
            
            // This month's average attendance
            $monthStart = date('Y-m-01');
            $avgStmt = $db->prepare("
                SELECT AVG(daily_count) as avg_attendance FROM (
                    SELECT COUNT(*) as daily_count 
                    FROM attendance 
                    WHERE date >= ? AND status IN ('Present', 'Late')
                    GROUP BY date
                ) as daily_stats
            ");
            $avgStmt->execute([$monthStart]);
            $avgAttendance = round($avgStmt->fetch(PDO::FETCH_ASSOC)['avg_attendance'] ?? 0, 1);
            ?>
            
            <div class="stat-card">
                <h3><?php echo $totalEmployees; ?></h3>
                <p>Total Employees</p>
            </div>
            <div class="stat-card">
                <h3><?php echo $todayPresent; ?></h3>
                <p>Present Today</p>
            </div>
            <div class="stat-card">
                <h3><?php echo $todayAbsent; ?></h3>
                <p>Absent Today</p>
            </div>
            <div class="stat-card">
                <h3><?php echo $avgAttendance; ?></h3>
                <p>Monthly Average</p>
            </div>
        </div>
        
        <h2>Today's Attendance (<?php echo date('M d, Y'); ?>)</h2>
        <table>
            <thead>
                <tr>
                    <th>Employee ID</th>
                    <th>Name</th>
                    <th>Department</th>
                    <th>Check-in Time</th>
                    <th>Status</th>
                    <th>Confidence</th>
                </tr>
            </thead>
            <tbody>
                <?php
                $attendanceData = json_decode($controller->getTodaysAttendance(), true);
                if($attendanceData['success'] && !empty($attendanceData['data'])) {
                    foreach($attendanceData['data'] as $record) {
                        $statusClass = 'status-' . strtolower($record['status']);
                        $checkInTime = date('H:i:s', strtotime($record['check_in_time']));
                        $confidence = round($record['face_confidence'] * 100, 1);
                        
                        echo "<tr>";
                        echo "<td>{$record['employee_id']}</td>";
                        echo "<td>{$record['full_name']}</td>";
                        echo "<td>{$record['department']}</td>";
                        echo "<td>{$checkInTime}</td>";
                        echo "<td><span class='{$statusClass}'>{$record['status']}</span></td>";
                        echo "<td>{$confidence}%</td>";
                        echo "</tr>";
                    }
                } else {
                    echo "<tr><td colspan='6' style='text-align: center;'>No attendance records for today</td></tr>";
                }
                ?>
            </tbody>
        </table>
        
        <h2>All Employees</h2>
        <table>
            <thead>
                <tr>
                    <th>Employee ID</th>
                    <th>Name</th>
                    <th>Department</th>
                    <th>Registered On</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <?php
                $employeesData = json_decode($controller->getAllEmployees(), true);
                if($employeesData['success'] && !empty($employeesData['data'])) {
                    foreach($employeesData['data'] as $employee) {
                        $registeredDate = date('M d, Y', strtotime($employee['created_at']));
                        
                        echo "<tr>";
                        echo "<td>{$employee['employee_id']}</td>";
                        echo "<td>{$employee['full_name']}</td>";
                        echo "<td>{$employee['department']}</td>";
                        echo "<td>{$registeredDate}</td>";
                        echo "<td>";
                        echo "<a href='view_employee.php?id={$employee['employee_id']}' class='btn btn-primary'>View</a> ";
                        echo "<a href='delete_employee.php?id={$employee['employee_id']}' class='btn btn-danger' onclick='return confirm(\"Are you sure?\")'>Delete</a>";
                        echo "</td>";
                        echo "</tr>";
                    }
                } else {
                    echo "<tr><td colspan='5' style='text-align: center;'>No employees registered</td></tr>";
                }
                ?>
            </tbody>
        </table>
    </div>
</body>
</html>
