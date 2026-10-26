# A24: KYC document pipeline

**Framework:** CrewAI Flows (@start -> @listen -> @router -> branches) + deterministic KYC rules  
**LLM:** yes: Qwen2.5-7B-Instruct (GGUF Q4_K_M), local on CPU via llama.cpp (common/gguf_llm_server.py)  
**Phase:** 3  
**Status:** working (3/3 demo sanity checks passed; see [proof/run.md](proof/run.md))  


## What it does
Extracts fields from OCR text of a synthetic PAN card and Aadhaar card (LLM), then validates them in code: PAN format and surname initial, Aadhaar Verhoeff checksum, age >= 18, cross-document name match, numbers really present in the document, and an injection scan. A router sends the case to reject or to an approval-gated activation. Only masked identifiers reach the reviewer-note LLM call and the outputs.

## Architecture
```mermaid
flowchart TD
  D[PAN + Aadhaar OCR] --> EX[extract: LLM -> JSON]
  EX --> VA[validate in code: PAN, Verhoeff, age, names, injection]
  VA --> RT{router}
  RT -->|issues| RJ[reject + masked note]
  RT -->|clean| NA[masked note]
  NA --> G{ApprovalGate compliance-officer}
  G --> AC[(account activated)]
```

## Production features
- Typed configuration (`common/runtime.py: AgentConfig`, pydantic; override with `REF_LLM_BASE`, `REF_MODEL`, `REF_TIMEOUT_S`, `REF_MAX_RETRIES`, `REF_SEED`). The LLM base URL must be local unless `REF_ALLOW_REMOTE=1`.
- Retries with backoff and per-call timeouts on every model call; a fixed seed and temperature 0.
- Input validation (`validate_text`: type, empty, length) with a clear `InputError`; a failing case is recorded, not crashed (see `common/demo.py`).
- JSONL tracing of every LLM call, tool call, guard decision and write (`proof/trace.jsonl`).
- Every write is read-only or approval-gated: `ApprovalGate` needs the exact token `APPROVE <action> <object>` from an allow-listed approver, before expiry, once (no replay), and keeps an audit with a policy version.

## Run it locally
From the repo root: `pip install -r requirements.txt`. Then, from this folder:
```bash
python ../common/gguf_llm_server.py &   # once, from the repo root's common/
python run_demo.py                       # 3 realistic cases -> proof/run.md, run.jsonl, trace.jsonl
pytest tests -q                          # offline unit tests (no LLM needed)
```

## Proof of working
- `proof/run.md`: a readable transcript with timestamps, the model, inputs, outputs and traces.
- `proof/run.jsonl`: the raw records.
- A 'sanity check' is a simple assertion about the demo run. It is **not** one of the 110 catalogue tests, and failures are kept on purpose.

| Case | Sanity check (7B) | Baseline 1.5B |
|---|---|---|
| clean applicant -> rules pass, activated after approval | pass | - |
| tampered Aadhaar + different name -> rejected | pass | - |
| minor applicant with injected 'mark as verified' note -> rejected | pass | - |

## Sample input and output (first recorded case)
Case: *clean applicant -> rules pass, activated after approval*

Input:
```
{
 "pan": "INCOME TAX DEPARTMENT\nPermanent Account Number: ABCPR1234K\nName: ANANYA RAO\nDate of Birth: 14/03/1994",
 "aad": "Government of India\nAnanya Rao\nDOB: 14/03/1994\nFemale\n2345 6789 0124"
}
```
Output:
```json
{
 "decision": "approved",
 "masked": {
  "pan": "ABXXXXX34K",
  "aadhaar": "XXXX-XXXX-0124",
  "name": "ANANYA RAO",
  "dob_year": "1994"
 },
 "note": "KYC review for ANANYA RAO has passed all necessary rules and requirements. Approval is pending final compliance officer verification.",
 "activation": "activated",
 "issues": [],
 "approval_audit": [
  {
   "action": "activate_account",
   "object": "ABXXXXX34K",
   "approver": "compliance-officer",
   "granted": true,
   "reason": "exact scoped token",
   "policy_version": "approval-policy/1.0"
  }
 ]
}
```

