"""Keyless clients: authenticate with Microsoft Entra ID, never API keys."""
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

from common.config import PROJECT_ENDPOINT

_credential = DefaultAzureCredential()


def project_client() -> AIProjectClient:
    return AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=_credential)


def openai_client():
    """OpenAI-compatible client authenticated with your Entra identity."""
    return project_client().get_openai_client()
