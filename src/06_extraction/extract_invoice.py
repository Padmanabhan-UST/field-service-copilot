"""Session 10: extract invoice fields with the prebuilt invoice model vs DIY OCR + LLM."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.identity import DefaultAzureCredential
from pydantic import BaseModel

from common.clients import openai_client
from common.config import CHAT_DEPLOYMENT, PROJECT_ENDPOINT

INVOICE_URL = (
    "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/"
    "master/curl/form-recognizer/rest-api/invoice.pdf"
)
KEY_FIELDS = ["VendorName", "InvoiceId", "InvoiceDate", "InvoiceTotal"]
REVIEW_BELOW = 0.8  # send to a person if any key field is less confident than this


class InvoiceLine(BaseModel):
    description: str
    amount: float


class Invoice(BaseModel):
    vendor_name: str
    invoice_id: str
    invoice_date: str
    invoice_total: float
    items: list[InvoiceLine]


def document_client() -> DocumentIntelligenceClient:
    return DocumentIntelligenceClient(PROJECT_ENDPOINT.split("/api/projects/")[0], DefaultAzureCredential())


def prebuilt(client: DocumentIntelligenceClient) -> None:
    print("=== Prebuilt invoice model")
    result = client.begin_analyze_document("prebuilt-invoice", AnalyzeDocumentRequest(url_source=INVOICE_URL)).result()
    fields = result.documents[0].fields
    for name in KEY_FIELDS:
        print(f"  {name:<12} {fields[name].content!r:<25} confidence {fields[name].confidence:.2f}")
    for line in fields["Items"].value_array:
        item = line.value_object
        print(f"  item: {item['Description'].value_string:<25} {item['Amount'].value_currency.amount:>8.2f}")
    low = [name for name in KEY_FIELDS if fields[name].confidence < REVIEW_BELOW]
    print("  -> send to a person: " + ", ".join(low) if low else "  -> auto-approve: all key fields confident")


def diy(client: DocumentIntelligenceClient) -> None:
    print("\n=== DIY: OCR (prebuilt-read) + LLM with structured outputs")
    text = client.begin_analyze_document("prebuilt-read", AnalyzeDocumentRequest(url_source=INVOICE_URL)).result().content
    response = openai_client().responses.parse(
        model=CHAT_DEPLOYMENT,
        instructions="Extract the invoice fields from this OCR text.",
        input=text,
        text_format=Invoice,
    )
    print(response.output_parsed.model_dump_json(indent=2))
    print("  -> no confidence scores: nothing tells you which fields to double-check")


def main() -> None:
    client = document_client()
    prebuilt(client)
    diy(client)


if __name__ == "__main__":
    main()