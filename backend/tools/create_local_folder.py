import os
from agents import function_tool
from typing import Annotated

@function_tool
def create_local_folder(
    base_path: Annotated[str, "The base directory where to create the folder"],
    folder_name: Annotated[str, "The name of the folder to create"]
) -> str:
    """Create a local folder and return its full path.
    
    Args:
        base_path: The base directory where to create the folder
        folder_name: The name of the folder to create
        
    Returns:
        The full path of the created folder
    """
    folder_path = os.path.join(base_path, folder_name)
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
    
    return folder_path