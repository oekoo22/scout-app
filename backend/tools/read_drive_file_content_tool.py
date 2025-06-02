import io
import pypdfium2 as pdfium
from googleapiclient.http import MediaIoBaseDownload
from agents import function_tool
from google_drive_auth import get_drive_service # Adjusted import path

@function_tool
def get_drive_file_text_content(file_id: str) -> str:
    """Reads a file from Google Drive (given its file_id) and returns its text content.
    Handles Google Docs, Sheets, Slides (by exporting to PDF), native PDFs, and plain text files.
    Internally fetches the Google Drive service.

    Args:
        file_id: The ID of the file in Google Drive.

    Returns:
        The extracted text content of the file as a string, or an error message string.

    Raises:
        ValueError: If the Drive service cannot be initialized or a critical, unrecoverable error occurs.
    """
    drive_service_to_use = get_drive_service()
    if not drive_service_to_use:
        print("Error: Google Drive service could not be initialized in get_drive_file_text_content.")
        # This is a critical failure, so raising an exception might be more appropriate
        # depending on how the caller handles it. For now, returning a message.
        raise ValueError("Google Drive service could not be initialized. Cannot process file.")

    try:
        file_metadata = drive_service_to_use.files().get(fileId=file_id, fields='id, name, mimeType').execute()
        mime_type = file_metadata.get('mimeType')
        file_name = file_metadata.get('name', f'Unknown File (ID: {file_id})')
        print(f"Processing file: '{file_name}' (ID: {file_id}, MIME: {mime_type})")

        content_bytes = b''
        text_content = ''
        processed_as_pdf = False

        # Handle GSuite types by exporting to PDF
        if mime_type in ['application/vnd.google-apps.document',
                         'application/vnd.google-apps.spreadsheet',
                         'application/vnd.google-apps.presentation']:
            gsuite_type_map = {
                'application/vnd.google-apps.document': 'Google Doc',
                'application/vnd.google-apps.spreadsheet': 'Google Sheet',
                'application/vnd.google-apps.presentation': 'Google Slides'
            }
            doc_type_name = gsuite_type_map.get(mime_type, "Google App")
            print(f"Exporting {doc_type_name} '{file_name}' to PDF for text extraction.")
            try:
                request = drive_service_to_use.files().export_media(fileId=file_id, mimeType='application/pdf')
                content_bytes = request.execute()
                if not content_bytes:
                    print(f"Error: Exporting {doc_type_name} '{file_name}' to PDF resulted in empty content.")
                    return f"[Could not extract text: Export to PDF for '{file_name}' yielded no content]"
                print(f"Successfully exported {doc_type_name} '{file_name}' to PDF, content length: {len(content_bytes)} bytes.")
            except Exception as export_error:
                print(f"Error exporting {doc_type_name} '{file_name}' (ID: {file_id}) to PDF: {export_error}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                return f"[Could not extract text: Error during PDF export for '{file_name}': {str(export_error)}]"

        # Process as PDF if it's a native PDF or if content_bytes was populated by GSuite export
        if mime_type == 'application/pdf' or content_bytes: # Check content_bytes from GSuite export
            if not content_bytes: # If it's a native PDF and content_bytes isn't already set from export
                print(f"Downloading native PDF '{file_name}' for text extraction.")
                try:
                    request = drive_service_to_use.files().get_media(fileId=file_id)
                    fh = io.BytesIO()
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                    content_bytes = fh.getvalue()
                    if not content_bytes:
                        print(f"Error: Downloading native PDF '{file_name}' resulted in empty content.")
                        return f"[Could not extract text: Native PDF download for '{file_name}' yielded no content]"
                    print(f"Successfully downloaded native PDF '{file_name}', content length: {len(content_bytes)} bytes.")
                except Exception as download_error:
                    print(f"Error downloading native PDF '{file_name}': {download_error}")
                    import traceback
                    print(f"Traceback: {traceback.format_exc()}")
                    return f"[Could not extract text: Error downloading native PDF '{file_name}': {str(download_error)}]"
            
            if content_bytes: # Ensure we have content before parsing
                print(f"Parsing PDF content for '{file_name}'. Length: {len(content_bytes)} bytes.")
                pdf_doc = None
                try:
                    pdf_doc = pdfium.PdfDocument(content_bytes)
                    extracted_pages = []
                    for page_index in range(len(pdf_doc)):
                        page = None
                        text_page = None
                        try:
                            page = pdf_doc[page_index]
                            text_page = page.get_textpage()
                            if text_page:
                                text_segment = text_page.get_text_range()
                                if text_segment:
                                    extracted_pages.append(text_segment)
                        finally:
                            if text_page: text_page.close()
                            if page: page.close()
                    text_content = "\n".join(extracted_pages)
                    processed_as_pdf = True
                    if not text_content.strip():
                        print(f"Warning: PDF parsing for '{file_name}' resulted in empty text. The document might be image-based or empty.")
                        return f"[No text content found in PDF '{file_name}'. The document might be image-based or empty.]"
                    print(f"Successfully parsed PDF and extracted text for '{file_name}'.")
                    return text_content.strip()
                except Exception as pdf_error:
                    print(f"Error parsing PDF content for '{file_name}': {pdf_error}")
                    import traceback
                    print(f"Traceback: {traceback.format_exc()}")
                    return f"[Could not extract text: Error parsing PDF for '{file_name}': {str(pdf_error)}]"
                finally:
                    if pdf_doc: pdf_doc.close()
            else:
                # This case should ideally not be reached if logic is correct, but as a safeguard
                print(f"Error: PDF processing block reached for '{file_name}' but content_bytes is empty.")
                return f"[Internal error: PDF processing attempted on empty content for '{file_name}']"

        # Process text files if not already processed as PDF
        elif not processed_as_pdf and mime_type and mime_type.startswith('text/'):
            print(f"Downloading text file '{file_name}' for content extraction.")
            try:
                request = drive_service_to_use.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                content_bytes = fh.getvalue()
                if not content_bytes:
                    print(f"Error: Downloading text file '{file_name}' resulted in empty content.")
                    return f"[Could not extract text: Text file download for '{file_name}' yielded no content]"
                try:
                    text_content = content_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    print(f"Warning: UTF-8 decoding failed for text file '{file_name}'. Trying latin-1.")
                    text_content = content_bytes.decode('latin-1', errors='replace')
                print(f"Successfully downloaded and decoded text file '{file_name}'.")
                return text_content.strip()
            except Exception as text_file_error:
                print(f"Error processing text file '{file_name}': {text_file_error}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                return f"[Could not extract text: Error processing text file '{file_name}': {str(text_file_error)}]"

        # Fallback for other types if not already processed as PDF
        elif not processed_as_pdf:
            print(f"Attempting to download and process unsupported/unknown MIME type '{mime_type}' for file '{file_name}'.")
            try:
                request = drive_service_to_use.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                content_bytes = fh.getvalue()
                if not content_bytes:
                    print(f"Error: Downloading file '{file_name}' (MIME: {mime_type}) resulted in empty content.")
                    return f"[Could not extract text: File download for '{file_name}' (MIME: {mime_type}) yielded no content]"
                # Attempt to decode as text, assuming it might be text-based
                text_content = content_bytes.decode('utf-8', errors='replace')
                if not text_content.strip():
                    print(f"Warning: Fallback processing for '{file_name}' (MIME: {mime_type}) resulted in empty or non-text content.")
                    return f"[Could not extract text or empty content from file '{file_name}' (MIME type: {mime_type})]"
                print(f"Successfully downloaded and decoded file '{file_name}' using fallback method.")
                return text_content.strip()
            except Exception as e:
                print(f"Could not process file '{file_name}' (MIME: {mime_type}) using fallback: {e}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                return f"[Error processing file '{file_name}' (MIME type: {mime_type}) using fallback: {str(e)}]"
        
        # If no specific processing path was taken and text_content is still empty.
        # This should ideally not be reached if all mime types are handled or fall into the generic else.
        if not text_content.strip():
            print(f"File '{file_name}' (ID: {file_id}, MIME: {mime_type}) could not be processed or yielded no content through any handler.")
            return f"[Unsupported file type or unable to process file '{file_name}' (MIME type: {mime_type}) to extract text]"
        
        # Should not be reached if all paths return explicitly
        return text_content.strip()

    except Exception as e:
        print(f"Critical error in get_drive_file_text_content for file_id {file_id}: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        # Propagate as a ValueError to indicate a more severe failure in the tool itself.
        raise ValueError(f"Failed to get/process file ID {file_id} from Google Drive. Error: {str(e)}")
    """Reads a file from Google Drive (given its file_id) and returns its text content.
    Handles Google Docs, Sheets, Slides (by exporting to PDF), native PDFs, and plain text files.
    Internally fetches the Google Drive service.

    Args:
        file_id: The ID of the file in Google Drive.

    Returns:
        The extracted text content of the file as a string.

    Raises:
        Exception: If the file cannot be accessed or processed, or if the Drive service cannot be initialized.
    """
    drive_service_to_use = get_drive_service()
    if not drive_service_to_use:
        # Consider logging this error as well
        print("Error: Google Drive service could not be initialized in get_drive_file_text_content.")
        # Return a meaningful message or raise a specific exception
        return "I am currently unable to access the Google Drive file because the drive service has not been initialized. Please ensure the drive service is properly set up and try again."
        # Alternatively, to propagate the error more strongly:
        # raise Exception("Google Drive service could not be initialized.")
    
    try:
        file_metadata = drive_service_to_use.files().get(fileId=file_id, fields='id, name, mimeType').execute()
        mime_type = file_metadata.get('mimeType')
        file_name = file_metadata.get('name', 'Unknown File')

        content_bytes = b''
        text_content = ''

        if mime_type == 'application/vnd.google-apps.document':
            print(f"Exporting Google Doc '{file_name}' (ID: {file_id}) to PDF for text extraction.")
            request = drive_service_to_use.files().export_media(fileId=file_id, mimeType='application/pdf')
            content_bytes = request.execute()
            # Fall through to PDF processing
        elif mime_type == 'application/vnd.google-apps.spreadsheet':
            print(f"Exporting Google Sheet '{file_name}' (ID: {file_id}) to PDF for text extraction.")
            request = drive_service_to_use.files().export_media(fileId=file_id, mimeType='application/pdf')
            content_bytes = request.execute()
            # Fall through to PDF processing
        elif mime_type == 'application/vnd.google-apps.presentation':
            print(f"Exporting Google Slides '{file_name}' (ID: {file_id}) to PDF for text extraction.")
            request = drive_service_to_use.files().export_media(fileId=file_id, mimeType='application/pdf')
            content_bytes = request.execute()
            # Fall through to PDF processing
        elif mime_type == 'application/pdf' or content_bytes: # content_bytes will be set if exported from GSuite type
            if not content_bytes: # If it's a native PDF, download it
                print(f"Downloading native PDF '{file_name}' (ID: {file_id}) for text extraction.")
                request = drive_service_to_use.files().get_media(fileId=file_id)
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
            request = drive_service_to_use.files().get_media(fileId=file_id)
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
                request = drive_service_to_use.files().get_media(fileId=file_id)
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
