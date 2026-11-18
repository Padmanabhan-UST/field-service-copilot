"""Session 9: trace one technician question end to end in Application Insights."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "src"))
sys.path.append(str(ROOT / "src" / "02_rag"))

from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

from ask_manuals import INSTRUCTIONS, search_manuals
from common.clients import openai_client
from common.config import APPLICATIONINSIGHTS_CONNECTION_STRING, CHAT_DEPLOYMENT

QUESTION = "My CP-200 shows E103 and makes a gravel noise. What do I do?"


def main() -> None:
    configure_azure_monitor(connection_string=APPLICATIONINSIGHTS_CONNECTION_STRING, credential=DefaultAzureCredential())
    tracer = trace.get_tracer("field-service-copilot")

    with tracer.start_as_current_span("technician-question") as root:
        root.set_attribute("app.question", QUESTION)

        with tracer.start_as_current_span("retrieve") as span:
            chunks = search_manuals(QUESTION)
            span.set_attribute("app.chunk_count", len(chunks))

        with tracer.start_as_current_span("generate") as span:
            sources = "\n\n".join(f"[{i}] {c['title']}\n{c['content']}" for i, c in enumerate(chunks, start=1))
            response = openai_client().responses.create(
                model=CHAT_DEPLOYMENT, instructions=INSTRUCTIONS, input=f"Sources:\n{sources}\n\nQuestion: {QUESTION}"
            )
            span.set_attribute("gen_ai.usage.input_tokens", response.usage.input_tokens)
            span.set_attribute("gen_ai.usage.output_tokens", response.usage.output_tokens)

        print(response.output_text)
        trace_id = format(root.get_span_context().trace_id, "032x")

    trace.get_tracer_provider().force_flush()
    print(f"\nTrace id: {trace_id}")
    print("Find it in 2-5 minutes: Application Insights > Transaction search (or Foundry > Tracing)")


if __name__ == "__main__":
    main()