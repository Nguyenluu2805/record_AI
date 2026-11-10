import sys
import os
import json
import asyncio

# Setup path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
os.environ['SERVER_PORT'] = '8000'

from fastapi.testclient import TestClient
from app.main import app

def test_full_system_flow():
    client = TestClient(app)
    print("=== 1. Test Config Endpoint ===")
    res_cfg = client.get("/api/config")
    assert res_cfg.status_code == 200
    cfg = res_cfg.json()
    print("Company:", cfg["company_name"])
    print("Leaders count:", len(cfg["leadership_members"]))
    assert "KIM LONG PHÁT" in cfg["company_name"]

    print("\n=== 2. Test Option 1 (Họp Nội Bộ) Flow ===")
    start_payload_1 = {
        "mode": "option_1",
        "title": "Cuộc họp Giao ban Triển khai Kế hoạch Trọng tâm Quý 4/2026",
        "chairperson": "Bà Phan Thị Phát (Tổng Giám Đốc)",
        "secretary": "Bà Lê Thu Thảo",
        "participants": [
            "Bà Phan Thị Phát - Tổng Giám Đốc",
            "Ông Đặng Minh Trí - Trưởng Phòng Kinh Doanh",
            "Ông Phạm Đức Huy - Trưởng Phòng Kỹ Thuật"
        ],
        "audio_source": "mic_only"
    }
    res_start = client.post("/api/meetings/start", json=start_payload_1)
    assert res_start.status_code == 200
    session_1 = res_start.json()
    sid_1 = session_1["session_id"]
    print("Session 1 created:", sid_1)

    # Thêm đoạn thoại
    t1 = {
        "speaker": "Bà Phan Thị Phát (Tổng Giám Đốc)",
        "text": "Yêu cầu Phòng Kinh Doanh hoàn tất hồ sơ hợp đồng 50 máy ion kiềm trước 17h ngày 12/11.",
        "timestamp": "09:05:00",
        "is_bookmark": True
    }
    res_t1 = client.post(f"/api/meetings/{sid_1}/transcript", json=t1)
    assert res_t1.status_code == 200

    # Thêm ghi chú nhanh
    res_note = client.post(f"/api/meetings/{sid_1}/note", json={"note": "Sếp nhấn mạnh kỷ luật deadline"})
    assert res_note.status_code == 200

    # Bookmark
    res_bm = client.post(f"/api/meetings/{sid_1}/bookmark", json={"custom_text": "Mốc chỉ đạo nóng của TGĐ"})
    assert res_bm.status_code == 200

    # Phân tích
    res_an = client.post(f"/api/meetings/{sid_1}/analyze")
    assert res_an.status_code == 200
    an_data = res_an.json()["analysis_state"]
    print("Option 1 Analysis Action Items count:", len(an_data.get("action_items", [])))

    # Xuất file Word Option 1
    res_exp1 = client.post(f"/api/meetings/{sid_1}/export-word", json={"include_internal": True})
    assert res_exp1.status_code == 200
    exp1_data = res_exp1.json()
    print("Option 1 Word file generated:", exp1_data["filename"])
    assert exp1_data["filename"].endswith(".docx")

    print("\n=== 3. Test Option 2 (Họp Đối Tác) Flow ===")
    start_payload_2 = {
        "mode": "option_2",
        "project_title": "Đàm phán Hợp đồng Cung cấp 60 Thiết bị Lọc nước Ion Kiềm iONPIA",
        "partner_name": "Công ty TNHH Đầu tư & Phát triển Tân Phát Đạt",
        "partner_reps": ["Ông Vũ Đình Toàn - Giám Đốc Dự Án"],
        "secretary": "Bà Lê Thu Thảo",
        "audio_source": "mic_system"
    }
    res_start2 = client.post("/api/meetings/start", json=start_payload_2)
    assert res_start2.status_code == 200
    sid_2 = res_start2.json()["session_id"]
    print("Session 2 created:", sid_2)

    # Thêm đoạn thoại đàm phán
    t2 = {
        "speaker": "Bà Hoàng Thị Nga (Trưởng BP Mua Sắm Tân Phát Đạt)",
        "text": "Chúng tôi đề nghị chiết khấu 10% và thời hạn thanh toán công nợ 30 ngày sau nghiệm thu.",
        "timestamp": "14:15:00",
        "is_bookmark": True
    }
    client.post(f"/api/meetings/{sid_2}/transcript", json=t2)
    res_an2 = client.post(f"/api/meetings/{sid_2}/analyze")
    assert res_an2.status_code == 200
    an2_data = res_an2.json()["analysis_state"]
    conf2 = an2_data.get("confidential_internal", {})
    print("Option 2 Deal Score:", conf2.get("deal_score"))

    # Xuất bản Nội Bộ (Full A + B + C)
    res_exp2_full = client.post(f"/api/meetings/{sid_2}/export-word", json={"include_internal": True})
    assert res_exp2_full.status_code == 200
    print("Option 2 Internal Word file:", res_exp2_full.json()["filename"])

    # Xuất bản Đối Tác (Chỉ A + C)
    res_exp2_partner = client.post(f"/api/meetings/{sid_2}/export-word", json={"include_internal": False})
    assert res_exp2_partner.status_code == 200
    print("Option 2 Partner Word file:", res_exp2_partner.json()["filename"])

    print("\n=== 4. Test Demo Scenario Endpoints ===")
    res_demo1 = client.get("/api/meetings/demo-scenario/option_1")
    assert res_demo1.status_code == 200
    assert len(res_demo1.json()["dialogues"]) > 0

    res_demo2 = client.get("/api/meetings/demo-scenario/option_2")
    assert res_demo2.status_code == 200
    assert len(res_demo2.json()["dialogues"]) > 0

    print("\n=======================================================")
    print("  ALL TESTS PASSED SUCCESSFULLY! 100% OPERATIONAL.")
    print("=======================================================")

if __name__ == "__main__":
    test_full_system_flow()
