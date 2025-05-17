import os
import shutil
from agents import function_tool

@function_tool
def create_folder(name: str) -> None:
    """Create a folder in the 'scout-app/backend/assets' folder named after the input string."""
    path = os.path.join(os.path.dirname(__file__), "../assets", name)
    if not os.path.exists(path):
        os.mkdir(path)

@function_tool
def move_file(old_path: str, new_path: str) -> bool:
    """
    Move a file from the 'scout-app/backend/assets' folder to another location in the same path.
    
    Args:
        old_path: Relative path to the file within the assets directory
        new_path: New relative path within the assets directory
    
    Returns:
        bool: True if successful, False otherwise
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets"))
    old_full_path = os.path.join(base_dir, old_path)
    new_full_path = os.path.join(base_dir, new_path)
    
    # Check if the source file exists
    if not os.path.exists(old_full_path):
        print(f"Error: File {old_full_path} does not exist.")
        return False
    
    # Make sure the target directory exists
    target_dir = os.path.dirname(new_full_path)
    if not os.path.exists(target_dir):
        try:
            os.makedirs(target_dir, exist_ok=True)
        except Exception as e:
            print(f"Fehler beim Erstellen des Zielverzeichnisses: {e}")
            return False
    
    try:
        shutil.move(old_full_path, new_full_path)
        print(f"Datei erfolgreich verschoben von {old_path} nach {new_path}")
        return True
    except Exception as e:
        print(f"Fehler beim Verschieben der Datei: {e}")
        return False
