from agents import function_tool
from typing import Annotated, Dict

@function_tool
def move_drive_file(
    drive_service: Annotated[object, "The authenticated Google Drive API service object."],
    file_id: Annotated[str, "The ID of the file in Google Drive to move."],
    target_folder_id: Annotated[str, "The ID of the destination folder in Google Drive."]
) -> Dict[str, str]:
    """Moves a file to a specified folder in Google Drive.

    This is achieved by updating the file's parentage. Any existing parents will be removed 
    and the target_folder_id will be set as the new parent.

    Args:
        drive_service: The authenticated Google Drive API service object.
        file_id: The ID of the file to move.
        target_folder_id: The ID of the folder to move the file into.

    Returns:
        A dictionary containing the 'file_id' and the 'moved_to_folder_id' upon success.
        
    Raises:
        ValueError: If file_id or target_folder_id is empty.
        Exception: If the move operation fails.
    """
    try:
        if not file_id or not file_id.strip():
            raise ValueError("File ID cannot be empty.")
        if not target_folder_id or not target_folder_id.strip():
            raise ValueError("Target folder ID cannot be empty.")

        # Retrieve the file to get its current parents
        file_metadata = drive_service.files().get(fileId=file_id, fields='parents').execute()
        previous_parents = ",".join(file_metadata.get('parents', []))

        # Update the file's parents
        updated_file = drive_service.files().update(
            fileId=file_id,
            addParents=target_folder_id,
            removeParents=previous_parents, # Remove all old parents to ensure a 'move'
            fields='id, parents'
        ).execute()

        new_parents = updated_file.get('parents')
        if target_folder_id in new_parents:
            print(f"File ID '{file_id}' successfully moved to folder ID '{target_folder_id}'.")
            return {'file_id': file_id, 'moved_to_folder_id': target_folder_id, 'status': 'success'}
        else:
            # This case should ideally not happen if the API call was successful and target_folder_id is valid
            print(f"Warning: File ID '{file_id}' move to folder ID '{target_folder_id}' attempted, but new parents list {new_parents} does not confirm.")
            raise Exception(f"Move operation for file ID '{file_id}' to folder '{target_folder_id}' did not confirm parent update.")

    except Exception as e:
        print(f"Error moving Google Drive file ID '{file_id}' to folder ID '{target_folder_id}': {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise ValueError(f"Failed to move file ID '{file_id}' to folder '{target_folder_id}' in Google Drive. Error: {str(e)}")
