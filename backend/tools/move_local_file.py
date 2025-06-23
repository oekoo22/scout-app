import os
import shutil
from agents import function_tool
from typing import Annotated

@function_tool
def move_local_file(
    source_file_path: Annotated[str, "The current full path of the file to move"],
    target_folder_path: Annotated[str, "The target folder path where to move the file"]
) -> dict:
    """Move a local file to a target folder and return confirmation.
    
    Args:
        source_file_path: The current full path of the file to move
        target_folder_path: The target folder path where to move the file
        
    Returns:
        Dictionary with move confirmation details
    """
    if not os.path.exists(source_file_path):
        return {
            "source_file_path": source_file_path,
            "target_folder_path": target_folder_path,
            "status": "failure",
            "error": f"Source file not found: {source_file_path}"
        }
    
    if not os.path.exists(target_folder_path):
        return {
            "source_file_path": source_file_path,
            "target_folder_path": target_folder_path,
            "status": "failure",
            "error": f"Target folder not found: {target_folder_path}"
        }
    
    try:
        # Get the filename from the source path
        filename = os.path.basename(source_file_path)
        
        # Create the destination path
        destination_path = os.path.join(target_folder_path, filename)
        
        # Move the file
        shutil.move(source_file_path, destination_path)
        
        return {
            "source_file_path": source_file_path,
            "target_folder_path": target_folder_path,
            "new_file_path": destination_path,
            "status": "success"
        }
        
    except Exception as e:
        return {
            "source_file_path": source_file_path,
            "target_folder_path": target_folder_path,
            "status": "failure",
            "error": str(e)
        }