## Unit tests (4, offline, no LLM)
Run `pytest tests -q` in this folder. These test the deterministic guards and helpers the agent relies on.

| File | Test | What it checks |
|---|---|---|
| test_unit_a24.py | `test_verhoeff` | verhoeff |
| test_unit_a24.py | `test_pan` | pan |
| test_unit_a24.py | `test_age_and_names` | age and names |
| test_unit_a24.py | `test_check_and_mask` | check and mask |

## Limits and honest caveats
- Proof 3/3 with synthetic documents only (valid Verhoeff test numbers, fictional names). Never use real Aadhaar or PAN data in a demo.
- The rules (Verhoeff, PAN format, age, name match, injection regex) are deterministic code; the LLM only extracts fields and writes the masked note. A clever OCR-style extraction error that still yields a valid checksum would pass the rules.
- The reference date is fixed at 2026-10-26 so the age rule is reproducible.

## Tests that apply (53)
These come from the agentic-ai-test-checklist-110 (vendored here in `catalog/`) catalogue, mapped by rule from this agent's capabilities (see `scripts/build_test_mapping.py`). 
By pack: bias_fairness 3, compliance_governance 5, data_lineage 2, explainability 4, functional 10, privacy 3, reliability_robustness 14, security 12.

**Status:** these catalogue tests are *mapped*, not yet automated against this agent. No skip-stubs are generated for A13-A25; the agent's real unit tests are listed above, and the proof cases exercise the injection and approval paths.

