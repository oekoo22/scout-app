import os
from agents import function_tool
from typing import Annotated

@function_tool
def rename_local_file(
    current_file_path: Annotated[str, "The current full path of the file"],
    new_filename: Annotated[str, "The new filename (without path)"]
) -> str:
    """Rename a local file and return the new file path.
    
    Args:
        current_file_path: The current full path of the file
        new_filename: The new filename (without path)
        
    Returns:
        The new full path of the renamed file
    """
    if not os.path.exists(current_file_path):
        raise FileNotFoundError(f"File not found at path: {current_file_path}")
    
    # Get the directory of the current file
    current_dir = os.path.dirname(current_file_path)
    
    # Create the new file path
    new_file_path = os.path.join(current_dir, new_filename)
    
    # Rename the file
    os.rename(current_file_path, new_file_path)
    
    return new_file_path