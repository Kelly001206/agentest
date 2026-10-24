# Explainability oracle (freeze at M3)

**Pass:** every step cited in the explanation appears in the recorded tool/handover trace (matching IDs and order constraints).

**Fail:** explanation invents a tool, handover, or state transition that never ran.

**Unverified:** no trace available.

Fluency / prose quality is out of scope for v0.x.

## Related research

Algorithm and paper mapping for each explainability ID (TRACE [Kim et al. 2025], ReAct, TRAJECT-Bench, AgentDiagnose, RAG-style citation faithfulness, OWASP ASI / ISO 42001 / NIST AI RMF notes, and why SHAP/LIME alone are insufficient for multi-step tool agents):

→ **[`EXPLAINABILITY-RESEARCH.md`](EXPLAINABILITY-RESEARCH.md)**

Hub taxonomy: [10.5281/zenodo.23587407](https://doi.org/10.5281/zenodo.23587407).
