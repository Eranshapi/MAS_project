import sys
import os

# Add the parent directory of src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.frontend.gui import run_gui
from src.utils.config import load_config
from src.backend.database import db

def main():
    # Load configuration
    config = load_config()
    
    # Ensure the database directory exists
    if not os.path.exists(config["CHROMA_DB_PATH"]):
        print(f"Error: Database directory '{config['CHROMA_DB_PATH']}' not found!")
        return
    
    # Print the number of chunks in the database
    try:
        total_chunks = db.get_total_chunks()
        print(f"\nTotal chunks in database: {total_chunks}\n")
    except Exception as e:
        print(f"Error accessing database: {str(e)}")
        return
    
    # Run the GUI
    run_gui()
    print("hello")

if __name__ == "__main__":
    main()
