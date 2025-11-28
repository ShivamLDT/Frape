#!/usr/bin/env python3
"""
Quick test script to verify beam installation and basic functionality
"""
import sys
import subprocess
import shutil


def test_command(cmd, description):
    """Test a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print(f"Output:\n{result.stdout}")
        if result.stderr:
            print(f"Errors:\n{result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("ERROR: Command timed out")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    """Run all tests"""
    print("Beam Installation Test Suite")
    print("="*60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Check if beam is installed
    if shutil.which("beam"):
        print("\n✓ Beam command found in PATH")
        tests_passed += 1
    else:
        print("\n✗ Beam command not found in PATH")
        print("  Try running: pip install -e .")
        tests_failed += 1
        return
    
    # Test 2: beam --version
    if test_command(["beam", "--version"], "Beam version"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 3: beam --help
    if test_command(["beam", "--help"], "Beam help"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 4: beam saas --help
    if test_command(["beam", "saas", "--help"], "SaaS help"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 5: Check if bench is available
    if shutil.which("bench"):
        print("\n✓ Bench command found (required for full functionality)")
        tests_passed += 1
        
        # Test 6: Compare beam and bench help (should forward correctly)
        if test_command(["beam", "init", "--help"], "Beam init help (forwarding to bench)"):
            tests_passed += 1
        else:
            tests_failed += 1
    else:
        print("\n⚠ Bench command not found")
        print("  Install with: pip install frappe-bench")
        print("  Beam will work but bench commands won't function")
        tests_failed += 1
    
    # Test 7: Test SaaS placeholder commands
    saas_commands = ["deploy", "scale", "monitor", "logs", "status"]
    for cmd in saas_commands:
        if test_command(["beam", cmd], f"SaaS command: {cmd}"):
            tests_passed += 1
        else:
            tests_failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Tests passed: {tests_passed}")
    print(f"Tests failed: {tests_failed}")
    print(f"Total tests: {tests_passed + tests_failed}")
    
    if tests_failed == 0:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed. See output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

