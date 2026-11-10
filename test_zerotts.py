import time
import os
import sys

# Đảm bảo UTF-8 cho console Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from zerotts import ZeroTTS

def main():
    print("=== Đang tải mô hình ZeroTTS (zeroweight-ai/ZeroTTS) ===")
    start_load = time.time()
    tts = ZeroTTS.from_pretrained("zeroweight-ai/ZeroTTS")
    load_duration = time.time() - start_load
    print(f"-> Tải mô hình thành công trong: {load_duration:.2f} giây")

    # Liệt kê các giọng nói có sẵn
    voices = tts.list_voices()
    print(f"-> Các giọng đọc hỗ trợ ({len(voices)}): {voices}")

    test_text = "Xin chào các bạn! Hôm nay chúng ta sẽ cùng nhau ôn tập lại kiến thức bài học nhé. Em đã sẵn sàng chưa?"
    
    # Chọn voice đầu tiên hoặc voice mong muốn (ví dụ: maichi, namanh)
    selected_voice = "maichi" if "maichi" in voices else voices[0]
    print(f"-> Đang thử nghiệm sinh âm thanh với voice: '{selected_voice}'")
    print(f"-> Văn bản mẫu: \"{test_text}\"")

    start_synth = time.time()
    audio = tts.synthesize(test_text, voice=selected_voice)
    synth_duration = time.time() - start_synth
    print(f"-> Sinh âm thanh hoàn tất trong: {synth_duration:.2f} giây")

    # Lưu file âm thanh kiểm tra
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"test_{selected_voice}.wav")
    tts.save_audio(audio, out_path)
    print(f"-> Đã lưu file âm thanh thành công tại: {out_path}")

if __name__ == "__main__":
    main()
