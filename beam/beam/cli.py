"""
Beam CLI - Main entry point that wraps bench commands and adds SaaS functionality
"""
import sys
import subprocess
import shutil
import platform
import os
from pathlib import Path


def is_git_bash():
    """Check if running in Git Bash"""
    # Git Bash sets these environment variables
    return (
        os.environ.get("MSYSTEM", "").startswith("MINGW") or
        "Git" in os.environ.get("SHELL", "") or
        "bash.exe" in os.environ.get("_", "")
    )


def is_wsl_available():
    """Check if WSL is available on Windows"""
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


def get_wsl_beam_path():
    """Get the path to beam in WSL"""
    # Convert Windows path to WSL path
    current_path = os.path.abspath(os.getcwd())
    if current_path.startswith("C:\\"):
        wsl_path = current_path.replace("C:\\", "/mnt/c/").replace("\\", "/")
    elif current_path.startswith("C:"):
        wsl_path = current_path.replace("C:", "/mnt/c").replace("\\", "/")
    else:
        # Try to find beam installation
        wsl_path = "~/.local/bin/beam"
    
    return wsl_path


def get_wsl_beam_path():
    """Get the path to beam executable in WSL"""
    # Try common locations - check /mnt/c/ first (most common)
    # Note: /mnt/c/ is standard, /mnt/host/c/ is used by some WSL2 configurations
    possible_paths = [
        "/mnt/c/Users/LDT/frappe/beam/.venv/bin/beam",  # Standard WSL path
        "/mnt/host/c/Users/LDT/frappe/beam/.venv/bin/beam",  # Alternative WSL2 path
        "~/.local/bin/beam",
        "/usr/local/bin/beam",
        "/usr/bin/beam",
    ]
    
    # Check which one exists using Ubuntu distribution
    for path in possible_paths:
        try:
            # Use sh -c to properly execute the test command
            result = subprocess.run(
                ["wsl", "-d", "Ubuntu", "sh", "-c", f"test -f '{path}'"],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                return path
        except:
            continue
    
    # If none found, try to find it using which
    try:
        result = subprocess.run(
            ["wsl", "-d", "Ubuntu", "which", "beam"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return None


def run_in_wsl(args):
    """Run beam command in WSL, hiding bench completely"""
    # Check if WSL is available
    if not is_wsl_available():
        print(
            "\n❌ WSL Not Available\n"
            "Beam requires WSL on Windows. Please install WSL:\n"
            "  wsl --install\n\n"
            "Run PowerShell as Administrator and execute: wsl --install",
            file=sys.stderr
        )
        sys.exit(1)
    
    # Try to start Ubuntu if it's not running
    try:
        # Test if Ubuntu is accessible
        test_result = subprocess.run(
            ["wsl", "-d", "Ubuntu", "--", "echo", "test"],
            capture_output=True,
            timeout=5
        )
        if test_result.returncode != 0:
            print(
                "\n⚠️  Ubuntu WSL is not running or accessible.\n"
                "Trying to start it...",
                file=sys.stderr
            )
            # Try to start Ubuntu
            subprocess.run(
                ["wsl", "-d", "Ubuntu", "--", "echo", "started"],
                timeout=10
            )
    except subprocess.TimeoutExpired:
        print(
            "\n❌ WSL Timeout\n"
            "Ubuntu WSL is not responding. Please try:\n"
            "  1. Open Ubuntu manually: wsl -d Ubuntu\n"
            "  2. Wait for it to start\n"
            "  3. Then try beam again",
            file=sys.stderr
        )
        sys.exit(1)
    except Exception as e:
        # Continue anyway - might work
        pass
    
    # Try to find beam in WSL
    beam_path = get_wsl_beam_path()
    
    if beam_path:
        # Use full path to beam with Ubuntu distribution
        wsl_cmd = ["wsl", "-d", "Ubuntu", beam_path] + args
    else:
        # Fallback: try just "beam" (might be in PATH)
        wsl_cmd = ["wsl", "-d", "Ubuntu", "beam"] + args
    
    # Execute in WSL
    try:
        result = subprocess.run(
            wsl_cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=30
        )
        
        # Check for WSL service errors
        if "Catastrophic failure" in result.stderr or "E_UNEXPECTED" in result.stderr:
            print(
                "\n❌ WSL Service Error\n"
                "WSL is having issues. Try these steps:\n\n"
                "1. Restart WSL service:\n"
                "   wsl --shutdown\n"
                "   wsl -d Ubuntu\n\n"
                "2. If that doesn't work, restart your computer\n\n"
                "3. Then try beam again",
                file=sys.stderr
            )
            return 1
        
        # If beam command not found, provide helpful message
        if result.returncode != 0 and ("not found" in result.stderr.lower() or "command not found" in result.stderr.lower()):
            # Beam not installed in WSL - provide helpful message
            print(
                "\n❌ Beam Not Found in WSL\n"
                "Beam needs to be installed in WSL to work from PowerShell.\n\n"
                "Quick Setup (One Time Only):\n"
                "  1. Open Ubuntu WSL: wsl -d Ubuntu\n"
                "  2. Navigate to beam: cd /mnt/c/Users/LDT/frappe/beam\n"
                "  3. Create venv: python3 -m venv .venv\n"
                "  4. Activate: source .venv/bin/activate\n"
                "  5. Install: pip install -e .\n"
                "  6. Add to PATH: echo 'export PATH=\"\\$PATH:/mnt/c/Users/LDT/frappe/beam/.venv/bin\"' >> ~/.bashrc\n"
                "  7. Close WSL and use beam from PowerShell\n\n"
                "See SETUP_UBUNTU.md for detailed instructions.",
                file=sys.stderr
            )
            return 1
        
        # Print output
        if result.stdout:
            print(result.stdout, end='')
        if result.stderr:
            print(result.stderr, end='', file=sys.stderr)
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print("Error: Command timed out in WSL", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        print(f"Error running in WSL: {e}", file=sys.stderr)
        return 1


def ensure_bench_installed():
    """Check if bench is installed, if not, provide helpful error message"""
    bench_path = shutil.which("bench")
    if not bench_path:
        print(
            "Error: 'bench' command not found.\n"
            "Please install frappe-bench first:\n"
            "  pip install frappe-bench\n\n"
            "Or if you're developing beam, install it with bench as a dependency.",
            file=sys.stderr
        )
        sys.exit(1)
    return bench_path


def is_saas_command(args):
    """Check if the command is a SaaS-specific command"""
    saas_commands = [
        "deploy",
        "scale",
        "monitor",
        "logs",
        "status",
        "saas",
    ]
    return args and args[0] in saas_commands


def handle_saas_command(args):
    """Handle SaaS-specific commands"""
    command = args[0] if args else None
    
    if command == "deploy":
        from beam.saas import deploy
        return deploy.main(args[1:])
    elif command == "scale":
        from beam.saas import scale
        return scale.main(args[1:])
    elif command == "monitor":
        from beam.saas import monitor
        return monitor.main(args[1:])
    elif command == "logs":
        from beam.saas import logs
        return logs.main(args[1:])
    elif command == "status":
        from beam.saas import status
        return status.main(args[1:])
    elif command == "saas":
        from beam.saas import saas_help
        return saas_help.main(args[1:])
    else:
        print(f"Unknown SaaS command: {command}", file=sys.stderr)
        print("Run 'beam saas --help' for available SaaS commands", file=sys.stderr)
        return 1


def forward_to_bench(args):
    """Forward command to bench (bench is completely hidden from user)"""
    # On Windows, run in WSL automatically
    if platform.system() == "Windows":
        return run_in_wsl(args)
    
    ensure_bench_installed()
    
    # Build bench command (hidden from user - they only see beam)
    bench_cmd = ["bench"] + args
    
    # Execute bench with same arguments, preserving exit codes
    try:
        result = subprocess.run(bench_cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        return 130
    except ModuleNotFoundError as e:
        if "pwd" in str(e) or "Unix" in str(e):
            print(
                "\n❌ Error: Bench requires Unix-like system (Linux/macOS/WSL)\n"
                "The 'pwd' module is Unix-specific and not available on Windows.\n\n"
                "If on Windows, beam should automatically use WSL.\n"
                "If this error persists, ensure WSL is installed: wsl --install",
                file=sys.stderr
            )
        else:
            print(f"Error: Missing module - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error executing bench: {e}", file=sys.stderr)
        return 1


def main():
    """Main entry point for beam CLI"""
    args = sys.argv[1:]
    
    # Handle help for beam itself
    if not args or args[0] in ["--help", "-h"]:
        show_beam_help()
        return 0
    
    # Handle version
    if args[0] == "--version" or args[0] == "-v":
        from beam import __version__
        print(f"beam version {__version__}")
        return 0
    
    # Check if it's a SaaS command
    if is_saas_command(args):
        # On Windows, SaaS commands can run natively or in WSL
        # For now, if on Windows and WSL available, use WSL for consistency
        if platform.system() == "Windows" and is_wsl_available():
            return run_in_wsl(args)
        return handle_saas_command(args)
    
    # For bench commands, automatically use WSL on Windows
    # Bench is completely hidden - user only interacts with beam
    return forward_to_bench(args)


def show_beam_help():
    """Show beam-specific help"""
    is_windows = platform.system() == "Windows"
    is_gitbash = is_git_bash()
    windows_note = ""
    
    if is_windows:
        if is_gitbash:
            windows_note = """
✅ Git Bash Detected - Beam will automatically use WSL for commands.
   You can use beam commands directly from Git Bash!

"""
        elif is_wsl_available():
            windows_note = """
✅ WSL Detected - Beam will automatically use WSL for commands.
   You can use beam commands directly from PowerShell or Git Bash!

"""
        else:
            windows_note = """
⚠️  Windows Detected - WSL Required
   Beam automatically uses WSL on Windows.
   Install WSL: wsl --install (run PowerShell as Administrator)
   Then use beam commands from PowerShell or Git Bash - no need to open WSL!

"""
    
    help_text = f"""Beam - SaaS-Ready Frappe Management Tool
{windows_note}Usage:
    beam [command] [options]

Core Commands:
    init              Initialize a new beam instance
    start             Start development processes
    new-site          Create a new site
    get-app           Download and add an app
    install-app       Install app on a site
    update            Update beam, apps, and sites
    setup             Setup production environment
    config            Configure beam settings
    ... and all other commands

SaaS Commands:
    deploy            Deploy application to cloud
    scale             Scale application resources
    monitor           Monitor application health
    logs              View application logs
    status            Check application status
    saas              Show SaaS command help

Examples:
    beam init my-app
    beam new-site example.com
    beam start
    beam deploy production
    beam status

For more information on a specific command:
    beam [command] --help

For SaaS-specific help:
    beam saas --help
"""
    print(help_text)


if __name__ == "__main__":
    sys.exit(main())

