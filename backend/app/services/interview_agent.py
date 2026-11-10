import os
import json
import re
from typing import Dict, Any, List, Optional, AsyncGenerator
from google import genai
from google.genai import types
from app.config import settings

SOCRATIC_SYSTEM_PROMPT = """Bạn là Giảng viên hỏi thi vấn đáp trực tiếp 1-1 với sinh viên.
Mục tiêu: Đánh giá mức độ hiểu bài và tư duy của sinh viên bằng phương pháp gợi mở.

QUY TẮC BẮT BUỘC:
1. Giao tiếp bằng Tiếng Việt tự nhiên, đĩnh đạc, ấm áp.
2. CỰC KỲ NGẮN GỌN: Mỗi lượt nói CHỈ TỪ 1 ĐẾN 2 CÂU (tối đa 25 đến 30 từ). Chỉ tập trung vào đúng 1 câu hỏi hoặc 1 gợi ý. Tuyệt đối không nói dài dòng.
3. KHÔNG DÙNG MARKDOWN: Tuyệt đối không dùng dấu sao (*), thăng (#), ngoặc vuông, gạch đầu dòng.
4. CHIẾN THUẬT GỢI MỞ:
   - Khi mở đầu: Chào sinh viên và hỏi ngay khái niệm trọng tâm đầu tiên.
   - Khi sinh viên trả lời đúng: Khen ngắn ("Rất tốt!", "Chính xác!") rồi hỏi tiếp ý tiếp theo hoặc hỏi ví dụ.
   - Khi sinh viên trả lời sai hoặc thiếu: Đưa ra một câu gợi ý nhỏ để sinh viên tự nhận ra đáp án.
"""

class InterviewSession:
    def __init__(self, session_id: str, lesson_data: Dict[str, Any], client: Optional[genai.Client] = None):
        self.session_id = session_id
        self.lesson_data = lesson_data
        self.client = client or (genai.Client(api_key=settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else None)
        self.history: List[Dict[str, str]] = []
        self.stage: str = "welcome"  # welcome -> questioning -> concluding -> finished
        self.concept_index: int = 0
        self.turn_count: int = 0
        self.max_turns: int = 12

    def get_context_prompt(self) -> str:
        key_concepts = self.lesson_data.get("key_concepts", [])
        title = self.lesson_data.get("title", "Bài học")
        subject = self.lesson_data.get("subject", "Tổng quát")
        
        concepts_text = "\n".join([
            f"- Khái niệm {i+1}: {c.get('concept')} (Tóm tắt: {c.get('summary')})"
            for i, c in enumerate(key_concepts)
        ])
        
        goals_text = "\n".join([f"- {g}" for g in self.lesson_data.get("interview_goals", [])])

        return f"""THÔNG TIN BÀI HỌC KHẢO THI:
Chủ đề: {title} ({subject})
Các khái niệm trọng tâm:
{concepts_text}

Mục tiêu khảo bài:
{goals_text}

Tiến độ hiện tại: Khái niệm đang hướng tới là khái niệm số {min(self.concept_index + 1, len(key_concepts))}/{len(key_concepts)}.
Tổng số lượt trao đổi: {self.turn_count}/{self.max_turns}.
"""

    async def generate_response_stream(self, student_text: Optional[str] = None) -> AsyncGenerator[str, None]:
        """
        Nhận câu trả lời/nói của sinh viên, sinh phản hồi từ Interview Agent dạng stream từng token/cụm từ.
        """
        self.turn_count += 1
        key_concepts = self.lesson_data.get("key_concepts", [])

        if student_text:
            self.history.append({"role": "user", "content": student_text})

        # Xây dựng prompt
        context = self.get_context_prompt()
        
        # Nếu chưa có lịch sử, khởi tạo câu chào và câu hỏi đầu tiên
        if not self.history:
            system_instruction = f"{SOCRATIC_SYSTEM_PROMPT}\n\n{context}\n\nNhiệm vụ: Chào sinh viên ngắn gọn, giới thiệu chủ đề {self.lesson_data.get('title')}, và đặt câu hỏi mở đầu về khái niệm đầu tiên."
            user_msg = "Thưa thầy/cô, em đã sẵn sàng bắt đầu buổi khảo bài ạ."
        else:
            system_instruction = f"{SOCRATIC_SYSTEM_PROMPT}\n\n{context}"
            user_msg = student_text or "..."

        full_response = ""
        
        # Kiểm tra nếu đã có Gemini API Key
        if self.client and settings.GEMINI_API_KEY:
            try:
                # Xây dựng contents từ history
                contents = []
                for h in self.history[-6:]:  # Lấy 6 lượt gần nhất để giữ context gọn
                    role = "model" if h["role"] == "assistant" else "user"
                    contents.append(types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=h["content"])]
                    ))
                if not contents:
                    contents.append(types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=user_msg)]
                    ))

                # Dùng gemini-flash-lite-latest: tốc độ < 1 giây, quota rộng, phản hồi tức thì
                response = await self.client.aio.models.generate_content(
                    model="gemini-flash-lite-latest",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.3,
                        max_output_tokens=80
                    )
                )

                if response.text:
                    clean_text = response.text.strip().replace("*", "").replace("#", "")
                    full_response = clean_text
                    yield clean_text

            except Exception as e:
                print(f"Lỗi gọi Gemini API: {e}")
                fallback = "Thầy đã nghe câu trả lời của em. Em có thể lấy một ví dụ cụ thể hơn được không?"
                full_response = fallback
                yield fallback
        else:
            # Chế độ mô phỏng khi chưa nhập GEMINI_API_KEY
            if not self.history or len(self.history) <= 1:
                mock_msg = f"Chào em! Hôm nay chúng ta sẽ ôn lại bài {self.lesson_data.get('title')}. Trước hết, em hãy cho thầy biết tính đóng gói trong OOP là gì và có lợi ích gì nhé?"
            else:
                mock_msg = "Rất tốt! Em đã nắm được ý chính. Vậy em hãy cho thầy một ví dụ thực tế về tính đa hình trong cuộc sống hoặc trong code nhé?"
            full_response = mock_msg
            yield mock_msg

        # Lưu lại câu trả lời của agent
        self.history.append({"role": "assistant", "content": full_response})

        # Cập nhật concept index ước lượng sau mỗi vài lượt
        if self.turn_count % 2 == 0 and self.concept_index < len(key_concepts) - 1:
            self.concept_index += 1

class InterviewManager:
    def __init__(self):
        self.sessions: Dict[str, InterviewSession] = {}

    def create_session(self, session_id: str, lesson_data: Dict[str, Any]) -> InterviewSession:
        session = InterviewSession(session_id, lesson_data)
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        return self.sessions.get(session_id)

    def remove_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

interview_manager = InterviewManager()
