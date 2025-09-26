<?php
class FaceRecognition {
    private $pythonScript;
    
    public function __construct() {
        $this->pythonScript = __DIR__ . '/face_recognition.py';
    }
    
    public function extractFaceEncoding($imagePath) {
        // Call Python script for face encoding (requires face_recognition library)
        $command = "python3 {$this->pythonScript} encode " . escapeshellarg($imagePath);
        $output = shell_exec($command);
        
        if($output) {
            return json_decode(trim($output), true);
        }
        
        return false;
    }
    
    public function compareFaces($encoding1, $encoding2, $tolerance = 0.6) {
        // Compare two face encodings
        $data = [
            'encoding1' => $encoding1,
            'encoding2' => $encoding2,
            'tolerance' => $tolerance
        ];
        
        $tempFile = tempnam(sys_get_temp_dir(), 'face_compare');
        file_put_contents($tempFile, json_encode($data));
        
        $command = "python3 {$this->pythonScript} compare " . escapeshellarg($tempFile);
        $output = shell_exec($command);
        
        unlink($tempFile);
        
        if($output) {
            return json_decode(trim($output), true);
        }
        
        return false;
    }
}