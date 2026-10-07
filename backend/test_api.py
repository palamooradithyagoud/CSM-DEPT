import json
from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app("development")
client = app.test_client()


def test_suite():
    print("\n==========================================")
    print("  PHASE 1 BACKEND AUTOMATED TEST SUITE   ")
    print("==========================================\n")

    # 1. System Health Endpoint
    res = client.get("/api/v1/health")
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["status"] == "online"
    print("[PASS] [TEST 1] System Health check endpoint /api/v1/health PASSED")

    # 2. Public Department Info
    res = client.get("/api/v1/public/department-info")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["department"]["shortCode"] == "CSE"
    assert "Dr. M. A. Jabbar" in data["data"]["department"]["hod"]["name"]
    print("[PASS] [TEST 2] Public Department Info /api/v1/public/department-info PASSED")

    # 3. Faculty Directory & Search Filtering
    res = client.get("/api/v1/public/faculty")
    assert res.status_code == 200
    faculty_list = res.get_json()["data"]["faculty"]
    assert len(faculty_list) >= 8, f"Expected at least 8 faculty, got {len(faculty_list)}"

    # Search filter test
    res = client.get("/api/v1/public/faculty?search=Machine+Learning")
    assert res.status_code == 200
    searched = res.get_json()["data"]["faculty"]
    assert len(searched) >= 1
    print(f"[PASS] [TEST 3] Faculty Directory ({len(faculty_list)} members) & Search filter PASSED")

    # 4. Department Events
    res = client.get("/api/v1/public/events")
    assert res.status_code == 200
    events = res.get_json()["data"]["events"]
    assert len(events) >= 4
    print(f"[PASS] [TEST 4] Department Events ({len(events)} events) PASSED")

    # 5. Student Achievements (Public showcase only)
    res = client.get("/api/v1/public/achievements")
    assert res.status_code == 200
    achievements = res.get_json()["data"]["achievements"]
    assert len(achievements) >= 3
    print(f"[PASS] [TEST 5] Student Achievements ({len(achievements)} accolades) PASSED")

    # 6. Official Announcements & Circulars
    res = client.get("/api/v1/public/announcements")
    assert res.status_code == 200
    announcements = res.get_json()["data"]["announcements"]
    assert len(announcements) >= 3
    print(f"[PASS] [TEST 6] Announcements & Circulars ({len(announcements)} circulars) PASSED")

    # 7. Academic Programs & Offerings
    res = client.get("/api/v1/public/programs")
    assert res.status_code == 200
    programs = res.get_json()["data"]["programs"]
    assert len(programs) == 4
    assert programs[0]["id"] == "btech-cse"
    print(f"[PASS] [TEST 7] Academic Programs ({len(programs)} degrees) PASSED")

    # 8. Department Gallery
    res = client.get("/api/v1/public/gallery")
    assert res.status_code == 200
    gallery = res.get_json()["data"]["gallery"]
    assert len(gallery) >= 6
    print(f"[PASS] [TEST 8] Department Gallery ({len(gallery)} photo archives) PASSED")

    # 9. Department News
    res = client.get("/api/v1/public/news")
    assert res.status_code == 200
    news = res.get_json()["data"]["news"]
    assert len(news) >= 3
    print(f"[PASS] [TEST 9] Department News ({len(news)} articles) PASSED")

    # 10. Public Statistics
    res = client.get("/api/v1/public/stats")
    assert res.status_code == 200
    stats = res.get_json()["data"]["stats"]
    assert stats["nbaAccredited"] is True
    print("[PASS] [TEST 10] Public Aggregate Statistics PASSED")

    # 11. Security Check: Invalid Login Credentials
    res = client.post("/api/v1/auth/login", json={"email": "hod@department.edu", "password": "WrongPassword"})
    assert res.status_code == 401
    assert res.get_json()["success"] is False
    print("[PASS] [TEST 11] Security: Invalid password rejected with 401 PASSED")

    res = client.post("/api/v1/auth/login", json={"email": "nonexistent@college.edu", "password": "Admin"})
    assert res.status_code == 401
    print("[PASS] [TEST 12] Security: Unregistered user rejected with 401 PASSED")

    # 12. Security Check: Protected Route without Token
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401
    print("[PASS] [TEST 13] Security: Protected endpoint without Bearer token rejected with 401 PASSED")

    # 13. Valid HOD Login & JWT Issuance
    res = client.post("/api/v1/auth/login", json={"email": "hod@department.edu", "password": "Admin@123"})
    assert res.status_code == 200
    auth_data = res.get_json()["data"]
    access_token = auth_data["accessToken"]
    refresh_token = auth_data["refreshToken"]
    user = auth_data["user"]
    assert user["role"] == "HOD"
    assert user["fullName"] == "Dr. M. A. Jabbar"
    print(f"[PASS] [TEST 14] Authentication: HOD login issued JWT tokens ({user['fullName']}, Role: {user['role']}) PASSED")

    # 14. Protected Route with Valid Bearer Token
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200
    user_me = res.get_json()["data"]["user"]
    assert user_me["id"] == user["id"]
    print("[PASS] [TEST 15] RBAC: Protected /auth/me verified identity via Bearer token PASSED")

    # 15. Token Refresh Endpoint
    res = client.post("/api/v1/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    assert res.status_code == 200
    new_token = res.get_json()["data"]["accessToken"]
    assert new_token is not None
    print("[PASS] [TEST 16] Authentication: Refresh token cycle succeeded PASSED")

    # 16. Academic Privacy Guard
    # Ensure public endpoints never expose student CGPA or attendance
    all_public_endpoints = [
        "/api/v1/public/department-info",
        "/api/v1/public/faculty",
        "/api/v1/public/events",
        "/api/v1/public/achievements",
        "/api/v1/public/announcements",
        "/api/v1/public/programs",
        "/api/v1/public/gallery",
        "/api/v1/public/news",
        "/api/v1/public/stats",
    ]
    for endpoint in all_public_endpoints:
        r = client.get(endpoint)
        content_text = json.dumps(r.get_json())
        assert "cgpa" not in content_text.lower(), f"Leak alert: 'cgpa' found in {endpoint}"
        assert "sgpa" not in content_text.lower(), f"Leak alert: 'sgpa' found in {endpoint}"
    print("[PASS] [TEST 17] Academic Privacy: Zero private student records (CGPA/SGPA) leaked in public APIs PASSED")

    print("\n==========================================")
    print("  ALL 17 PHASE 1 TESTS PASSED SUCCESSFULLY! ")
    print("==========================================\n")


if __name__ == "__main__":
    test_suite()
