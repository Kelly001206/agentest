"""Helper for offline unit tests: load an agent folder's module under a unique name so that
`pytest a*/tests` can collect every agent in one session without module-name clashes."""
import importlib.util, os, sys

def load(test_file: str, module: str = "agent"):
    d = os.path.dirname(os.path.dirname(os.path.abspath(test_file)))
    if d not in sys.path: sys.path.insert(0, d)
    name = f"{os.path.basename(d)}_{module}"
    if name in sys.modules: return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, os.path.join(d, f"{module}.py"))
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m
