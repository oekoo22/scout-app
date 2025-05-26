from agents import function_tool
from typing import Annotated, Dict, Optional

@function_tool
def create_drive_folder(
    drive_service: Annotated[object, "The authenticated Google Drive API service object."],
    new_folder_name: Annotated[str, "The name for the new folder."],
    parent_folder_id: Annotated[Optional[str], "Optional. The ID of the parent folder. If None, folder is created in root."] = None
) -> Dict[str, str]:
    """Creates a new folder in Google Drive.

    Args:
        drive_service: The authenticated Google Drive API service object.
        new_folder_name: The name for the new folder.
        parent_folder_id: Optional. The ID of the parent folder. If not provided, 
                          the folder will be created in the root directory of 'My Drive'.

    Returns:
        A dictionary containing 'id' and 'name' of the newly created folder.
        
    Raises:
        ValueError: If new_folder_name is empty.
        Exception: If the folder creation fails.
    """
    try:
        if not new_folder_name or not new_folder_name.strip():
            raise ValueError("New folder name cannot be empty.")

        folder_metadata = {
            'name': new_folder_name.strip(),
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_folder_id:
            folder_metadata['parents'] = [parent_folder_id]
        
        created_folder = drive_service.files().create(
            body=folder_metadata,
            fields='id, name'
        ).execute()
        
        folder_id = created_folder.get('id')
        folder_name = created_folder.get('name')
        print(f"Folder '{folder_name}' (ID: {folder_id}) successfully created in Google Drive.")
        return {'id': folder_id, 'name': folder_name}

    except Exception as e:
        print(f"Error creating Google Drive folder '{new_folder_name}': {e}")
        # Log full traceback for server-side debugging
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise ValueError(f"Failed to create folder '{new_folder_name}' in Google Drive. Error: {str(e)}")
