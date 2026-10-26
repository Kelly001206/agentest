"""Deterministic KYC rules (no LLM): PAN format, Aadhaar Verhoeff checksum, DOB/age, name match, masking."""
from __future__ import annotations
import re, datetime, difflib

_D = [[0,1,2,3,4,5,6,7,8,9],[1,2,3,4,0,6,7,8,9,5],[2,3,4,0,1,7,8,9,5,6],[3,4,0,1,2,8,9,5,6,7],[4,0,1,2,3,9,5,6,7,8],
      [5,9,8,7,6,0,4,3,2,1],[6,5,9,8,7,1,0,4,3,2],[7,6,5,9,8,2,1,0,4,3],[8,7,6,5,9,3,2,1,0,4],[9,8,7,6,5,4,3,2,1,0]]
_P = [[0,1,2,3,4,5,6,7,8,9],[1,5,7,6,2,8,3,0,9,4],[5,8,0,3,7,9,6,1,4,2],[8,9,1,6,0,4,3,5,2,7],[9,4,5,3,1,2,6,8,7,0],
      [4,2,8,6,5,7,3,9,0,1],[2,7,9,3,8,0,6,4,1,5],[7,0,4,6,9,1,3,2,5,8]]
_INV = [0,4,3,2,1,5,6,7,8,9]

def verhoeff_valid(num: str) -> bool:
    c = 0
    for i, ch in enumerate(reversed(num)): c = _D[c][_P[i % 8][int(ch)]]
    return c == 0

def verhoeff_digit(num: str) -> str:
    c = 0
    for i, ch in enumerate(reversed(num)): c = _D[c][_P[(i + 1) % 8][int(ch)]]
    return str(_INV[c])

def aadhaar_ok(a: str) -> bool:
    d = re.sub(r"[\s-]", "", a or "")
    return bool(re.fullmatch(r"[2-9]\d{11}", d)) and verhoeff_valid(d)

def pan_ok(p: str) -> bool:
    return bool(re.fullmatch(r"[A-Z]{3}[PCHFATBLJG][A-Z]\d{4}[A-Z]", (p or "").strip().upper()))

def age_on(dob: str, today: datetime.date) -> int | None:
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            d = datetime.datetime.strptime(dob.strip(), fmt).date()
            return today.year - d.year - ((today.month, today.day) < (d.month, d.day))
        except Exception: pass
    return None

def name_match(a: str, b: str) -> float:
    n = lambda s: " ".join(sorted(re.sub(r"[^a-z ]", "", (s or "").lower()).split()))
    return round(difflib.SequenceMatcher(None, n(a), n(b)).ratio(), 2)

def mask_aadhaar(a: str) -> str:
    d = re.sub(r"\D", "", a or ""); return "XXXX-XXXX-" + d[-4:] if len(d) >= 4 else "XXXX"

def mask_pan(p: str) -> str:
    p = (p or "").upper(); return p[:2] + "XXXXX" + p[-3:] if len(p) == 10 else "XXXX"

def check(fields: dict, today: datetime.date) -> list[str]:
    """Return a list of issue codes; empty list = all rules pass."""
    issues = []
    if not pan_ok(fields.get("pan", "")): issues.append("PAN_FORMAT")
    elif fields.get("pan", "").upper()[4] != (re.sub(r"[^A-Za-z ]", "", fields.get("pan_name", "")).split() or ["?"])[-1][0].upper():
        issues.append("PAN_SURNAME_INITIAL")
    if not aadhaar_ok(fields.get("aadhaar", "")): issues.append("AADHAAR_CHECKSUM")
    age = age_on(fields.get("dob", ""), today)
    if age is None: issues.append("DOB_UNREADABLE")
    elif age < 18: issues.append("UNDER_18")
    if name_match(fields.get("pan_name", ""), fields.get("aadhaar_name", "")) < 0.85: issues.append("NAME_MISMATCH")
    return issues
