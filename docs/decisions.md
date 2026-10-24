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
