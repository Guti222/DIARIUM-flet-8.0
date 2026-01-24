#!/usr/bin/env python3
"""
Setup script for DIARIUM
Run this script to set up your development environment
"""
import os
import sys
import subprocess


def create_virtual_env():
    """Create a virtual environment"""
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "venv"])
    print("✅ Virtual environment created!")


def install_dependencies():
    """Install required dependencies"""
    print("\nInstalling dependencies...")
    
    # Determine the correct pip path
    if sys.platform == "win32":
        pip_path = os.path.join("venv", "Scripts", "pip")
    else:
        pip_path = os.path.join("venv", "bin", "pip")
    
    subprocess.run([pip_path, "install", "-r", "requirements.txt"])
    print("✅ Dependencies installed!")


def main():
    """Main setup function"""
    print("=" * 50)
    print("DIARIUM Setup Script")
    print("=" * 50)
    
    # Check if virtual environment already exists
    if os.path.exists("venv"):
        print("\n⚠️  Virtual environment already exists.")
        response = input("Do you want to recreate it? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
        print("Removing existing virtual environment...")
        import shutil
        try:
            shutil.rmtree("venv")
        except Exception as e:
            print(f"❌ Error removing virtual environment: {e}")
            print("Please remove the 'venv' directory manually and try again.")
            return
    
    create_virtual_env()
    install_dependencies()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("=" * 50)
    print("\nTo activate the virtual environment:")
    if sys.platform == "win32":
        print("  venv\\Scripts\\activate")
    else:
        print("  source venv/bin/activate")
    print("\nTo run the application:")
    print("  python main.py")
    print("\nTo see examples:")
    print("  python examples.py")


if __name__ == "__main__":
    main()
