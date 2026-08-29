"""Runner de tests sin dependencias (no requiere pytest).

Uso desde la raíz del proyecto:
    python -m test.run_all

Con pytest instalado también funciona:
    pytest
"""

from __future__ import annotations

import importlib
import traceback

MODULES = [
    "test.test_parser",
    "test.test_analyzer_report",
    "test.test_examples_input",
]


def main() -> int:
    total = passed = failed = 0
    for mod_name in MODULES:
        print(f"\n=== {mod_name} ===")
        mod = importlib.import_module(mod_name)
        for name in dir(mod):
            if not name.startswith("test_"):
                continue
            fn = getattr(mod, name)
            if not callable(fn):
                continue
            total += 1
            try:
                fn()
                passed += 1
                print(f"  ✓ {name}")
            except Exception:  # noqa: BLE001
                failed += 1
                print(f"  ✗ {name}")
                traceback.print_exc()

    print(f"\n== resultado: {passed}/{total} OK, {failed} fallidos ==")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
