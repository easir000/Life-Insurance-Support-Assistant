#!/usr/bin/env python3
"""
Script to run the CLI interface from the project root
"""
import sys
import os
from pathlib import Path

def main():
    """Main entry point"""
    # Get the project root directory (where this script is located, one level up)
    project_root = Path(__file__).parent.parent
    app_dir = project_root / "app"
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    try:
        # Import the CLI interface directly
        from app.cli_interface import main as cli_main
        cli_main()
    except ImportError as e:
        print(f"Import error: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Project root: {project_root}")
        print(f"Looking for app directory: {app_dir}")
        print("Make sure you're running this from the project root directory")
        print("Available directories:")
        for item in project_root.iterdir():
            if item.is_dir():
                print(f"  {item.name}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running CLI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()