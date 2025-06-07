import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class."""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    # Spotify API configuration
    SPOTIFY_CLIENT_ID = os.environ.get('CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
    
    # Application configuration
    CSV_FILE = os.environ.get('CSV_FILE', 'adjacency_list.csv')
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', '10'))
    RATE_LIMIT_DELAY = float(os.environ.get('RATE_LIMIT_DELAY', '0.333'))  # 3 requests per second
    MAX_RETRIES = int(os.environ.get('MAX_RETRIES', '3'))
    RETRY_DELAY = int(os.environ.get('RETRY_DELAY', '10'))
    
    # Search configuration
    MAX_SEARCH_TIME = int(os.environ.get('MAX_SEARCH_TIME', '300'))  # 5 minutes max
    CLEANUP_INTERVAL = int(os.environ.get('CLEANUP_INTERVAL', '3600'))  # 1 hour
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration values."""
        errors = []
        
        if not cls.SPOTIFY_CLIENT_ID:
            errors.append("SPOTIFY_CLIENT_ID (CLIENT_ID) is required")
            
        if not cls.SPOTIFY_CLIENT_SECRET:
            errors.append("SPOTIFY_CLIENT_SECRET (CLIENT_SECRET) is required")
            
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(errors))
        
        return True

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration class based on environment."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])