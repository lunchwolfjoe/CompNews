#!/usr/bin/env python3
"""
Startup script for CompNews application.
This script initializes the database and starts the Streamlit app.
"""

import os
import sys
import subprocess

# Add src to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

def initialize_database():
    """Initialize the database tables"""
    try:
        from database.connection import init_db
        print("Initializing database...")
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False
    return True

def main():
    print("🚀 Starting CompNews Application...")
    
    # Initialize database
    if not initialize_database():
        print("❌ Failed to initialize database. Exiting.")
        sys.exit(1)
    
    # Start Streamlit app
    print("🌐 Starting Streamlit server...")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down application...")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 