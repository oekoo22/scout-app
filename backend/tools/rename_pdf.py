import os
from agents import function_tool

@function_tool
def rename_pdf(old_name, new_name):
    """Rename a PDF file in the assets folder

    Args:
        old_name (str): The current name of the PDF file
        new_name (str): The new name of the PDF file
    """
    old_path = os.path.join("assets", old_name)
    new_path = os.path.join("assets", new_name)
    os.rename(old_path, new_path)

if __name__ == "__main__":
    rename_pdf("test.pdf", "test2.pdf")