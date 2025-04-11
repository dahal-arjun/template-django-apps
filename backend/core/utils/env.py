import os
from pathlib import Path
from dotenv import load_dotenv

def load_env_files():
    """Load environment variables from .env files."""
    env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
    
    # Load .env file if it exists
    if os.path.exists(env_path):
        load_dotenv(env_path)
    
    # Load environment-specific .env file
    env = os.getenv('DJANGO_ENV', 'development')
    env_file = f'.env.{env}'
    env_path = Path(__file__).resolve().parent.parent.parent.parent / env_file
    
    if os.path.exists(env_path):
        load_dotenv(env_path)