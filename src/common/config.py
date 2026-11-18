"""Loads settings from .env so no endpoints or names are hard-coded."""
import os
from dotenv import load_dotenv

load_dotenv()


def require(name: str) -> str:
    value = os.getenv(name)
    if not value or "<" in value:
        raise RuntimeError(f"Set {name} in your .env file (see .env.example).")
    return value


PROJECT_ENDPOINT = require("PROJECT_ENDPOINT")
CHAT_DEPLOYMENT = require("CHAT_DEPLOYMENT")
EMBEDDING_DEPLOYMENT = os.getenv("EMBEDDING_DEPLOYMENT", "")
SEARCH_ENDPOINT = require("SEARCH_ENDPOINT")
APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")
IMAGE_DEPLOYMENT = os.getenv("IMAGE_DEPLOYMENT", "")
FOUNDRY_RESOURCE_ID = os.getenv("FOUNDRY_RESOURCE_ID", "")
AZURE_REGION = os.getenv("AZURE_REGION", "")
