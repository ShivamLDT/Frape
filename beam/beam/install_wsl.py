"""
Automatic WSL installation helper
This script installs beam in WSL when beam is installed on Windows
"""
import subprocess
import sys
import platform
import os


def is_wsl_available():
    """Check if WSL is available"""
    if platform.system() != "Windows":
        return False
    try:
        result = subprocess.run(
            ["wsl", "--status"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_wsl_python():
    """Check if Python/pip is available in WSL"""
    try:
        result = subprocess.run(
            ["wsl", "which", "python3"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False


def check_wsl_pipx():
    """Check if pipx is available in WSL"""
    try:
        result = subprocess.run(
            ["wsl", "which", "pipx"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False


def install_beam_in_wsl():
    """Install beam in WSL automatically"""
    if not is_wsl_available():
        print("\n⚠️  WSL not detected. Beam will work, but you'll need WSL to use bench commands.")
        print("   Install WSL: wsl --install (run PowerShell as Administrator)")
        return False
    
    # Check if Python is installed in WSL
    if not check_wsl_python():
        print("\n⚠️  Python not found in WSL.")
        print("   Please install Python in WSL first:")
        print("   1. Open WSL: wsl")
        print("   2. Run: sudo apt update")
        print("   3. Run: sudo apt install python3 python3-pip python3-venv")
        print("   4. Then reinstall beam: pip install -e .")
        return False
    
    # Check if pipx is available (preferred for CLI tools)
    has_pipx = check_wsl_pipx()
    
    print("\n🔧 Detected WSL - Installing beam in WSL automatically...")
    
    # Get the current directory (beam source)
    current_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # Convert Windows path to WSL path
    if current_dir.startswith("C:\\"):
        wsl_path = current_dir.replace("C:\\", "/mnt/c/").replace("\\", "/")
    elif current_dir.startswith("C:"):
        wsl_path = current_dir.replace("C:", "/mnt/c").replace("\\", "/")
    else:
        print("⚠️  Could not determine WSL path. Please install beam in WSL manually.")
        print(f"   Path: {current_dir}")
        return False
    
    # First verify the path exists in WSL
    check_path_cmd = ["wsl", "test", "-d", wsl_path]
    path_check = subprocess.run(check_path_cmd, capture_output=True, timeout=5)
    
    if path_check.returncode != 0:
        print(f"⚠️  Path not accessible in WSL: {wsl_path}")
        print("   This might be a WSL configuration issue.")
        print("   You can install manually:")
        print(f"   1. Open WSL: wsl")
        print(f"   2. Find the correct path (try: ls /mnt/c/Users/)")
        print(f"   3. Navigate to beam directory")
        print(f"   4. Run: pip3 install -e .")
        return False
    
    # Build WSL command to install beam
    # Try pipx first (best for CLI tools), then venv, then system with flag
    if has_pipx:
        # Use pipx for CLI tool installation
        install_cmd = [
            "wsl",
            "bash",
            "-c",
            f"cd {wsl_path} && pipx install -e ."
        ]
        install_method = "pipx"
    else:
        # Use venv to avoid externally-managed-environment error
        install_cmd = [
            "wsl",
            "bash",
            "-c",
            f"cd {wsl_path} && python3 -m venv .venv && .venv/bin/pip install -e . --quiet"
        ]
        install_method = "venv"
    
    try:
        print(f"   Installing in WSL at: {wsl_path} (using {install_method})")
        result = subprocess.run(
            install_cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            if install_method == "venv":
                print("✅ Successfully installed beam in WSL (using virtual environment)!")
                print("   Note: Beam is installed in .venv - make sure it's in your PATH")
            else:
                print("✅ Successfully installed beam in WSL!")
            print("   You can now use beam commands from PowerShell.")
            return True
        else:
            # If venv method failed, try with --break-system-packages as last resort
            if install_method == "venv" and "externally-managed" in result.stderr:
                print("   Trying alternative installation method...")
                alt_cmd = [
                    "wsl",
                    "bash",
                    "-c",
                    f"cd {wsl_path} && pip3 install -e . --break-system-packages --quiet"
                ]
                alt_result = subprocess.run(
                    alt_cmd,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if alt_result.returncode == 0:
                    print("✅ Successfully installed beam in WSL!")
                    print("   You can now use beam commands from PowerShell.")
                    return True
            
            print("⚠️  Installation in WSL had issues:")
            if result.stderr:
                # Show relevant error messages
                error_lines = result.stderr.strip().split('\n')
                for line in error_lines[-5:]:  # Show last 5 lines
                    if line.strip() and "error" in line.lower():
                        print(f"   {line}")
            
            # Provide manual installation instructions
            print("\n   Manual installation options:")
            print(f"   Option 1 (Recommended - Using venv):")
            print(f"     1. Open WSL: wsl")
            print(f"     2. Run: cd {wsl_path}")
            print(f"     3. Run: python3 -m venv .venv")
            print(f"     4. Run: .venv/bin/pip install -e .")
            print(f"     5. Add to PATH: export PATH=\"$PATH:{wsl_path}/.venv/bin\"")
            print(f"\n   Option 2 (Using pipx - Best for CLI tools):")
            print(f"     1. Open WSL: wsl")
            print(f"     2. Run: sudo apt install pipx")
            print(f"     3. Run: cd {wsl_path}")
            print(f"     4. Run: pipx install -e .")
            print(f"\n   Option 3 (System-wide - Not recommended):")
            print(f"     1. Open WSL: wsl")
            print(f"     2. Run: cd {wsl_path}")
            print(f"     3. Run: pip3 install -e . --break-system-packages")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Installation timed out. Please install manually in WSL.")
        return False
    except Exception as e:
        print(f"⚠️  Error installing in WSL: {e}")
        print("\n   You can install manually:")
        print(f"   1. Open WSL: wsl")
        print(f"   2. Run: cd {wsl_path}")
        print(f"   3. Run: pip3 install -e .")
        return False


if __name__ == "__main__":
    # Only run on Windows
    if platform.system() == "Windows":
        install_beam_in_wsl()
    else:
        print("Not Windows - WSL installation skipped.")

