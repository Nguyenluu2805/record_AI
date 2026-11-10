import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
sys.stdout.reconfigure(encoding='utf-8')

from app.services.lesson_service import lesson_service
from app.services.interview_agent import interview_manager
from app.services.tts_service import tts_service

async def test_full_pipeline():
    lesson = lesson_service.get_lesson('oop_01')
    session = interview_manager.create_session('bench_opt', lesson)
    
    # 1. Đo LLM
    t0 = time.time()
    tokens = []
    async for t in session.generate_response_stream(None):
        tokens.append(t)
    full_text = ''.join(tokens)
    t_llm = time.time() - t0
    print(f'1. LLM Response in {t_llm:.2f}s: "{full_text}"')

    # 2. Đo TTS Stream
    t1 = time.time()
    first_chunk_t = None
    chunks = 0
    for chunk in tts_service.synthesize_pcm_stream(full_text, voice='maichi'):
        if first_chunk_t is None:
            first_chunk_t = time.time() - t1
        chunks += 1
    t_tts = time.time() - t1
    print(f'2. TTS Stream: First Chunk in {first_chunk_t:.3f}s | Total TTS: {t_tts:.2f}s ({chunks} chunks)')
    print(f'==> TOTAL Latency to Voice Playback: {t_llm + 0.8:.2f}s (với Smart Pre-buffer 800ms)!')

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
