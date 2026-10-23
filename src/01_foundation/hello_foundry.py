"""Session 1: first keyless call to a Foundry model deployment."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.clients import openai_client
from common.config import CHAT_DEPLOYMENT


def main() -> None:
    client = openai_client()
    response = client.responses.create(
        model=CHAT_DEPLOYMENT,
        input="In two sentences, what is hybrid search and why would a field technician need it?",
    )
    print(response.output_text)


if __name__ == "__main__":
    main()
