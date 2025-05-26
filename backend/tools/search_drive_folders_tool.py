from agents import function_tool
from typing import Annotated, List, Dict

@function_tool
def search_drive_folders(
    drive_service: Annotated[object, "The authenticated Google Drive API service object."],
    folder_name_query: Annotated[str, "The name or part of the name of the folder to search for."]
) -> List[Dict[str, str]]:
    """Searches for folders in Google Drive by name.

    Args:
        drive_service: The authenticated Google Drive API service object.
        folder_name_query: The name (or partial name) to query for. 
                           The search will look for folders whose name contains this query string.

    Returns:
        A list of dictionaries, where each dictionary contains 'id' and 'name' of a found folder.
        Returns an empty list if no folders match or an error occurs.
    """
    folders_found = []
    try:
        if not folder_name_query or not folder_name_query.strip():
            # Consider if an empty query should list all root folders or return error/empty.
            # For now, returning empty for an empty query to avoid overly broad results.
            print("Folder name query is empty. Returning no results.")
            return []

        query = f"mimeType='application/vnd.google-apps.folder' and name contains '{folder_name_query.strip()}' and trashed=false"
        
        page_token = None
        while True:
            response = drive_service.files().list(
                q=query,
                spaces='drive',
                fields='nextPageToken, files(id, name)',
                pageToken=page_token
            ).execute()
            
            for folder in response.get('files', []):
                folders_found.append({'id': folder.get('id'), 'name': folder.get('name')})
            
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        
        print(f"Found {len(folders_found)} folder(s) matching query '{folder_name_query}': {folders_found}")
        return folders_found

    except Exception as e:
        print(f"Error searching for Google Drive folders with query '{folder_name_query}': {e}")
        # Log full traceback for server-side debugging
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        # Return empty list on error to allow agent to proceed (e.g., by creating a folder)
        return []
