#!/bin/bash

# Activate virtual environment and run the Spotify degrees of separation program
echo "Activating virtual environment..."
source venv/bin/activate

echo "Starting Degrees of Spotify..."
echo "Choose which version to run:"
echo "1. Console version (Spotipy.py)"
echo "2. GUI version (SpotipyGUI.py)"
echo "3. Test Spotify functions (spotifyFunctions.py)"
read -p "Enter your choice (1, 2, or 3): " choice

case $choice in
    1)
        python Spotipy.py
        ;;
    2)
        python SpotipyGUI.py
        ;;
    3)
        python spotifyFunctions.py
        ;;
    *)
        echo "Invalid choice. Running console version by default..."
        python Spotipy.py
        ;;
esac