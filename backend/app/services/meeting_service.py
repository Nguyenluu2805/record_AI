"""
Quản lý Phiên Họp Thời Gian Thực (Meeting Session Service)
CÔNG TY CỔ PHẦN TẬP ĐOÀN KIM LONG PHÁT
Thực thi luồng phân tích trực tiếp (Real-time Analysis) & Tích hợp Gemini LLM
"""

import os
import json
import asyncio
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types

from app.config import settings
from app.services.vocabulary import get_vocabulary_prompt, LEADERSHIP_MEMBERS
from app.services.prompts import (
    SYSTEM_PROMPT_OPTION_1,
    SYSTEM_PROMPT_OPTION_2,
    ANALYSIS_JSON_PROMPT_OPTION_1,
    ANALYSIS_JSON_PROMPT_OPTION_2
)
from app.services.docx_exporter import docx_exporter

class MeetingSession:
    def __init__(self, session_id: str, mode: str = "option_1", metadata: Optional[Dict[str, Any]] = None):
        self.session_id = session_id
        self.mode = mode  # "option_1" (Họp Nội Bộ) hoặc "option_2" (Họp Đối Tác)
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.status = "in_progress"  # "in_progress", "paused", "completed"
        
        # Danh sách các đoạn thoại trực tiếp
        self.transcripts: List[Dict[str, Any]] = []
        # Ghi chú nhanh của Thư ký
        self.secretary_notes: List[Dict[str, Any]] = []
        # Các mốc bookmark nóng ⭐
        self.hot_bookmarks: List[Dict[str, Any]] = []
        
        # Kết quả phân tích trực tiếp (Live State)
        self.analysis_state: Dict[str, Any] = self._init_default_analysis()

    def _init_default_analysis(self) -> Dict[str, Any]:
        """Khởi tạo cấu trúc dữ liệu ban đầu cho bản phân tích tùy theo Option"""
        if self.mode == "option_1":
            return {
                "meeting_title": self.metadata.get("title", "Cuộc họp Giao ban Nội bộ"),
                "summary_goals": [],
                "leader_directions": [],
                "department_reports": [],
                "speech_analytics": [],
                "agreed_issues": [],
                "pending_issues": [],
                "hot_bookmarks": [],
                "action_items": []
            }
        else:
            return {
                "project_title": self.metadata.get("project_title", "Cuộc họp Đàm phán Đối tác"),
                "partner_name": self.metadata.get("partner_name", "Đối tác / Khách hàng"),
                "customer_pain_points": [],
                "klp_proposals": [],
                "commercial_terms": [],
                "confidential_internal": {
                    "deal_score": 7.0,
                    "deal_score_explanation": "Đang theo dõi tiến trình đàm phán ban đầu...",
                    "buying_signals": [],
                    "objections_and_red_flags": [],
                    "partner_speakers_analysis": []
                },
                "follow_up_plan": []
            }

    def add_transcript_segment(self, speaker: str, text: str, timestamp: Optional[str] = None, is_bookmark: bool = False, note: str = "") -> Optional[Dict[str, Any]]:
        """Thêm một đoạn thoại mới khi một người vừa nói xong (lọc bỏ tiếng ồn/khoảng lặng)"""
        if not text or not str(text).strip():
            return None
        clean_text = str(text).strip()
        noise_markers = ["[tiếng ồn]", "tiếng ồn", "[im lặng]", "im lặng", "[tiếng thở]", "noise", "silence", "[âm thanh]"]
        if clean_text.lower() in noise_markers or (clean_text.startswith("[") and clean_text.endswith("]")) or len(clean_text) < 2:
            return None

        ts = timestamp or datetime.now().strftime("%H:%M:%S")
        segment = {
            "id": len(self.transcripts) + 1,
            "speaker": speaker,
            "text": clean_text,
            "timestamp": ts,
            "is_bookmark": is_bookmark,
            "note": note
        }
        self.transcripts.append(segment)
        
        if is_bookmark:
            self.hot_bookmarks.append({
                "timestamp": ts,
                "speaker": speaker,
                "content": text
            })
            
        if note:
            self.secretary_notes.append({
                "timestamp": ts,
                "note": note
            })

        # Tự động cập nhật tỷ lệ nói sơ bộ
        self._calculate_speech_ratios()
        return segment

    def mark_bookmark(self, transcript_id: Optional[int] = None, custom_text: str = "") -> Dict[str, Any]:
        """Thư ký đánh dấu trọng tâm từng đoạn phát biểu (hỗ trợ toggle và chọn đoạn text)"""
        ts = datetime.now().strftime("%H:%M:%S")
        target = None

        if transcript_id is not None:
            for t in self.transcripts:
                if t.get("id") == transcript_id:
                    target = t
                    break
            if not target and 1 <= transcript_id <= len(self.transcripts):
                target = self.transcripts[transcript_id - 1]
        elif self.transcripts:
            target = self.transcripts[-1]

        if target:
            # Nếu đoạn này đã được đánh dấu rồi và không có custom_text mới -> toggle off
            if target.get("is_bookmark") and not custom_text:
                target["is_bookmark"] = False
                target_id = target.get("id")
                self.hot_bookmarks = [
                    bm for bm in self.hot_bookmarks 
                    if not (bm.get("transcript_id") == target_id or (bm.get("speaker") == target.get("speaker") and bm.get("content") == target.get("text")))
                ]
                if "hot_bookmarks" in self.analysis_state:
                    self.analysis_state["hot_bookmarks"] = self.hot_bookmarks
                return {
                    "is_bookmark": False,
                    "transcript_id": target.get("id"),
                    "speaker": target.get("speaker"),
                    "content": target.get("text"),
                    "hot_bookmarks": self.hot_bookmarks
                }
            else:
                # Đánh dấu đoạn này
                target["is_bookmark"] = True
                content = custom_text.strip() if custom_text.strip() else target.get("text", "")
                speaker = target.get("speaker", "Chủ trì / Đại biểu")
                target_id = target.get("id")

                # Cập nhật hoặc thêm mới vào hot_bookmarks
                existing = next((bm for bm in self.hot_bookmarks if bm.get("transcript_id") == target_id), None)
                if existing:
                    existing["content"] = content
                    existing["timestamp"] = ts
                else:
                    bm_item = {
                        "transcript_id": target_id,
                        "timestamp": target.get("timestamp", ts),
                        "speaker": speaker,
                        "content": content
                    }
                    self.hot_bookmarks.append(bm_item)

                if "hot_bookmarks" in self.analysis_state:
                    self.analysis_state["hot_bookmarks"] = self.hot_bookmarks

                return {
                    "is_bookmark": True,
                    "transcript_id": target_id,
                    "speaker": speaker,
                    "content": content,
                    "bookmark": bm_item if not existing else existing,
                    "hot_bookmarks": self.hot_bookmarks
                }

        # Nếu chưa có đoạn thoại nào nhưng thư ký bấm đánh dấu chung
        bm_item = {
            "transcript_id": None,
            "timestamp": ts,
            "speaker": "Chủ trì / Thư ký",
            "content": custom_text or "Ý kiến chỉ đạo quan trọng cần theo dõi"
        }
        self.hot_bookmarks.append(bm_item)
        if "hot_bookmarks" in self.analysis_state:
            self.analysis_state["hot_bookmarks"] = self.hot_bookmarks
        return {
            "is_bookmark": True,
            "transcript_id": None,
            "bookmark": bm_item,
            "hot_bookmarks": self.hot_bookmarks
        }

    def add_secretary_note(self, note_text: str) -> Dict[str, Any]:
        """Thư ký gõ ghi chú nhanh trong lúc họp"""
        ts = datetime.now().strftime("%H:%M:%S")
        note_obj = {
            "timestamp": ts,
            "note": note_text
        }
        self.secretary_notes.append(note_obj)
        return note_obj

    def delete_transcript_segment(self, transcript_id: Any) -> bool:
        """Xóa một đoạn thoại dư thừa hoặc nhận diện sai khỏi danh sách chữ thoại"""
        initial_len = len(self.transcripts)
        t_id_str = str(transcript_id)
        
        # Lọc bỏ segment có id trùng khớp
        self.transcripts = [
            t for t in self.transcripts 
            if str(t.get("id")) != t_id_str
        ]
        
        # Nếu có trong hot_bookmarks cũng xóa bỏ
        self.hot_bookmarks = [
            bm for bm in self.hot_bookmarks 
            if str(bm.get("transcript_id")) != t_id_str
        ]
        if "hot_bookmarks" in self.analysis_state:
            self.analysis_state["hot_bookmarks"] = self.hot_bookmarks

        # Tính toán lại tỷ lệ phát biểu
        self._calculate_speech_ratios()
        return len(self.transcripts) < initial_len

    def _calculate_speech_ratios(self):
        """Tính toán tỷ lệ phần trăm thời lượng phát biểu theo số từ"""
        if not self.transcripts:
            return
            
        speaker_words: Dict[str, int] = {}
        total_words = 0
        for t in self.transcripts:
            spk = t["speaker"]
            words = len(t["text"].split())
            speaker_words[spk] = speaker_words.get(spk, 0) + words
            total_words += words
            
        if total_words == 0:
            return

        analytics = []
        for spk, words in speaker_words.items():
            pct = round((words / total_words) * 100)
            analytics.append({
                "speaker": spk,
                "ratio_percent": pct,
                "key_points": f"Đã đóng góp {words} từ thảo luận.",
                "attitude": "Tích cực",
                "contribution_eval": "Đạt yêu cầu"
            })
            
        if self.mode == "option_1" and "speech_analytics" in self.analysis_state:
            # Giữ lại các chi tiết phân tích sâu nếu đã có
            existing_evals = {item["speaker"]: item for item in self.analysis_state.get("speech_analytics", [])}
            for a in analytics:
                if a["speaker"] in existing_evals:
                    a["key_points"] = existing_evals[a["speaker"]].get("key_points", a["key_points"])
                    a["attitude"] = existing_evals[a["speaker"]].get("attitude", a["attitude"])
                    a["contribution_eval"] = existing_evals[a["speaker"]].get("contribution_eval", a["contribution_eval"])
            self.analysis_state["speech_analytics"] = analytics

    async def run_ai_analysis(self) -> Dict[str, Any]:
        """
        Gọi Gemini AI để phân tích trực tiếp toàn bộ dữ liệu họp tính đến hiện tại.
        Nếu API có sự cố, tự động dùng Fallback Parser để giao diện không bị gián đoạn.
        """
        if not self.transcripts:
            return self.analysis_state

        transcript_text = "\n".join([
            f"[{t['timestamp']}] {t['speaker']} (⭐ Bookmark: {t['is_bookmark']}): {t['text']}"
            for t in self.transcripts
        ])
        
        notes_text = "\n".join([f"- [{n['timestamp']}] {n['note']}" for n in self.secretary_notes]) or "Không có ghi chú thêm."
        
        vocab_prompt = get_vocabulary_prompt()

        if self.mode == "option_1":
            system_instruction = f"{SYSTEM_PROMPT_OPTION_1}\n\n{vocab_prompt}"
            user_prompt = f"""Dưới đây là biên bản chữ thoại đang chạy trực tiếp và ghi chú của Thư ký:
=== CHỮ THOẠI TRỰC TIẾP ===
{transcript_text}

=== GHI CHÚ NHANH CỦA THƯ KÝ ===
{notes_text}

{ANALYSIS_JSON_PROMPT_OPTION_1}
"""
        else:
            system_instruction = f"{SYSTEM_PROMPT_OPTION_2}\n\n{vocab_prompt}"
            user_prompt = f"""Dưới đây là biên bản chữ thoại đang chạy trực tiếp và ghi chú của Thư ký trong cuộc đàm phán:
=== CHỮ THOẠI TRỰC TIẾP ===
{transcript_text}

=== GHI CHÚ NHANH CỦA THƯ KÝ ===
{notes_text}

{ANALYSIS_JSON_PROMPT_OPTION_2}
"""

        # Thử gọi Gemini AI
        api_key = settings.GEMINI_API_KEY
        client = genai.Client(api_key=api_key) if api_key else None
        parsed_result = None

        if client:
            try:
                response = await asyncio.wait_for(
                    client.aio.models.generate_content(
                        model=settings.GEMINI_MODEL,
                        contents=[
                            types.Content(
                                role="user",
                                parts=[types.Part.from_text(text=user_prompt)]
                            )
                        ],
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.2,
                            max_output_tokens=2048,
                            response_mime_type="application/json"
                        )
                    ),
                    timeout=15.0
                )
                if response.text:
                    cleaned_json = response.text.strip()
                    # Loại bỏ markdown backticks nếu model vô tình sinh ra
                    cleaned_json = re.sub(r"^```json\s*", "", cleaned_json)
                    cleaned_json = re.sub(r"\s*```$", "", cleaned_json)
                    parsed_result = json.loads(cleaned_json)
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    print("[Meeting AI] Gemini API đạt giới hạn Quota Free Tier (429). Hệ thống tự động kích hoạt Rule-based Intelligent Engine để phân tích mượt mà.")
                else:
                    print(f"Lỗi gọi Gemini AI phân tích (chuyển sang fallback): {e}")

        # Nếu không có API hoặc parse lỗi, áp dụng cơ chế phân tích thông minh dựa trên quy luật
        if not parsed_result:
            parsed_result = self._fallback_rule_based_analysis()

        # Cập nhật vào state
        if parsed_result:
            self.analysis_state = parsed_result
            # Luôn giữ lại danh sách bookmark nóng đã đánh dấu
            self.analysis_state["hot_bookmarks"] = self.hot_bookmarks
            self._calculate_speech_ratios()

        return self.analysis_state

    def _fallback_rule_based_analysis(self) -> Dict[str, Any]:
        """Cơ chế trích xuất dự phòng thông minh khi offline hoặc hết quota API"""
        if self.mode == "option_1":
            directions = []
            dept_reports = []
            agreed = []
            pending = []
            action_items = []

            for t in self.transcripts:
                spk = t["speaker"]
                text = t["text"]
                if "Tổng Giám Đốc" in spk or "Chủ tịch" in spk or "Lãnh đạo" in spk:
                    directions.append(f"Chỉ đạo: {text}")
                    if "đồng ý" in text.lower() or "duyệt" in text.lower() or "chốt" in text.lower():
                        agreed.append(text)
                    if "tuần sau" in text.lower() or "họp phiên" in text.lower():
                        pending.append("Vấn đề cần họp phiên chuyên đề riêng vào tuần tới.")
                else:
                    dept_reports.append({"speaker": spk, "content": text})

                # Trích xuất action item
                if any(w in text.lower() for w in ["phụ trách", "hoàn thành", "trước ngày", "deadline", "chốt hợp đồng", "nghiệm thu"]):
                    action_items.append({
                        "stt": f"0{len(action_items)+1}",
                        "task": text[:120] + "...",
                        "pic": spk.split("(")[0].strip(),
                        "coordinating_dept": "Phòng ban liên quan",
                        "deadline": "Theo chỉ đạo cuộc họp",
                        "kpi": "Báo cáo / Nghiệm thu hoàn thành"
                    })

            # Summary goals: trích xuất nếu có chỉ đạo hoặc để rỗng []
            summary_goals = []
            if directions:
                summary_goals = [d.replace("Chỉ đạo: ", "") for d in directions[:3]]

            return {
                "meeting_title": self.metadata.get("title", "Cuộc họp Giao ban Nội bộ"),
                "summary_goals": summary_goals,
                "leader_directions": directions,
                "department_reports": dept_reports,
                "speech_analytics": [],
                "agreed_issues": agreed,
                "pending_issues": pending,
                "hot_bookmarks": self.hot_bookmarks,
                "action_items": action_items
            }
        else:
            pains = []
            proposals = []
            commercial_terms = []
            follow_up = []

            for t in self.transcripts:
                spk = t["speaker"]
                text = t["text"]
                if any(w in text.lower() for w in ["cần", "yêu cầu", "muốn", "tiêu chuẩn"]):
                    pains.append(text[:120])
                if any(w in text.lower() for w in ["đề xuất", "chính sách", "cam kết", "chiết khấu"]):
                    proposals.append(text[:120])
                if any(w in text.lower() for w in ["giá", "thanh toán", "tiến độ", "bảo hành", "phạt"]):
                    commercial_terms.append({
                        "term_name": "Điều khoản phát sinh",
                        "klp_offer": text[:80],
                        "partner_demand": "Ghi nhận theo đối thoại",
                        "status": "Đang thảo luận"
                    })
                if any(w in text.lower() for w in ["gửi", "báo cáo", "trình", "ngày mai"]):
                    follow_up.append({
                        "party": spk.split("(")[0].strip(),
                        "task": text[:120],
                        "pic": spk.split("(")[0].strip(),
                        "deadline": "Theo thống nhất",
                        "priority": "Quan trọng"
                    })

            return {
                "project_title": self.metadata.get("project_title", "Cuộc họp Đàm phán Đối tác"),
                "partner_name": self.metadata.get("partner_name", "Đối tác / Khách hàng"),
                "customer_pain_points": pains,
                "klp_proposals": proposals,
                "commercial_terms": commercial_terms,
                "confidential_internal": {
                    "deal_score": 7.0,
                    "deal_score_explanation": "Đang theo dõi diễn biến thực tế cuộc đàm phán.",
                    "buying_signals": [],
                    "objections_and_red_flags": [],
                    "partner_speakers_analysis": []
                },
                "follow_up_plan": follow_up
            }

    def save_transcript_text(self) -> Dict[str, Any]:
        """
        Lưu trữ toàn bộ đoạn text chữ thoại nguyên văn bóc tách từ file ghi âm vào máy tính.
        Định dạng text chuẩn có mốc thời gian [HH:MM:SS], tên người nói và ghi chú.
        """
        os.makedirs(settings.TRANSCRIPTS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        mode_label = "NoiBo" if self.mode == "option_1" else "DoiTac"
        filename = f"ChuThoai_{mode_label}_{self.session_id}_{timestamp}.txt"
        file_path = os.path.join(settings.TRANSCRIPTS_DIR, filename)

        title = self.metadata.get("title") or self.metadata.get("project_title") or "Cuộc họp Tập đoàn Kim Long Phát"
        chairperson = self.metadata.get("chairperson") or "Chủ trì cuộc họp"
        secretary = self.metadata.get("secretary") or "Thư ký cuộc họp"
        date_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        lines = []
        lines.append("=" * 80)
        lines.append("CÔNG TY CỔ PHẦN TẬP ĐOÀN KIM LONG PHÁT")
        lines.append("BĂNG GHI CHỮ THOẠI NGUYÊN VĂN BÓC TÁCH TỪ FILE GHI ÂM CUỘC HỌP")
        lines.append("=" * 80)
        lines.append(f"1. Tên cuộc họp: {title}")
        lines.append(f"2. Thời gian tạo bản ghi: {date_str}")
        lines.append(f"3. Chủ trì: {chairperson}")
        lines.append(f"4. Thư ký ghi nhận: {secretary}")
        if self.metadata.get("partner_name"):
            lines.append(f"5. Đơn vị đối tác: {self.metadata.get('partner_name')}")
        lines.append(f"6. Tổng số lượt phát biểu: {len(self.transcripts)}")
        if self.metadata.get("audio_recording_file"):
            lines.append(f"7. File ghi âm gốc liên kết: {self.metadata.get('audio_recording_file')}")
        lines.append("=" * 80)
        lines.append("")
        lines.append("NỘI DUNG CHỮ THOẠI CHI TIẾT THEO TIẾN TRÌNH THỜI GIAN:")
        lines.append("-" * 80)

        if not self.transcripts:
            lines.append("(Không có dữ liệu thoại được ghi nhận)")
        else:
            for idx, t in enumerate(self.transcripts, 1):
                ts = t.get("timestamp", "00:00:00")
                spk = t.get("speaker", "Người phát biểu")
                txt = t.get("text", "").strip()
                bm = " [TRỌNG TÂM]" if t.get("is_bookmark") else ""
                lines.append(f"[{ts}] {spk}{bm}:")
                lines.append(f"  {txt}")
                if t.get("note"):
                    lines.append(f"  -> Ghi chú thư ký: {t.get('note')}")
                lines.append("")

        if self.secretary_notes:
            lines.append("-" * 80)
            lines.append("CÁC GHI CHÚ NHANH CỦA THƯ KÝ TRONG CUỘC HỌP:")
            for n in self.secretary_notes:
                lines.append(f"- [{n.get('timestamp')}] {n.get('note')}")
            lines.append("")

        lines.append("=" * 80)
        lines.append("KẾT THÚC BẢN GHI CHỮ THOẠI CUỘC HỌP")
        lines.append("=" * 80)

        content = "\n".join(lines)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.metadata["transcript_text_file"] = filename
        self.metadata["transcript_text_path"] = file_path

        # Tự động sao chép vào thư mục do người dùng chọn nếu có
        storage_dir = self.metadata.get("storage_dir")
        if storage_dir and os.path.exists(file_path):
            import shutil
            try:
                os.makedirs(storage_dir, exist_ok=True)
                shutil.copy2(file_path, os.path.join(storage_dir, filename))
            except Exception:
                pass

        return {
            "filename": filename,
            "file_path": file_path,
            "download_url": f"/api/download/transcripts/{filename}",
            "text_content": content
        }

    def export_word(self, include_internal: bool = True) -> str:
        """Xuất ra file Word .docx chuẩn hành chính KLP kèm phụ lục chữ thoại"""
        if self.mode == "option_1":
            file_path = docx_exporter.export_option_1(self.metadata, self.analysis_state, transcripts=self.transcripts)
        else:
            file_path = docx_exporter.export_option_2(self.metadata, self.analysis_state, include_internal_confidential=include_internal, transcripts=self.transcripts)

        filename = os.path.basename(file_path)
        self.metadata["exported_word_file"] = filename
        self.metadata["exported_word_path"] = file_path

        # Tự động sao chép vào thư mục người dùng chọn nếu có
        storage_dir = self.metadata.get("storage_dir")
        if storage_dir and os.path.exists(file_path):
            import shutil
            try:
                os.makedirs(storage_dir, exist_ok=True)
                shutil.copy2(file_path, os.path.join(storage_dir, filename))
            except Exception:
                pass

        return file_path

    def get_all_files(self) -> List[Dict[str, Any]]:
        """Lấy danh sách toàn bộ các file đã tạo trong phiên họp (Audio, Text, Word)"""
        files = []
        import shutil

        storage_dir = self.metadata.get("storage_dir")
        if storage_dir:
            try:
                os.makedirs(storage_dir, exist_ok=True)
            except Exception:
                pass

        # 1. File Ghi âm (.webm / .wav)
        audio_filename = self.metadata.get("audio_recording_file")
        audio_path = self.metadata.get("audio_recording_path")
        if audio_path and os.path.exists(audio_path):
            size_bytes = os.path.getsize(audio_path)
            size_mb = round(size_bytes / (1024 * 1024), 2)
            if storage_dir and not os.path.exists(os.path.join(storage_dir, audio_filename)):
                try:
                    shutil.copy2(audio_path, os.path.join(storage_dir, audio_filename))
                except Exception:
                    pass
            files.append({
                "type": "audio",
                "label": "Tệp Ghi Âm Gốc Cuộc Họp",
                "format": "WEBM",
                "filename": audio_filename,
                "file_path": audio_path,
                "size_display": f"{size_mb} MB",
                "download_url": f"/api/download/recordings/{audio_filename}"
            })

        # 2. File Chữ thoại nguyên văn (.txt)
        txt_filename = self.metadata.get("transcript_text_file")
        txt_path = self.metadata.get("transcript_text_path")
        if txt_path and os.path.exists(txt_path):
            size_bytes = os.path.getsize(txt_path)
            size_kb = round(size_bytes / 1024, 1)
            if storage_dir and not os.path.exists(os.path.join(storage_dir, txt_filename)):
                try:
                    shutil.copy2(txt_path, os.path.join(storage_dir, txt_filename))
                except Exception:
                    pass
            files.append({
                "type": "text",
                "label": "Bản Text Chữ Thoại Bóc Tách Nguyên Văn",
                "format": "TXT",
                "filename": txt_filename,
                "file_path": txt_path,
                "size_display": f"{size_kb} KB",
                "download_url": f"/api/download/transcripts/{txt_filename}"
            })

        # 3. File Word (.docx)
        word_filename = self.metadata.get("exported_word_file")
        word_path = self.metadata.get("exported_word_path")
        if word_path and os.path.exists(word_path):
            size_bytes = os.path.getsize(word_path)
            size_kb = round(size_bytes / 1024, 1)
            if storage_dir and not os.path.exists(os.path.join(storage_dir, word_filename)):
                try:
                    shutil.copy2(word_path, os.path.join(storage_dir, word_filename))
                except Exception:
                    pass
            files.append({
                "type": "docx",
                "label": "Biên Bản Cuộc Họp Chuẩn Doanh Nghiệp KLP",
                "format": "DOCX",
                "filename": word_filename,
                "file_path": word_path,
                "size_display": f"{size_kb} KB",
                "download_url": f"/api/download/{word_filename}"
            })

        return files

class MeetingManager:
    def __init__(self):
        self.sessions: Dict[str, MeetingSession] = {}

    def create_session(self, mode: str = "option_1", metadata: Optional[Dict[str, Any]] = None) -> MeetingSession:
        session_id = f"klp_{mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.sessions)+1}"
        session = MeetingSession(session_id=session_id, mode=mode, metadata=metadata)
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[MeetingSession]:
        return self.sessions.get(session_id)

meeting_manager = MeetingManager()
