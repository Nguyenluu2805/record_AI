"""
Dịch vụ Nhận diện Giọng nói Tiếng Việt Trực tiếp & Xử lý File Ghi Âm (Speech-to-Text & Diarization)
Tập đoàn Kim Long Phát
Tích hợp Gemini Audio Multimodal API và Từ điển chuyên ngành
"""

import io
import os
import re
import wave
import json
import time
import asyncio
from typing import Optional, List, Dict, Any
from google import genai
from google.genai import types
from app.config import settings
from app.services.vocabulary import get_vocabulary_prompt

def detect_audio_mime(data: bytes, filename: Optional[str] = None) -> str:
    """Xác định MIME type chính xác của file hoặc mẩu âm thanh"""
    if filename:
        ext = os.path.splitext(filename.lower())[1]
        ext_map = {
            ".wav": "audio/wav",
            ".mp3": "audio/mp3",
            ".m4a": "audio/mp4",
            ".mp4": "audio/mp4",
            ".webm": "audio/webm",
            ".ogg": "audio/ogg",
            ".aac": "audio/aac",
            ".flac": "audio/flac"
        }
        if ext in ext_map:
            return ext_map[ext]

    if data.startswith(b'RIFF'):
        return 'audio/wav'
    elif data.startswith(b'\x1aE\xdf\xa3'):
        return 'audio/webm'
    elif data.startswith(b'OggS'):
        return 'audio/ogg'
    elif data.startswith(b'ID3') or data.startswith(b'\xff\xfb') or data.startswith(b'\xff\xf3') or data.startswith(b'\xff\xf2'):
        return 'audio/mp3'
    elif len(data) > 8 and data[4:8] == b'ftyp':
        return 'audio/mp4'
    return 'audio/wav'

def ensure_wav_bytes(audio_bytes: bytes, sample_rate: int = 16000, channels: int = 1, sampwidth: int = 2) -> bytes:
    """Đảm bảo audio_bytes có header RIFF WAV hợp lệ nếu là raw PCM"""
    if audio_bytes.startswith(b'RIFF') or audio_bytes.startswith(b'\x1aE\xdf\xa3') or audio_bytes.startswith(b'ID3') or audio_bytes.startswith(b'OggS'):
        return audio_bytes
    
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_bytes)
    return buf.getvalue()

