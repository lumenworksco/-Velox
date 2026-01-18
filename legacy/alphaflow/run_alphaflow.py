#!/usr/bin/env python3
"""
AlphaFlow Trading Platform - Launcher

A professional algorithmic trading platform with Bloomberg Terminal-inspired UI.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main application
from app.main_window import main

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 AlphaFlow Trading Platform v6.3.0")
    print("=" * 60)
    print("Starting AlphaFlow...")
    print()

    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 AlphaFlow terminated by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting AlphaFlow: {e}")
        print("\nPlease ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
