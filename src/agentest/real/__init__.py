"""Real (non-noop) checks for the 41 catalogue IDs.

* ``ids``      - the 41 IDs and what each real check verifies
* ``probes``   - concrete inputs sent to the 12 vendored reference agents
* ``live``     - runs probes against the vendored agents (needs a local model)
* ``checks``   - deterministic oracles over recorded episodes (pass / fail / n/a)
* ``samples``  - the same 41 IDs against the 15 teaching sample agents
* ``report``   - builds the 41 x 27 results matrix
"""
