#!/usr/bin/env python3
"""
Release validation script for Redis MCP Server.

This script helps validate that a release is ready for publishing by:
1. Checking version consistency
2. Running tests
3. Building the package
4. Validating package metadata
5. Running security scans
"""

import subprocess
import sys
import json
import os
from pathlib import Path


def run_command(cmd, check=True, capture_output=True):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check, capture_output=capture_output, text=True)
    if capture_output:
        return result.stdout.strip()
    return result


def check_version_consistency():
    """Check that hatch-vcs version matches git tag."""
    print("\n🔍 Checking version consistency...")
    
    try:
        # Get version from hatch-vcs
        hatch_version = run_command(["uv", "run", "python", "-m", "hatchling", "version"])
        print(f"Hatch-VCS version: {hatch_version}")
        
        # Get latest git tag
        try:
            git_tag = run_command(["git", "describe", "--tags", "--abbrev=0"])
            git_version = git_tag.lstrip('v')
            print(f"Git tag version: {git_version}")
            
            if hatch_version == git_version:
                print("✅ Version consistency check passed")
                return True
            else:
                print(f"❌ Version mismatch: {hatch_version} != {git_version}")
                return False
        except subprocess.CalledProcessError:
            print("⚠️  No git tags found, skipping git version check")
            return True
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get version: {e}")
        return False


def run_tests():
    """Run the test suite."""
    print("\n🧪 Running tests...")
    
    try:
        run_command(["uv", "run", "pytest", "tests/", "-v"], capture_output=False)
        print("✅ Tests passed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Tests failed")
        return False


def run_security_scan():
    """Run security scans."""
    print("\n🔒 Running security scans...")
    
    success = True
    
    # Install security tools
    try:
        run_command(["uv", "add", "--dev", "bandit[toml]", "safety"])
    except subprocess.CalledProcessError:
        print("⚠️  Failed to install security tools")
        return False
    
    # Run bandit
    try:
        run_command(["uv", "run", "bandit", "-r", "src/"], capture_output=False)
        print("✅ Bandit security scan passed")
    except subprocess.CalledProcessError:
        print("❌ Bandit security scan failed")
        success = False
    
    # Run safety
    try:
        run_command(["uv", "run", "safety", "check"], capture_output=False)
        print("✅ Safety vulnerability scan passed")
    except subprocess.CalledProcessError:
        print("❌ Safety vulnerability scan failed")
        success = False
    
    return success


def build_package():
    """Build the package."""
    print("\n📦 Building package...")
    
    try:
        run_command(["uv", "build", "--sdist", "--wheel"], capture_output=False)
        print("✅ Package built successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Package build failed")
        return False


def validate_package():
    """Validate the built package."""
    print("\n✅ Validating package...")
    
    try:
        # Install twine if not already installed
        run_command(["uv", "add", "--dev", "twine"])
        
        # Check package
        run_command(["uv", "run", "twine", "check", "dist/*"], capture_output=False)
        print("✅ Package validation passed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Package validation failed")
        return False


def check_dependencies():
    """Check that all dependencies are properly specified."""
    print("\n📋 Checking dependencies...")
    
    try:
        # Sync dependencies
        run_command(["uv", "sync", "--all-extras", "--dev"], capture_output=False)
        print("✅ Dependencies synced successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Dependency sync failed")
        return False


def lint_code():
    """Run code linting."""
    print("\n🧹 Running code linting...")
    
    success = True
    
    try:
        # Install linting tools
        run_command(["uv", "add", "--dev", "ruff", "black", "isort"])
        
        # Run ruff
        try:
            run_command(["uv", "run", "ruff", "check", "src/", "tests/"], capture_output=False)
            print("✅ Ruff linting passed")
        except subprocess.CalledProcessError:
            print("❌ Ruff linting failed")
            success = False
        
        # Run black
        try:
            run_command(["uv", "run", "black", "--check", "src/", "tests/"], capture_output=False)
            print("✅ Black formatting check passed")
        except subprocess.CalledProcessError:
            print("❌ Black formatting check failed")
            success = False
        
        # Run isort
        try:
            run_command(["uv", "run", "isort", "--check-only", "src/", "tests/"], capture_output=False)
            print("✅ Import sorting check passed")
        except subprocess.CalledProcessError:
            print("❌ Import sorting check failed")
            success = False
            
        return success
        
    except subprocess.CalledProcessError:
        print("❌ Failed to install linting tools")
        return False


def main():
    """Main validation function."""
    print("🚀 Redis MCP Server Release Validation")
    print("=" * 50)
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    checks = [
        ("Version Consistency", check_version_consistency),
        ("Dependencies", check_dependencies),
        ("Code Linting", lint_code),
        ("Security Scans", run_security_scan),
        ("Tests", run_tests),
        ("Package Build", build_package),
        ("Package Validation", validate_package),
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ {check_name} failed with exception: {e}")
            results[check_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check_name:.<30} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 All validation checks passed! Ready for release.")
        return 0
    else:
        print("❌ Some validation checks failed. Please fix the issues before releasing.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
