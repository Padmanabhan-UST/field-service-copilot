"""Session 9: score the RAG pipeline on a test set with groundedness and relevance evaluators."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "src"))
sys.path.append(str(ROOT / "src" / "02_rag"))

from azure.ai.evaluation import AzureOpenAIModelConfiguration, GroundednessEvaluator, RelevanceEvaluator
from azure.identity import DefaultAzureCredential

from ask_manuals import INSTRUCTIONS, search_manuals
from common.clients import openai_client
from common.config import CHAT_DEPLOYMENT, PROJECT_ENDPOINT

TEST_SET = ROOT / "data" / "eval" / "rag_eval.jsonl"
RESULTS = ROOT / "data" / "eval" / "rag_eval_results.json"
THRESHOLD = 3  # evaluator scores run from 1 to 5


def rag(query: str) -> tuple[str, str]:
    """Same retrieve + generate steps as ask_manuals.py; returns (response, context)."""
    chunks = search_manuals(query)
    context = "\n\n".join(f"[{i}] {c['title']}\n{c['content']}" for i, c in enumerate(chunks, start=1))
    response = openai_client().responses.create(
        model=CHAT_DEPLOYMENT, instructions=INSTRUCTIONS, input=f"Sources:\n{context}\n\nQuestion: {query}"
    )
    return response.output_text, context


def main() -> None:
    judge = AzureOpenAIModelConfiguration(
        azure_endpoint=PROJECT_ENDPOINT.split("/api/projects/")[0],
        azure_deployment=CHAT_DEPLOYMENT,
        api_version="2024-10-21",
    )
    credential = DefaultAzureCredential()
    groundedness = GroundednessEvaluator(model_config=judge, credential=credential, threshold=THRESHOLD)
    relevance = RelevanceEvaluator(model_config=judge, credential=credential, threshold=THRESHOLD)

    rows, failures = [], []
    for line in TEST_SET.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        case = json.loads(line)
        query = case["query"]
        response, context = rag(query)
        if case.get("expected") == "refuse":
            passed = "can't find" in response.lower()
            row = {"query": query, "response": response, "expected": "refuse", "passed": passed}
            print(f"{'PASS' if passed else 'FAIL'} refusal  {query}")
        else:
            g = groundedness(query=query, context=context, response=response)["groundedness"]
            r = relevance(query=query, response=response)["relevance"]
            passed = g >= THRESHOLD and r >= THRESHOLD
            row = {"query": query, "response": response, "groundedness": g, "relevance": r, "passed": passed}
            print(f"{'PASS' if passed else 'FAIL'} G={g:.0f} R={r:.0f}  {query}")
        rows.append(row)
        if not passed:
            failures.append(query)

    RESULTS.write_text(json.dumps({"failures": failures, "rows": rows}, indent=2), encoding="utf-8")
    print(f"\n{len(rows) - len(failures)}/{len(rows)} passed")
    if failures and "--gate" in sys.argv:
        sys.exit(1)  # a non-zero exit code fails the CI job


if __name__ == "__main__":
    main()