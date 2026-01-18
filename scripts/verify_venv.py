#!/usr/bin/env python3
"""
Virtual Environment Verification Script
Verify virtual environment is properly configured and available
"""
import sys
import os
from pathlib import Path

# Project root directory - dynamic detection
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR
for _ in range(3):
    if (PROJECT_ROOT / '.venv').exists() or (PROJECT_ROOT / 'project_config.json').exists():
        break
    PROJECT_ROOT = PROJECT_ROOT.parent


def check_venv_structure():
    """Check virtual environment structure"""
    print("=" * 60)
    print("Virtual Environment Structure Check")
    print("=" * 60)

    venv_path = PROJECT_ROOT / '.venv'

    if not venv_path.exists():
        print("[X] .venv directory does not exist")
        return False

    print(f"[OK] .venv directory exists: {venv_path}")

    # Check required directories
    required_dirs = ['bin', 'lib']
    for dir_name in required_dirs:
        dir_path = venv_path / dir_name
        if dir_path.exists():
            print(f"[OK] {dir_name}/ directory exists")
        else:
            print(f"[X] {dir_name}/ directory does not exist")
            return False

    # Check Python interpreter
    python_paths = [
        venv_path / 'bin' / 'python3',
        venv_path / 'bin' / 'python',
    ]

    python_path = None
    for py_path in python_paths:
        if py_path.exists():
            python_path = py_path
            print(f"[OK] Python interpreter: {py_path}")
            break

    if not python_path:
        print("[X] Python interpreter not found")
        return False

    return python_path


def check_python_version(python_path):
    """Check Python version"""
    print("\n" + "=" * 60)
    print("Python Version Check")
    print("=" * 60)

    try:
        import subprocess
        result = subprocess.run(
            [str(python_path), '--version'],
            capture_output=True,
            text=True
        )
        version = result.stdout.strip() or result.stderr.strip()
        print(f"[OK] Python version: {version}")
        return True
    except Exception as e:
        print(f"[X] Python version check failed: {e}")
        return False


def check_pip():
    """Check pip installation"""
    print("\n" + "=" * 60)
    print("pip Check")
    print("=" * 60)

    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, '-m', 'pip', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"[OK] pip version: {result.stdout.strip()}")
            return True
        else:
            print(f"[X] pip check failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"[X] pip check failed: {e}")
        return False


def check_dependencies():
    """Check core dependencies"""
    print("\n" + "=" * 60)
    print("Core Dependencies Check")
    print("=" * 60)

    # Add project paths to sys.path
    src_path = PROJECT_ROOT / 'src'
    web_path = PROJECT_ROOT / 'web'
    scripts_path = PROJECT_ROOT / 'scripts'

    paths_to_add = [str(src_path), str(web_path), str(scripts_path)]
    for p in paths_to_add:
        if p not in sys.path:
            sys.path.insert(0, p)

    core_modules = [
        ('src', 'Core Module'),
        ('web', 'Web Module'),
        ('fastapi', 'FastAPI'),
        ('PyQt5', 'PyQt5'),
        ('uvicorn', 'Uvicorn'),
        ('loguru', 'Loguru'),
        ('psutil', 'Psutil'),
        ('yaml', 'PyYAML'),
    ]

    all_ok = True
    for module_name, display_name in core_modules:
        try:
            __import__(module_name)
            print(f"[OK] {display_name} ({module_name})")
        except ImportError as e:
            print(f"[X] {display_name} ({module_name}): {e}")
            all_ok = False

    return all_ok


def check_project_imports():
    """Check project module imports"""
    print("\n" + "=" * 60)
    print("Project Module Imports Check")
    print("=" * 60)

    # Add src and scripts directories to path
    src_path = PROJECT_ROOT / 'src'
    scripts_path = PROJECT_ROOT / 'scripts'
    web_path = PROJECT_ROOT / 'web'

    paths_to_add = [str(src_path), str(scripts_path), str(web_path)]
    for p in paths_to_add:
        if p not in sys.path:
            sys.path.insert(0, p)

    project_modules = [
        ('src.config.app_config', 'Config Module'),
        ('scripts.unified_launcher', 'Unified Launcher'),
        ('web.app', 'Web App'),
    ]

    all_ok = True
    for module_name, display_name in project_modules:
        try:
            __import__(module_name)
            print(f"[OK] {display_name}")
        except ImportError as e:
            print(f"[X] {display_name}: {e}")
            all_ok = False

    return all_ok


def main():
    """Main function"""
    print("\n")
    print("+" + "=" * 58 + "+")
    print("|" + " " * 15 + "Virtual Environment Verifier" + " " * 12 + "|")
    print("+" + "=" * 58 + "+")
    print()

    results = []

    # 1. Check virtual environment structure
    python_path = check_venv_structure()
    results.append(("Venv Structure", python_path is not None))

    if not python_path:
        print("\n[X] Virtual environment is broken, please recreate:")
        print(f"   rm -rf {PROJECT_ROOT / '.venv'}")
        print(f"   python3 -m venv {PROJECT_ROOT / '.venv'}")
        return 1

    # 2. Check Python version
    results.append(("Python Version", check_python_version(python_path)))

    # 3. Check pip
    results.append(("pip Check", check_pip()))

    # 4. Check core dependencies
    results.append(("Core Dependencies", check_dependencies()))

    # 5. Check project module imports
    results.append(("Project Imports", check_project_imports()))

    # Summary
    print("\n" + "=" * 60)
    print("Verification Results Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "[OK] Pass" if passed else "[X] Fail"
        print(f"  {name:20} | {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("+" + "=" * 58 + "+")
        print("|" + " " * 18 + "[OK] All Checks Passed" + " " * 19 + "|")
        print("+" + "=" * 58 + "+")
        return 0
    else:
        print("+" + "=" * 58 + "+")
        print("|" + " " * 15 + "[X] Some Checks Failed" + " " * 16 + "|")
        print("+" + "=" * 58 + "+")
        return 1


if __name__ == '__main__':
    sys.exit(main())

