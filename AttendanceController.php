<?php
class AttendanceController {
    private $db;
    
    public function __construct($database) {
        $this->db = $database;
    }
    
    public function registerEmployee($data) {
        try {
            $stmt = $this->db->prepare("
                INSERT INTO employees (employee_id, full_name, department, face_encoding, face_image) 
                VALUES (:employee_id, :full_name, :department, :face_encoding, :face_image)
            ");
            
            $faceEncoding = $this->extractFaceFeatures($data['face_image']);
            
            $stmt->bindParam(':employee_id', $data['employee_id']);
            $stmt->bindParam(':full_name', $data['full_name']);
            $stmt->bindParam(':department', $data['department']);
            $stmt->bindParam(':face_encoding', $faceEncoding);
            $stmt->bindParam(':face_image', $data['face_image']);
            
            if($stmt->execute()) {
                return json_encode([
                    'success' => true, 
                    'message' => 'Employee registered successfully',
                    'employee_id' => $data['employee_id']
                ]);
            } else {
                throw new Exception('Failed to register employee');
            }
        } catch(Exception $e) {
            return json_encode([
                'success' => false, 
                'error' => $e->getMessage()
            ]);
        }
    }
    
    public function markAttendance($data) {
        try {
            // First, recognize the face
            $recognition = json_decode($this->recognizeFace($data), true);
            
            if(!$recognition['success']) {
                return json_encode([
                    'success' => false,
                    'error' => 'Face not recognized'
                ]);
            }
            
            $employeeId = $recognition['employee_id'];
            $confidence = $recognition['confidence'];
            $today = date('Y-m-d');
            
            // Check if attendance already marked today
            $checkStmt = $this->db->prepare("
                SELECT id FROM attendance 
                WHERE employee_id = :employee_id AND date = :date
            ");
            $checkStmt->bindParam(':employee_id', $employeeId);
            $checkStmt->bindParam(':date', $today);
            $checkStmt->execute();
            
            if($checkStmt->rowCount() > 0) {
                return json_encode([
                    'success' => false,
                    'error' => 'Attendance already marked for today'
                ]);
            }
            
            // Mark attendance
            $currentTime = date('H:i:s');
            $status = $this->determineStatus($currentTime);
            
            $stmt = $this->db->prepare("
                INSERT INTO attendance (employee_id, date, status, face_confidence) 
                VALUES (:employee_id, :date, :status, :confidence)
            ");
            
            $stmt->bindParam(':employee_id', $employeeId);
            $stmt->bindParam(':date', $today);
            $stmt->bindParam(':status', $status);
            $stmt->bindParam(':confidence', $confidence);
            
            if($stmt->execute()) {
                // Get employee details
                $empStmt = $this->db->prepare("SELECT * FROM employees WHERE employee_id = :employee_id");
                $empStmt->bindParam(':employee_id', $employeeId);
                $empStmt->execute();
                $employee = $empStmt->fetch(PDO::FETCH_ASSOC);
                
                return json_encode([
                    'success' => true,
                    'message' => 'Attendance marked successfully',
                    'employee' => [
                        'id' => $employee['employee_id'],
                        'name' => $employee['full_name'],
                        'department' => $employee['department']
                    ],
                    'time' => date('H:i:s'),
                    'status' => $status
                ]);
            } else {
                throw new Exception('Failed to mark attendance');
            }
        } catch(Exception $e) {
            return json_encode([
                'success' => false,
                'error' => $e->getMessage()
            ]);
        }
    }
    
    public function recognizeFace($data) {
        try {
            $inputFaceEncoding = $this->extractFaceFeatures($data['face_image']);
            
            if(!$inputFaceEncoding) {
                return json_encode([
                    'success' => false,
                    'error' => 'No face detected in image'
                ]);
            }
            
            // Get all registered employees
            $stmt = $this->db->prepare("SELECT employee_id, full_name, face_encoding FROM employees");
            $stmt->execute();
            $employees = $stmt->fetchAll(PDO::FETCH_ASSOC);
            
            $bestMatch = null;
            $highestConfidence = 0;
            $threshold = 0.6; // Confidence threshold for recognition
            
            foreach($employees as $employee) {
                if($employee['face_encoding']) {
                    $confidence = $this->compareFaceEncodings($inputFaceEncoding, $employee['face_encoding']);
                    
                    if($confidence > $highestConfidence && $confidence > $threshold) {
                        $highestConfidence = $confidence;
                        $bestMatch = $employee;
                    }
                }
            }
            
            if($bestMatch) {
                return json_encode([
                    'success' => true,
                    'employee_id' => $bestMatch['employee_id'],
                    'name' => $bestMatch['full_name'],
                    'confidence' => $highestConfidence
                ]);
            } else {
                return json_encode([
                    'success' => false,
                    'error' => 'Face not recognized'
                ]);
            }
        } catch(Exception $e) {
            return json_encode([
                'success' => false,
                'error' => $e->getMessage()
            ]);
        }
    }
    
    public function getTodaysAttendance($date = null) {
        try {
            $date = $date ?? date('Y-m-d');
            
            $stmt = $this->db->prepare("
                SELECT 
                    a.employee_id,
                    e.full_name,
                    e.department,
                    a.check_in_time,
                    a.status,
                    a.face_confidence
                FROM attendance a
                JOIN employees e ON a.employee_id = e.employee_id
                WHERE a.date = :date
                ORDER BY a.check_in_time DESC
            ");
            
            $stmt->bindParam(':date', $date);
            $stmt->execute();
            $attendance = $stmt->fetchAll(PDO::FETCH_ASSOC);
            
            return json_encode([
                'success' => true,
                'data' => $attendance,
                'date' => $date
            ]);
        } catch(Exception $e) {
            return json_encode([
                'success' => false,
                'error' => $e->getMessage()
            ]);
        }
    }
    
    public function getAllEmployees() {
        try {
            $stmt = $this->db->prepare("
                SELECT employee_id, full_name, department, created_at 
                FROM employees 
                ORDER BY created_at DESC
            ");
            $stmt->execute();
            $employees = $stmt->fetchAll(PDO::FETCH_ASSOC);
            
            return json_encode([
                'success' => true,
                'data' => $employees
            ]);
        } catch(Exception $e) {
            return json_encode([
                'success' => false,
                'error' => $e->getMessage()
            ]);
        }
    }
    
    private function extractFaceFeatures($base64Image) {
        // This is a simplified version. In a real implementation, you would:
        // 1. Decode the base64 image
        // 2. Use a face recognition library (like dlib, OpenCV, or face_recognition)
        // 3. Extract face landmarks and create a face encoding
        
        // For demo purposes, we'll create a simple hash of the image
        $imageData = base64_decode(preg_replace('#^data:image/\w+;base64,#i', '', $base64Image));
        
        if(!$imageData) {
            return false;
        }
        
        // Create a simple feature vector (in real implementation, use proper face encoding)
        $features = [];
        $hash = md5($imageData);
        
        // Convert hash to numeric features (simplified approach)
        for($i = 0; $i < 32; $i += 2) {
            $features[] = hexdec(substr($hash, $i, 2)) / 255.0;
        }
        
        return json_encode($features);
    }
    
    private function compareFaceEncodings($encoding1, $encoding2) {
        // This is a simplified comparison. In real implementation, use proper distance calculation
        $features1 = json_decode($encoding1, true);
        $features2 = json_decode($encoding2, true);
        
        if(!$features1 || !$features2 || count($features1) !== count($features2)) {
            return 0;
        }
        
        // Calculate simple similarity (in real implementation, use euclidean distance)
        $similarity = 0;
        for($i = 0; $i < count($features1); $i++) {
            $similarity += abs($features1[$i] - $features2[$i]);
        }
        
        // Convert to confidence (0-1)
        $confidence = max(0, 1 - ($similarity / count($features1)));
        return $confidence;
    }
    
    private function determineStatus($checkInTime) {
        $time = strtotime($checkInTime);
        $cutoffTime = strtotime('09:30:00'); // 9:30 AM cutoff for late
        
        if($time <= $cutoffTime) {
            return 'Present';
        } else {
            return 'Late';
        }
    }
}