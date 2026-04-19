# Phase 2 Sub-Plan: LLM Feedback Layer

## Objective

Transform structured analysis report into constrained natural-language feedback via provider abstraction, with Ollama as default and Claude as fallback.

## Entry criteria

- Phase 1 completed and approved.
- /analyze report contract stable at schema_version=1.

## Pre-implementation context checklist

- Confirm output contract for feedback object:
  - summary
  - per_error_explanations
  - encouragement
  - next_suggestion
- Confirm provider configuration strategy:
  - LLM_PROVIDER selects provider (ollama | claude).
  - LLM_MODEL selects model per provider.
- Confirm runtime secrets and environment variables:
  - ANTHROPIC_API_KEY only required for Claude provider.
- Confirm prompt safety requirement:
  - model must not invent errors beyond report content.
- Confirm multilingual behavior:
  - meta_language independent of practice language.

## Architecture choices to state before coding

1. Provider abstraction location and shape:
   - Choice target: app/llm/providers.py with abstract LLMProvider async interface.
   - Alternative: protocol typing only without base class.
2. Prompt composition strategy:
   - Choice target: external prompt template file in app/llm/prompts/feedback_v1.md.
   - Alternative: inline prompt strings in provider code.
3. Response validation path:
   - Choice target: strict Pydantic validation with clear parse errors.
   - Alternative: tolerant dict parsing.

## Implementation sequence

1. Define FeedbackResponse Pydantic model.
2. Define LLMProvider abstract interface.
3. Implement OllamaProvider using Ollama OpenAI-compatible endpoint.
4. Implement ClaudeProvider via anthropic SDK.
5. Implement provider factory using environment-based selection.
6. Write feedback prompt with:
   - schema context
   - no-fabrication rule
   - meta_language instruction
   - JSON output constraints
   - few-shot examples
7. Add POST /feedback endpoint that validates input report and returns FeedbackResponse.
8. Add startup check for default Ollama model availability (pull or fail clearly).
9. Add integration tests with mocked providers.
10. Add hallucination guard test using no-error report.

## Verification pack

Run and capture output:

```bash
curl -X POST -H "Content-Type: application/json" \
     -d @sample_report.json \
     http://localhost:8000/feedback | jq
pytest
```

Human verification scenarios:

- Compare output quality across Ollama and Claude for same synthetic reports.
- No-error report must return no invented errors.
- meta_language=de-DE must return German text for English practice report.

Expected evidence:

- Both providers satisfy FeedbackResponse schema.
- Hallucination guard passes.
- Ollama model is loaded and reachable.

## Required documentation updates

- docs/llm-providers.md: architecture, provider swap, adding providers, model guidance.
- app/llm/prompts/feedback_v1.md: prompt with design notes.
- README.md: provider configuration and env vars.
- CHANGELOG.md: Phase 2 entry.

## Exit criteria

- /feedback functional with both providers.
- Output strictly tied to report content.
- Provider selection and model selection documented.
- Stop and wait for explicit user approval.

## Known risks and mitigations

- Risk: model returns malformed JSON.
  - Mitigation: validation + retry with stricter system reminder.
- Risk: Ollama warm start latency.
  - Mitigation: startup model check and clear boot-time logs.
