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

## Schedule (Sat & Sun, 2–4 PM IST)
- Oct 24: foundation + first keyless call (src/01_foundation)
- Oct 25: manuals → AI Search → RAG
- Oct 31: Prompt Shields, content filters, structured outputs
- Nov 1: agent + OpenAPI tool + approval gate
- Nov 7: evaluations, tracing, CI gate
- Nov 8: invoices + Content Understanding
- Nov 14: vision (photo, masked edit, video)
- Nov 15: speech + translation
- Nov 21–22: mock exams, demo video, teardown

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
