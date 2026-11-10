# CLAUDE.md: Field Service Copilot

## Goal
Portfolio POC for a job switch into cloud/AI architect roles, built while
preparing for Microsoft AI-103 (Azure AI Apps and Agents Developer Associate).
Exam target: week of Nov 23–28, 2026. Every component should map to an exam
skill AND a realistic use case.

## About me
13+ years .NET/Azure, newer to Python. Explain Python idioms briefly when they
differ from C#. I want hands-on learning: I do portal steps myself; you guide,
write code, and explain WHY each service/setting was chosen.

## The app
AI assistant for technicians maintaining industrial equipment:
1. RAG over equipment manuals: AI Search hybrid + semantic ranker
2. Invoice field extraction: prebuilt invoice model / Content Understanding
3. Agent: OpenAPI tool (mock device API), structured outputs for work orders,
   human approval before "order spare part"
4. Damaged-part photo analysis; image editing with masks
5. Inspection video segmentation: Content Understanding video analyzer
6. Voice note → report → translation: Speech (phrase list), Translator
   (glossary), TTS
7. Safety/ops: Prompt Shields, content filters, evaluations, tracing,
   CI eval gate (GitHub Actions)

## Rules
- Keyless only: DefaultAzureCredential / managed identity, never API keys.
  Data role: Foundry User, formerly "Azure AI User" (Owner doesn't grant data access).
- Config via .env (see .env.example); never commit .env.
- Use azure-ai-projects; get an OpenAI client via project.get_openai_client().
  Verify current SDK APIs against docs rather than relying on memory.
- Log every design choice in docs/decisions.md (context, decision, rejected
  alternatives). Update the README status table as features land.
- Small, frequent commits.
- Who changes what: Claude may edit and commit Markdown docs (CLAUDE.md,
  README.md, docs/). I write all code and config myself (.py, .env,
  requirements, workflows): give me the code/steps to type, then review it.
  Ask before any other change (installs, Azure, pushes).

## Budget (Azure free account, must not cost money)
- Standard / Global Standard deployments only, never Provisioned Throughput
- Free tiers: AI Search Free, Document Intelligence F0, Speech F0
- Delete custom speech endpoints after testing; keep image/video generation
  calls minimal; one resource group (rg-ai103)

## Schedule (catch-up plan, daily, revised Nov 10; nothing cut)
Done: Oct 24 foundation + first keyless call; Oct 25–Nov 10 manuals ingested
into AI Search (38 chunks).
- Nov 11 (1 h): RAG query: hybrid + semantic ranker + citations
- Nov 12 (1 h): structured outputs for work orders
- Nov 13 (1.5 h): content filters, Prompt Shields, groundedness detection
- Nov 14 (1 h): agent + OpenAPI tool (mock device API)
- Nov 15 (1.5 h): agent + search tool + human approval before ordering a part
- Nov 16 (1.5 h): evaluations + tracing (App Insights)
- Nov 17 (1.5 h): CI eval gate in GitHub Actions, keyless via OIDC
- Nov 18 (1 h): Document Intelligence prebuilt invoice vs DIY OCR
- Nov 19 (1.5 h): Content Understanding: documents + video segmentation
- Nov 20 (1.5 h): vision: damaged-part photo + masked image edit
- Nov 21 (2 h): speech: STT + phrase list + Custom Speech + Translator
  glossary + TTS (delete custom endpoint same day)
- Nov 22 (1.5 h): demo recording, README polish, teardown of rg-ai103
  (firm date: free credit ends ~Nov 23)
- Nov 23–25 (1 h/day): mock exams + review mistakes (no Azure needed)
- Nov 26–28: exam
If a session runs late, shift later sessions but keep the Nov 22 teardown.

## My weak areas (diagnostic, 12/15): spend extra time here
- Structured outputs vs few-shot prompting (platform control beats prompt)
- Prompt Shields vs groundedness vs content filters
- Custom Speech / phrase lists
- Document Intelligence prebuilt models vs DIY OCR
- Vision overall (got it right, but guessing)
Recurring trap: when a requirement says "always/reliably", choose the
purpose-built service or platform control, not prompts or DIY code.

## End of each session
Ask me 3 exam-style questions on what we built, then remind me to commit.
