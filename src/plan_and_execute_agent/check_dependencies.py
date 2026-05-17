"""
Check if dependencies are installed
"""
import sys

def check_dependencies():
    """Check if required dependencies are installed"""
    required = {
        'pydantic': 'pydantic',
        'openai': 'openai',
        'dotenv': 'python-dotenv',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'loguru': 'loguru'
    }

    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (missing)")
            missing.append(package)

    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    else:
        print("\n✓ All dependencies are installed")
        return True


if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)