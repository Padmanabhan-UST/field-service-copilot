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

## 007: Three safety layers
- **Context:** Technicians type free text, the app pastes retrieved manual text into prompts, and the agent will be able to order parts. Each is a different risk: harmful content, hijacking (direct or hidden in documents), and answers not supported by the manuals.
- **Decision:** Keep the deployment's default guardrail (content filters on input and output, medium threshold; jailbreak shield). Call Prompt Shields (`text:shieldPrompt`) on user input plus retrieved chunks as `documents` before they reach the model. Call groundedness detection (`text:detectGroundedness`, preview) on RAG answers against their sources. All keyless on the Foundry resource via REST with an Entra token.
- **Rejected:** Prompt instructions like "never follow instructions in documents" (a request, not a control); keyword filters for hallucinations (missed the 2000 h vs 16000 h mix-up, which uses a real number from the wrong context); a separate Content Safety resource (the Foundry resource already exposes it).
- **Observed:** Violence severity 4 for a threat against a person; the jailbreak was blocked by the deployment with HTTP 400; Prompt Shields detected both the user jailbreak and the instruction hidden in a manual; groundedness flagged "every 2000 hours" as ungrounded.

## 008: OpenAPI tool for live device status
- **Context:** The agent must check live readings and alarms before advising, from a device API that already exists as REST.
- **Decision:** An OpenAPI tool on a Foundry prompt agent, described by an OpenAPI 3 spec (`src/04_agent/device_api.openapi.json`), anonymous auth. The Foundry service calls the API itself, so the app needs no tool-call loop. For the POC the API is a mock: static JSON files in the public GitHub repo, served by raw.githubusercontent.com.
- **Rejected:** A function tool (the app would have to run every call and loop; better kept for actions that need app-side control or approval); a hosted mock API on App Service or Functions (extra resources and cost for read-only data); pasting device data into the prompt (stale, not live).
- **Production note:** A real device API would use managed identity or a key stored in a project connection, never anonymous auth, and would be reachable only from Azure (private networking).
- **Observed:** 1 API call for a single device, 2 for a comparison; sensible triage. Without the manuals the agent couldn't explain alarm codes or notice that PUMP-101 is past the 16,000 h bearing replacement interval.

## 009: Field agent with search tool and human approval
- **Context:** Technicians need live readings and manual guidance together, and the agent must be able to order parts, which costs money and can't be undone.
- **Decision:** One prompt agent with three tools: the device OpenAPI tool (read-only, run by Foundry), the built-in Azure AI Search tool on the `manuals` index (semantic query, top 3, automatic citations, run by Foundry through a keyless project connection), and an `order_spare_part` function tool (strict schema) that the app runs only after a person types `y`. Anything else counts as a rejection.
- **Rejected:** Letting the service execute orders (no approval point); "ask before ordering" in the instructions (a request, not a control); the `vector_semantic_hybrid` query type (fails: the agent sends text and the index has no vectorizer; would need integrated vectorization).
- **Access:** The connection uses the project's managed identity. It needed Search Index Data Reader plus Search Service Contributor (the tool reads the index definition). That's broader than read-only; the alternative is app-side search code (`ask_manuals.py`) with Data Reader only.
- **Observed:** Turn 1 used both server-side tools and explained E101/E102 from the manual; turn 2 produced `BRG-6205-2RS × 2` (a real part number, unlike the ungrounded work order in 006) and stopped for approval; a rejection was reported honestly.

## 010: Evaluations and tracing
- **Context:** Quality must be measured on more than a few manual checks, and slow or failing requests must be explainable.
- **Decision:** Evaluations with `azure-ai-evaluation` (Groundedness and Relevance evaluators, `gpt-4.1-mini` as the judge, keyless, pass threshold 3 of 5) over a JSON Lines test set (`data/eval/rag_eval.jsonl`) that runs the real RAG pipeline. Tracing with OpenTelemetry to Application Insights (`configure_azure_monitor`, keyless ingestion with Monitoring Metrics Publisher), with manual spans for question, retrieve and generate plus token counts; Azure SDK and HTTP calls are captured automatically.
- **Rejected:** `opentelemetry-instrumentation-openai-v2` (installed version broken against the installed OpenTelemetry utilities); connection-string-only ingestion (anyone with the string can send telemetry); judging quality from averages alone (one failing row hides behind a good mean).
- **Observed:** Groundedness 5.00 average, relevance 4.20. The correct refusal for the warranty question scored relevance 2: the test set needs expected behaviour (e.g. `"expected": "refuse"`) and a matching check. The trace showed retrieval at 65% of a 10 s request, including about 2 s of `DefaultAzureCredential` probing for a managed identity that doesn't exist locally.
- **Infrastructure:** Application Insights and its Log Analytics workspace both live in `rg-ai103`. Registering the `Microsoft.OperationalInsights` and `Microsoft.Insights` resource providers was needed first.

