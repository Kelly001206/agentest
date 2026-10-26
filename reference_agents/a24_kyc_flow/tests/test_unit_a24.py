"""Offline unit tests (no LLM) for the deterministic KYC rules."""
import os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.testing import load
R = load(__file__, module="kyc_rules")
T = datetime.date(2026, 10, 26)

def test_verhoeff():
    assert R.aadhaar_ok("2345 6789 0124") and not R.aadhaar_ok("2345 6789 0123") and not R.aadhaar_ok("1234 5678 9012")
def test_pan():
    assert R.pan_ok("ABCPR1234K") and not R.pan_ok("ABC1R1234K") and not R.pan_ok("ABCXR1234K")
def test_age_and_names():
    assert R.age_on("14/03/1994", T) == 32 and R.age_on("21/06/2010", T) == 16 and R.age_on("bad", T) is None
    assert R.name_match("ANANYA RAO", "Ananya Rao") == 1.0 and R.name_match("VIKRAM SETHI", "Vikas Sharma") < 0.85
def test_check_and_mask():
    ok = dict(pan="ABCPR1234K", pan_name="ANANYA RAO", aadhaar="2345 6789 0124", aadhaar_name="Ananya Rao", dob="14/03/1994")
    assert R.check(ok, T) == []
    assert "PAN_SURNAME_INITIAL" in R.check({**ok, "pan": "ABCPX1234K"}, T)
    assert R.mask_aadhaar("2345 6789 0124") == "XXXX-XXXX-0124" and R.mask_pan("ABCPR1234K") == "ABXXXXX34K"
