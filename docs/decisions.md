# Design decisions

Short records of why each choice was made. Format: context, decision, alternatives rejected.

## 001: Keyless authentication
- **Context:** The app calls Foundry models and Azure AI services.
- **Decision:** Microsoft Entra ID via DefaultAzureCredential locally and managed identity when deployed, with least-privilege data roles (Foundry User, formerly named Azure AI User).
- **Rejected:** API keys in config (secret sprawl); Key Vault-stored keys (still a secret to rotate); Contributor role (too broad); Foundry Owner (also manages the account, more than the app needs); Azure AI Administrator (control plane only, can't call models); Azure AI Developer (legacy hub-based role).

## 002: Standard deployments over provisioned throughput
- **Context:** Low, bursty POC traffic on a budget.
- **Decision:** Standard / Global Standard deployments.
- **Rejected:** Provisioned throughput (reserved capacity is billed continuously; suited to steady production load needing predictable latency).

## 003: gpt-4.1-mini as the chat model
- **Context:** Q&A, tool calling and structured outputs for technicians, on a free-trial budget.
- **Decision:** gpt-4.1-mini, Global Standard serverless deployment, low TPM limit as a guard against runaway loops. Single Foundry resource and project in one region, inside resource group rg-ai103.
- **Rejected:** Larger models (higher cost per token, not needed for short answers); managed compute deployments (billed per hour even when idle); hub-based projects (legacy, extra dependencies).

## 004: Manual ingestion for RAG
- **Context:** Technicians search manuals by exact codes (E101, BRG-6205-2RS) and by symptoms in their own words ("pump shakes").
- **Decision:** Azure AI Search Free tier, RBAC only (local auth disabled). One chunk per `##`/`###` manual section, with "Manual > Section" as the title, embedded together with the content using text-embedding-3-small (1536 dims, HNSW). Semantic configuration on title + content. Embeddings are called on the Foundry *resource* endpoint (`/openai/v1`), because the project endpoint returns 404 for embeddings; still keyless via an Entra bearer token provider.
- **Rejected:** Fixed-size chunks (split procedures mid-step); embedding content without the title (sections like "Safety" lose which machine they belong to); text-embedding-3-large (higher cost, no benefit for short manuals); API keys for Search (breaks the keyless rule).
- **Lesson:** An existing index field's type can't be changed; the index had to be deleted and recreated. In production, use a new index version plus an alias swap.

## 005: Grounded answers with citations
- **Context:** Technicians must be able to trust and check answers; the model has never seen the Contoso manuals.
- **Decision:** Retrieve the top 3 chunks with hybrid search (keyword + vector, k=10) re-ordered by the semantic ranker, pass them as numbered sources, and instruct the model to answer only from them, cite inline ([1]) and say "I can't find that in the manuals" when the sources don't cover the question. Return the source titles with every answer.
- **Rejected:** Asking the model without retrieval (invents part numbers); keyword-only search (misses symptoms described in other words); vector-only search (weak on exact codes like BRG-6205-2RS); fine-tuning on the manuals (expensive, goes stale when manuals change, no citations).
- **Observed:** A refusal for an uncovered question (warranty) works. One answer used a fact from source [2] but cited only [1][3], so citation accuracy needs automated evaluation (planned for evaluations).

## 006: Structured outputs for work orders
- **Context:** Work orders feed downstream systems (scheduling, parts ordering) that need a fixed shape: allowed priority values, parts with quantities, numeric hours.
- **Decision:** Structured outputs (`json_schema`, `strict: true`) via `responses.parse` with a Pydantic `WorkOrder` model; `Literal` for priority, nested `PartLine` objects for parts.
- **Rejected:** Prompt-only "reply in JSON" (0 of 3 attempts parseable: wrapped in ```json fences); few-shot examples (still best effort); JSON mode (valid syntax only, any field names); stripping fences in code (workaround for a problem the platform solves).
- **Observed limit:** The schema guarantees shape, not correctness. The model returned the part number "grease" instead of GRS-LC2-400G and invented generic steps without lockout/tagout. Fix: ground the work order in retrieved manual sections (agent + search) and validate part numbers against the spare-parts list before ordering.