class STTService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.quota_cooldown_until = 0

    async def transcribe_audio_chunk(self, audio_bytes: bytes, sample_rate: int = 16000, participants: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Nhận diện giọng nói tiếng Việt từ mẩu âm thanh ngắn trực tiếp bằng Gemini Audio.
        Trả về dict: {"text": "...", "suggested_speaker": "..."}
        """
        if not self.client or not audio_bytes:
            return {"text": "", "suggested_speaker": ""}

        if time.time() < self.quota_cooldown_until:
            return {"text": "", "suggested_speaker": ""}

        try:
            mime_type = detect_audio_mime(audio_bytes)
            if mime_type == 'audio/wav':
                data_to_send = ensure_wav_bytes(audio_bytes, sample_rate=sample_rate)
            else:
                data_to_send = audio_bytes

            # Nếu âm thanh quá ngắn (< 0.4s), bỏ qua để tránh nhiễu
            if len(data_to_send) < 44 + sample_rate * 2 * 0.4 and mime_type == 'audio/wav':
                return {"text": "", "suggested_speaker": ""}

            participants_str = ", ".join(participants) if participants else "Các thành viên trong phòng họp"
            vocab_context = get_vocabulary_prompt()

            prompt = f"""Bạn là Thư ký AI phụ trách nghe nhận diện giọng nói tiếng Việt trong cuộc họp của CÔNG TY CỔ PHẦN TẬP ĐOÀN KIM LONG PHÁT.
{vocab_context}

Nhiệm vụ:
Chuyển đoạn âm thanh thành văn bản tiếng Việt chính xác nhất. Chú ý các tên riêng (Kim Long Phát, iONPIA, SPE/PEM, Nam Sài Gòn...) và các số liệu tiền tệ, %, ngày tháng.
Nếu đoạn âm thanh chỉ là tiếng ồn, im lặng, tiếng thở hoặc không có tiếng nói người rõ ràng, hãy trả về rỗng: ""
Tuyệt đối KHÔNG tự đoán tên người nói, KHÔNG thêm chú thích ngoài lề, chỉ trả về nội dung người nói phát biểu.
"""

            response = await self.client.aio.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=[
                    types.Part.from_bytes(
                        data=data_to_send,
                        mime_type=mime_type
                    ),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=500
                )
            )

            if response.text:
                raw_text = response.text.strip().replace('"', '').replace("'", "")
                
                # Danh sách lọc triệt để tiếng ồn và câu rác
                noise_markers = [
                    "không nghe thấy", "không có âm thanh", "im lặng", "âm thanh không rõ",
                    "tiếng ồn", "[tiếng ồn]", "tiếng thở", "[tiếng thở]", "[âm thanh]",
                    "không có tiếng nói", "[tiếng động]", "noise", "silence", "[im lặng]"
                ]
                
                lower_text = raw_text.lower()
                if any(phrase in lower_text for phrase in noise_markers) or len(raw_text) < 2:
                    return {"text": "", "suggested_speaker": ""}

                # Loại bỏ tiền tố [Tên]: nếu có
                content_text = raw_text
                if ":" in raw_text and ("[" in raw_text or "Ông" in raw_text or "Bà" in raw_text):
                    parts = raw_text.split(":", 1)
                    content_text = parts[1].strip()

                if any(phrase in content_text.lower() for phrase in noise_markers) or len(content_text) < 2:
                    return {"text": "", "suggested_speaker": ""}

                return {
                    "text": content_text,
                    "suggested_speaker": ""
                }
            return {"text": "", "suggested_speaker": ""}
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                self.quota_cooldown_until = time.time() + 60.0
                print(f"[STT] Gemini API đạt giới hạn Quota Free Tier (429). Tự động tạm dừng gửi audio chunk 60s, hệ thống tiếp tục nhận diện qua Web Speech API và chuyển văn bản.")
            else:
                print(f"Lỗi nhận dạng âm thanh Gemini STT: {e}")
            return {"text": "", "suggested_speaker": ""}

    async def transcribe_audio_file(self, audio_bytes: bytes, filename: str, participants: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Nhận diện toàn bộ một file ghi âm cuộc họp (.mp3, .wav, .m4a, .webm, ...)
        Tự động phân tách người nói (Speaker Diarization) và mốc thời gian [HH:MM:SS].
        Trả về danh sách các lượt thoại chuẩn để đưa vào biên bản.
        """
        if not self.client or not audio_bytes:
            return []

        try:
            mime_type = detect_audio_mime(audio_bytes, filename=filename)
            participants_str = ", ".join(participants) if participants else "Lãnh đạo và các bộ phận tham dự"
            vocab_context = get_vocabulary_prompt()

            prompt = f"""Bạn là Trợ lý Thư ký AI cao cấp của CÔNG TY CỔ PHẦN TẬP ĐOÀN KIM LONG PHÁT.
{vocab_context}
Danh sách người tham dự cuộc họp: {participants_str}

Nhiệm vụ:
Nghe toàn bộ file ghi âm cuộc họp đính kèm và chuyển đổi thành văn bản tiếng Việt chi tiết theo từng lượt đối thoại theo trình tự thời gian (Speaker Diarization).
Hãy nhận diện chuẩn xác tên người nói dựa trên danh bạ Kim Long Phát được cung cấp.

YÊU CẦU ĐỊNH DẠNG ĐẦU RA:
Trả về DUY NHẤT một mảng JSON các đối tượng (không bọc code block markdown nếu có thể, hoặc bọc json):
[
  {{
    "timestamp": "00:00:15",
    "speaker": "Họ tên người phát biểu (kèm chức vụ nếu xác định được)",
    "text": "Nội dung người đó đã phát biểu chính xác từng câu chữ, số liệu",
    "is_bookmark": false
  }}
]
Nếu có đoạn chỉ đạo quan trọng, chốt số liệu hoặc yêu cầu quyết liệt của Lãnh đạo/Đối tác, đặt "is_bookmark": true.
"""

            response = await self.client.aio.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=[
                    types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type=mime_type
                    ),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=8192,
                    response_mime_type="application/json"
                )
            )

            if response.text:
                cleaned_text = response.text.strip()
                cleaned_text = re.sub(r"^```json\s*", "", cleaned_text)
                cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
                dialogues = json.loads(cleaned_text)
                if isinstance(dialogues, list):
                    return dialogues

            return []
        except Exception as e:
            print(f"Lỗi nhận dạng file âm thanh đầy đủ Gemini STT: {e}")
            return []

    async def transcribe_general_audio(self, audio_bytes: bytes, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Chuyển đổi âm thanh thành văn bản tiếng Việt thuần túy (General Speech-to-Text).
        Hỗ trợ cả thu âm trực tiếp và tải file ghi âm (.mp3, .wav, .m4a, .webm...).
        """
        if not self.client or not audio_bytes:
            return {"full_text": "", "segments": [], "word_count": 0}

        try:
            mime_type = detect_audio_mime(audio_bytes, filename=filename)
            vocab_context = get_vocabulary_prompt()

            prompt = f"""Bạn là chuyên gia chuyển giọng nói tiếng Việt thành văn bản (Speech-to-Text) có độ chính xác cao nhất.
{vocab_context}

Nhiệm vụ:
Nghe file âm thanh và chuyển đổi toàn bộ thành văn bản tiếng Việt chuẩn ngữ pháp, đầy đủ dấu câu, viết hoa danh từ riêng, số liệu, tiền tệ chính xác.
Đồng thời chia các đoạn thoại theo mốc thời gian [HH:MM:SS].

YÊU CẦU ĐỊNH DẠNG ĐẦU RA:
Trả về DUY NHẤT một đối tượng JSON:
{{
  "full_text": "Toàn bộ nội dung văn bản liền mạch hoàn chỉnh, đúng ngữ pháp tiếng Việt...",
  "segments": [
    {{
      "timestamp": "00:00:05",
      "speaker": "Người phát biểu",
      "text": "Nội dung đoạn nói..."
    }}
  ]
}}
"""

            response = await self.client.aio.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=[
                    types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type=mime_type
                    ),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=8192,
                    response_mime_type="application/json"
                )
            )

            if response.text:
                cleaned_text = response.text.strip()
                cleaned_text = re.sub(r"^```json\s*", "", cleaned_text)
                cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
                result = json.loads(cleaned_text)
                
                full_text = result.get("full_text", "")
                segments = result.get("segments", [])
                
                if not full_text and segments:
                    full_text = " ".join([s.get("text", "") for s in segments])
                    
                word_count = len(full_text.split()) if full_text else 0
                return {
                    "full_text": full_text,
                    "segments": segments,
                    "word_count": word_count
                }

            return {"full_text": "", "segments": [], "word_count": 0}
        except Exception as e:
            print(f"Lỗi chuyển giọng nói thành văn bản Gemini STT: {e}")
            return {"full_text": "", "segments": [], "word_count": 0}

stt_service = STTService()
