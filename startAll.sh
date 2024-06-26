#!/bin/bash
echo "Listing all containers..."
docker ps -a
# Stop all running containers
echo "Stopping all running containers..."
docker stop $(docker ps -q)
# Remove all stopped containers
echo "Removing all stopped containers..."
docker rm $(docker ps -a -q)
# Prune the system (remove all unused data)
echo "Pruning the system..."
docker system prune -f
echo "All containers stopped and pruned successfully."
docker pull ollama/ollama:latest
mkdir ollama-models
docker run -d -p 11434:11434 --name ollama2 -v $(pwd)/ollama-models:/ollama/models ollama/ollama:latest
docker exec ollama2 ollama pull llama3
docker exec ollama2 ollama pull nomic-embed-text
docker pull qdrant/qdrant
docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage:z qdrant/qdrant &
cd backend
source .venv/activate
pip install -r requirements.txt
pip install nltk
pip install ollama
pip install mattsollamatools
python3 ImportJsonFiles.py
python3 wsServer.py
cd ..
cd frontend
npm install
npm start


# URL to open
url="http://127.0.0.1:3000/"

# Function to open URL in Chrome
open_in_chrome() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open -a "Google Chrome" "$url"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        google-chrome "$url" || chromium-browser "$url"
    else
        echo "Unsupported OS: $OSTYPE"
        exit 1
    fi
}

# Call the function
open_in_chrome
