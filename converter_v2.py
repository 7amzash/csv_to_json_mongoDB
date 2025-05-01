# -------------------------
# MODULE IMPORTS
# -------------------------
import pandas as pd  # To load and manipulate tabular data from CSV
import os  # For file/directory path management and command-like navigation
import json  # To convert the DataFrame into JSON format for MongoDB
import time  # Used for introducing delay to make the progress bar visible
from prompt_toolkit import prompt  # For user-friendly, interactive command-line prompts
from prompt_toolkit.completion import PathCompleter  # Enables tab-based file path completion
from tqdm import tqdm  # For displaying a progress bar during JSON saving
from pymongo import MongoClient  # MongoDB driver to connect, insert, query the database
import subprocess  # To run an external shell command like launching `mongosh` (MongoDB shell)

# -------------------------
# MAIN APPLICATION FUNCTION
# -------------------------
def main():
    os.chdir(os.environ.get("MOUNT_PATH", "/host"))  # Ensures the user starts in the /host directory, which is volume-mounted from the host OS
    path_completer = PathCompleter()  # Enable autocompletion for paths in prompts

    while True:
        # Prompt user to interact with the environment or select a CSV file
        user_input = prompt(
            "\n📄 Enter the full path of the CSV file to convert (or 'pwd', 'ls', 'cd <folder>', 'delete <file>', 'exit'): ",
            completer=path_completer
        ).strip()

        # -------------------------
        # COMMAND HANDLING SECTION
        # -------------------------
        if user_input.lower() == 'exit':
            print("👋 Exiting program. Goodbye!")
            os._exit(0)

        elif user_input.lower() == 'pwd':
            print(f"📂 Current Directory: {os.getcwd()}")
            continue

        elif user_input.lower() == 'ls':
            print("📄 Files and directories in current location:")
            for f in os.listdir():
                print(f"  └── {f}")
            continue

        elif user_input.lower().startswith('cd '):
            path = user_input[3:].strip()
            try:
                os.chdir(path)
                print(f"📁 Changed directory to: {os.getcwd()}")
            except Exception as e:
                print(f"❌ Failed to change directory: {e}")
            continue

        elif user_input.lower().startswith('delete '):
            target_file = user_input[7:].strip()
            try:
                if os.path.isfile(target_file):
                    os.remove(target_file)
                    print(f"🗑️ File deleted: {target_file}")
                else:
                    print(f"❌ File not found: {target_file}")
            except Exception as e:
                print(f"❌ Failed to delete file: {e}")
            continue

        # -------------------------
        # CSV FILE HANDLING
        # -------------------------
        csv_path = user_input
        if not os.path.isfile(csv_path):
            print("❌ File not found. Please check the path.")
            continue

        try:
            df = pd.read_csv(csv_path)  # Load CSV as pandas DataFrame
            num_rows = len(df)  # Count number of records
            print(f"\U0001F4C4 Successfully read {num_rows} rows from CSV file.")
        except Exception as e:
            print(f"❌ Failed to read CSV: {e}")
            continue

        # -------------------------
        # POST-IMPORT OPTIONS
        # -------------------------
        while True:
            save_option = prompt("💾 What do you want to do? (yes = save to file / no = show on screen / import = MongoDB): ").strip().lower()

            # Save to JSON file
            if save_option == 'yes':
                json_path = prompt(
                    "\U0001F4C1 Enter the path to save the JSON file (including filename): ",
                    completer=path_completer
                ).strip()
                try:
                    print("💾 Saving JSON file, please wait...")
                    for _ in tqdm(range(100), desc="Progress", ncols=100):
                        time.sleep(0.01)
                    df.to_json(json_path, orient='records', indent=4)
                    print(f"✅ Successfully wrote {num_rows} records to JSON file: {json_path}")
                    break
                except Exception as e:
                    print(f"❌ Failed to save JSON: {e}")
                    break

            # Display JSON content directly on terminal
            elif save_option == 'no':
                print("✅ Here is the JSON output:")
                print(df.to_json(orient='records', indent=4))
                print(f"🖨️ Displayed {num_rows} records from CSV in JSON format.")
                break

            # Import JSON data into MongoDB
            elif save_option == 'import':
                try:
                    db_name = prompt("🗄️ Enter MongoDB database name: ").strip()
                    collection_name = prompt("📚 Enter MongoDB collection name: ").strip()

                    # Connect to MongoDB running in another container using the Docker Compose service name
                    client = MongoClient(
                        host=os.environ.get("MONGODB_HOST", "mongodb"),
                        port=int(os.environ.get("MONGODB_PORT", 27017))
                    )
                    db = client[db_name]
                    collection = db[collection_name]

                    # Optional check: if collection is not empty, offer to clear it
                    doc_count = collection.count_documents({})
                    if doc_count > 0:
                        confirm_clear = prompt(
                            f"⚠️ Collection '{collection_name}' already contains {doc_count} documents. Clear it before import? (yes/no): "
                        ).strip().lower()
                        if confirm_clear == 'yes':
                            collection.delete_many({})
                            print("🧹 Collection cleared.")

                    # Convert DataFrame to JSON, then insert into MongoDB
                    data = json.loads(df.to_json(orient='records'))
                    if isinstance(data, list):
                        result = collection.insert_many(data)
                        print(f"✅ Imported {len(result.inserted_ids)} records into {db_name}.{collection_name}.")
                    else:
                        result = collection.insert_one(data)
                        print(f"✅ Imported 1 record into {db_name}.{collection_name}.")

                    # Launch interactive MongoDB shell (mongosh)
                    print("💻 Opening Mongo Shell... (type `exit` to return to the app)")
                    subprocess.call(["mongosh", "--host", os.environ.get("MONGODB_HOST", "mongodb"), db_name])
                    continue  # Return to import menu after shell

                except Exception as e:
                    print(f"❌ MongoDB import failed: {e}")
                    break

            # If user input is invalid
            else:
                print("❓ Invalid option. Please type 'yes', 'no', or 'import'.")

# -------------------------
# SCRIPT ENTRY POINT
# -------------------------
if __name__ == "__main__":
    main()