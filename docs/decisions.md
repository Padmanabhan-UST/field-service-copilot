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
