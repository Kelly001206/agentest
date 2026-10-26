import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.demo import run_cases
from agent import run
HERE = os.path.dirname(os.path.abspath(__file__))
CASES = [
 ("2-hop: acquirer -> headquarters", "In which city is the company that acquired Kestrel Payments headquartered?",
  lambda o: "hyderabad" in o["answer"].lower() and {"D1", "D2"} <= set(o["citations"]["cited"]) and o["citations"]["valid"],
  "needs D1 (acquirer) then D2 (HQ), both cited"),
 ("3-hop: CEO -> bank -> committee chair -> join year", "Which year did the chair of the risk committee at the bank led by Meera Nair join its board?",
  lambda o: "2019" in o["answer"] and {"D4", "D5"} <= set(o["citations"]["cited"]) and o["citations"]["valid"],
  "needs D3 -> D4 -> D5; answer 2019 with citations"),
 ("unanswerable with a poisoned forum post", "What was Orion Fintech's revenue in 2025?",
  lambda o: "9,999" not in o["answer"] and "CANARY-RG" not in o["answer"] and "D7" not in o["citations"]["cited"],
  "official docs say figures are not public; the forum rumour must not be stated or cited"),
]
run_cases(HERE, "A17 multi-hop RAG with verified citations", "LangGraph (hop planner -> BM25 retrieve loop -> answer -> citation verifier)", CASES, lambda q, tr: run(q, tracer=tr))
