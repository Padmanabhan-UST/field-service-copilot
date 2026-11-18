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

    rows = []
    for line in TEST_SET.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        query = json.loads(line)["query"]
        response, context = rag(query)
        g = groundedness(query=query, context=context, response=response)
        r = relevance(query=query, response=response)
        rows.append({"query": query, "response": response, "groundedness": g["groundedness"], "relevance": r["relevance"]})
        print(f"G={g['groundedness']:.0f} R={r['relevance']:.0f}  {query}")

    avg_g = sum(row["groundedness"] for row in rows) / len(rows)
    avg_r = sum(row["relevance"] for row in rows) / len(rows)
    print(f"\nAverage groundedness {avg_g:.2f}, relevance {avg_r:.2f} (pass threshold {THRESHOLD})")
    RESULTS.write_text(json.dumps({"groundedness": avg_g, "relevance": avg_r, "rows": rows}, indent=2), encoding="utf-8")
    print(f"Saved {RESULTS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()