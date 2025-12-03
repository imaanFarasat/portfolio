import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Google API
    GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID')
    GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    
    # Shopify
    SHOPIFY_SHOP_URL = os.getenv('SHOPIFY_SHOP_URL')
    SHOPIFY_ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
    SHOPIFY_API_VERSION = os.getenv('SHOPIFY_API_VERSION', '2024-01')
    
    # Webhook
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '')
    
    # OpenAI (for product descriptions)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

