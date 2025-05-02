 #==== IMPORTS ====

import pandas as pd  # Provides high-performance data manipulation and analysis tools, especially for reading/writing CSV and DataFrame operations.

import os  # Gives access to operating system functionalities such as file/directory manipulation (cd, ls, etc.).

import json  # Enables conversion between Python objects and JSON strings (used when saving to or interacting with JSON formats).

import time  # Offers time-related functions; here it's used to simulate loading delays (e.g., in progress bars).

from prompt_toolkit import prompt  # Replaces basic `input()` with an advanced terminal prompt that supports features like autocompletion and styling.

from prompt_toolkit.history import InMemoryHistory  # Enables command history in the prompt (use up/down arrow keys to recall previous inputs).

from prompt_toolkit.completion import WordCompleter, PathCompleter, Completer  # Used to implement autocompletion for commands and file paths.

from tqdm import tqdm  # Provides a visually appealing progress bar in the terminal, useful to indicate ongoing processing.

from pymongo import MongoClient  # MongoDB client used to connect and perform operations on MongoDB databases.

import subprocess  # Allows execution of shell commands from within Python (e.g., to launch `mongosh` shell).


# ==== CUSTOM COMPLETER CLASS ====

# Defines a custom completer that smartly decides between command and file path completion.
class CommandOrPathCompleter(Completer):
    def __init__(self, command_completer, path_completer):
        self.command_completer = command_completer  # Handles known command suggestions (e.g., 'ls', 'cd', etc.)
        self.path_completer = path_completer  # Handles filesystem path autocompletion.

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor  # Get the text the user has typed so far before the cursor.
        parts = text.strip().split()  # Split input into words (command and its arguments).

        if not parts:
            # If nothing is typed, show available commands.
            yield from self.command_completer.get_completions(document, complete_event)
            return

        command = parts[0]  # First word is assumed to be the command (e.g., 'cd').

        if command in ['cd', 'ls', 'delete']:
            if text.endswith(" ") or len(parts) >= 2:
                # If a space was typed or an argument is being entered, switch to path completion.
                arg_text = text[len(command) + 1:]  # Extract only the argument part.
                from prompt_toolkit.document import Document
                new_document = Document(text=arg_text, cursor_position=len(arg_text))
                yield from self.path_completer.get_completions(new_document, complete_event)
                return

        # If only a command is being typed, suggest matching command completions.
        if len(parts) == 1:
            yield from self.command_completer.get_completions(document, complete_event)


# ==== MAIN FUNCTION ====

