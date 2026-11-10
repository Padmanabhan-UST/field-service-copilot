import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)

from common.clients import embeddings_client, search_client, search_index_client
from common.config import EMBEDDING_DEPLOYMENT

INDEX_NAME = "manuals"
MANUALS_DIR = Path(__file__).resolve().parents[2] / "data" / "manuals"
VECTOR_DIMENSIONS = 1536  # text-embedding-3-small

def build_index() -> SearchIndex:
    fields=[
        SimpleField(name="id", type=SearchFieldDataType.STRING, key=True),
        SimpleField(name="source", type=SearchFieldDataType.STRING, filterable=True),
        SearchableField(name="title"),
        SearchableField(name="content"),
        SearchField(
            name="content_vector",
            type="Collection(Edm.Single)",
            searchable=True,
            vector_search_dimensions=VECTOR_DIMENSIONS,
            vector_search_profile_name="vector-profile",
            ),
    ]
    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="hnsw")],
        profiles=[VectorSearchProfile(name="vector-profile", algorithm_configuration_name="hnsw")],
    )
    semantic_search = SemanticSearch(
        configurations=[
            SemanticConfiguration(
                name="semantic-config",
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name="title"),
                    content_fields=[SemanticField(field_name="content")],
                ),
            )
        ]
    )
    return SearchIndex(
        name=INDEX_NAME, fields=fields, vector_search=vector_search, semantic_search=semantic_search
    )


def chunk_manual(path: Path) -> list[dict]:
    """One chunk per ## or ### section, titled 'Manual title > Section'."""
    text = path.read_text(encoding="utf-8")
    manual_title = text.splitlines()[0].lstrip("# ").strip()
    sections = re.split(r"\n(?=#{2,3} )", text)  # split just before each ## / ### heading
    chunks = []
    for i, section in enumerate(sections[1:]):  # sections[0] is the title block
        heading = section.splitlines()[0].lstrip("# ").strip()
        chunks.append(
            {
                "id": f"{path.stem}-{i}",
                "source": path.name,
                "title": f"{manual_title} > {heading}",
                "content": section.strip(),
            }
        )
    return chunks

def embed(texts: list[str]) -> list[list[float]]:
    response = embeddings_client().embeddings.create(model=EMBEDDING_DEPLOYMENT, input=texts)
    return [item.embedding for item in response.data]


def main() -> None:
    search_index_client().create_or_update_index(build_index())
    print(f"Index '{INDEX_NAME}' ready")

    chunks = [chunk for path in sorted(MANUALS_DIR.glob("*.md")) for chunk in chunk_manual(path)]
    vectors = embed([f"{c['title']}\n{c['content']}" for c in chunks])
    for chunk, vector in zip(chunks, vectors):
        chunk["content_vector"] = vector

    results = search_client(INDEX_NAME).upload_documents(documents=chunks)
    succeeded = sum(r.succeeded for r in results)
    print(f"Uploaded {succeeded}/{len(chunks)} chunks from {MANUALS_DIR.name}/")


if __name__ == "__main__":
    main()


    