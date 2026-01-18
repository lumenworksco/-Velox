#!/usr/bin/env python3
"""
AlphaFlow Trading Platform - Launcher

A professional algorithmic trading platform with Bloomberg Terminal-inspired UI.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 AlphaFlow Trading Platform v6.3.0")
    print("=" * 60)
    print("Initializing...")

    try:
        # Check for required dependencies
        print("Checking dependencies...")
        try:
            import PyQt6
            print("✓ PyQt6 found")
        except ImportError:
            print("✗ PyQt6 not found - install with: pip install PyQt6")
            sys.exit(1)

        try:
            import pandas
            print("✓ pandas found")
        except ImportError:
            print("✗ pandas not found - install with: pip install pandas")
            sys.exit(1)

        print("✓ All critical dependencies found")
        print("\nStarting AlphaFlow GUI...")
        print("(If the window doesn't appear, check for errors below)")
        print()

        # Import and run the main application
        from app.main_window import main
        main()

    except KeyboardInterrupt:
        print("\n\n👋 AlphaFlow terminated by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting AlphaFlow: {e}")
        import traceback
        traceback.print_exc()
        print("\nPlease ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
