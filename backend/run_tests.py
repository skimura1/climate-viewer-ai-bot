#!/usr/bin/env python3
"""
Simple test runner for the climate viewer AI bot backend.
Run this script to execute all tests without using API tokens.
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests using pytest"""
    print("🧪 Running Climate Agent Tests...")
    print("=" * 50)
    
    # Change to backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Run tests with pytest
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "test_climate_agent.py",
            "test_main.py",
            "-v",
            "--tb=short"
        ], capture_output=True, text=True)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        # Print summary
        print("=" * 50)
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print(f"❌ Some tests failed (exit code: {result.returncode})")
            
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

def run_specific_test(test_file):
    """Run a specific test file"""
    print(f"🧪 Running {test_file}...")
    print("=" * 50)
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            test_file,
            "-v",
            "--tb=short"
        ], capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        print("=" * 50)
        if result.returncode == 0:
            print("✅ Test passed!")
        else:
            print(f"❌ Test failed (exit code: {result.returncode})")
            
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test file
        test_file = sys.argv[1]
        exit_code = run_specific_test(test_file)
    else:
        # Run all tests
        exit_code = run_tests()
    
    sys.exit(exit_code)
