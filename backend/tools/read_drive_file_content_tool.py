import io
import pypdfium2 as pdfium
from googleapiclient.http import MediaIoBaseDownload
from agents import function_tool

@function_tool
def get_drive_file_text_content(drive_service: object, file_id: str) -> str:
    """Reads a file from Google Drive (given its file_id) and returns its text content.
    Handles Google Docs, Sheets, Slides (by exporting to PDF), native PDFs, and plain text files.
    Args:
        drive_service: The authenticated Google Drive API service object.
        file_id: The ID of the file in Google Drive.
    Returns:
        The extracted text content of the file as a string.
    Raises:
        Exception: If the file cannot be accessed or processed.
    """
    try:
        file_metadata = drive_service.files().get(fileId=file_id, fields='id, name, mimeType').execute()
        mime_type = file_metadata.get('mimeType')
        file_name = file_metadata.get('name', 'Unknown File')

        content_bytes = b''
        text_content = ''

        if mime_type == 'application/vnd.google-apps.document':
            print(f"Exporting Google Doc '{file_name}' (ID: {file_id}) to PDF for text extraction.")
            request = drive_service.files().export_media(fileId=file_id, mimeType='application/pdf')
            content_bytes = request.execute()
            # Fall through to PDF processing
        elif mime_type == 'application/vnd.google-apps.spreadsheet':
            print(f"Exporting Google Sheet '{file_name}' (ID: {file_id}) to PDF for text extraction.")
            request = drive_service.files().export_media(fileId=file_id, mimeType='application/pdf')
            content_bytes = request.execute()
            # Fall through to PDF processing
        elif mime_type == 'application/vnd.google-apps.presentation':
            print(f"Exporting Google Slides '{file_name}' (ID: {file_id}) to PDF for text extraction.")
            request = drive_service.files().export_media(fileId=file_id, mimeType='application/pdf')
            content_bytes = request.execute()
            # Fall through to PDF processing
        elif mime_type == 'application/pdf' or content_bytes: # content_bytes will be set if exported from GSuite type
            if not content_bytes: # If it's a native PDF, download it
                print(f"Downloading native PDF '{file_name}' (ID: {file_id}) for text extraction.")
                request = drive_service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                content_bytes = fh.getvalue()
            
            print(f"Parsing PDF content for '{file_name}' (ID: {file_id}).")
            pdf_doc = pdfium.PdfDocument(content_bytes)
            for page in pdf_doc:
                text_content += page.get_textpage().get_text_range() + "\n"
            pdf_doc.close()
            return text_content.strip()
        
        elif mime_type and mime_type.startswith('text/'):
            print(f"Downloading text file '{file_name}' (ID: {file_id}) for content extraction.")
            request = drive_service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            content_bytes = fh.getvalue()
            try:
                text_content = content_bytes.decode('utf-8')
            except UnicodeDecodeError:
                text_content = content_bytes.decode('latin-1', errors='replace') # Fallback decoding
            return text_content.strip()

        else: # Try to download and decode other types as a last resort
            print(f"Attempting to download and process unsupported MIME type '{mime_type}' for file '{file_name}' (ID: {file_id}).")
            try:
                request = drive_service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                content_bytes = fh.getvalue()
                text_content = content_bytes.decode('utf-8', errors='replace')
                if not text_content.strip():
                     return f"[Could not extract text or empty content from file '{file_name}' (MIME type: {mime_type})]"
                return text_content.strip()
            except Exception as e:
                print(f"Could not process file '{file_name}' (ID: {file_id}, MIME: {mime_type}): {e}")
                return f"[Error processing file '{file_name}' (MIME type: {mime_type}): {str(e)}]"

    except Exception as e:
        print(f"Error in get_drive_file_text_content for file_id {file_id}: {e}")
        # Log full traceback for server-side debugging
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise ValueError(f"Failed to get/process file ID {file_id} from Google Drive. Error: {str(e)}")