def main():
    # Set the working directory to Docker mount point if defined, otherwise default to '/host'
    os.chdir(os.environ.get("MOUNT_PATH", "/host"))

    # Set up the file path completer for filesystem navigation
    path_completer = PathCompleter()

    # Define valid shell-like commands for this tool
    command_completer = WordCompleter(['ls', 'pwd', 'cd', 'delete', 'exit'], ignore_case=True)

    # Combine command and path completers into one smart completer
    smart_completer = CommandOrPathCompleter(command_completer, path_completer)

    # Create a history object to allow recalling previous commands using up/down arrow keys
    history = InMemoryHistory()

    # ==== MAIN PROMPT LOOP ====
    while True:
        # Display prompt with command history and autocompletion
        user_input = prompt(
            message="\n📄 Enter the full path of the CSV file to convert (or 'pwd', 'ls', 'cd <folder>', 'delete <file>', 'exit'): ",
            completer=smart_completer,
            history=history
        ).strip()  # Trim whitespace from the user input

        # ==== COMMAND HANDLING ====

        # Exit command
        if user_input.lower() == 'exit':
            print("👋 Exiting program. Goodbye!")
            os._exit(0)  # Forcefully exits the entire script immediately

        # Show current working directory
        elif user_input.lower() == 'pwd':
            print(f"📂 Current Directory: {os.getcwd()}")
            continue  # Loop again

        # List files and folders in the current directory
        elif user_input.lower() == 'ls':
            print("📄 Files and directories in current location:")
            for f in os.listdir():  # Get all entries in the current directory
                print(f"  └── {f}")
            continue

        # Change directory command
        elif user_input.lower().startswith('cd '):
            path = user_input[3:].strip()  # Extract the target path
            try:
                os.chdir(path)  # Change the working directory
                print(f"📁 Changed directory to: {os.getcwd()}")
            except Exception as e:
                print(f"❌ Failed to change directory: {e}")
            continue

        # Delete a file
        elif user_input.lower().startswith('delete '):
            target_file = user_input[7:].strip()  # Extract filename
            try:
                if os.path.isfile(target_file):  # Check if it's a valid file
                    os.remove(target_file)  # Delete the file
                    print(f"🗑️ File deleted: {target_file}")
                else:
                    print(f"❌ File not found: {target_file}")
            except Exception as e:
                print(f"❌ Failed to delete file: {e}")
            continue

        # ==== PROCESS CSV ====

        csv_path = user_input  # Assume input is a CSV file path
        if not os.path.isfile(csv_path):  # Check if file exists
            print("❌ File not found. Please check the path.")
            continue

        try:
            df = pd.read_csv(csv_path)  # Load CSV into a DataFrame
            num_rows = len(df)  # Count the number of rows loaded
            print(f"📊 Successfully loaded {num_rows} rows from CSV file.")
        except Exception as e:
            print(f"❌ Failed to read CSV: {e}")
            continue

        # ==== ACTION LOOP (Save, Print, or Import) ====

        while True:
            save_option = prompt("💾 What do you want to do? (yes = save to file / no = show on screen / import = MongoDB): ").strip().lower()

            # Save DataFrame to JSON file
            if save_option == 'yes':
                json_path = prompt("📁 Enter the path to save the JSON file (including filename): ", completer=path_completer).strip()
                try:
                    print("💾 Saving JSON file...")
                    for _ in tqdm(range(100), desc="Progress", ncols=100):  # Simulate progress
                        time.sleep(0.01)
                    df.to_json(json_path, orient='records', indent=4)  # Save in JSON format
                    print(f"✅ Saved {num_rows} records to: {json_path}")
                    break
                except Exception as e:
                    print(f"❌ Failed to save JSON: {e}")
                    break

            # Show JSON in terminal output
            elif save_option == 'no':
                print("✅ JSON output:")
                print(df.to_json(orient='records', indent=4))
                break

            # Import into MongoDB
            elif save_option == 'import':
                try:
                    db_name = prompt("🗄️ Enter MongoDB database name: ").strip()
                    collection_name = prompt("📚 Enter MongoDB collection name: ").strip()

                    # Connect to MongoDB server using environment vars or default values
                    client = MongoClient(
                        host=os.environ.get("MONGODB_HOST", "mongodb"),
                        port=int(os.environ.get("MONGODB_PORT", 27017))
                    )
                    db = client[db_name]
                    collection = db[collection_name]

                    doc_count = collection.count_documents({})  # Count current documents
                    if doc_count > 0:
                        confirm_clear = prompt(
                            f"⚠️ Collection '{collection_name}' already contains {doc_count} documents. Clear it before import? (yes/no): "
                        ).strip().lower()
                        if confirm_clear == 'yes':
                            collection.delete_many({})  # Remove existing documents
                            print("🧹 Existing documents cleared.")

                    data = json.loads(df.to_json(orient='records'))  # Convert DataFrame to JSON list

                    # Insert either list of documents or single document into MongoDB
                    if isinstance(data, list):
                        result = collection.insert_many(data)
                        print(f"✅ Inserted {len(result.inserted_ids)} records into {db_name}.{collection_name}.")
                    else:
                        result = collection.insert_one(data)
                        print(f"✅ Inserted 1 record into {db_name}.{collection_name}.")

                    # Open MongoDB shell for inspection
                    print("💻 Opening MongoDB shell... (type 'exit' to return)")
                    subprocess.call(["mongosh", "--host", os.environ.get("MONGODB_HOST", "mongodb"), db_name])
                    continue

                except Exception as e:
                    print(f"❌ MongoDB import failed: {e}")
                    break

            else:
                print("❓ Please enter 'yes', 'no', or 'import'.")


# ==== ENTRY POINT ====

if __name__ == "__main__":
    main()  # Starts the program if this script is run directly (not imported as a module)
