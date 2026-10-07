import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Access your config values in Python
api_key = os.getenv("FIREBASE_API_KEY")
project_id = os.getenv("FIREBASE_PROJECT_ID")

print(f"Loaded project: {project_id}")