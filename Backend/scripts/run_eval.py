
import argparse, json, httpx

def main():
    p = argparse.ArgumentParser()
    p.add_argument("cases", help="Path to eval_cases.json")
    p.add_argument("--base", default="http://localhost:8000")
    p.add_argument("--api-key", default="local-dev-key")
    args = p.parse_args()

    with open(args.cases, "r", encoding="utf-8") as f:
        cases = json.load(f)

    ok = 0
    for c in cases:
        payload = c["payload"]
        r = httpx.post(f"{args.base}/payments/decide",
                       json=payload,
                       headers={"Content-Type":"application/json","X-API-Key":args.api_key})
        if r.status_code != 200:
            print(f"❌ {c['name']}: HTTP {r.status_code}")
            continue
        got = r.json().get("decision")
        exp = c["expected"]
        if got == exp:
            print(f"✅ {c['name']}: {got}")
            ok += 1
        else:
            print(f"❌ {c['name']}: got {got}, expected {exp}")
    print(f"\nResult: {ok}/{len(cases)} correct")

if __name__ == "__main__":
    main()
