"""
Quick Test Validation Script

This script runs a few basic tests to validate that the test suite is properly configured
and can execute successfully. Use this for quick verification before running the full suite.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return success/failure"""
    print(f"\n🔍 {description}")
    print("-" * 40)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ SUCCESS")
        if result.stdout:
            print("Output:", result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        print("Error:", e.stderr[:200] if e.stderr else str(e))
        return False

def main():
    print("🧪 Document AI Q&A System - Test Validation")
    print("="*50)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Error: main.py not found. Please run from project root directory.")
        return False
    
    # Check if test files exist
    test_files = ["test_comprehensive_suite.py", "conftest.py", "pytest.ini"]
    missing_files = [f for f in test_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing test files: {', '.join(missing_files)}")
        return False
    
    print("✅ All test files found")
    
    # Test 1: Check pytest installation
    if not run_command([sys.executable, "-m", "pytest", "--version"], "Checking pytest installation"):
        print("💡 Try: pip install pytest pytest-asyncio")
        return False
    
    # Test 2: Validate test collection
    if not run_command([sys.executable, "-m", "pytest", "--collect-only", "-q"], "Collecting tests"):
        return False
    
    # Test 3: Run a simple unit test
    test_cmd = [
        sys.executable, "-m", "pytest", 
        "test_comprehensive_suite.py::TestDocumentChunking::test_chunking_empty_or_whitespace_text",
        "-v", "--tb=short"
    ]
    if not run_command(test_cmd, "Running sample unit test"):
        return False
    
    # Test 4: Validate test markers
    if not run_command([sys.executable, "-m", "pytest", "--markers"], "Checking test markers"):
        return False
    
    print("\n" + "="*50)
    print("🎉 Test validation completed successfully!")
    print("\nNext steps:")
    print("  • Run full test suite: python run_tests.py --all")
    print("  • Run specific tests: python run_tests.py --unit")
    print("  • Run with coverage: python run_tests.py --coverage")
    print("  • Quick development tests: python run_tests.py --quick")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
