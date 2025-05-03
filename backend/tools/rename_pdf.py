import os
from agents import function_tool
from typing import Annotated

@function_tool
def rename_pdf(
    old_name: Annotated[str, "The current name of the PDF file"],
    new_name: Annotated[str, "The new name of the PDF file"]
) -> None:
    """Rename a PDF file in the assets folder.
    
    Args:
        old_name: The current name of the PDF file
        new_name: The new name of the PDF file
    """
    # Get the path of the PDF file in the assets folder
    old_path = os.path.join(os.path.dirname(__file__), "../assets", old_name)
    new_path = os.path.join(os.path.dirname(__file__), "../assets", new_name)
    os.rename(old_path, new_path)