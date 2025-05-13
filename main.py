from src.frontend.gui import run_gui
from src.utils.config import load_config

def main():
    # Load configuration
    load_config()
    
    # Run the GUI
    run_gui()

if __name__ == "__main__":
    main()
