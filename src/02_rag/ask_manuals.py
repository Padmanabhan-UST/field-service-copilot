import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from azure.search.documents.models import VectorizedQuery
from common.clients import embeddings_client,openai_client, search_client
from common.config import CHAT_DEPLOYMENT,EMBEDDING_DEPLOYMENT

INDEX_NAME = "manuals"

INSTRUCTIONS = (
    "You are an assistant for field technicians. Answer ONLY from the numbered sources provided. "
    "Cite sources inline like [1] or [2]. If the sources don't contain the answer, say "
    "\"I can't find that in the manuals.\" Keep answers short and practical."
)

def search_manuals(question: str, mode: str = "hybrid", top: int = 3) -> list[dict]:
    kwargs = {"top": top, "select": ["title", "source", "content"]}
    if mode in ("keyword", "hybrid"):
        kwargs["search_text"] = question
    if mode in ("vector", "hybrid"):
        vector = embeddings_client().embeddings.create(model=EMBEDDING_DEPLOYMENT, input=[question]).data[0].embedding
        kwargs["vector_queries"] = [VectorizedQuery(vector=vector, k_nearest_neighbors=10, fields="content_vector")]
    if mode == "hybrid":
        kwargs["query_type"] = "semantic"
        kwargs["semantic_configuration_name"] = "semantic-config"
    return list(search_client(INDEX_NAME).search(**kwargs))

def answer(question: str) -> str:
    chunks = search_manuals(question)
    sources = "\n\n".join(f"[{i}] {c['title']}\n{c['content']}" for i, c in enumerate(chunks, start=1))
    response = openai_client().responses.create(
        model=CHAT_DEPLOYMENT,
        instructions=INSTRUCTIONS,
        input=f"Sources:\n{sources}\n\nQuestion: {question}",
    )
    citations = "\n".join(f"  [{i}] {c['title']}" for i, c in enumerate(chunks, start=1))
    return f"{response.output_text}\n\nSources:\n{citations}"

def compare(question: str) -> None:
    print(f"\n=== {question}")
    for mode in ("keyword", "vector", "hybrid"):
        best = search_manuals(question, mode, top=1)[0]["title"]
        print(f"  {mode:<8} -> {best}")


def main() -> None:
    compare("BRG-6205-2RS")
    compare("my pump makes a noise like gravel")

    for question in [
        "My CP-200 is making a gravel noise and shows E103. What do I do?",
        "How do I replace the bearing on the CP-200 and which part do I need?",
        "What is the warranty period for the AC-75?",
    ]:
        print(f"\n### {question}\n{answer(question)}")


if __name__ == "__main__":
    main()