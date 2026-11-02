"""Runs every scenario x mode through the FastAPI app and prints the results."""
from fastapi.testclient import TestClient

from server import app

client = TestClient(app)
MODES = ["vulnerable", "allowlist", "hardened"]


def show(scenario, mode):
    r = client.post("/run", json={"scenario": scenario, "mode": mode}).json()
    print(f"\n=== scenario={scenario:9} mode={mode:10} -> "
          f"{'COMPROMISED' if r['compromised'] else 'safe'} ===")
    for line in r["trace"]:
        print("  ", line)
    for m in r["outbox"]:
        print(f"   OUTBOX: to={m['to']} subject={m['subject']!r}\n           body={m['body']!r}")
    print("   Agent told user:", r["final_answer"].replace("\n", " | "))
    return r["compromised"]


if __name__ == "__main__":
    print("Malicious email in scenario 'exfil':")
    print(client.get("/inbox", params={"scenario": "exfil"}).json()[-1]["body"])

    # baseline: no attack, vulnerable agent behaves normally
    show("none", "vulnerable")

    results = {(s, m): show(s, m) for s in ("exfil", "internal") for m in MODES}

    print("\n\nSUMMARY (True = attacker succeeded)")
    print(f"{'scenario':10}" + "".join(f"{m:12}" for m in MODES))
    for s in ("exfil", "internal"):
        print(f"{s:10}" + "".join(f"{str(results[(s, m)]):12}" for m in MODES))
