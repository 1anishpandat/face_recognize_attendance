import os
import sys
import subprocess
import winreg
import shutil

def check_admin():
    """Check if running as administrator"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def create_batch_file():
    """Create the shutdown batch file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    startup_dir = os.path.join(script_dir, 'startup')
    
    if not os.path.exists(startup_dir):
        os.makedirs(startup_dir)
    
    batch_path = os.path.join(startup_dir, 'mark_shutdown.bat')
    
    batch_content = '''@echo off
REM SHUTDOWN ATTENDANCE MARKER - BLOCKING VERSION
setlocal

echo ======================================================================== >> "%TEMP%\\shutdown_log.txt"
echo SHUTDOWN MARKER STARTED: %date% %time% >> "%TEMP%\\shutdown_log.txt"

cd /d "%~dp0"
if exist "..\\src\\mark_shutdown.py" cd ..

if not exist "logs" mkdir logs

python.exe src\\mark_shutdown.py
set EXIT_CODE=%ERRORLEVEL%

echo Python exit: %EXIT_CODE% at %time% >> "%TEMP%\\shutdown_log.txt"

timeout /t 2 /nobreak >nul

exit /b %EXIT_CODE%
'''
    
    with open(batch_path, 'w') as f:
        f.write(batch_content)
    
    print(f"✓ Created batch file: {batch_path}")
    return batch_path

