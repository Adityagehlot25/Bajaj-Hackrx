#!/usr/bin/env python3
"""
Test runner script for HackRx API tests.

This script provides convenient commands for running different test suites
and handles environment setup for testing.

Usage:
    python run_hackrx_tests.py                    # Run all HackRx API tests
    python run_hackrx_tests.py --unit             # Run only unit tests
    python run_hackrx_tests.py --integration      # Run only integration tests
    python run_hackrx_tests.py --auth             # Run only auth tests
    python run_hackrx_tests.py --coverage         # Run with coverage report
    python run_hackrx_tests.py --verbose          # Verbose output
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path


def setup_environment():
    """Set up environment variables and paths for testing."""
    # Add current directory to Python path
    current_dir = Path(__file__).parent.absolute()
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Set test environment variables if not already set
    os.environ.setdefault('TESTING', 'true')
    os.environ.setdefault('PYTHONPATH', str(current_dir))
    
    # Load environment variables from .env if it exists
    env_file = current_dir / '.env'
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print(f"✅ Loaded environment variables from {env_file}")
        except ImportError:
            print("⚠️  python-dotenv not installed, skipping .env file loading")


def check_dependencies():
    """Check if required testing dependencies are installed."""
    required_packages = [
        ('pytest', 'pytest'),
        ('fastapi', 'fastapi'),
        ('httpx', 'httpx'),
    ]
    
    missing_packages = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("❌ Missing required testing packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall missing packages with:")
        print("pip install -r requirements_test.txt")
        return False
    
    print("✅ All required testing packages are installed")
    return True


def run_tests(test_args: list):
    """
    Run pytest with the specified arguments.
    
    Args:
        test_args: List of arguments to pass to pytest
    """
    # Base pytest command
    cmd = ['python', '-m', 'pytest']
    
    # Add test arguments
    cmd.extend(test_args)
    
    print(f"🚀 Running: {' '.join(cmd)}")
    print("=" * 60)
    
    # Run the tests
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='Run HackRx API tests')
    
    # Test selection options
    parser.add_argument('--unit', action='store_true', 
                       help='Run only unit tests')
    parser.add_argument('--integration', action='store_true',
                       help='Run only integration tests')  
    parser.add_argument('--api', action='store_true',
                       help='Run only API endpoint tests')
    parser.add_argument('--auth', action='store_true',
                       help='Run only authentication tests')
    parser.add_argument('--hackrx', action='store_true',
                       help='Run only HackRx specific tests')
    
    # Output options
    parser.add_argument('--coverage', action='store_true',
                       help='Run with coverage report')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose test output')
    parser.add_argument('--quiet', action='store_true',
                       help='Quiet test output')
    
    # Test file options
    parser.add_argument('--file', type=str,
                       help='Run specific test file')
    parser.add_argument('--test', type=str,
                       help='Run specific test function')
    
    # Additional pytest options
    parser.add_argument('--no-cov', action='store_true',
                       help='Disable coverage reporting')
    parser.add_argument('--html-cov', action='store_true',
                       help='Generate HTML coverage report')
    
    args = parser.parse_args()
    
    # Set up environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Build pytest command arguments
    test_args = []
    
    # Test selection markers
    markers = []
    if args.unit:
        markers.append('unit')
    if args.integration:
        markers.append('integration')
    if args.api:
        markers.append('api')
    if args.auth:
        markers.append('auth')  
    if args.hackrx:
        markers.append('hackrx')
    
    if markers:
        test_args.extend(['-m', ' or '.join(markers)])
    
    # Specific file or test
    if args.file:
        test_args.append(args.file)
        if args.test:
            test_args[-1] += f'::{args.test}'
    elif args.test:
        # If test specified but no file, assume it's in the main test file
        test_args.append(f'test_hackrx_api.py::{args.test}')
    else:
        # Default: run HackRx API tests
        test_args.append('test_hackrx_api.py')
    
    # Output options
    if args.verbose:
        test_args.extend(['-v', '--tb=long'])
    elif args.quiet:
        test_args.append('-q')
    
    # Coverage options
    if args.coverage and not args.no_cov:
        test_args.extend([
            '--cov=hackrx_api_fixed',
            '--cov=robust_document_parser', 
            '--cov=gemini_vector_embedder',
            '--cov=faiss_store',
            '--cov=gemini_answer',
            '--cov-report=term-missing'
        ])
        
        if args.html_cov:
            test_args.append('--cov-report=html:htmlcov')
    
    # Additional useful options for API testing
    test_args.extend([
        '--tb=short',
        '--durations=10'  # Show slowest 10 tests
    ])
    
    # Run the tests
    return run_tests(test_args)


if __name__ == '__main__':
    """Entry point for the test runner."""
    try:
        exit_code = main()
        if exit_code == 0:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n❌ Tests failed with exit code {exit_code}")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Test runner interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        sys.exit(1)
