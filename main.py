"""
Wireless Link Budget GUI - Main Entry Point
===========================================
Course: 3171608 - Wireless Communication (WC)
Department of Information Technology

Run this file to start the Wireless Link Budget Application:
    python main.py
"""

import sys
import os

# Enable Windows High-DPI scaling for sharp fonts on modern displays
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


def check_dependencies():
    """Verify that all essential libraries are available."""
    missing = []
    for pkg in ["tkinter", "matplotlib", "numpy", "reportlab"]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"Error: Missing required packages: {', '.join(missing)}")
        print("Please install them using: pip install -r requirements.txt")
        sys.exit(1)


def main():
    print("=" * 65)
    print("  WIRELESS LINK BUDGET GUI APPLICATION")
    print("  Course: 3171608 - Wireless Communication (WC)")
    print("  Micro-Project Evaluation Software")
    print("=" * 65)

    check_dependencies()

    try:
        from gui_app import launch_gui
        print("Launching Graphical User Interface...")
        launch_gui()
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