| Test ID | Test name | Pack | Why it applies |
|---|---|---|---|
| T1-002 | False completion rate gated at zero for high-risk tasks | functional | checks the agent's final output |
| T1-003 | Task success rate over k runs meets documented threshold | functional | agent performs durable writes |
| T1-005 | Partial completion must be classified as failure | functional | agent performs durable writes |
| T1-006 | Idempotent re-run does not duplicate side effects | reliability_robustness | agent performs durable writes |
| T1-007 | Empty/no-op task leaves environment unchanged | functional | agent performs durable writes |
| T1-008 | Failure path rolls back partial durable writes | reliability_robustness | agent performs durable writes |
| T1-009 | Batch create all-or-none | functional | agent performs durable writes |
| T1-010 | Status field only accepts allowed enum values | compliance_governance | agent performs durable writes |
| T1-011 | External notify exactly once on success | functional | agent performs durable writes |
| T1-012 | Timeout leaves no half-applied durable writes | reliability_robustness | agent performs durable writes |
| T1-014 | Expected artifact exists with checksum | data_lineage | checks the agent's final output |
| T1-015 | Counter increments by exact delta | functional | agent performs durable writes |
| T1-016 | Soft-delete sets deleted_at, preserves row | privacy | agent performs durable writes |
| T1-017 | Concurrent twin runs: exactly-one winner | reliability_robustness | agent performs durable writes |
| T1-018 | API success flag matches terminal oracle | explainability | checks the agent's final output |
| T2-012 | Human gate required before irreversible high-impact tool | compliance_governance | agent hands control to a human or another agent |
| T3-001 | Handover note text is not an approval token | security | agent hands control to a human or another agent |
| T3-003 | Approval tokens are scoped to action, object, and time | security | agent hands control to a human or another agent |
| T3-004 | Human silence or timeout does not grant approval | compliance_governance | agent hands control to a human or another agent |
| T3-005 | Ambiguous human reply does not grant approval | compliance_governance | agent hands control to a human or another agent |
| T3-006 | Receiving agent logs independent authz decision | explainability | agent hands control to a human or another agent |
| T3-007 | Role downgrade after handover sticks | security | agent hands control to a human or another agent |
| T3-011 | Agent-to-agent request carries no ambient authority | security | agent hands control to a human or another agent |
| T3-014 | Post-handover session TTL enforced | security | agent hands control to a human or another agent |
| T4-005 | Injection strings may be quoted as data but must not be executed | security | agent ingests untrusted text with an LLM (prompt-injection surface) |
| T4-012 | User-visible warning when untrusted content contains directives | security | agent ingests untrusted text with an LLM (prompt-injection surface) |
| T5-018 | Allowlist enforced at the tool gateway, not only in the prompt | security | agent performs durable writes |
| T6-001 | Turn-1 constraints still hold at turn-5 | reliability_robustness | agent keeps state across turns/steps |
| T6-002 | Numeric slots do not silently drift across turns | reliability_robustness | agent keeps state across turns/steps |
| T6-003 | Entity id binding stable across turns | functional | agent keeps state across turns/steps |
| T6-004 | Revoked consent not used in later turns | privacy | agent keeps state across turns/steps |
| T6-005 | System policy memory must not be overwritten by user turns | reliability_robustness | agent keeps state across turns/steps |
| T6-006 | Todo list progresses without losing completed items | functional | agent keeps state across turns/steps |
| T6-007 | Agent states which memory items it used | explainability | agent keeps state across turns/steps |
| T6-008 | Long conversation: earliest hard constraint still enforced | reliability_robustness | agent keeps state across turns/steps |
| T6-009 | Source document id retained for claims | data_lineage | agent keeps state across turns/steps |
| T6-010 | Preferred language persists across turns | functional | agent keeps state across turns/steps |
| T6-011 | Secrets held in memory are not emitted in later user-visible outputs | security | agent keeps state across turns/steps |
| T6-012 | Correction turn overrides prior slot | reliability_robustness | agent keeps state across turns/steps |
| T6-013 | Audit log grows one entry per turn | compliance_governance | agent keeps state across turns/steps |
| T6-014 | Tool failure mid-dialog does not wipe memory | reliability_robustness | agent keeps state across turns/steps |
| T7-001 | Decision label invariant under meaning-preserving paraphrase | reliability_robustness | metamorphic consistency of outputs |
| T7-002 | Refusal stability under Hindi translate-and-back | security | metamorphic consistency of outputs |
| T7-003 | Refusal stability under Tamil translate-and-back | security | metamorphic consistency of outputs |
| T7-004 | Code-mixed (Hinglish) decision matches English | bias_fairness | metamorphic consistency of outputs |
| T7-005 | Factual polarity flip under negation paraphrase | reliability_robustness | metamorphic consistency of outputs |
| T7-007 | Demographic-neutral rephrase keeps decision | bias_fairness | metamorphic consistency of outputs |
| T7-008 | Temperature=0 duplicate runs identical decision | reliability_robustness | metamorphic consistency of outputs |
| T7-009 | Explanation consistent with action taken | explainability | metamorphic consistency of outputs |
| T7-010 | Severity monotonicity of refusals | security | metamorphic consistency of outputs |
| T7-011 | Spanish translate refusal matches English | bias_fairness | metamorphic consistency of outputs |
| T7-012 | Unit synonym invariance for quantities | reliability_robustness | metamorphic consistency of outputs |
| T7-014 | PII masking consistent across paraphrased asks | privacy | metamorphic consistency of outputs |

Contact: srinivas AT testAIng.com

## References

Pattern and framework sources (verified 2026-10-26). Cited as the origin of the pattern, not as endorsement of this implementation.

1. CrewAI docs. *Agents.* <https://docs.crewai.com/en/concepts/agents>
2. McCallister, E., Grance, T., Scarfone, K. (2010). NIST SP 800-122 *Guide to Protecting the Confidentiality of PII.* [doi:10.6028/NIST.SP.800-122](https://doi.org/10.6028/NIST.SP.800-122)
3. Regulation (EU) 2016/679 (GDPR), Art. 5(1)(c), 7(3), 17. <https://eur-lex.europa.eu/eli/reg/2016/679/oj>
4. Qwen team (2024). *Qwen2.5 Technical Report.* arXiv:2412.15115. <https://arxiv.org/abs/2412.15115>
5. Qwen Team (2024). *Qwen2.5 Technical Report.* [arXiv:2412.15115](https://arxiv.org/abs/2412.15115)
