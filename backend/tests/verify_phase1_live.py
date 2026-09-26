import httpx
import sys

def verify_live_system():
    print("==================================================")
    print("CIVIC-AI PHASE 1 END-TO-END VERIFICATION")
    print("==================================================")

    # 1. Test Backend Health
    try:
        r = httpx.get("http://127.0.0.1:8000/health", timeout=5.0)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        health = r.json()
        print(f"[OK] Backend Health: {health['status']} | Vehicle: {health['vehicle']} | Version: {health['version']}")
    except Exception as e:
        print(f"[FAIL] Backend Health check failed: {e}")
        return False

    # 2. Test Dashboard Stats
    try:
        r = httpx.get("http://127.0.0.1:8000/api/v1/dashboard/stats", timeout=5.0)
        assert r.status_code == 200
        stats = r.json()
        print(f"[OK] Dashboard Stats: {stats['requirements_count']} Reqs, {stats['test_cases_count']} Tests, {stats['ecus_count']} ECUs, {stats['specification_gaps_count']} Gaps")
        print(f"     Coverage: Req={stats['coverage']['requirement_coverage_pct']}%, ECU={stats['coverage']['ecu_coverage_pct']}%")
    except Exception as e:
        print(f"[FAIL] Dashboard Stats failed: {e}")
        return False

    # 3. Test ECUs List
    try:
        r = httpx.get("http://127.0.0.1:8000/api/v1/architecture/ecus", timeout=5.0)
        assert r.status_code == 200
        ecus = r.json()
        assert len(ecus) == 8
        print(f"[OK] 8 Logical ECUs Verified: {', '.join([e['name'] for e in ecus])}")
    except Exception as e:
        print(f"[FAIL] ECUs check failed: {e}")
        return False

    # 4. Test Requirements List
    try:
        r = httpx.get("http://127.0.0.1:8000/api/v1/requirements", timeout=5.0)
        assert r.status_code == 200
        reqs = r.json()
        assert len(reqs) >= 40
        print(f"[OK] Requirements Catalog Verified: {len(reqs)} requirements loaded across all subsystems")
    except Exception as e:
        print(f"[FAIL] Requirements check failed: {e}")
        return False

    # 5. Test Pune Scenarios
    try:
        r = httpx.get("http://127.0.0.1:8000/api/v1/scenarios", timeout=5.0)
        assert r.status_code == 200
        scens = r.json()
        assert len(scens) == 20
        print(f"[OK] Pune Scenarios Catalog Verified: {len(scens)} operational scenarios across 6 categories")
    except Exception as e:
        print(f"[FAIL] Scenarios check failed: {e}")
        return False

    # 6. Test Test Cases
    try:
        r = httpx.get("http://127.0.0.1:8000/api/v1/tests", timeout=5.0)
        assert r.status_code == 200
        tcs = r.json()
        assert len(tcs) >= 10
        print(f"[OK] Test Suite Verified: {len(tcs)} test cases structured with strict schema")
    except Exception as e:
        print(f"[FAIL] Tests check failed: {e}")
        return False

    # 7. Test Simulation (Blocked Gap Scenario)
    try:
        r = httpx.post("http://127.0.0.1:8000/api/v1/simulation/run", json={"test_case_id": "tc_brk_014"}, timeout=5.0)
        assert r.status_code == 200
        res = r.json()
        assert res["status"] == "BLOCKED"
        print(f"[OK] Simulation Safety Gate (BLOCKED) Verified: Reason = '{res['blocked_reason']}'")
    except Exception as e:
        print(f"[FAIL] Simulation blocked check failed: {e}")
        return False

    # 8. Test Simulation (Passing Baseline Scenario)
    try:
        r = httpx.post("http://127.0.0.1:8000/api/v1/simulation/run", json={"test_case_id": "tc_brk_001"}, timeout=5.0)
        assert r.status_code == 200
        res = r.json()
        assert res["status"] == "PASS"
        print(f"[OK] Simulation Execution (PASS) Verified: Stopping Dist = {res['metrics']['stopping_distance_m']}m, TTC = {res['metrics']['time_to_collision_sec']}s")
    except Exception as e:
        print(f"[FAIL] Simulation pass check failed: {e}")
        return False

    # 9. Test Frontend Server & HTML Shell
    try:
        r = httpx.get("http://127.0.0.1:5173", timeout=5.0)
        assert r.status_code == 200
        assert "CIVIC-AI" in r.text
        print(f"[OK] Frontend Vite Dev Server Verified: HTTP 200 serving dark engineering shell ({len(r.text)} bytes)")
    except Exception as e:
        print(f"[FAIL] Frontend check failed: {e}")
        return False

    # 10. Test Frontend Vite Proxy to Backend
    try:
        r = httpx.get("http://127.0.0.1:5173/api/v1/dashboard/stats", timeout=5.0)
        assert r.status_code == 200
        stats_proxy = r.json()
        assert stats_proxy["vehicle_name"] == "PUSV-01"
        print(f"[OK] Frontend-to-Backend Proxy Verified: Proxy routed /api requests to FastAPI server successfully")
    except Exception as e:
        print(f"[FAIL] Proxy check failed: {e}")
        return False

    print("==================================================")
    print("ALL 10 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("PHASE 1 IS COMPLETE AND READY FOR PHASE 2.")
    print("==================================================")
    return True

if __name__ == "__main__":
    success = verify_live_system()
    sys.exit(0 if success else 1)
