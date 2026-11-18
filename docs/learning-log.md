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
| 5 | Nov 11 | Structured outputs | Work order from a free-text report: prompt-only JSON vs strict schema with Pydantic | 2/3 |
| 6 | Nov 11 | Safety layers | Harm analysis, jailbreak blocked by the deployment, Prompt Shields (user + document attacks), groundedness detection | 2/3 |
| 7 | Nov 18 | Agent + OpenAPI tool | Device-status agent; Foundry calls a mock REST API (static JSON on GitHub) described by an OpenAPI spec | 3/3 |
| 8 | Nov 18 | Agent + search + approval | Field agent: device API + built-in Azure AI Search tool (citations) + order function gated by a human | 3/3 |
| 9 | Nov 18 | Evaluations + tracing | Groundedness and relevance over a JSON Lines test set; manual OpenTelemetry spans to Application Insights | 3/3 |
| 10 | Nov 18 | Document Intelligence | Prebuilt invoice model with confidence-based routing vs DIY OCR + LLM | 2/3 |
| 11 | Nov 18 | Vision | Generated damaged-part photo, structured damage report from a multimodal model, prompt-only image edit | 3/3 |
| 12 | Nov 18 | Speech + translation | TTS voice note, fast transcription with a phrase list, Translator with dynamic dictionary, German TTS (Custom Speech as theory) | 2/3 |

Status: 12 of 13 hands-on sessions done. Catch-up day: remaining sessions run back to back.

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

### 5. Structured outputs (Nov 11)

| Approach | What it guarantees |
|---|---|
| Prompt only ("reply in JSON") | Nothing; it's a request |
| Few-shot examples | Nothing; better imitation, still a request |
| JSON mode (`json_object`) | Valid JSON syntax only; field names and types can be anything |
| Structured outputs (`json_schema`, `strict: true`) | JSON that matches your schema: required fields, types, allowed values |
| Function calling with `strict: true` | Same mechanism, for tool arguments |

| Python piece | Plain meaning |
|---|---|
| Pydantic `BaseModel` | A typed class that becomes the JSON schema; like a C# record with validation |
| `Literal["low", ...]` | Only these values allowed, like an enum |
| `responses.parse(..., text_format=WorkOrder)` | Sends the schema in strict mode and returns a typed object (`output_parsed`) |
| `model_validate_json(raw)` | Parse and validate in one step; raises `ValidationError` |

