import json
from pathlib import Path
import yaml

TEST_LIST_FILE = Path("test_list.yaml")
RESULTS_AUTO_FILE = Path("result_test_auto.json")
RESULTS_SELENIUM_FILE = Path("result_test_selenium.json")


# --------------------------
# Chargement des fichiers
# --------------------------

def load_test_list():
    if not TEST_LIST_FILE.exists():
        print("❌ test_list.yaml introuvable.")
        return []
    with TEST_LIST_FILE.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def load_results(path):
    """Charge un fichier JSON sous forme { 'TC001': 'passed', ... }"""
    if not path.exists():
        return {}

    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    # Si format {"TC016": "passed"} -> OK
    if isinstance(data, dict):
        return data

    # Sinon si format liste -> convertir
    if isinstance(data, list):
        converted = {}
        for item in data:
            tid = item.get("id") or item.get("test_case_id")
            status = item.get("status")
            if tid:
                converted[tid] = status
        return converted

    return {}


# --------------------------
# Fonction d’interprétation
# --------------------------

def interpret_status(raw):
    if not raw:
        return "🕳Not found"
    s = str(raw).lower()
    if s in {"passed", "ok", "success"}:
        return "✅Passed"
    if s in {"failed", "error"}:
        return "❌Failed"
    return "🕳Not found"


# --------------------------
# Programme principal
# --------------------------

def main():
    test_list = load_test_list()
    auto_results = load_results(RESULTS_AUTO_FILE)
    selenium_results = load_results(RESULTS_SELENIUM_FILE)

    total = len(test_list)
    passed = failed = not_found = manual = 0

    print()

    for test in test_list:
        test_id = test.get("id")
        test_type = test.get("type", "auto")

        # ---------- MANUAL ----------
        if test_type == "manual":
            status = "🫱Manual test needed"
            manual += 1

        # ---------- SELENIUM ----------
        elif test_type == "auto-selenium":
            raw = selenium_results.get(test_id)
            status = interpret_status(raw)

            if status.startswith("✅"):
                passed += 1
            elif status.startswith("❌"):
                failed += 1
            else:
                not_found += 1

        # ---------- UNITTEST ----------
        else:
            raw = auto_results.get(test_id)
            status = interpret_status(raw)

            if status.startswith("✅"):
                passed += 1
            elif status.startswith("❌"):
                failed += 1
            else:
                not_found += 1

        print(f"{test_id} | {test_type} | {status}")

    # ---------- Summary ----------
    def pct(n): return (n / total * 100) if total else 0

    print("\n=== SUMMARY ===")
    print(f"Number of tests: {total}")
    print(f"✅Passed tests: {passed} ({pct(passed):.1f}%)")
    print(f"❌Failed tests: {failed} ({pct(failed):.1f}%)")
    print(f"🕳Not found tests: {not_found} ({pct(not_found):.1f}%)")
    print(f"🫱Manual tests: {manual} ({pct(manual):.1f}%)")
    print(f"Total valid (Passed + Manual): {passed + manual} ({pct(passed + manual):.1f}%)")


if __name__ == "__main__":
    main()
