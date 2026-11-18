import pytest
from fastapi.testclient import TestClient
from main import app
from app.services.matcher_service import matcher_service
from app.services.calendar_service import calendar_service

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "ContestMate API"
    assert data["status"] == "online"

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_contests():
    response = client.get("/api/contests")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) > 0

def test_get_recommended_contests():
    response = client.get("/api/contests/recommended")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) > 0

def test_calendar_events_format():
    response = client.get("/api/calendar/events")
    assert response.status_code == 200
    events = response.json()
    assert isinstance(events, list)
    assert len(events) > 0
    event = events[0]
    assert "id" in event
    assert "title" in event
    assert "start" in event
    assert "allDay" in event
    assert "extendedProps" in event
    assert "organizer" in event["extendedProps"]
    assert "category" in event["extendedProps"]
    assert "dday" in event["extendedProps"]

def test_bookmarks_flow():
    # 1. 목록 조회
    get_res = client.get("/api/contests")
    contest_id = get_res.json()["items"][0]["id"]

    # 2. 북마크 추가
    add_res = client.post(f"/api/bookmarks/{contest_id}")
    assert add_res.status_code == 200

    # 3. 북마크 목록 확인
    bm_list_res = client.get("/api/bookmarks")
    assert bm_list_res.status_code == 200
    bm_items = bm_list_res.json()
    assert any(b["contest_id"] == contest_id for b in bm_items)

    # 4. 북마크 해제
    del_res = client.delete(f"/api/bookmarks/{contest_id}")
    assert del_res.status_code == 200

def test_preferences_update():
    pref_res = client.get("/api/preferences")
    assert pref_res.status_code == 200
    current_pref = pref_res.json()

    update_payload = {
        **current_pref,
        "keywords": ["AI", "해커톤", "테스트키워드"],
        "keyword_match_type": "AND"
    }
    put_res = client.put("/api/preferences", json=update_payload)
    assert put_res.status_code == 200
    updated = put_res.json()
    assert "테스트키워드" in updated["keywords"]
    assert updated["keyword_match_type"] == "AND"

def test_admin_collector_status():
    res = client.get("/api/admin/collector-status")
    assert res.status_code == 200
    data = res.json()
    assert "total_contests" in data
    assert "collectors" in data
