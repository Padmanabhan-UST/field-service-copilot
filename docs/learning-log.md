# Learning log

What each session built, the concepts behind it, and the exam traps it covered. Updated at the end of every session.

## Progress at a glance

| # | Date | Session | Built | Quiz |
|---|---|---|---|---|
| 0 | Oct 23 | Tooling | Git, Python 3.12, Azure CLI, repo pushed to GitHub, venv | – |
| 1 | Oct 23 | Agents playground (local practice) | 3 agent exercises typed by hand: basic chat, function tool, structured output | 3/3 |
| 2 | Oct 24 | Foundation | Azure free trial, budget alert, rg-ai103, Foundry resource + project, gpt-4.1-mini, Foundry User role, first keyless call | 3/3 |
| 3 | Oct 25 – Nov 10 | Manual ingestion | AI Search (Free, RBAC only), embedding model, Search roles, 3 manuals chunked, embedded and indexed (38 chunks) | 1/3 |
| 4 | Nov 10 | RAG query | Hybrid + semantic search, grounded answers with citations, refusal when manuals don't cover a question | 2/3 |

Status: 4 of 13 hands-on sessions done, 1 day ahead of schedule.

## Session details

### 0. Tooling (Oct 23)

| Topic | What to remember |
|---|---|
| Git setup | Name and email decide whether GitHub links commits to your account |
| GitHub remote | Use the username (`Padmanabhan-UST`), not the display name; "Repository not found" can also mean "not signed in" |
| Python venv | Per-project package folder, roughly a project-local NuGet restore |
| Local-only files | `.git/info/exclude` ignores files without changing the shared `.gitignore` |

### 1. Agents playground (Oct 23)

| Concept | Plain meaning |
|---|---|
| Model vs agent | Model = brain. Agent = brain + instructions + tools + memory, saved under a name and version |
| `create_version` | Agents are immutable; every change makes a new version |
| `agent_reference` in `extra_body` | Tells the Responses API to run the saved agent instead of a bare model |
| Conversation vs `previous_response_id` | Server-side history vs chaining one response to the last |
| Function tool | The model only asks for the call; your code runs it and returns `function_call_output` |
| Structured outputs | JSON schema with `strict=True`, enforced by the platform |

Exam traps: "always valid JSON" means structured outputs, not few-shot prompting. With no version pinned, the latest agent version runs.

### 2. Foundation (Oct 24)

| Concept | Plain meaning |
|---|---|
| Subscription, resource group | Billing container; one folder (`rg-ai103`) so teardown is one delete |
| Budget | Sends alerts only, never stops spending; the free-trial spending limit is the real safety net |
| Foundry resource vs project | One resource gives one endpoint for many AI services; projects isolate agents, files and evaluations |
| Serverless vs managed compute vs PTU | Pay per token / VMs billed per hour / reserved throughput billed continuously |
| Control plane vs data plane | Administer the service (ARM, Owner, Contributor) vs use it (service URL, "User" and "Data" roles) |
| Foundry User role | Renamed from "Azure AI User"; Owner alone gets 403 when calling a model |
| `DefaultAzureCredential` | Uses `az login` locally and managed identity in Azure, with the same code and no secrets |

Exam traps: Owner but 403 → assign a data-plane role. "Only Entra ID auth" → disable local (key) auth. Private network → private endpoints. Customer-controlled keys → customer-managed keys in Key Vault.

### 3. Manual ingestion (Oct 25 – Nov 10)

| Concept | Plain meaning |
|---|---|
| Pipeline | Create index → chunk → embed → upload ("shelves, slices, fingerprints, shelve them") |
| Chunking | One chunk per manual section; "Manual > Section" title keeps context |
| Embeddings | Text turned into 1,536 numbers capturing meaning; index and query must use the same model |
| Field kinds | `SimpleField` = key or filter, `SearchableField` = text, `SearchField` = vectors and anything special |
| HNSW | Fast, approximate nearest-vector search (vs exhaustive KNN: exact, slow) |
| Push vs pull indexing | Your code uploads (push) vs an indexer + skillset pulls from Blob/SQL on a schedule |
| Search roles | Service Contributor = index schema; Index Data Contributor = upload; Index Data Reader = query only |

Problems hit and fixed:

| Problem | Cause | Fix |
|---|---|---|
| Vector field created as text | Used `SearchableField` for the vector | Use `SearchField` with dimensions and a vector profile |
| "Existing field cannot be changed" | Index fields are immutable | Delete and recreate; in production, new index version + alias swap |
| 404 on embeddings | Project endpoint doesn't serve embeddings | Call the Foundry resource endpoint (`embeddings_client()`) |

Exam traps: changing a field type needs a new index (alias for zero downtime). Keep the index in sync with Blob Storage automatically → indexer. Query-only app → Search Index Data Reader.

### 4. RAG query (Nov 10)

| Concept | Plain meaning |
|---|---|
| RAG | Retrieve the best chunks, add them to the prompt as numbered sources, generate an answer that cites them |
| Hybrid search | `search_text` (keyword) + `vector_queries` (vector), merged by the service |
| Semantic ranker | Re-reads the top results and puts the best answer first (`query_type="semantic"`) |
| Grounding | Instructions: answer only from sources, cite `[n]`, say "I can't find that" otherwise |
| Fetch wide, keep narrow | `k_nearest_neighbors=10`, `top=3` |
| `VectorizedQuery` vs `VectorizableTextQuery` | You send the vector vs Search embeds the text using a vectorizer on the index |

Observed: the warranty question was correctly refused. One answer used a fact from source [2] but didn't cite it, which evaluations should catch.

Exam traps: relevant results in the wrong order → semantic ranker. Never answer outside the documents → RAG + grounding instructions + groundedness evaluation (not fine-tuning, not temperature 0).

## Quiz mistakes to revisit before the exam

| Session | Question | Wrong answer | Right answer and why |
|---|---|---|---|
| 3 | Change a field type in production | Update with `create_or_update_index` | New index version + alias swap; existing fields are immutable |
| 3 | Exact codes and plain-language symptoms | Vector only | Hybrid; vectors are weak on exact codes like `BRG-6205-2RS` |
| 4 | Which parameter adds the vector part | `semantic_configuration_name` | `vector_queries`; "semantic" only re-orders results |
