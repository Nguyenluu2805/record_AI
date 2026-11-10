import time
import threading
import re
import numpy as np
import onnxruntime as ort
from typing import Generator, List, Optional
from zerotts import ZeroTTS
from app.config import settings

def clean_tts_text(text: str) -> str:
    """Loại bỏ ký tự markdown, emoji, ký tự lạ để ZeroTTS đọc tự nhiên nhất"""
    if not text:
        return ""
    # Bỏ markdown như **, *, #, _, ~, `, >, -
    cleaned = re.sub(r'[\*#_~`>\-\[\]\(\)]', ' ', text)
    # Bỏ emoji và ký hiệu đặc biệt
    cleaned = re.sub(r'[^\w\s\.,\?!:;áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựíìỉĩịýỳỷỹỵđÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÍÌỈĨỊÝỲỶỸỴĐ]', ' ', cleaned)
    # Rút gọn dấu chấm lửng (...) và dấu lặp lại để tránh dừng ngắt quãng quá lâu
    cleaned = re.sub(r'\.{2,}', '.', cleaned)
    cleaned = re.sub(r',+', ',', cleaned)
    cleaned = re.sub(r'!+', '!', cleaned)
    cleaned = re.sub(r'\?+', '?', cleaned)
    # Chuẩn hóa khoảng trắng
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def split_sentences(text: str) -> List[str]:
    """Phân tách văn bản thành các câu tự nhiên theo dấu chấm, chấm hỏi, chấm than hoặc xuống dòng"""
    cleaned = clean_tts_text(text)
    if not cleaned:
        return []
    raw_sentences = re.split(r'(?<=[.?!;\n])\s+', cleaned.strip())
    sentences = []
    buf = ""
    for s in raw_sentences:
        s = s.strip()
        if not s:
            continue
        if buf:
            buf = f"{buf} {s}"
        else:
            buf = s
        
        # Gom các câu quá ngắn (< 5 từ) với câu tiếp theo để tránh mẩu âm thanh rời rạc
        if len(buf.split()) >= 5:
            sentences.append(buf)
            buf = ""
    if buf:
        if sentences and len(buf.split()) < 3:
            sentences[-1] = f"{sentences[-1]} {buf}"
        else:
            sentences.append(buf)
    return sentences

class TTSService:
    _instance: Optional['TTSService'] = None
    _lock = threading.Lock()

    def __init__(self):
        available_providers = ort.get_available_providers()
        print(f"ONNX Runtime Providers khả dụng: {available_providers}")
        
        # Sử dụng CPUExecutionProvider tối ưu 4 threads (nhanh hơn DirectML 1.5x và không bị trễ kernel launch)
        providers = ['CPUExecutionProvider']
        print("⚡ Kích hoạt CPU đa luồng tối ưu (intra_op_num_threads=4) cho ZeroTTS!")

        print(f"Đang khởi tạo ZeroTTS với providers: {providers}...")
        self.model = ZeroTTS.from_pretrained(
            "zeroweight-ai/ZeroTTS",
            providers=providers,
            intra_op_num_threads=4
        )
        print("Đang warmup mô hình ZeroTTS...")
        self.model.warmup()
        print("ZeroTTS đã sẵn sàng phục vụ.")
        self.default_voice = settings.DEFAULT_TTS_VOICE
        self.sample_rate = 48000

    @classmethod
    def get_instance(cls) -> 'TTSService':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def list_voices(self) -> List[str]:
        return self.model.list_voices()

    def synthesize_sentences_pcm(
        self,
        text: str,
        voice: Optional[str] = None,
        stop_event: Optional[threading.Event] = None
    ) -> Generator[tuple[bytes, bool, str], None, None]:
        """
        Sinh âm thanh theo từng câu hoàn chỉnh (Sentence-level Synthesis).
        Mỗi câu được sinh nguyên khối (non-streaming) để đạt 100% chất lượng phòng thu,
        ngữ điệu tiếng Việt tự nhiên, không bị méo tiếng hay khựng giật do micro-chunks.
        """
        selected_voice = voice or self.default_voice
        sentences = split_sentences(text)
        if not sentences:
            return

        total = len(sentences)
        for idx, sentence in enumerate(sentences):
            if stop_event and stop_event.is_set():
                print("TTS bị dừng do tín hiệu ngắt lời (barge-in).", flush=True)
                break

            try:
                t0 = time.time()
                audio = self.model.synthesize(sentence, voice=selected_voice)
                gen_time = time.time() - t0
                flat_audio = audio.flatten()
                audio_dur = flat_audio.size / self.sample_rate
                int16_audio = (np.clip(flat_audio, -1.0, 1.0) * 32767.0).astype(np.int16)
                pcm_bytes = int16_audio.tobytes()

                is_last = (idx == total - 1)
                print(f"🎙️ [TTS Câu {idx+1}/{total}] Sinh xong {audio_dur:.2f}s audio trong {gen_time:.2f}s: '{sentence}'", flush=True)
                yield (pcm_bytes, is_last, sentence)
            except Exception as e:
                print(f"Lỗi synthesize câu '{sentence}': {e}", flush=True)

    def synthesize_pcm_stream(
        self, 
        text: str, 
        voice: Optional[str] = None, 
        stop_event: Optional[threading.Event] = None
    ) -> Generator[bytes, None, None]:
        """
        Sinh âm thanh theo từng câu hoàn chỉnh (Sentence-level Synthesis).
        Mỗi câu nguyên khối đạt 100% chất lượng phòng thu, ngữ điệu tự nhiên.
        """
        for pcm_bytes, _, _ in self.synthesize_sentences_pcm(text, voice, stop_event):
            yield pcm_bytes

    def synthesize_full_pcm(self, text: str, voice: Optional[str] = None) -> bytes:
        selected_voice = voice or self.default_voice
        sanitized_text = clean_tts_text(text)
        if not sanitized_text:
            return b""
        audio = self.model.synthesize(sanitized_text, voice=selected_voice)
        flat_audio = audio.flatten()
        int16_audio = (np.clip(flat_audio, -1.0, 1.0) * 32767.0).astype(np.int16)
        return int16_audio.tobytes()

tts_service = TTSService.get_instance()
