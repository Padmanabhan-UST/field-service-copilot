"""Session 8: field agent combining live device data, manual search and a human-approved spare-part order."""
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from azure.ai.projects.models import (
    AISearchIndexResource,
    AzureAISearchTool,
    AzureAISearchToolResource,
    FunctionTool,
    PromptAgentDefinition,
)

from common.clients import project_client
from common.config import CHAT_DEPLOYMENT
from device_agent import build_tools as device_api_tool

AGENT_NAME = "field-service-agent"

INSTRUCTIONS = (
    "You help field technicians. Always check live device status with the device API first. "
    "Explain alarms and procedures only from the manuals (search tool) and cite them. "
    "To order parts, call order_spare_part with exact part numbers from the manual's spare parts list; "
    "never invent part numbers. Orders need human approval."
)

ORDER_TOOL = FunctionTool(
    name = "order_spare_part",
    description= "Order a spare part for a device. Needs human approval. Only use exact part numbers from the manual.",
    parameters={
        "type": "object",
        "properties": {
            "device_id": {"type": "string"},
            "part_number": {"type": "string"},
            "quantity": {"type": "integer"},
            "reason": {"type": "string"},
        },
        "required": ["device_id", "part_number", "quantity", "reason"],
        "additionalProperties": False,
    },
    strict= True
)

def manuals_search_tool(project) -> AzureAISearchTool:
    connection = next(c for c in project.connections.list() if "AZURE_AI_SEARCH" in str(c.type))
    return AzureAISearchTool(
        azure_ai_search=AzureAISearchToolResource(
            indexes=[
                AISearchIndexResource(
                    project_connection_id=connection.id, index_name="manuals", query_type="semantic", top_k=3
                )
            ]
        )
    )

def approve_and_order(args: dict) -> dict:
    """The human approval gate: nothing is ordered unless a person types y."""
    print(f"\n  APPROVAL NEEDED: {args['quantity']} x {args['part_number']} for {args['device_id']}")
    print(f"  Reason: {args['reason']}")
    if input("  Approve this order? (y/n): ").strip().lower() != "y":
        return {"status": "rejected", "message": "The supervisor rejected this order."}
    return {"status": "ordered", "order_id": f"PO-{args['device_id']}-{args['part_number']}"}

def ask(client, agent_ref: dict, question: str, previous_id: str | None = None):
    print(f"\nYou: {question}")
    chain = {"previous_response_id": previous_id} if previous_id else {}
    response = client.responses.create(input=question, extra_body=agent_ref, **chain)
    while True:
        print(f"  [steps: {', '.join(item.type for item in response.output)}]")
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            break
        outputs = [
            {
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(approve_and_order(json.loads(call.arguments))),
            }
            for call in calls
        ]
        response = client.responses.create(input=outputs, previous_response_id=response.id, extra_body=agent_ref)
    print(f"Agent: {response.output_text}")
    return response


def main() -> None:
    project = project_client()
    agent = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=CHAT_DEPLOYMENT,
            instructions=INSTRUCTIONS,
            tools=[device_api_tool(), manuals_search_tool(project), ORDER_TOOL],
        ),
    )
    print(f"Created agent {agent.name} v{agent.version}")

    agent_ref = {"agent_reference": {"name": agent.name, "version": agent.version, "type": "agent_reference"}}
    with project.get_openai_client() as client:
        try:
            first = ask(client, agent_ref, "PUMP-101 is shaking and running hot. What's wrong and what does the manual say?")
            ask(client, agent_ref, "Order the parts needed for the bearing replacement.", first.id)
        finally:
            project.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print(f"\nDeleted agent {agent.name} v{agent.version}")


if __name__ == "__main__":
    main()
