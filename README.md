# CSV to JSON + MongoDB Import Tool

This project is a fully Dockerized, interactive command-line application that allows users to:

- Load and inspect CSV files
- Convert CSV files into JSON format
- Save or preview JSON output
- Import data into a MongoDB database
- Interact with the MongoDB shell (`mongosh`)
- Navigate and manipulate files within the host system using tab-completion

The tool is built using Python and designed for portability, extensibility, and ease of use in local or educational environments.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Mounting Files from Host](#mounting-files-from-host)
- [Common Commands](#common-commands)
- [Troubleshooting](#troubleshooting)
- [Cleanup](#cleanup)
- [License](#license)

---

## Features

- Interactive command-line interface with autocompletion via `prompt_toolkit`
- CSV-to-JSON conversion with `pandas` and `tqdm` for progress display
- Flexible options: show JSON, save to file, or import to MongoDB
- MongoDB import includes duplicate handling and optional collection wipe
- Embedded MongoDB shell (`mongosh`) access from within the app
- Docker-based deployment with support for named volumes and host path mounting

---

## Architecture

The app runs as a containerized Python service that mounts a directory from the host system to access files. MongoDB is run as a separate service within the same Docker Compose network.

```
Host System
│
├── run.sh                    ← Launches Dockerized app with dynamic volume
├── docker-compose.yml       ← Defines 'app' and 'mongodb' services
├── Dockerfile               ← Builds Python + mongosh image
├── converter_v2.py          ← Main interactive CLI script
├── .env                     ← Defines HOST_PATH and config (optional)
└── [Your CSV Folder]        ← Mounted into container as /host
```

---

## Requirements

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- Bash-compatible terminal (Linux, macOS, or WSL)

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/csv-json-mongodb-tool.git
   cd csv-json-mongodb-tool
   ```

2. (Optional) Create a `.env` file:

   ```bash
   echo "HOST_PATH=/absolute/path/to/your/folder" > .env
   ```

3. Make the run script executable:

   ```bash
   chmod +x run.sh
   ```

---

## Usage

To start the application:

```bash
HOST_PATH=/your/path ./run.sh
```

Or if using `.env`, just run:

```bash
./run.sh
```

The app will open an interactive terminal. You can:

- Navigate folders (`cd`, `ls`, `pwd`)
- Select and load a CSV file
- Choose one of three options:
  - Display JSON in terminal
  - Save JSON to a file
  - Import JSON into MongoDB

You will also be prompted whether to clear the MongoDB collection before import, and have the option to enter a live Mongo shell session.

---

## Configuration

These environment variables control runtime behavior:

| Variable       | Required | Default     | Description                                 |
|----------------|----------|-------------|---------------------------------------------|
| `HOST_PATH`    | Yes      | (none)      | Path on host system to mount into container |
| `MOUNT_PATH`   | No       | `/host`     | Container path to access mounted files      |
| `MONGODB_HOST` | No       | `mongodb`   | Hostname of MongoDB service (container name)|
| `MONGODB_PORT` | No       | `27017`     | MongoDB port                                |

You can define these inline, via `.env`, or export them manually.

---

## Mounting Files from Host

The application relies on Docker bind mounts to access your host filesystem.

For example, if you want to work with a CSV located at:

```
/mnt/g/Etudes/sales.csv
```

You must provide the parent folder using `HOST_PATH`:

```bash
HOST_PATH=/mnt/g/Etudes ./run.sh
```

This makes the file accessible in the container at:

```
/host/sales.csv
```

---

## Common Commands Inside the App

| Command Example           | Description                                     |
|---------------------------|-------------------------------------------------|
| `ls`                      | List contents of current directory              |
| `pwd`                     | Print current directory                         |
| `cd folder_name`          | Change to a different folder                    |
| `delete file_name`        | Delete a file in the current directory          |
| `exit`                    | Quit the application                            |
| `filename.csv`            | Load and process the CSV file                   |

After CSV load, you’ll be prompted to:

- Display as JSON
- Save to JSON file
- Import into MongoDB

---

## Troubleshooting

- **File Not Found?**  
  Ensure the folder containing the CSV is mounted using `HOST_PATH`.

- **MongoDB Not Connecting?**  
  Make sure Docker Compose is running both the app and the MongoDB service.

- **Cannot see `/mnt/g/...` files?**  
  Share your G: drive in Docker Desktop settings under "Resources > File Sharing".

- **Prompt autocompletion not working?**  
  Use a compatible terminal (WSL, macOS Terminal, or Linux). Windows CMD is not fully supported.

---

## Cleanup

To stop and clean up all running containers and volumes:

```bash
./run.sh --down
```

To force rebuild the app image:

```bash
./run.sh --rebuild
```

To view logs:

```bash
./run.sh --logs
```

---

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
