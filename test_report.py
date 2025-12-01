import json
from pathlib import Path
import yaml

TEST_LIST_FILE = Path("test_list.yaml")
RESULTS_FILE = Path("result_test_auto.json")


def load_test_list():
    with TEST_LIST_FILE.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def load_results():
    with RESULTS_FILE.open(encoding="utf-8") as f:
        data = json.load(f) or {}
    return data if isinstance(data, dict) else {}


def interpret_status(raw_status):
    if not raw_status:
        return "Not found"
    s = str(raw_status).lower()
    if s in {"passed", "ok", "success"}:
        return "✅Passed"
    if s in {"failed", "fail", "error"}:
        return "❌Failed"
    return "Not found"


def main():
    test_list = load_test_list()
    auto_results = load_results()
    total = len(test_list)
    passed = failed = not_found = manual = 0

    for test in test_list:
        test_id = test.get("id", "UNKNOWN")
        test_type = test.get("type", "auto")

        if test_type == "manual":
            status = "🫱Manual test needed"
            manual += 1
        else:
            status = interpret_status(auto_results.get(test_id))
            if status.startswith("✅"):
                passed += 1
            elif status.startswith("❌"):
                failed += 1
            else:
                not_found += 1

        print(f"{test_id} | {test_type} | {status}")

    def pct(n):
        return (n / total * 100) if total else 0.0
    
    print()
    print(f"Number of tests: {total}")
    print(f"✅Passed tests: {passed} ({pct(passed):.1f}%)")
    print(f"❌Failed tests: {failed} ({pct(failed):.1f}%)")
    print(f"Not found tests: {not_found} ({pct(not_found):.1f}%)")
    print(f"🫱Test to pass manually: {manual} ({pct(manual):.1f}%)")
    print(f"✅Passed + 🫱Manual: {passed + manual} ({pct(passed + manual):.1f}%)")


if __name__ == "__main__":
    main()
