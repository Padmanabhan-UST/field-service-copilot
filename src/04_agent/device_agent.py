import json
import sys                                                    
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))    


from azure.ai.projects.models import (
    OpenApiAnonymousAuthDetails,
    OpenApiFunctionDefinition,
    OpenApiTool,
    PromptAgentDefinition,
)

from common.clients import project_client
from common.config import CHAT_DEPLOYMENT


AGENT_NAME = "device-status-agent"

SPEC_PATH = Path(__file__).resolve().parent / "device_api.openapi.json"

INSTRUCTIONS = (
    "You help field technicians maintaining pumps and compressors. Always check live device status with "
    "the device API before giving advice. Mention active alarm codes, the readings that matter, and "
    "what to do next, in at most five sentences."
)

def build_tools() -> OpenApiTool:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    return OpenApiTool(
        openapi = OpenApiFunctionDefinition(
            name="device_api",
            description="Live telemetry and alarms for plant equipment, looked up by device ID.",
            spec=spec,
            auth=OpenApiAnonymousAuthDetails(),
        )
    )

def main() -> None:
    project = project_client()
    agent = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(model=CHAT_DEPLOYMENT, instructions = INSTRUCTIONS, tools =[build_tools()])
    )
    print(f"Created agent {agent.name} v{agent.version}")
    agent_ref = {"agent_reference": {"name": agent.name, "version": agent.version, "type": "agent_reference"}}

    with project.get_openai_client() as client:
        try:
            for question in [
                "Is PUMP-101 healthy?",
                "Compare PUMP-202 and AC75-007. Which one needs attention first?",
            ]:
                response = client.responses.create(input=question, extra_body=agent_ref)
                calls = [item for item in response.output if item.type == "openapi_call"]
                print(f"\nYou:   {question}")
                print(f"  [Foundry made {len(calls)} API call(s)]")
                print(f"Agent: {response.output_text}")
        finally:
            project.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print(f"\nDeleted agent {agent.name} v{agent.version}")


if __name__ == "__main__":
    main()