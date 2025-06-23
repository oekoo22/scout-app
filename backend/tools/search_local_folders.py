import os
from agents import function_tool
from typing import Annotated, List

@function_tool
def search_local_folders(
    base_path: Annotated[str, "The base directory to search in"],
    folder_name_pattern: Annotated[str, "The folder name or pattern to search for"]
) -> List[str]:
    """Search for local folders that match a given pattern.
    
    Args:
        base_path: The base directory to search in
        folder_name_pattern: The folder name or pattern to search for
        
    Returns:
        List of full paths to matching folders
    """
    matching_folders = []
    
    if not os.path.exists(base_path):
        return matching_folders
    
    try:
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path):
                # Simple pattern matching - check if pattern is in folder name (case insensitive)
                if folder_name_pattern.lower() in item.lower():
                    matching_folders.append(item_path)
    except PermissionError:
        # Return empty list if we can't access the directory
        pass
    
    return matching_folders