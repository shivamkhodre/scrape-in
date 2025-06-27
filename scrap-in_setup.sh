#!/bin/bash

# Exit on any error
set -e

# Define variables
REPO_URL="https://github.com/shivamkhodre/scrpe-in.git"  # Replace with your repository URL
TARGET_PATH="$HOME/Desktop/ScrapIN"
VENV_NAME="venv"

echo "Starting project setup..."

# Step 1: Clone the repository
if [ ! -d "$TARGET_PATH" ]; then
    echo "Cloning repository..."
    git clone "$REPO_URL" "$TARGET_PATH"
else
    echo "Target directory already exists. Pulling latest changes..."
    cd "$TARGET_PATH" && git pull
fi

cd "$TARGET_PATH"

# Step 2: Create a virtual environment
if [ ! -d "$VENV_NAME" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_NAME"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_NAME/bin/activate"

# Step 3: Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "No requirements.txt file found!"
fi

mkdir -p logs

# Step 4: Check if Docker is installed
echo "Checking if Docker is installed..."
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Installing Docker..."

    # Update package index
    sudo apt-get update -y

    # Install Docker
    sudo apt-get install -y docker.io

    # Start and enable Docker service
    sudo systemctl start docker
    sudo systemctl enable docker

    echo "Docker installed successfully."
else
    echo "Docker is already installed."
fi

# Final message
echo "Project setup is complete. Virtual environment and Docker are ready to use."