Observed: prompt-only JSON was parseable 0 of 3 times (wrapped in ```json fences). Strict schema worked first time. But the schema-valid output still had `"grease"` instead of part `GRS-LC2-400G` and invented steps without lockout/tagout.

Exam traps: "must always match a schema" → structured outputs, not few-shot, not JSON mode, not retries. Structured outputs guarantees shape, not truth; correctness needs grounding (RAG) plus validation against real data.

Also covered: model choice = requirements → shortlist (catalog, leaderboards) → evaluate on your own data → smallest model that passes. Mixed simple and complex prompts at lowest cost → model router.

### 6. Safety layers (Nov 11)

| Layer | Question it answers | Checks |
|---|---|---|
| Content filters | Is this text harmful? | Hate, sexual, violence, self-harm; severity safe/low/medium/high; on input and output; part of the deployment's guardrail |
| Prompt Shields: user prompt attack | Is the user trying to hijack the model? | Jailbreaks typed in chat ("you are DAN, ignore your rules") |
| Prompt Shields: document attack | Is content the model reads trying to hijack it? | Instructions hidden in documents, emails, tool output (indirect prompt injection) |
| Groundedness detection | Is the answer supported by the sources? | Answer vs grounding sources; preview API |
| Custom blocklist | Is a forbidden term present? | Exact terms you define, e.g. competitor names |
| Protected material | Is it reproducing copyrighted text or code? | Known lyrics, articles, public code |

Observed: Violence severity 4 for a threat against a person. The jailbreak was blocked by the deployment's default guardrail (HTTP 400) without any setup. Prompt Shields flagged both the typed jailbreak and the instruction hidden in a "manual". Groundedness flagged "every 2000 hours" (a real number from the regreasing row, used for replacement).

How it's called: REST on the Foundry resource (`/contentsafety/text:analyze`, `text:shieldPrompt`, `text:detectGroundedness`), keyless with an Entra token for the `cognitiveservices` scope.

Also covered: in a chat app, every turn runs the same pipeline: shield the user prompt, retrieve, shield the documents, generate (deployment guardrail filters input and output), check groundedness. Centralize rules for many apps with an AI gateway (API Management).

Exam traps: who wrote the attack decides the shield type. Typed by the user → user prompt attack. Hidden in an email, document or web page the model reads → document attack. Unsupported claims → groundedness, not content filters. Specific words → blocklist, not a severity threshold.

### 7. Agent + OpenAPI tool (Nov 18)

| | Function tool | OpenAPI tool |
|---|---|---|
| Who calls the API | Your app (`function_call` → you run it → `function_call_output`) | The Foundry service (`openapi_call` → `openapi_call_output`) |
| You provide | JSON schema for arguments | OpenAPI 3 spec: server, paths, parameters |
| API must be reachable from | Your app | Azure |
| Auth | Whatever your code does | Anonymous, key via project connection, or managed identity |
| Best for | App-side logic, control, approval before acting | Existing REST APIs, no glue code |

| Other agent tools | Use for |
|---|---|
| Azure AI Search | Grounding in your own index |
| File search | Files uploaded to the agent (managed vector store) |
| Code interpreter | Python in a sandbox: maths, charts, CSV analysis |
| Web search / Bing grounding | Current public information |
| MCP | Tools exposed by an MCP server |
| Azure Functions | Your own serverless code |

Problems hit and fixed: `ModuleNotFoundError: common` (missing `sys.path.append`); `openApi=` instead of `openapi=` (keyword arguments are case-sensitive); agent name with underscores rejected (letters, digits, hyphens only, max 63).

Observed: 1 API call for one device, 2 for a comparison. Without the manuals the agent couldn't explain alarm codes or notice PUMP-101 is past its 16,000 h bearing interval.

Exam traps: existing REST API + no execution code → OpenAPI tool. Secure tool auth → managed identity, never keys in instructions or specs. Agent names: hyphens, not underscores.

### 8. Agent + search tool + human approval (Nov 18)

| Tool | Type | Run by | Why |
|---|---|---|---|
| Device status | OpenAPI | Foundry | Read-only, existing API |
| Manual search | Azure AI Search tool | Foundry, via project connection | Built-in grounding with `url_citation` annotations |
| Order spare part | Function tool (strict) | Your app, after a person types `y` | Real-world action needs a control point outside the model |

| Concept | Plain meaning |
|---|---|
| Project connection | Stored "where and how" for an external resource; keyless = project managed identity |
| Project managed identity | The identity Foundry uses for tool calls, separate from the Foundry resource's identity and from you |
| Query types | `simple`, `semantic`, `vector`, `vector_simple_hybrid`, `vector_semantic_hybrid` |
| Integrated vectorization | A vectorizer on the index embeds text queries; needed when the caller (agent, portal) sends text but wants vector search |
| Fail-safe approval | Only an explicit `y` approves; anything else rejects |

Problems hit and fixed: `tool_user_error` on every search (role not yet active, and the tool also needs Search Service Contributor to read the index definition); `vector_semantic_hybrid` fails (no vectorizer on the index); `previous_response_id=None` rejected by the API (send it only when set).

Observed: one turn used the device API and the search tool together; the order request used the real part number `BRG-6205-2RS`; a rejected order was reported honestly.

Exam traps: human approval → function tool (or a tool with approval required), never instructions. Agent with vector search over an index → vectorizer on the index. Keyless tool connections → grant roles to the project's managed identity.

Also covered: a vectorizer is an index setting that lets Search embed text queries itself. Your index has none; `ask_manuals.py` worked because your code embedded the question. The agent's `semantic` search is text only (keyword + semantic ranker, Microsoft's model inside Search), so no embedding model was involved.

### 9. Evaluations + tracing (Nov 18)

| | Evaluations | Tracing |
|---|---|---|
| Question | How good are the answers? | What happened inside this one request? |
| How | Test set (JSON Lines) + evaluators scoring 1–5 | Spans with timings and attributes |
| When | Before release, after every change (CI gate) | Continuously, and for debugging |
| Where | Results file, Foundry evaluations | Application Insights, Foundry tracing |

| Concept | Plain meaning |
|---|---|
| Groundedness evaluator | Is the response supported by the context? |
| Relevance evaluator | Does the response answer the query? |
| AI-assisted evaluator ("LLM as judge") | A model scores the output; configured with `AzureOpenAIModelConfiguration` |
| Threshold | Pass mark (3 of 5); a CI gate fails below it |
| Trace / span | One request / one step in it; nested `with` blocks create child spans |
| `configure_azure_monitor` | Sends spans to Application Insights; Azure SDK and HTTP calls are captured automatically |
| Monitoring Metrics Publisher | Role for keyless (Entra) telemetry ingestion |
| Resource provider registration | A subscription must register e.g. `Microsoft.OperationalInsights` before creating that resource type |

Problems hit and fixed: `MissingSubscriptionRegistration` (registered the resource providers); the SDK's App Insights helper refuses keyless connections (connection string from `.env` instead); `opentelemetry-instrumentation-openai-v2` broken (manual spans instead).

Observed: groundedness 5.00, relevance 4.20. The correct warranty refusal scored relevance 2, because single metrics don't capture "should refuse". The trace showed retrieval at 65% of 10 s, including about 2 s of `DefaultAzureCredential` probing for a managed identity that doesn't exist on a laptop.

Exam traps: quality across a test set → evaluation; slow step in one request → tracing. Authenticated telemetry only → Entra ingestion + Monitoring Metrics Publisher + disable local auth. Traces can contain personal data → limit access, control content recording. In production, prefer a specific credential (managed identity) over `DefaultAzureCredential`'s probing.

### 10. Document Intelligence (Nov 18)

| Model | Gives you | Use when |
|---|---|---|
| Read (`prebuilt-read`) | Text (OCR) | You only need the words |
| Layout (`prebuilt-layout`) | Text + tables + selection marks + structure, no named fields | Structure matters but no standard field set fits |
| Prebuilt (`prebuilt-invoice`, receipt, ID document, W-2, business card…) | Named fields + confidence + bounding boxes | A standard document type |
| Custom extraction | Your own named fields, trained on 5+ labeled samples | Your own form layout |
| Composed | Several custom models behind one ID, routed by a classifier | Many different custom forms coming through one entry point |

| Python piece | Meaning |
|---|---|
| `begin_analyze_document(...).result()` | Long-running operation: submit, then wait (like awaiting a Task) |
| `.content` vs `.value_string` / `.value_date` / `.value_currency` | Text as printed vs typed value |
| `.confidence` | 0–1 per field; drives auto-approve vs human review |
| `value_array` / `value_object` | Line items: list of objects with their own fields |

Observed: prebuilt and DIY gave identical results on a clean sample invoice. Only prebuilt gave confidences (0.93–0.96), so only it could auto-approve safely.

Exam traps: standard document type → prebuilt model, not OCR + LLM. Your own form → custom extraction model. Text, tables and checkboxes without named fields → layout model. Route uncertain extractions to people → confidence scores.

### 11. Vision (Nov 18)

| Task | Model type |
|---|---|
| Understand an image (describe, judge damage, read text) | Multimodal chat model with image input |
| Create an image from text | Image generation model |
| Change an image, region guaranteed | Masked edit (inpainting): transparent mask pixels = area to change |
| Change an image, by description only | Prompt-only edit (rest of the image not guaranteed) |
| Company-specific classes or objects, with labeled photos | Custom image classification / object detection |

| Python piece | Meaning |
|---|---|
| `{"type": "input_image", "image_url": "data:image/png;base64,..."}` | Sending a picture next to `input_text` in the Responses API |
| `base64.b64encode(...).decode()` | Bytes to base64 text (like `Convert.ToBase64String`) |
| `images.generate` / `images.edit` | Create / change a picture |

Problems hit and fixed: no OpenAI image models offered to the subscription (used Microsoft's MAI-Image-2.7-Flash); MAI models are served on `/mai/v1`, not `/openai/v1`; MAI edits reject mask files, so masked inpainting stayed theory.

Observed: report `corrosion / high / replace: true`; the edit kept the scene and replaced the bearing. The model read a handwritten note in a photo and used it as evidence: text in images can carry prompt injections.

Exam traps: change only one region, everything else identical → masked edit. Many labeled photos and fixed company classes → custom vision model. Image input → `input_image` content, not instructions or search.

### 12. Speech + translation (Nov 18)

| Need | Tool |
|---|---|
| Text → natural speech | Neural text-to-speech with SSML (voice, language, rate, pronunciation) |
| File → text in one call | Fast transcription (`transcriptions:transcribe`) |
| Live streaming speech | Real-time recognition (Speech SDK) |
| Many files, asynchronous | Batch transcription |
| A few known phrases, no training, now | Phrase list |
| Many terms, accents, noise, reliably | Custom Speech (plain text, pronunciation, audio + human transcripts; compare WER; endpoint billed per hour) |
| Brand voice | Custom neural voice |
| Keep terms exact in short text translations | Translator dynamic dictionary (`<mstrans:dictionary>`) |
| Consistent terms across whole documents | Document Translation + glossary file |
| Translation tuned to a domain | Custom Translator |

Observed: without a phrase list, "two BRG sixty-two oh five bearings" became "to be our G6205"; only the full spoken phrase in the phrase list fixed it, which shows the limit of phrase lists. Translator kept `E103` and `BRG 6205` exact in German. Translator with Entra auth needs `Ocp-Apim-ResourceId` and `Ocp-Apim-Subscription-Region`.

Exam traps: few terms + no training → phrase list; many terms + accents + noise → Custom Speech. Single short texts → dynamic dictionary; whole documents → glossary.

## Quiz mistakes to revisit before the exam

| Session | Question | Wrong answer | Right answer and why |
|---|---|---|---|
| 3 | Change a field type in production | Update with `create_or_update_index` | New index version + alias swap; existing fields are immutable |
| 3 | Exact codes and plain-language symptoms | Vector only | Hybrid; vectors are weak on exact codes like `BRG-6205-2RS` |
| 4 | Which parameter adds the vector part | `semantic_configuration_name` | `vector_queries`; "semantic" only re-orders results |
| 5 | What JSON mode guarantees | Schema field names and types | Valid JSON syntax only; schema conformance needs structured outputs |
| 6 | Hidden instruction inside an email the agent reads | Prompt Shields, user prompt attack | Prompt Shields, document attack; the attacker wrote the email, not the user |
| 10 | Text, tables and checkboxes with no named fields | Custom extraction model | Layout model; custom models are for extracting your own named fields |
| 12 | Keep product codes unchanged in short, one-at-a-time text translations | Document Translation with a glossary | Dynamic dictionary markup in the request; glossaries are for whole documents |
