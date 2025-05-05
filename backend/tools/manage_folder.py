import os
import shutil

def create_folder(name: str) -> None:
    """Create a folder in the 'scout-app/backend/assets' folder named after the input string."""
    path = os.path.join(os.path.dirname(__file__), "../assets", name)
    if not os.path.exists(path):
        os.mkdir(path)

def move_file(old_path: str, new_path: str) -> None:
    """Move a file from the 'scout-app/backend/assets' folder to another in the same path."""
    shutil.move(os.path.join(os.path.dirname(__file__), "../assets", old_path),
                os.path.join(os.path.dirname(__file__), "../assets", new_path))
