# Use official Python 3.12 lightweight image based on Debian slim
FROM python:3.12-slim

# ───────────────────────────────────────────
# Set the working directory inside the container for application logic
WORKDIR /app

# Copy the main application script into the container image
COPY converter_v2.py .

# ───────────────────────────────────────────
# Install Python dependencies required by the app
RUN pip install pandas prompt_toolkit tqdm pymongo
# pandas          - For reading/manipulating CSV files
# prompt_toolkit  - For rich user input with tab completion
# tqdm            - For progress bars
# pymongo         - To allow connecting and importing to MongoDB

# ───────────────────────────────────────────
# Install MongoDB Shell (`mongosh`) to allow in-container MongoDB CLI use

RUN apt-get update && \
    apt-get install -y wget gnupg curl && \
    # Fetch MongoDB GPG key and add to system's keyrings
    wget -qO - https://pgp.mongodb.com/server-6.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-6.0.gpg && \
    # Add MongoDB 6.0 official APT repository for Debian Bookworm
    echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/debian bookworm/mongodb-org/6.0 main" > /etc/apt/sources.list.d/mongodb-org-6.0.list && \
    apt-get update && \
    # Install only mongosh (not full MongoDB server)
    apt-get install -y mongodb-mongosh && \
    # Clean up to reduce image size
    apt-get clean && rm -rf /var/lib/apt/lists/*
# mongosh is needed to launch the MongoDB shell after importing data.

# ───────────────────────────────────────────
# Switch to /data where host filesystem will be mounted (/host) via docker-compose
WORKDIR /data

# ───────────────────────────────────────────
# Run the main Python script when the container starts
ENTRYPOINT ["python", "/app/converter_v2.py"]