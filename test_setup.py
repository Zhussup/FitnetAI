#!/usr/bin/env python3
"""
Test script to verify the application setup
"""

import sys
import subprocess

def test_imports():
    """Test if all required packages can be imported"""
    packages = [
        'fastapi',
        'uvicorn',
        'dotenv',
        'google.generativeai',
        'bcrypt',
        'sqlalchemy'
    ]
    
    print("Testing imports...")
    for package in packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError as e:
            print(f"✗ {package}: {e}")
            return False
    return True

def test_syntax():
    """Test Python syntax"""
    print("\nTesting main.py syntax...")
    result = subprocess.run([sys.executable, "-m", "py_compile", "main.py"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ main.py syntax is correct")
        return True
    else:
        print(f"✗ Syntax error: {result.stderr}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("FitnetAI Project Tests")
    print("=" * 50)
    
    if test_imports() and test_syntax():
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed")
        sys.exit(1)
