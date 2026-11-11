"""Keyless clients: authenticate with Microsoft Entra ID, never API keys."""
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI
import requests
from common.config import PROJECT_ENDPOINT, SEARCH_ENDPOINT

_credential = DefaultAzureCredential()


def project_client() -> AIProjectClient:
    return AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=_credential)


def openai_client():
    """OpenAI-compatible client authenticated with your Entra identity."""
    return project_client().get_openai_client()

def search_index_client():
    """Control Plane for the index: create or update its definitions"""
    return SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=_credential)

def search_client(index_name: str):
    """Data plane: upload and query documents in one index"""
    return SearchClient(endpoint=SEARCH_ENDPOINT, index_name=index_name, credential=_credential)

def embeddings_client() -> OpenAI:
    """Embeddings are served on the Foundry resource endpoint, not the project endpoint."""
    resource_endpoint = PROJECT_ENDPOINT.split("/api/projects/")[0]
    return OpenAI(
        base_url=f"{resource_endpoint}/openai/v1/",
        api_key=get_bearer_token_provider(_credential, "https://ai.azure.com/.default"),
    )

def content_safety(operation: str, body: dict, api_version: str = "2024-09-01") -> dict:
    """Call an Azure AI Content Safety operation on the Foundry resource, keyless."""
    resource_endpoint = PROJECT_ENDPOINT.split("/api/projects/")[0]
    token = _credential.get_token("https://cognitiveservices.azure.com/.default").token
    response = requests.post(
        f"{resource_endpoint}/contentsafety/text:{operation}",
        params={"api-version": api_version},
        headers={"Authorization": f"Bearer {token}"},
        json=body,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()