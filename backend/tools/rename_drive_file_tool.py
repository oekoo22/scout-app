from agents import function_tool
from google_drive_auth import get_drive_service

@function_tool
def rename_drive_file(
    file_id: str,
    new_name: str
) -> str:
    """Renames a file in Google Drive.

    Args:
        file_id: The ID of the file in Google Drive.
        new_name: The new name for the file.

    Returns:
        The new name of the file if successful.
    
    Raises:
        Exception: If the renaming operation fails or if drive service cannot be obtained.
    """
    try:
        drive_service = get_drive_service()
        if not drive_service:
            raise Exception("Could not obtain Google Drive service. User might not be authenticated.")

        if not new_name or not new_name.strip():
            raise ValueError("New name cannot be empty.")
        
        file_metadata = {'name': new_name.strip()}
        updated_file = drive_service.files().update(
            fileId=file_id,
            body=file_metadata,
            fields='id, name'
        ).execute()
        
        successfully_renamed_name = updated_file.get('name')
        print(f"File with ID '{file_id}' successfully renamed to '{successfully_renamed_name}' in Google Drive.")
        return successfully_renamed_name
    except Exception as e:
        print(f"Error renaming Google Drive file ID '{file_id}' to '{new_name}': {e}")
        # Log full traceback for server-side debugging
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise ValueError(f"Failed to rename file ID '{file_id}' in Google Drive. Error: {str(e)}")
