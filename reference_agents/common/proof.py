"""Write proof-of-run logs: runs/<agent>-run.jsonl and runs/<agent>-run.md"""
import json, os, platform, datetime
from .config import LLM_MODEL

class ProofLog:
    def __init__(self, agent_dir, agent_id, framework, uses_llm=True):
        self.dir = os.environ.get("REF_PROOF_DIR") or os.path.join(agent_dir, "proof"); os.makedirs(self.dir, exist_ok=True)
        self.agent_id, self.framework, self.uses_llm = agent_id, framework, uses_llm
        self.records = []
    def add(self, case, input, output, trace=None, passed=None, note=""):
        r = {"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
             "agent": self.agent_id, "framework": self.framework,
             "model": LLM_MODEL if self.uses_llm else "none (no LLM)",
             "host": platform.node(), "case": case, "input": input, "output": output,
             "trace": trace or [], "check_passed": passed, "note": note}
        self.records.append(r); print(json.dumps(r, ensure_ascii=False, default=str)[:1500], flush=True)
    def save(self):
        with open(os.path.join(self.dir, "run.jsonl"), "w") as f:
            for r in self.records: f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
        md = [f"# Proof of run: {self.agent_id}", "", f"- Framework: {self.framework}",
              f"- Model: {self.records[0]['model'] if self.records else '-'}",
              f"- Runs: {len(self.records)}; sanity checks passed: {sum(1 for r in self.records if r['check_passed'])}/{len(self.records)}",
              "- Generated automatically by `run_demo.py`; raw records in `run.jsonl`.",
              "- 'Sanity check' is a simple built-in assertion about this demo run, not one of the 110 catalogue tests.", ""]
        for r in self.records:
            md += [f"## {r['case']}", f"_{r['timestamp']}_", "", "**Input**", "```", str(r['input'])[:3000], "```",
                   "**Output**", "```", json.dumps(r['output'], ensure_ascii=False, indent=1, default=str)[:4000] if not isinstance(r['output'], str) else r['output'][:4000], "```"]
            if r["trace"]:
                md += ["**Trace**", "```"] + [json.dumps(t, ensure_ascii=False, default=str)[:600] for t in r["trace"]] + ["```"]
            md += [f"**Sanity check passed:** {r['check_passed']}" + (f" ({r['note']})" if r['note'] else ""), ""]
        open(os.path.join(self.dir, "run.md"), "w").write("\n".join(md))
