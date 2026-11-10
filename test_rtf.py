import time
import sys
sys.stdout.reconfigure(encoding='utf-8')
from zerotts import ZeroTTS

text = 'Chào em, hôm nay chúng ta học bài nhé. Em đã chuẩn bị sẵn sàng chưa?'

for prov_name, prov in [('CPU', ['CPUExecutionProvider']), ('DirectML', ['DmlExecutionProvider', 'CPUExecutionProvider'])]:
    print(f"--- Đang đo lường {prov_name} ---")
    tts = ZeroTTS.from_pretrained('zeroweight-ai/ZeroTTS', providers=prov)
    tts.warmup()
    
    # Đo synthesize full
    t0 = time.time()
    audio = tts.synthesize(text, voice='maichi')
    synth_t = time.time() - t0
    audio_dur = len(audio) / 48000.0
    rtf = synth_t / audio_dur
    print(f"[{prov_name} Full]: Thời gian sinh: {synth_t:.2f}s | Thời lượng audio: {audio_dur:.2f}s | RTF: {rtf:.2f}x")

    # Đo streaming
    t0 = time.time()
    first_chunk_t = None
    chunks = 0
    for chunk in tts.synthesize_stream(text, voice='maichi'):
        if first_chunk_t is None:
            first_chunk_t = time.time() - t0
        chunks += 1
    stream_t = time.time() - t0
    print(f"[{prov_name} Stream]: First Chunk: {first_chunk_t:.3f}s | Tổng thời gian stream: {stream_t:.2f}s cho {chunks} chunks\n")
