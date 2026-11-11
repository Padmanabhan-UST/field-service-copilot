import sys
from pathlib import Path
from typing import Literal

sys.path.append(str(Path(__file__).resolve().parents[1]))

from pydantic import BaseModel, Field, ValidationError
from common.clients import openai_client
from common.config import CHAT_DEPLOYMENT

INSTRUCTIONS = "Turn the technician's report into a maintenance work order. Use only facts from the report."

REPORT = (
    "PUMP-101 at the north plant is shaking badly, 7.8 mm/s on the drive end, and there is a grinding noise. "
    "Probably the bearings. We'll need two new BRG-6205-2RS and some grease. Two of us, about 3 hours."
)

class PartLine(BaseModel):
    part_number: str
    quantity: int

class WorkOrder(BaseModel):
    device_id: str
    priority: Literal["low", "medium", "high", "critical"]
    summary: str = Field(description="One Sentence, max 20 words")
    steps: list[str]
    parts: list[PartLine]
    estimated_hours: float

def prompt_only(client) -> str:
    response = client.responses.create(
        model = CHAT_DEPLOYMENT,
        instructions = INSTRUCTIONS + "Reply in JSON with device_id, priority, summary, steps, parts, estimated_hours.",
        input = REPORT
    )
    return response.output_text

def structured(client) -> WorkOrder:
    """The reliable way: the platform enforces the schema."""
    response = client.responses.parse(
        model=CHAT_DEPLOYMENT,
        instructions=INSTRUCTIONS,
        input=REPORT,
        text_format=WorkOrder,
    )
    return response.output_parsed

def main() -> None:
    client = openai_client()
    print("=== Prompt only, checked against the same schema")
    for attempt in range(1, 4):
        raw = prompt_only(client)
        try:
            WorkOrder.model_validate_json(raw)
            print(f"  attempt {attempt}: valid")
        except ValidationError as error:
            print(f"  attempt {attempt}: invalid ({error.error_count()} problems), starts with {raw[:40]!r}")

    print("\n=== Structured outputs")
    order = structured(client)
    print(order.model_dump_json(indent=2))
    print(f"\nTyped access: priority={order.priority!r}, first part={order.parts[0].part_number}")

if __name__== "__main__":
    main()
