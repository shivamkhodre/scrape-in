#!/bin/bash

# Exit on any error
set -e

# Define variables
REPO_URL="https://github.com/shivamkhodre/scrpe-in.git"  # Replace with your repository URL
TARGET_PATH="$HOME/Desktop/ScrapIN"
VENV_NAME="venv"
PYTHON_VERSION_REQUIRED="3.8"

echo "Starting project setup..."

# Step 1: Check for package manager
PACKAGE_MANAGER=""

if command -v apt-get &>/dev/null; then
    PACKAGE_MANAGER="apt-get"
elif command -v yum &>/dev/null; then
    PACKAGE_MANAGER="yum"
elif command -v dnf &>/dev/null; then
    PACKAGE_MANAGER="dnf"
elif command -v brew &>/dev/null; then
    PACKAGE_MANAGER="brew"
elif command -v pacman &>/dev/null; then
    PACKAGE_MANAGER="pacman"
else
    echo "No supported package manager found (apt-get, yum, dnf, brew, pacman). Please install required dependencies manually."
    exit 1
fi

echo "Using package manager: $PACKAGE_MANAGER"

# Step 2: Check and Install Python 3.11 if required
check_python() {
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 -c "import platform; print(platform.python_version())")
        if [[ "$(printf '%s\n' "$PYTHON_VERSION_REQUIRED" "$PYTHON_VERSION" | sort -V | head -n1)" != "$PYTHON_VERSION_REQUIRED" ]]; then
            echo "Python version is less than $PYTHON_VERSION_REQUIRED. Installing Python 3.11..."
            install_python
        else
            echo "Python version $PYTHON_VERSION is sufficient."
        fi
    else
        echo "Python is not installed. Installing Python 3.11..."
        install_python
    fi
}

install_python() {
    if [ "$PACKAGE_MANAGER" == "apt-get" ]; then
        sudo apt-get update -y
        sudo apt-get install -y software-properties-common
        sudo add-apt-repository -y ppa:deadsnakes/ppa
        sudo apt-get update -y
        sudo apt-get install -y python3.11 python3.11-venv python3.11-distutils
    elif [ "$PACKAGE_MANAGER" == "yum" ] || [ "$PACKAGE_MANAGER" == "dnf" ]; then
        sudo $PACKAGE_MANAGER install -y gcc libffi-devel zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel
        cd /usr/src
        sudo curl -O https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz
        sudo tar xzf Python-3.11.0.tgz
        cd Python-3.11.0
        sudo ./configure --enable-optimizations
        sudo make altinstall
        cd ..
        sudo rm -rf Python-3.11.0.tgz Python-3.11.0
    elif [ "$PACKAGE_MANAGER" == "brew" ]; then
        brew install python@3.11
    elif [ "$PACKAGE_MANAGER" == "pacman" ]; then
        sudo pacman -Syu python python-pip
    fi
    echo "Python 3.11 installed successfully."
}

# Call the function to check and install Python
check_python

# Step 3: Clone the repository
if [ ! -d "$TARGET_PATH" ]; then
    echo "Cloning repository..."
    git clone "$REPO_URL" "$TARGET_PATH"
else
    echo "Target directory already exists. Pulling latest changes..."
    cd "$TARGET_PATH" && git pull
fi

cd "$TARGET_PATH"

# Step 4: Create a virtual environment
if [ ! -d "$VENV_NAME" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_NAME"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_NAME/bin/activate"

# Step 5: Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "No requirements.txt file found!"
fi

mkdir -p logs

# Step 6: Check if Docker is installed
echo "Checking if Docker is installed..."
if ! command -v docker &>/dev/null; then
    echo "Docker is not installed. Installing Docker..."
    if [ "$PACKAGE_MANAGER" == "apt-get" ]; then
        sudo apt-get update -y
        sudo apt-get install -y docker.io
    elif [ "$PACKAGE_MANAGER" == "yum" ] || [ "$PACKAGE_MANAGER" == "dnf" ]; then
        sudo $PACKAGE_MANAGER install -y docker
    elif [ "$PACKAGE_MANAGER" == "brew" ]; then
        brew install --cask docker
    elif [ "$PACKAGE_MANAGER" == "pacman" ]; then
        sudo pacman -Syu docker
    fi
else
    echo "Docker is already installed."
fi

# Step 7: Start Docker (if systemctl is not found)
echo "Starting Docker..."
if command -v systemctl &>/dev/null; then
    sudo systemctl start docker
    sudo systemctl enable docker
else
    echo "systemctl not found. Starting Docker manually (if supported)."
    sudo dockerd &
fi

# Final message
echo "Project setup is complete. Virtual environment and Docker are ready to use."
