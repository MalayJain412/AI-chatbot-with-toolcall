import os
import logging
import dotenv

dotenv.load_dotenv()

# Azure OpenAI Configuration
try:
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT", "gpt-4.1-mini")
    AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "2025-01-01-preview")

    logging.info(f"\n\nAzure OpenAI Endpoint: {AZURE_OPENAI_ENDPOINT}")
    logging.info(f"\n\nAzure OpenAI Deployment: {AZURE_DEPLOYMENT}")
except Exception as e:
    logging.error("Error loading configuration from environment variables", exc_info=True)
    raise e

# Email Configuration
try:
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("APP_PASSWORD")
    admin_email = os.getenv("ADMIN_EMAIL")
except Exception as e:
    logging.error("Error loading email configuration from environment variables", exc_info=True)
    raise e