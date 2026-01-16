import csv
import os
from datetime import datetime
import socket
import sys
import time

def get_log_path():
    """Get the path for attendance log file"""
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    project_root = os.path.dirname(script_dir)
    logs_dir = os.path.join(project_root, 'logs')
    
    try:
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
    except Exception as e:
        logs_dir = script_dir
    
    log_file = os.path.join(logs_dir, 'attendance_log.csv')
    return log_file

def write_debug_log(message):
    """Write debug information to desktop"""
    try:
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        debug_log = os.path.join(desktop, 'attendance_debug.txt')
        with open(debug_log, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now()} - {message}\n")
    except:
        pass

def mark_attendance():
    """Mark attendance by logging login details to CSV"""
    file_path = None
    max_retries = 3
    retry_delay = 2
    
    try:
        write_debug_log("=== SCRIPT STARTED ===")
        write_debug_log(f"Script location: {os.path.abspath(__file__)}")
        write_debug_log(f"Working directory: {os.getcwd()}")
        
        # Wait for system to be fully ready
        initial_delay = 5
        write_debug_log(f"Waiting {initial_delay} seconds for system to be ready...")
        time.sleep(initial_delay)
        
        file_path = get_log_path()
        write_debug_log(f"Log path: {file_path}")
        
        # Get current details
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        day = now.strftime("%A")
        time_str = now.strftime("%H:%M:%S")
        computer_name = socket.gethostname()
        
        try:
            username = os.getlogin()
        except Exception as e:
            write_debug_log(f"os.getlogin() failed: {e}")
            username = os.environ.get('USER') or os.environ.get('USERNAME') or 'Unknown'
        
        write_debug_log(f"User: {username}, Computer: {computer_name}, Date: {date}")
        
        # Retry logic for file writing
        for attempt in range(1, max_retries + 1):
            try:
                write_debug_log(f"Write attempt {attempt}/{max_retries}")
                
                # Check if file exists and has content
                file_exists = os.path.exists(file_path)
                has_content = file_exists and os.path.getsize(file_path) > 10
                
                write_debug_log(f"File exists: {file_exists}, Has content: {has_content}")
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Open file with retry
                file_handle = None
                for file_attempt in range(3):
                    try:
                        file_handle = open(file_path, 'a', newline='', encoding='utf-8')
                        break
                    except PermissionError:
                        write_debug_log(f"File locked, waiting... (attempt {file_attempt + 1})")
                        time.sleep(1)
                
                if not file_handle:
                    raise Exception("Could not open file after multiple attempts")
                
                try:
                    writer = csv.writer(file_handle)
                    
                    # Write header if new file
                    if not has_content:
                        write_debug_log("Writing header")
                        writer.writerow(['Date', 'Day', 'Time', 'Computer Name', 'User', 'Event', 'Status'])
                    
                    # Write attendance record
                    writer.writerow([date, day, time_str, computer_name, username, 'Login', 'Success'])
                    write_debug_log("Attendance record written")
                    
                    # Force write to disk
                    file_handle.flush()
                    os.fsync(file_handle.fileno())
                    write_debug_log("Data flushed to disk")
                    
                finally:
                    file_handle.close()
                    write_debug_log("File closed")
                
                # Verify the write was successful
                time.sleep(0.5)
                if os.path.exists(file_path):
                    new_size = os.path.getsize(file_path)
                    write_debug_log(f"File size after write: {new_size} bytes")
                    
                    # Read back to verify
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if lines:
                            write_debug_log(f"Total lines: {len(lines)}")
                            write_debug_log(f"Last line: {lines[-1].strip()}")
                    
                    print(f"✓ Attendance marked successfully!")
                    print(f"  Date: {date} ({day})")
                    print(f"  Time: {time_str}")
                    print(f"  User: {username}")
                    print(f"  Computer: {computer_name}")
                    print(f"  Log file: {file_path}")
                    print(f"  File size: {new_size} bytes")
                    
                    write_debug_log("=== SCRIPT COMPLETED SUCCESSFULLY ===\n")
                    return True
                else:
                    raise Exception("File not found after writing")
                    
            except Exception as e:
                write_debug_log(f"Attempt {attempt} failed: {e}")
                
                if attempt < max_retries:
                    write_debug_log(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise
        
        return False
        
    except Exception as e:
        error_msg = f"Error marking attendance: {e}"
        print(f"✗ {error_msg}")
        write_debug_log(f"ERROR: {error_msg}")
        
        import traceback
        tb = traceback.format_exc()
        write_debug_log(f"Traceback:\n{tb}")
        
        # Write error to desktop
        try:
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            error_log = os.path.join(desktop, 'attendance_error.txt')
            with open(error_log, 'a') as error_file:
                error_file.write(f"\n{'='*60}\n")
                error_file.write(f"{datetime.now()} - ERROR\n")
                error_file.write(f"{'='*60}\n")
                error_file.write(f"Error: {error_msg}\n")
                error_file.write(f"Script: {os.path.abspath(__file__)}\n")
                error_file.write(f"Working dir: {os.getcwd()}\n")
                error_file.write(f"Log path: {file_path if file_path else 'N/A'}\n")
                error_file.write(f"Traceback:\n{tb}\n")
        except:
            pass
        
        write_debug_log("=== SCRIPT FAILED ===\n")
        return False

if __name__ == "__main__":
    print("="*60)
    print("ATTENDANCE MARKER - Starting...")
    print(f"Time: {datetime.now()}")
    print("="*60)
    print()
    
    result = mark_attendance()
    
    print()
    print("="*60)
    if result:
        print("STATUS: SUCCESS ✓")
    else:
        print("STATUS: FAILED ✗")
    print("="*60)
    
    # Keep window open
    print("\nWindow will close in 10 seconds...")
    time.sleep(10)  