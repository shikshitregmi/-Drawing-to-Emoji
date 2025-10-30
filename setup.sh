#!/bin/bash

echo "Setting up Draw to Emoji App..."

# Create virtual environment
python3 -m venv emoji_env
source emoji_env/bin/activate

# Install requirements
pip install -r requirements.txt

# Create necessary directories
mkdir -p assets
mkdir -p utils
mkdir -p models

# Make sure emoji database exists
if [ ! -f "assets/emoji_database.json" ]; then
    echo "Error: Please make sure assets/emoji_database.json exists"
    exit 1
fi

echo "Setup complete!"
echo "To run the app:"
echo "source emoji_env/bin/activate && streamlit run app.py"