def setup_shutdown_script(batch_path):
    """Setup shutdown script using CORRECT method for Windows 10/11"""
    
    try:
        print("\n" + "=" * 70)
        print("SETTING UP SHUTDOWN SCRIPT")
        print("=" * 70)
        print()
        
        # METHOD 1: Use gpedit.msc scripts location
        # This is where Windows actually reads shutdown scripts from
        
        # Get Windows directory
        windows_dir = os.environ.get('SystemRoot', 'C:\\Windows')
        scripts_dir = os.path.join(windows_dir, 'System32', 'GroupPolicy', 'Machine', 'Scripts', 'Shutdown')
        
        # Create scripts directory
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir)
            print(f"✓ Created scripts directory: {scripts_dir}")
        
        # Copy batch file to scripts directory
        dest_batch = os.path.join(scripts_dir, 'mark_shutdown.bat')
        shutil.copy2(batch_path, dest_batch)
        print(f"✓ Copied batch file to: {dest_batch}")
        
        # Create scripts.ini file
        ini_path = os.path.join(os.path.dirname(scripts_dir), 'scripts.ini')
        ini_content = f'''[Shutdown]
0CmdLine={dest_batch}
0Parameters=
'''
        
        with open(ini_path, 'w') as f:
            f.write(ini_content)
        print(f"✓ Created scripts.ini: {ini_path}")
        
        # METHOD 2: Also set registry for redundancy
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\State\Machine\Scripts\Shutdown\0"
        
        try:
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            winreg.SetValueEx(key, "Script", 0, winreg.REG_SZ, dest_batch)
            winreg.SetValueEx(key, "Parameters", 0, winreg.REG_SZ, "")
            winreg.SetValueEx(key, "IsPowershell", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "ExecTime", 0, winreg.REG_QWORD, 0)
            winreg.CloseKey(key)
            print("✓ Registry configured")
        except Exception as e:
            print(f"⚠ Registry warning: {e}")
        
        # Update Group Policy
        print("\nUpdating Group Policy...")
        subprocess.run("gpupdate /force", shell=True, capture_output=True)
        
        print()
        print("=" * 70)
        print("✓ SETUP COMPLETE!")
        print("=" * 70)
        print()
        print("CRITICAL: You MUST restart your computer now!")
        print()
        print("After restart:")
        print("  1. Log in normally")
        print("  2. Shut down your computer")
        print("  3. Turn back on and check:")
        print("     - Desktop/attendance_shutdown_debug.txt")
        print("     - logs/attendance_log.csv (look for 'Shutdown' entry)")
        print()
        
        return True
        
    except PermissionError:
        print("\n✗ PERMISSION DENIED!")
        print("\nYou MUST run as Administrator:")
        print("  1. Right-click Command Prompt")
        print("  2. Select 'Run as administrator'")
        print("  3. Navigate to project folder")
        print(f"  4. Run: python {os.path.basename(__file__)}")
        return False
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_shutdown_script():
    """Test the shutdown script"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    python_script = os.path.join(script_dir, 'src', 'mark_shutdown.py')
    
    print("\n" + "=" * 70)
    print("TESTING SHUTDOWN SCRIPT")
    print("=" * 70)
    print()
    
    if not os.path.exists(python_script):
        print(f"✗ Script not found: {python_script}")
        return False
    
    print("Running mark_shutdown.py...")
    print()
    
    result = subprocess.run([sys.executable, python_script], capture_output=True, text=True)
    
    print(f"Exit code: {result.returncode}")
    
    if result.stdout:
        print("\nOutput:")
        print(result.stdout)
    
    if result.stderr:
        print("\nErrors:")
        print(result.stderr)
    
    print("\nCheck these files:")
    print("  - Desktop/attendance_shutdown_debug.txt")
    print("  - logs/attendance_log.csv")
    print()
    
    return result.returncode == 0

def remove_shutdown_script():
    """Remove shutdown script"""
    try:
        print("\n" + "=" * 70)
        print("REMOVING SHUTDOWN SCRIPT")
        print("=" * 70)
        print()
        
        windows_dir = os.environ.get('SystemRoot', 'C:\\Windows')
        scripts_dir = os.path.join(windows_dir, 'System32', 'GroupPolicy', 'Machine', 'Scripts', 'Shutdown')
        dest_batch = os.path.join(scripts_dir, 'mark_shutdown.bat')
        
        if os.path.exists(dest_batch):
            os.remove(dest_batch)
            print(f"✓ Removed: {dest_batch}")
        
        ini_path = os.path.join(os.path.dirname(scripts_dir), 'scripts.ini')
        if os.path.exists(ini_path):
            os.remove(ini_path)
            print(f"✓ Removed: {ini_path}")
        
        # Remove registry
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\State\Machine\Scripts\Shutdown\0"
            winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            print("✓ Removed registry entries")
        except:
            pass
        
        subprocess.run("gpupdate /force", shell=True, capture_output=True)
        
        print("\n✓ Shutdown script removed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("\n" + "=" * 70)
    print("SHUTDOWN ATTENDANCE TRACKING - FINAL SETUP")
    print("=" * 70)
    print()
    
    if sys.platform != 'win32':
        print("✗ This script only works on Windows!")
        input("\nPress Enter to exit...")
        return
    
    if not check_admin():
        print("✗ NOT RUNNING AS ADMINISTRATOR!")
        print("\nYou MUST run this as Administrator.")
        print("\nHow to run as Administrator:")
        print("  1. Press Windows key + X")
        print("  2. Click 'Command Prompt (Admin)' or 'PowerShell (Admin)'")
        print("  3. Navigate to project folder")
        print(f"  4. Run: python {os.path.basename(__file__)}")
        print()
        input("Press Enter to exit...")
        return
    
    print("✓ Running as Administrator")
    print()
    
    while True:
        print("=" * 70)
        print("MENU")
        print("=" * 70)
        print()
        print("  1. Setup shutdown tracking (RECOMMENDED)")
        print("  2. Test shutdown script manually")
        print("  3. Remove shutdown tracking")
        print("  4. Exit")
        print()
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == '1':
            batch_path = create_batch_file()
            setup_shutdown_script(batch_path)
            
        elif choice == '2':
            test_shutdown_script()
            
        elif choice == '3':
            remove_shutdown_script()
            
        elif choice == '4':
            break
            
        else:
            print("\n✗ Invalid choice")
        
        print()
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()

