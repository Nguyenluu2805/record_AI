/**
 * AudioPlayer: Phát âm thanh PCM 16-bit 48kHz mono nhận qua WebSocket theo từng câu trọn vẹn (Sentence-level).
 * - Mỗi câu được phát nguyên khối, giữ nguyên 100% ngữ điệu và chất lượng âm thanh gốc.
 * - Giữa các câu có khoảng dừng thở tự nhiên (120ms) đúng chuẩn đàm thoại sư phạm.
 * - Tuyệt đối không bao giờ ngắt ngang (turn guard) trước khi toàn bộ câu của lượt nói kết thúc.
 */
class PCMStreamPlayer {
  constructor(options = {}) {
    this.sampleRate = options.sampleRate || 48000;
    this.audioCtx = null;
    this.nextStartTime = 0;
    this.activeNodes = [];
    this.isPlaying = false;
    this.isStreamEnded = false;
    this.onStartSpeaking = options.onStartSpeaking || (() => {});
    this.onStopSpeaking = options.onStopSpeaking || (() => {});
    this.speakingCheckTimer = null;
  }

  initContext() {
    if (!this.audioCtx) {
      const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
      this.audioCtx = new AudioCtxClass({ sampleRate: this.sampleRate });
    }
    if (this.audioCtx.state === 'suspended') {
      this.audioCtx.resume();
    }
  }

  prepareForNewTurn() {
    this.isStreamEnded = false;
    this.isPlaying = true;
    if (this.speakingCheckTimer) {
      clearTimeout(this.speakingCheckTimer);
      this.speakingCheckTimer = null;
    }
    if (this.audioCtx) {
      this.nextStartTime = this.audioCtx.currentTime;
    } else {
      this.nextStartTime = 0;
    }
  }

  playChunkBase64(base64Data, sampleRate = 48000) {
    this.initContext();

    // 1. Giải mã base64 sang raw bytes
    const binaryString = window.atob(base64Data);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }

    // 2. Chuyển Int16Array sang Float32Array [-1.0, 1.0]
    const int16Array = new Int16Array(bytes.buffer);
    if (int16Array.length === 0) return;

    const float32Array = new Float32Array(int16Array.length);
    for (let i = 0; i < int16Array.length; i++) {
      float32Array[i] = int16Array[i] / 32768.0;
    }

    // 3. Tạo AudioBuffer hoàn chỉnh cho câu nói
    const audioBuffer = this.audioCtx.createBuffer(1, float32Array.length, sampleRate);
    audioBuffer.getChannelData(0).set(float32Array);

    // 4. Lên lịch phát câu này
    this.scheduleSentence(audioBuffer);
  }

  scheduleSentence(audioBuffer) {
    const currentTime = this.audioCtx.currentTime;
    
    // Nếu chưa có âm thanh phát hoặc nextStartTime đã trôi qua
    let startTime = this.nextStartTime;
    if (startTime < currentTime + 0.04) {
      startTime = currentTime + 0.05;
    }

    const source = this.audioCtx.createBufferSource();
    source.buffer = audioBuffer;

    const gainNode = this.audioCtx.createGain();
    source.connect(gainNode);
    gainNode.connect(this.audioCtx.destination);

    const duration = audioBuffer.duration;
    // Micro fade-in (5ms) và fade-out (5ms) ở 2 đầu câu để triệt tiêu hoàn toàn tiếng click DAC
    gainNode.gain.setValueAtTime(0.0, startTime);
    gainNode.gain.linearRampToValueAtTime(1.0, startTime + 0.005);
    gainNode.gain.setValueAtTime(1.0, startTime + duration - 0.005);
    gainNode.gain.linearRampToValueAtTime(0.0, startTime + duration);

    source.start(startTime);
    this.activeNodes.push(source);

    // Cập nhật nextStartTime: thời gian câu này kết thúc + 120ms khoảng lặng tự nhiên (nhịp thở tự nhiên giữa các câu)
    this.nextStartTime = startTime + duration + 0.12;

    if (!this.isPlaying) {
      this.isPlaying = true;
      this.onStartSpeaking();
    }

    source.onended = () => {
      const idx = this.activeNodes.indexOf(source);
      if (idx !== -1) {
        this.activeNodes.splice(idx, 1);
      }
      this.checkSpeakingEnd();
    };
  }

  /**
   * Gọi khi server báo đã gửi xong câu cuối cùng của lượt nói (agent_speaking_end)
   */
  notifyStreamEnd() {
    this.isStreamEnded = true;
    this.checkSpeakingEnd();
  }

  checkSpeakingEnd() {
    if (this.speakingCheckTimer) clearTimeout(this.speakingCheckTimer);

    // CHỈ KHI SERVER ĐÃ XÁC NHẬN HẾT CÂU (isStreamEnded = true) MỚI ĐƯỢC KẾT THÚC LƯỢT NÓI!
    // Tránh tuyệt đối việc kết thúc sớm khi AI đang sinh câu tiếp theo
    if (!this.isStreamEnded) {
      return;
    }

    this.speakingCheckTimer = setTimeout(() => {
      if (this.isStreamEnded && this.activeNodes.length === 0 && this.audioCtx && this.audioCtx.currentTime >= this.nextStartTime - 0.15) {
        this.isPlaying = false;
        this.isStreamEnded = false;
        this.nextStartTime = 0;
        this.onStopSpeaking();
      }
    }, 200);
  }

  /**
   * Ngắt âm thanh ngay lập tức (Barge-in / Cancel)
   */
  stop() {
    if (this.speakingCheckTimer) {
      clearTimeout(this.speakingCheckTimer);
      this.speakingCheckTimer = null;
    }

    for (const node of this.activeNodes) {
      try {
        node.stop();
        node.disconnect();
      } catch (e) {}
    }
    this.activeNodes = [];

    this.isPlaying = false;
    this.isStreamEnded = false;
    if (this.audioCtx) {
      this.nextStartTime = this.audioCtx.currentTime;
    } else {
      this.nextStartTime = 0;
    }

    this.onStopSpeaking();
  }
}
