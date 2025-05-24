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
async def main(file_name_to_process: str):
    status_updates = []
    error_message = None
    final_renamed_file = None
    final_target_folder = None
    final_moved_path = None

    try:
        # Run entire workflow in one trace
        with trace("Scout Orchestrator Trace"):
            msg = f"Read the file '{file_name_to_process}', then organize it with the given tools."
            status_updates.append(f"Starting orchestration for: {file_name_to_process}")

            read_file_run = await Runner.run(reader_agent, msg)
            # Assuming read_file_run.final_output is relevant context/keyword for renaming
            # And read_file_run.to_input_list() is what rename_agent expects as input for the file to be renamed.
            # This part might need adjustment based on actual agent contracts.
            # For rename_agent, the input should be the name of the file to rename.
            # Let's assume the input to rename_agent should be file_name_to_process if read_file_run doesn't provide it explicitly.
            # The original code passed `input_items` from `read_file.to_input_list()` to rename_agent.
            input_for_rename = read_file_run.to_input_list() # This should resolve to the filename to be renamed or context for it.
            status_updates.append(f"Reader agent processed. Output: {read_file_run.final_output}. Input for rename: {input_for_rename}")

            # If input_for_rename is not the actual filename, but context, then rename_agent needs the filename.
            # The rename_agent's prompt: "Your job is to rename a PDF File. You get an input from another agent. That input is the name of the file you should rename."
            # Let's assume the primary argument to Runner.run for rename_agent should be the file path/name it's supposed to rename.
            # If read_file_run.to_input_list() provides this, great. Otherwise, it might need to be file_name_to_process.
            # For now, sticking to the structure implied by the original code for agent inputs.
            renamed_file_run = await Runner.run(rename_agent, input_for_rename) 
            
            # Extract new filename from rename_agent's output
            if hasattr(renamed_file_run.final_output, 'filename'):
                final_renamed_file = renamed_file_run.final_output.filename
            elif isinstance(renamed_file_run.final_output, dict) and 'filename' in renamed_file_run.final_output:
                final_renamed_file = renamed_file_run.final_output['filename']
            elif isinstance(renamed_file_run.final_output, str): # If it's just the string
                final_renamed_file = renamed_file_run.final_output
            else:
                raise ValueError(f"Rename agent did not return expected filename. Got: {renamed_file_run.final_output}")
            status_updates.append(f"File renamed to: {final_renamed_file}")

            # Folder agent should operate on the newly renamed file
            foldered_file_run = await Runner.run(folder_agent, f"Organize the file called {final_renamed_file}")
            if hasattr(foldered_file_run.final_output, 'folder_name'):
                final_target_folder = foldered_file_run.final_output.folder_name
            elif isinstance(foldered_file_run.final_output, str):
                final_target_folder = foldered_file_run.final_output
            else:
                raise ValueError(f"Folder agent did not return expected folder name. Got: {foldered_file_run.final_output}")
            status_updates.append(f"File to be organized in folder: {final_target_folder}")

            moved_file_run = await Runner.run(file_mover_agent, f"Move the file called {final_renamed_file} to the folder {final_target_folder}")
            # Assuming the file_mover_agent works with paths relative to an 'assets' or similar base directory for tools
            # The actual final path might be constructed based on where file_mover_agent places it.
            # For now, let's assume the 'final_target_folder' is a conceptual destination.
            final_moved_path = f"{final_target_folder}/{final_renamed_file}" # Example path construction
            status_updates.append(f"File move requested. Mover output: {moved_file_run.final_output}")
            status_updates.append("Orchestration completed.")

    except Exception as e:
        error_message = str(e)
        status_updates.append(f"Error during orchestration: {error_message}")

    return {
        "original_file": file_name_to_process,
        "renamed_file": final_renamed_file,
        "target_folder": final_target_folder,
        "final_path_suggestion": final_moved_path, # This is a suggested path
        "status_updates": status_updates,
        "error_message": error_message
    }

if __name__ == "__main__":
    # Example usage:
    test_file = "test_file.pdf" # Make sure this file exists in backend/assets/
    # Create a dummy file in backend/assets/ for local testing if it doesn't exist
    assets_dir = os.path.join(os.path.dirname(__file__), "../assets")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    dummy_file_path = os.path.join(assets_dir, test_file)
    if not os.path.exists(dummy_file_path):
        print(f"Warning: {test_file} not found in backend/assets/. Creating a dummy file.")
        with open(dummy_file_path, "w") as f:
            f.write("This is a test PDF content for Scout orchestrator testing.")
            
    orchestration_result = asyncio.run(main(test_file))
    print("\nOrchestration Result:")
    for key, value in orchestration_result.items():
        if key == "status_updates" and isinstance(value, list):
            print(f"  {key}:")
            for update in value:
                print(f"    - {update}")
        else:
            print(f"  {key}: {value}")