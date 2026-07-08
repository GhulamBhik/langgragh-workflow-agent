import json
import requests
from pathlib import Path
from datetime import datetime


API_URL = "http://localhost:8000/query"


BASE_DIR = Path(__file__).parent
print(BASE_DIR)
INPUT_FILE = (
    BASE_DIR
    / "data"
    / "sample_inputs"
    / "prompts.json"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "sample_outputs"
    / "results.json"
)


def load_prompts():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_results(results):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            results,
            f,
            indent=4,
            ensure_ascii=False
        )


def run_tests():

    prompts = load_prompts()

    results = []

    print(
        f"Running {len(prompts)} workflow tests...\n"
    )


    for index, item in enumerate(prompts, start=1):

        query = item["query"]
        expected_route = item["route"]

        print(
            f"[{index}/{len(prompts)}] {query}"
        )

        try:

            response = requests.post(
                API_URL,
                json={
                    "query": query
                },
                timeout=120
            )


            if response.status_code != 200:

                results.append(
                    {
                        "query": query,
                        "expected_route": expected_route,
                        "status": "FAILED",
                        "error": response.text
                    }
                )

                print("❌ API ERROR\n")
                continue


            data = response.json()


            actual_route = data.get(
                "route",
                ""
            )


            passed = (
                actual_route == expected_route
            )


            results.append(
                {
                    "query": query,
                    "expected_route": expected_route,
                    "actual_route": actual_route,
                    "intent": data.get(
                        "intent",
                        ""
                    ),
                    "review": data.get(
                        "review",
                        ""
                    ),
                    "final_answer": data.get(
                        "final_answer",
                        ""
                    ),
                    "status": (
                        "PASSED"
                        if passed
                        else "FAILED"
                    )
                }
            )


            if passed:
                print(
                    "✅ PASSED\n"
                )
            else:
                print(
                    f"❌ FAILED "
                    f"(Expected {expected_route}, got {actual_route})\n"
                )


        except Exception as e:

            results.append(
                {
                    "query": query,
                    "expected_route": expected_route,
                    "status": "ERROR",
                    "error": str(e)
                }
            )

            print(
                f"❌ ERROR: {e}\n"
            )


    save_results(results)


    passed_count = sum(
        1
        for r in results
        if r.get("status") == "PASSED"
    )


    print("=" * 50)
    print(
        f"Completed: {len(results)} tests"
    )
    print(
        f"Passed: {passed_count}/{len(results)}"
    )
    print(
        f"Results saved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    run_tests()