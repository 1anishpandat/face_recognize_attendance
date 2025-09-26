

import sys
import json
import face_recognition
import cv2
import numpy as np
from PIL import Image
import io
import base64

def encode_face(image_path):
    """Extract face encoding from image"""
    try:
        # Load image
        image = face_recognition.load_image_file(image_path)
        
        # Find face encodings
        face_encodings = face_recognition.face_encodings(image)
        
        if len(face_encodings) > 0:
            # Return the first face encoding found
            encoding = face_encodings[0].tolist()
            return json.dumps({
                'success': True,
                'encoding': encoding
            })
        else:
            return json.dumps({
                'success': False,
                'error': 'No face found in image'
            })
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e)
        })

def compare_faces(data_file):
    """Compare two face encodings"""
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        encoding1 = np.array(data['encoding1'])
        encoding2 = np.array(data['encoding2'])
        tolerance = data.get('tolerance', 0.6)
        
        # Calculate face distance
        distance = face_recognition.face_distance([encoding1], encoding2)[0]
        
        # Convert distance to confidence
        confidence = max(0, 1 - distance)
        is_match = distance <= tolerance
        
        return json.dumps({
            'success': True,
            'is_match': is_match,
            'confidence': confidence,
            'distance': distance
        })
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e)
        })

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'No command specified'}))
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "encode" and len(sys.argv) >= 3:
        result = encode_face(sys.argv[2])
        print(result)
    elif command == "compare" and len(sys.argv) >= 3:
        result = compare_faces(sys.argv[2])
        print(result)
    else:
        print(json.dumps({'error': 'Invalid command or arguments'}))