#!/usr/bin/env python3
"""
Comprehensive Test Runner for Document AI Q&A System

This script provides an easy way to run different categories of tests
with proper configuration and reporting.

Usage:
    python run_tests.py --all                    # Run all tests
    python run_tests.py --unit                   # Run only unit tests
    python run_tests.py --integration            # Run only integration tests
    python run_tests.py --performance            # Run only performance tests
    python run_tests.py --security               # Run only security tests
    python run_tests.py --quick                  # Run quick tests (exclude slow)
    python run_tests.py --coverage               # Run tests with detailed coverage
    python run_tests.py --verbose                # Run with verbose output
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

def run_pytest_command(args_list, description):
    """Run pytest with specified arguments"""
    print(f"\n🚀 {description}")
    print("=" * 60)
    
    cmd = ["python", "-m", "pytest"] + args_list
    print(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
    else:
        print(f"❌ {description} - FAILED")
    
    return result.returncode

def main():
    parser = argparse.ArgumentParser(
        description="Test runner for Document AI Q&A System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Test categories
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--security", action="store_true", help="Run security tests only")
    parser.add_argument("--explainability", action="store_true", help="Run explainability tests only")
    
    # Test modes
    parser.add_argument("--quick", action="store_true", help="Run quick tests (exclude slow)")
    parser.add_argument("--slow", action="store_true", help="Run only slow tests")
    parser.add_argument("--coverage", action="store_true", help="Run with detailed coverage reporting")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--debug", action="store_true", help="Debug mode with extra logging")
    
    # Specific test files
    parser.add_argument("--file", type=str, help="Run specific test file")
    parser.add_argument("--test", type=str, help="Run specific test function")
    
    args = parser.parse_args()
    
    # Base pytest arguments
    base_args = []
    
    # Add verbosity
    if args.verbose or args.debug:
        base_args.append("-v")
    if args.debug:
        base_args.extend(["--log-cli", "--log-cli-level=DEBUG"])
    
    # Add coverage if requested
    if args.coverage or args.all:
        base_args.extend([
            "--cov=main",
            "--cov=gemini_answer",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--cov-report=xml:coverage.xml"
        ])
    
    # Test execution results
    results = []
    
    if args.all:
        # Run comprehensive test suite
        test_args = base_args + [
            "test_comprehensive_suite.py",
            "--tb=short",
            "--durations=10"
        ]
        results.append(run_pytest_command(test_args, "Comprehensive Test Suite"))
        
    elif args.unit:
        # Run unit tests only
        test_args = base_args + [
            "-m", "unit",
            "test_comprehensive_suite.py",
            "--tb=line"
        ]
        results.append(run_pytest_command(test_args, "Unit Tests"))
        
    elif args.integration:
        # Run integration tests only
        test_args = base_args + [
            "-m", "integration",
            "test_comprehensive_suite.py",
            "--tb=short"
        ]
        results.append(run_pytest_command(test_args, "Integration Tests"))
        
    elif args.performance:
        # Run performance tests only
        test_args = base_args + [
            "-m", "performance",
            "test_comprehensive_suite.py",
            "--tb=line",
            "--durations=0"  # Show all durations
        ]
        results.append(run_pytest_command(test_args, "Performance Tests"))
        
    elif args.security:
        # Run security tests only
        test_args = base_args + [
            "-m", "security",
            "test_comprehensive_suite.py",
            "--tb=short"
        ]
        results.append(run_pytest_command(test_args, "Security Tests"))
        
    elif args.explainability:
        # Run explainability tests only
        test_args = base_args + [
            "-m", "explainability",
            "test_comprehensive_suite.py",
            "--tb=short"
        ]
        results.append(run_pytest_command(test_args, "Explainability Tests"))
        
    elif args.quick:
        # Run quick tests (exclude slow ones)
        test_args = base_args + [
            "-m", "not slow",
            "test_comprehensive_suite.py",
            "--tb=line"
        ]
        results.append(run_pytest_command(test_args, "Quick Test Suite"))
        
    elif args.slow:
        # Run only slow tests
        test_args = base_args + [
            "-m", "slow",
            "test_comprehensive_suite.py",
            "--tb=short"
        ]
        results.append(run_pytest_command(test_args, "Slow Test Suite"))
        
    elif args.file:
        # Run specific test file
        test_args = base_args + [args.file]
        if args.test:
            test_args.extend(["-k", args.test])
        results.append(run_pytest_command(test_args, f"Test File: {args.file}"))
        
    else:
        # Default: run basic test suite
        test_args = base_args + [
            "test_comprehensive_suite.py::TestDocumentIngestion",
            "test_comprehensive_suite.py::TestDocumentChunking",
            "test_comprehensive_suite.py::TestEmbeddingGeneration",
            "--tb=short"
        ]
        results.append(run_pytest_command(test_args, "Basic Test Suite"))
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results if result == 0)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Test Suites: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    
    if failed_tests == 0:
        print("\n🎉 All test suites passed!")
        if args.coverage or args.all:
            print("📋 Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n⚠️  {failed_tests} test suite(s) failed")
        sys.exit(1)
    
    print("\n💡 Test Tips:")
    print("  • Use --verbose for detailed output")
    print("  • Use --coverage for coverage analysis")
    print("  • Use --quick for faster development testing")
    print("  • Use --unit/--integration for focused testing")
    print("  • Check htmlcov/index.html for coverage details")

if __name__ == "__main__":
    # Ensure we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    main()
