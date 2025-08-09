#!/usr/bin/env python3
"""
Script chạy test cases cho Chat API
Sử dụng để test tất cả functionality của chat với các ngôn ngữ khác nhau
"""

import os
import sys
import unittest
import subprocess

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

def run_unit_tests():
    """Chạy unit tests với unittest"""
    print("Running Unit Tests...\n")
    
    # Chạy test file
    test_file = os.path.join(backend_dir, 'tests', 'test_chat.py')
    
    if os.path.exists(test_file):
        try:
            # Run the test file
            result = subprocess.run([
                sys.executable, '-m', 'unittest', 
                'tests.test_chat', '-v'
            ], cwd=backend_dir, capture_output=True, text=True)
            
            print("STDOUT:")
            print(result.stdout)
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
                
            return result.returncode == 0
        except Exception as e:
            print(f"Error running unit tests: {e}")
            return False
    else:
        print(f"Test file not found: {test_file}")
        return False

def run_java_examples():
    """Chạy Java example tests"""
    print("\nRunning Java Example Tests...\n")
    
    try:
        # Import và chạy Java examples
        from tests.test_java_examples import run_all_java_tests
        run_all_java_tests()
        return True
    except Exception as e:
        print(f"Error running Java examples: {e}")
        return False

def check_dependencies():
    """Kiểm tra dependencies"""
    print("Checking Dependencies...\n")
    
    required_packages = [
        'flask',
        'unittest',
        'json'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"OK {package}")
        except ImportError:
            print(f"MISSING {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Please install them before running tests.")
        return False
    
    print("\nAll dependencies are available.\n")
    return True

def main():
    """Main function để chạy tất cả tests"""
    print("AI Programming Assistant - Chat API Test Suite")
    print("="*60)
    
    # Check dependencies first
    if not check_dependencies():
        return
    
    success_count = 0
    total_tests = 2
    
    # Run unit tests
    if run_unit_tests():
        print("PASS Unit tests passed")
        success_count += 1
    else:
        print("FAIL Unit tests failed")
    
    # Run Java examples
    if run_java_examples():
        print("PASS Java examples completed")
        success_count += 1
    else:
        print("FAIL Java examples failed")
    
    # Summary
    print("\n" + "="*60)
    print("Test Results Summary:")
    print(f"Passed: {success_count}/{total_tests}")
    print(f"Failed: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("\nAll tests completed successfully!")
        print("\nTest Coverage:")
        print("- Chat API endpoints")
        print("- Java code explanation")
        print("- Quick actions (comment, debug)")
        print("- Error handling")
        print("- Input validation")
        print("- Performance tests")
    else:
        print("\nSome tests failed. Please check the output above.")
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("1. Fix any failing tests")
    print("2. Add more language examples (Python, JavaScript, etc.)")
    print("3. Test with real Azure OpenAI integration")
    print("4. Add integration tests with frontend")

if __name__ == "__main__":
    main()
