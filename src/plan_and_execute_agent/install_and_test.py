"""
Install dependencies and run simple test
"""
import subprocess
import sys


def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False


if __name__ == "__main__":
    # Install dependencies
    if install_dependencies():
        print("\nNow you can run:")
        print("  python test_simple.py  # Run simple test")
        print("  python main.py         # Run main example")
    else:
        print("\nPlease install dependencies manually:")
        print("  pip install -r requirements.txt")