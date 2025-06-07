#!/usr/bin/env python3
"""
Run script for the Degrees of Spotify Flask application.
"""

import os
import sys
from app import app
from config import Config

def main():
    """Main function to run the Flask application."""
    try:
        # Validate configuration
        Config.validate_config()
        print("✓ Configuration validated successfully")
        
        # Check if adjacency list file exists
        if os.path.exists(Config.CSV_FILE):
            print(f"✓ Found adjacency list file: {Config.CSV_FILE}")
        else:
            print(f"⚠ Adjacency list file not found: {Config.CSV_FILE}")
            print("  The application will create it when artists are added.")
        
        print("\n" + "="*50)
        print("🎵 Starting Degrees of Spotify Web Application")
        print("="*50)
        print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
        print(f"Debug mode: {Config.DEBUG}")
        print(f"CSV file: {Config.CSV_FILE}")
        print("="*50)
        port = int(os.environ.get('PORT', 5001))
        print("\n🌐 Application will be available at:")
        print(f"   http://localhost:{port}")
        print(f"   http://127.0.0.1:{port}")
        print("\n📱 API endpoints:")
        print("   POST /api/search - Start artist search")
        print("   GET  /api/search/<id>/status - Get search status")
        print("   GET  /api/search/<id>/result - Get search result")
        print("   GET  /api/artists/search - Search for artists")
        print("\n🛑 Press Ctrl+C to stop the server")
        print("="*50 + "\n")
        
        # Run the Flask application
        port = int(os.environ.get('PORT', 5001))
        app.run(
            debug=Config.DEBUG,
            host='0.0.0.0',
            port=port,
            threaded=True
        )
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n💡 Make sure you have a .env file with:")
        print("   CLIENT_ID=your_spotify_client_id")
        print("   CLIENT_SECRET=your_spotify_client_secret")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()