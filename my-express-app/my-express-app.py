import requests
import sys
import time

AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJrYXZpeWEuZzIwMjJAdml0c3R1ZGVudC5hYy5pbiIsImV4cCI6MTc3ODkzMDY5OSwiaWF0IjoxNzc4OTI5Nzk5LCJpc3MiOiJBZmZvcmQgTWVkaWNhbCBUZWNobm9sb2dpZXMgUHJpdmF0ZSBMaW1pdGVkIiwianRpIjoiMWZjNDAxNTQtODZlMS00MjNmLTkxY2QtNzIxNGE3ODYzNTdjIiwibG9jYWxlIjoiZW4tSU4iLCJuYW1lIjoia2F2aXlhIGciLCJzdWIiOiIxMDI2YmI2Zi1mODhkLTRmZTMtOWVjNC0xMWU2YmUzMjRmNjMifSwiZW1haWwiOiJrYXZpeWEuZzIwMjJAdml0c3R1ZGVudC5hYy5pbiIsIm5hbWUiOiJrYXZpeWEgZyIsInJvbGxObyI6IjIybWlzMDM3NSIsImFjY2Vzc0NvZGUiOiJTZkZ1V2ciLCJjbGllbnRJRCI6IjEwMjZiYjZmLWY4OGQtNGZlMy05ZWM0LTExZTZiZTMyNGY2MyIsImNsaWVudFNlY3JldCI6ImZOR3pyV254eWdVTWJnTnEifQ.O5AkOmUW9JdJfJLbWQ7kThlUyRC08q2sXSMC4YGZ_ac"
BASE_URL = "http://4.224.186.213/evaluation-service"
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json",
}

def fetch_depots():
    print("[*] Fetching depots...")
    resp = requests.get(f"{BASE_URL}/depots", headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    depots = data.get("depots", data)
    print(f"    Found {len(depots)} depot(s)")
    return depots

def fetch_vehicles():
    print("[*] Fetching vehicles...")
    resp = requests.get(f"{BASE_URL}/vehicles", headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    vehicles = data.get("vehicles", data)
    print(f"    Found {len(vehicles)} vehicle task(s)")
    return vehicles

def solve_knapsack(capacity, items):
    n = len(items)
    if n == 0 or capacity <= 0:
        return 0, []

    dp = [0] * (capacity + 1)
    keep = [[False] * (capacity + 1) for _ in range(n)]

    for i in range(n):
        duration = items[i]["Duration"]
        impact = items[i]["Impact"]
        for w in range(capacity, duration - 1, -1):
            if dp[w - duration] + impact > dp[w]:
                dp[w] = dp[w - duration] + impact
                keep[i][w] = True

    max_impact = dp[capacity]
    selected = []
    w = capacity
    for i in range(n - 1, -1, -1):
        if keep[i][w]:
            selected.append(items[i])
            w -= items[i]["Duration"]

    selected.reverse()
    return max_impact, selected

def main():
    start = time.time()

    depots = fetch_depots()
    vehicles = fetch_vehicles()

    print()
    print("  VEHICLE MAINTENANCE SCHEDULER - RESULTS")

    grand_total_impact = 0
    grand_total_hours_used = 0
    grand_total_hours_available = 0

    for depot in depots:
        depot_id = depot["ID"]
        capacity = depot["MechanicHours"]
        grand_total_hours_available += capacity

        print(f"  DEPOT {depot_id}  |  Available Mechanic-Hours: {capacity}")

        max_impact, selected = solve_knapsack(capacity, vehicles)
        total_duration = sum(v["Duration"] for v in selected)
        grand_total_impact += max_impact
        grand_total_hours_used += total_duration

        print(f"  Max Impact Score : {max_impact}")
        print(f"  Hours Used       : {total_duration} / {capacity}")
        print(f"  Tasks Selected   : {len(selected)} / {len(vehicles)}")
        print()

        if selected:
            print(f"  {'No.':<5} {'TaskID':<40} {'Duration':>10} {'Impact':>10}")
            print(f"  {'---':<5} {'------':<40} {'--------':>10} {'------':>10}")
            for idx, v in enumerate(selected, 1):
                print(f"  {idx:<5} {v['TaskID']:<40} {v['Duration']:>10} {v['Impact']:>10}")
        else:
            print("  (No tasks selected)")

    print(f"  SUMMARY")
    print(f"  Total Depots           : {len(depots)}")
    print(f"  Total Vehicle Tasks    : {len(vehicles)}")
    print(f"  Grand Total Impact     : {grand_total_impact}")
    print(f"  Grand Total Hours Used : {grand_total_hours_used} / {grand_total_hours_available}")
    print(f"  Execution Time         : {time.time() - start:.3f}s")

if __name__ == "__main__":
    main()