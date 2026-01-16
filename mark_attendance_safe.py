import csv

import os

from datetime import datetime

import socket

import sys

import time

import json



def get_log_paths():

    """Get paths for both CSV and backup JSON log files"""

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

    

    csv_file = os.path.join(logs_dir, 'attendance_log.csv')

    json_file = os.path.join(logs_dir, 'attendance_log.json')

    txt_file = os.path.join(logs_dir, 'attendance_log.txt')

    

    return csv_file, json_file, txt_file



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

    """Mark attendance using multiple file formats for redundancy"""

    try:

        write_debug_log("=== SCRIPT STARTED ===")

        write_debug_log(f"Script location: {os.path.abspath(__file__)}")

        write_debug_log(f"Working directory: {os.getcwd()}")

        

        time.sleep(2)

        

        csv_path, json_path, txt_path = get_log_paths()

        write_debug_log(f"CSV path: {csv_path}")

        write_debug_log(f"JSON path: {json_path}")

        write_debug_log(f"TXT path: {txt_path}")

        

        # Get current details

        now = datetime.now()

        date = now.strftime("%Y-%m-%d")

        day = now.strftime("%A")

        time_str = now.strftime("%H:%M:%S")

        computer_name = socket.gethostname()

        

        try:

            username = os.getlogin()

        except:

            username = os.environ.get('USER') or os.environ.get('USERNAME') or 'Unknown'

        

        # Create attendance record

        record = {

            'Date': date,

            'Day': day,

            'Time': time_str,

            'Computer Name': computer_name,

            'User': username,

            'Event': 'Login',

            'Status': 'Success'

        }

        

        write_debug_log(f"Record: {record}")

        

        success_count = 0

        

        # METHOD 1: Write to plain text file (most reliable)

        try:

            with open(txt_path, 'a', encoding='utf-8') as f:

                if os.path.getsize(txt_path) == 0 if os.path.exists(txt_path) else True:

                    f.write("="*80 + "\n")

                    f.write("ATTENDANCE LOG\n")

                    f.write("="*80 + "\n\n")

                

                f.write(f"Date: {date} ({day})\n")

                f.write(f"Time: {time_str}\n")

                f.write(f"User: {username}\n")

                f.write(f"Computer: {computer_name}\n")

                f.write(f"Event: Login\n")

                f.write(f"Status: Success\n")

                f.write("-"*80 + "\n\n")

                f.flush()

                os.fsync(f.fileno())

            

            txt_size = os.path.getsize(txt_path)

            write_debug_log(f"âœ“ TXT file written successfully ({txt_size} bytes)")

            success_count += 1

        except Exception as e:

            write_debug_log(f"âœ— TXT file error: {e}")

        

        # METHOD 2: Write to JSON file (structured, Excel-safe)

        try:

            records = []

            if os.path.exists(json_path) and os.path.getsize(json_path) > 0:

                with open(json_path, 'r', encoding='utf-8') as f:

                    records = json.load(f)

            

            records.append(record)

            

            with open(json_path, 'w', encoding='utf-8') as f:

                json.dump(records, f, indent=2, ensure_ascii=False)

                f.flush()

                os.fsync(f.fileno())

            

            json_size = os.path.getsize(json_path)

            write_debug_log(f"âœ“ JSON file written successfully ({json_size} bytes, {len(records)} records)")

            success_count += 1

        except Exception as e:

            write_debug_log(f"âœ— JSON file error: {e}")

        

        # METHOD 3: Write to CSV file (for Excel compatibility)

        try:

            csv_exists = os.path.exists(csv_path) and os.path.getsize(csv_path) > 10

            

            # Use a temporary file first, then rename (atomic operation)

            temp_csv = csv_path + '.tmp'

            

            with open(temp_csv, 'a', newline='', encoding='utf-8') as f:

                writer = csv.writer(f)

                

                if not csv_exists:

                    writer.writerow(['Date', 'Day', 'Time', 'Computer Name', 'User', 'Event', 'Status'])

                

                writer.writerow([date, day, time_str, computer_name, username, 'Login', 'Success'])

                f.flush()

                os.fsync(f.fileno())

            

            # Replace the original file

            if os.path.exists(csv_path):

                os.remove(csv_path)

            os.rename(temp_csv, csv_path)

            

            csv_size = os.path.getsize(csv_path)

            write_debug_log(f"âœ“ CSV file written successfully ({csv_size} bytes)")

            success_count += 1

        except Exception as e:

            write_debug_log(f"âœ— CSV file error: {e}")

            # Clean up temp file if it exists

            if os.path.exists(temp_csv):

                try:

                    os.remove(temp_csv)

                except:

                    pass

        

        # Verify files exist and have content

        for path, name in [(txt_path, 'TXT'), (json_path, 'JSON'), (csv_path, 'CSV')]:

            if os.path.exists(path):

                size = os.path.getsize(path)

                write_debug_log(f"{name} file exists: {size} bytes")

            else:

                write_debug_log(f"{name} file NOT FOUND")

        

        print(f"âœ“ Attendance marked successfully!")

        print(f"  Date: {date} ({day})")

        print(f"  Time: {time_str}")

        print(f"  User: {username}")

        print(f"  Computer: {computer_name}")

        print(f"  Files written: {success_count}/3")

        print(f"\n  Log files:")

        print(f"    TXT: {txt_path}")

        print(f"    JSON: {json_path}")

        print(f"    CSV: {csv_path}")

        

        write_debug_log(f"Successfully wrote to {success_count}/3 files")

        write_debug_log("=== SCRIPT COMPLETED SUCCESSFULLY ===\n")

        

        return success_count > 0

        

    except Exception as e:

        error_msg = f"Error marking attendance: {e}"

        print(f"âœ— {error_msg}")

        write_debug_log(f"ERROR: {error_msg}")

        

        import traceback

        tb = traceback.format_exc()

        write_debug_log(f"Traceback:\n{tb}")

        

        try:

            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')

            error_log = os.path.join(desktop, 'attendance_error.txt')

            with open(error_log, 'a') as error_file:

                error_file.write(f"\n{'='*60}\n")

                error_file.write(f"{datetime.now()} - ERROR\n")

                error_file.write(f"{'='*60}\n")

                error_file.write(f"Error: {error_msg}\n")

                error_file.write(f"Traceback:\n{tb}\n")

        except:

            pass

        

        write_debug_log("=== SCRIPT FAILED ===\n")

        return False



if __name__ == "__main__":

    print("="*60)

    print("ATTENDANCE MARKER - Starting...")

    print("="*60)

    print()

    

    result = mark_attendance()

    

    print()

    print("="*60)

    if result:

        print("STATUS: SUCCESS")

    else:

        print("STATUS: FAILED")

    print("="*60)

    

    print("\nWindow will close in 10 seconds...")

    time.sleep(10)