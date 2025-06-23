from agents import Agent, Runner, set_default_openai_key, trace, ItemHelpers
from dotenv import load_dotenv
import os
import asyncio
from scout_agents.reader_agent import reader_agent
from scout_agents.rename_agent import rename_agent
from scout_agents.file_mover_agent import file_mover_agent
from scout_agents.folder_agent import folder_agent

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

# Run with python -m backend.agents.scout_orchestrator
async def main(pdf_file_path: str, original_file_name: str, use_local_processing: bool = True):
    status_updates = []
    error_message = None
    current_file_path = pdf_file_path
    current_file_name = original_file_name if original_file_name else "unknown_file" # Fallback if not provided
    final_renamed_name = current_file_name # Initialize with original or fallback name
    final_target_folder_name = None
    final_target_folder_path = None # Local folder path instead of ID
    final_moved_path_info = None # Local file path after move

    try:
        with trace("Scout Orchestrator Local PDF Trace"):
            status_updates.append(f"Starting local PDF orchestration for file: {current_file_path}, original name: {current_file_name}")

            # Process local PDF file
            try:
                status_updates.append(f"Running Reader Agent for file: {current_file_path}")
                reader_payload = {
                    "file_path": current_file_path,
                    "original_file_name": current_file_name,
                    "task_prompt": f"Read the content of local PDF file '{current_file_path}' (original name: '{current_file_name}') and extract key information for organization."
                }
                read_file_run = await Runner.run(
                    reader_agent, 
                    reader_payload["task_prompt"]
                )
                #if read_file_run.error:
                 #   raise Exception(f"Reader Agent Error: {read_file_run.error_message}")
                extracted_content_model = read_file_run.final_output
                status_updates.append(f"Reader agent processed. Output content: {getattr(extracted_content_model, 'content', 'N/A')}")
                context_for_agents = getattr(extracted_content_model, 'content', '') # Use .content attribute
            except Exception as e:
                error_message = str(e)
                status_updates.append(f"Error during Reader Agent execution: {error_message}")
                raise

            # 2. Rename Agent
            try:
                status_updates.append(f"Running Rename Agent for file: {current_file_name}")
                rename_payload = {
                    "file_path": current_file_path,
                    "current_file_name": current_file_name,
                    "context": context_for_agents,
                    "task_prompt": f"Based on the context ('{context_for_agents[:200]}...') and current name, suggest a new, concise, and descriptive filename for the local PDF file '{current_file_name}' at '{current_file_path}'. Output only the new filename."
                }
                rename_file_run = await Runner.run(
                    rename_agent, 
                    rename_payload["task_prompt"]
                )
                renamed_file_info = rename_file_run.final_output
                # Extract new filename from rename_agent's output (RenameFileOutput(filename: str))
                if hasattr(renamed_file_info, 'filename') and isinstance(renamed_file_info.filename, str) and renamed_file_info.filename.strip():
                    final_renamed_name = renamed_file_info.filename.strip()
                    status_updates.append(f"Rename agent suggested new name: '{final_renamed_name}'")
                else:
                    status_updates.append(f"Rename agent did not return a valid new filename (got: {renamed_file_info}), using current name: {current_file_name}")
                # Note: actual rename operation happens within the agent. File path may change.
                # Update the current file path if rename was successful
                if final_renamed_name != current_file_name:
                    import os
                    current_file_dir = os.path.dirname(current_file_path)
                    current_file_path = os.path.join(current_file_dir, final_renamed_name)
                current_file_name = final_renamed_name # Update current name for subsequent agents
            except Exception as e:
                error_message = str(e)
                status_updates.append(f"Error during Rename Agent execution: {error_message}")
                raise

            # 3. Folder Agent
            folder_payload = {
                "file_path": current_file_path, 
                "file_name": current_file_name, 
                "context": context_for_agents, # Pass the extracted string content
                "task_prompt": f"Based on the content and name ('{current_file_name}') of local PDF file '{current_file_path}', determine a suitable local folder structure. If a relevant folder like 'Project Reports' or 'Invoices' exists, use it. Otherwise, create a new folder with an appropriate name. Output the folder name and path."
            }
            try:
                status_updates.append(f"Running Folder Agent for file: {current_file_name}")
                folder_suggestion_run = await Runner.run(
                    folder_agent, 
                    folder_payload["task_prompt"]
                )
                folder_info = folder_suggestion_run.final_output
                # Extract folder_name and folder_path from folder_agent's output (LocalFolderOutput(folder_name: str, folder_path: str))
                if hasattr(folder_info, 'folder_name') and hasattr(folder_info, 'folder_path'):
                    final_target_folder_name = getattr(folder_info, 'folder_name', None)
                    final_target_folder_path = getattr(folder_info, 'folder_path', None)
                    if not final_target_folder_name or not final_target_folder_path:
                        status_updates.append(f"Folder agent returned incomplete data: Name='{final_target_folder_name}', Path='{final_target_folder_path}'. Cannot proceed with move.")
                        raise ValueError(f"Folder agent did not return a valid folder name and path. Got: Name='{final_target_folder_name}', Path='{final_target_folder_path}'")
                else:
                    status_updates.append(f"Folder agent did not return expected LocalFolderOutput. Got: {folder_info}. Cannot proceed with move.")
                    raise ValueError(f"Folder agent did not return expected LocalFolderOutput. Got: {folder_info}")
                status_updates.append(f"File '{current_file_name}' at '{current_file_path}' to be organized in folder: '{final_target_folder_name}' (Path: {final_target_folder_path}) ")
            except Exception as e:
                error_message = str(e)
                status_updates.append(f"Error during Folder Agent execution: {error_message}")
                raise

            # 4. File Mover Agent
            # Ensure final_target_folder_path is valid before attempting move
            if not final_target_folder_path:
                status_updates.append(f"Cannot move file: Target folder path is missing. Skipping move operation.")
                final_moved_path_info = {"status": "skipped", "reason": "Missing target folder path"}
            else:
                mover_payload = {
                    "file_path": current_file_path,
                    "file_name": current_file_name,
                    "target_folder_name": final_target_folder_name,
                    "target_folder_path": final_target_folder_path, 
                    "task_prompt": f"Move the local PDF file '{current_file_name}' from '{current_file_path}' into the local folder named '{final_target_folder_name}' (Path: '{final_target_folder_path}'). Confirm success or report issues."
                }
                try:
                    status_updates.append(f"Running File Mover Agent for file: {current_file_name} to folder: {final_target_folder_name}")
                    move_file_run = await Runner.run(
                        file_mover_agent, 
                        mover_payload["task_prompt"]
                    )
                    final_moved_path_info = move_file_run.final_output
                    status_updates.append(f"File move processed. Mover output: {final_moved_path_info}")
                except Exception as e:
                    error_message = str(e)
                    status_updates.append(f"Error during File Mover Agent execution: {error_message}")
                    raise
            
            status_updates.append("Local PDF orchestration completed.")

    except Exception as e:
        error_message = str(e)
        status_updates.append(f"Error during orchestration: {error_message}")
        # Log full traceback for server-side debugging
        import traceback
        print(f"Orchestrator Error: {error_message}\n{traceback.format_exc()}")

    # Prepare final_path_suggestion string
    final_path_suggestion_str = None
    if final_moved_path_info:
        if isinstance(final_moved_path_info, dict):
            fmpi_status = final_moved_path_info.get('status', 'unknown')
            fmpi_detail = str(final_moved_path_info)
        elif hasattr(final_moved_path_info, 'status'): # Assuming it's an object
            fmpi_status = getattr(final_moved_path_info, 'status', 'unknown')
            fmpi_detail = str(final_moved_path_info) # Or format specific attributes
        else:
            fmpi_status = 'unknown'
            fmpi_detail = str(final_moved_path_info)
        
        final_path_suggestion_str = f"Move status: {fmpi_status}. Details: {fmpi_detail}"

    return {
        "original_file": original_file_name or os.path.basename(pdf_file_path), # String
        "renamed_file": final_renamed_name, # String
        "target_folder": final_target_folder_name, # String (can be None)
        "final_path_suggestion": final_path_suggestion_str, # String (can be None)
        "status_updates": status_updates,
        "error_message": error_message
    }

# if __name__ == "__main__":
    # Example usage (commented out as it requires live drive_service and file_id):
    # test_file_id = "your_google_drive_file_id_here" 
    # test_original_name = "test_document.pdf"
    # # You would need to set up a mock or real drive_service for local testing
    # class MockDriveService:
    #     def files(self):
    #         # Implement mock methods as needed by agents for testing
    #         pass 
    # mock_service = MockDriveService()
    # orchestration_result = asyncio.run(main(test_file_id, mock_service, test_original_name))
    # print("\nOrchestration Result:")
    # for key, value in orchestration_result.items():
    #     if key == "status_updates" and isinstance(value, list):
    #         print(f"  {key}:")
    #         for update in value:
    #             print(f"    - {update}")
    #     else:
    #         print(f"  {key}: {value}")