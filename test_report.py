import json
from pathlib import Path
import yaml

TEST_LIST_FILE = Path("test_list.yaml")
AUTO_RESULTS_FILE = Path("result_test_auto.json")
SELENIUM_RESULTS_FILE = Path("result_test_selenium.json")


def load_test_list():
    if not TEST_LIST_FILE.exists():
        print(f"❌ Fichier introuvable : {TEST_LIST_FILE}")
        return []
    with TEST_LIST_FILE.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or []

def load_results(file_path: Path):
    if not file_path.exists():
        print(f"⚠ Aucun fichier {file_path}, aucun résultat chargé.")
        return {}

    with file_path.open(encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        return data

    results = {}
    if isinstance(data, list):
        for item in data:
            tid = item.get("id") or item.get("test_case_id")
            status = item.get("status") or item.get("outcome")
            if tid and status:
                results[tid] = status
    return results



def interpret_status(raw):
    if not raw:
        return "🕳Not found"

    s = str(raw).lower()

    if s in {"passed", "ok", "success"}:
        return "✅Passed"
    if s in {"failed", "fail", "error"}:
        return "❌Failed"

    return "🕳Not found"


# PROGRAMME PRINCIPAL
def main():
    test_list = load_test_list()
    auto_results = load_results(AUTO_RESULTS_FILE)
    selenium_results = load_results(SELENIUM_RESULTS_FILE)

    total = len(test_list)
    passed = failed = manual = not_found = 0

    output_lines = []

    for test in test_list:
        test_id = test.get("id")
        ttype = test.get("type", "auto")

        if ttype == "manual":
            status = "🫱Manual test needed"
            manual += 1

        elif ttype == "auto-selenium":
            status = interpret_status(selenium_results.get(test_id))
            if status.startswith("✅"):
                passed += 1
            elif status.startswith("❌"):
                failed += 1
            else:
                not_found += 1

        else:  # AUTO DJANGO
            status = interpret_status(auto_results.get(test_id))
            if status.startswith("✅"):
                passed += 1
            elif status.startswith("❌"):
                failed += 1
            else:
                not_found += 1

        line = f"{test_id} | {ttype} | {status}"
        print(line)
        output_lines.append(line)


    def pct(n): 
        return (n / total * 100) if total else 0

    summary = f"""
=== SUMMARY ===
Number of tests: {total}
✅Passed tests: {passed} ({pct(passed):.1f}%)
❌Failed tests: {failed} ({pct(failed):.1f}%)
🕳Not found tests: {not_found} ({pct(not_found):.1f}%)
🫱Manual tests: {manual} ({pct(manual):.1f}%)
Total valid (Passed + Manual): {passed + manual} ({pct(passed + manual):.1f}%)
"""

    print(summary)
    output_lines.append(summary)

   
    with open("test_report_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print("📄 test_report_output.txt généré pour la CI.")


# --------------------------------------------------------------
if __name__ == "__main__":
    main()