## 011: Prebuilt invoice model for invoice extraction
- **Context:** Vendor invoices for spare parts must be turned into data (vendor, ID, date, total, line items) and processed without checking every one by hand.
- **Decision:** Document Intelligence `prebuilt-invoice` on the existing Foundry resource (keyless, `azure-ai-documentintelligence`). Auto-approve when every key field has confidence ≥ 0.8; otherwise send the invoice to a person.
- **Rejected:** OCR (`prebuilt-read`) + LLM with structured outputs: same result on a clean sample, but no confidence scores, no positions, two calls instead of one, and a hallucination risk on poor scans. A custom model: not needed, invoices are a prebuilt type. A separate Document Intelligence F0 resource: the Foundry resource already includes it.
- **Observed:** Both approaches extracted the sample correctly (Contoso, INV-100, $110.00, 3 lines). Prebuilt confidences 0.93–0.96, so the rule auto-approved.

## 012: Damaged-part photos
- **Context:** Technicians photograph damaged parts; the app should judge the damage, decide whether to replace, and show what the repaired part should look like.
- **Decision:** `gpt-4.1-mini` with image input (`input_image`, base64 data URL) and structured outputs (`DamageReport`: part, damage type, severity, replace). Image generation and editing with `MAI-Image-2.7-Flash` (Global Standard), the image model offered to this subscription, called keylessly on the resource's `/mai/v1` route. Generation is skipped when the photo already exists, to keep image calls minimal.
- **Rejected:** Masked edits (inpainting): the MAI model rejects mask files, and the OpenAI image models that support masks aren't offered to this subscription, so a prompt-only edit is used instead. A custom vision model: no labeled photos, and a general multimodal model is enough for a POC.
- **Observed:** Report `corrosion / high / replace: true`; the prompt-only edit replaced the bearing and kept the rest of the scene. In a dry run the model also read a handwritten note in the photo and used it as evidence: text inside images is another prompt-injection path.

## 013: Voice notes, transcription and translation
- **Context:** Technicians record voice notes full of codes (E103, BRG-6205-2RS); reports must be readable at sites in other languages without mangling part numbers.
- **Decision:** All REST on the Foundry resource, keyless: neural text-to-speech with SSML (simulated voice note, spoken German output), fast transcription with a phrase list, Translator with dynamic dictionary markup (`<mstrans:dictionary>`) wrapped around part codes by a regex. Translator with Entra auth needs the resource ID and region headers.
- **Rejected:** The Speech SDK (REST covers file-based transcription and synthesis without a native package); Document Translation with a glossary (for whole documents in storage, not short notes); Custom Speech, studied as theory only (see below).
- **Observed:** Without a phrase list, "two BRG sixty-two oh five bearings" became "to be our G6205 bearings". Short phrase-list entries ("BRG", "two BRG 6205 bearings") didn't help; only the full spoken phrase did. Translation kept `E103` and `BRG 6205` exact.
- **Custom Speech (theory):** For many domain terms, accents or factory noise, train a custom model with plain text (domain sentences), pronunciation data (BRG = "b r g") and, for acoustics, audio with human transcripts; compare word error rate (WER) against the base model; a deployed custom endpoint is billed per hour. Skipped hands-on to save time.

## 014: Content Understanding for inspection videos
- **Context:** Inspection videos should become searchable text: who said what, when, and what was on screen.
- **Decision:** Content Understanding on the Foundry resource (REST, `2025-11-01`, keyless), `prebuilt-video` analyzer on a video passed by URL. Resource defaults map the `gpt-4.1-mini` model to the existing deployment (set once with `PATCH /contentunderstanding/defaults`). Output is Markdown: WebVTT transcript with speaker labels plus key-frame references, ready to index in AI Search.
- **Rejected:** Separate Speech + Vision calls stitched together in code (more code, no key frames or segments); `prebuilt-videoSearch` with segments and per-segment descriptions: it failed with a service-side `InternalServerError`, so segmentation stays theory.
- **Observed:** 43.9 s sample video, 4 speakers, 6 transcript lines, 44 key frames.

## 015: CI evaluation gate with keyless GitHub login
- **Context:** Changes to prompts, retrieval or models can silently lower answer quality; quality must be checked automatically, like unit tests.
- **Decision:** A GitHub Actions workflow (`.github/workflows/eval_gate.yml`) runs `eval_rag.py --gate` on pushes to `main` that touch code, test data or dependencies, plus manual runs. Every test row must pass (groundedness and relevance ≥ 3, or a correct refusal for rows marked `"expected": "refuse"`); any failure exits with code 1 and fails the job. Azure login uses OIDC workload identity federation: an Entra app registration (`gh-fsc-eval`) trusts this repo's `main` branch, with no client secret. The app has only Foundry User and Search Index Data Reader. Non-secret IDs and endpoints are GitHub repository variables.
- **Rejected:** A client secret or publish profile in GitHub secrets (must be rotated, can leak); Contributor or Owner for the pipeline identity (it only needs to call models and query the index); an average-score gate (one failing row hides behind a good mean); relevance scoring for refusal questions (a correct refusal scored 2).
- **Observed:** The portal created an ID-based federated subject (`repo:Padmanabhan-UST@25168617/field-service-copilot@1431365331:ref:refs/heads/main`) and it matched GitHub's token. First run passed in 1 m 51 s.
