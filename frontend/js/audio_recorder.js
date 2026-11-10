/**
 * AudioRecorder - Quản lý thu âm 2 kênh (Micro + Âm thanh hệ thống) & Bóc tách Giọng nói
 * CÔNG TY CỔ PHẦN TẬP ĐOÀN KIM LONG PHÁT
 * Thiết kế tự phục hồi tức thì, chống ngắt mic khi im lặng và nhả chữ thoại trực tiếp không độ trễ
 */

class MeetingAudioRecorder {
    constructor() {
        this.audioContext = null;
        this.micStream = null;
        this.systemStream = null;
        this.mixedStream = null;
        this.mediaRecorder = null;
        this.analyser = null;
        this.isRecording = false;
        this.isPaused = false;
        this.permissionDenied = false;
        this.recordedBlobs = [];
        this.onRecordingComplete = null;
        
        // Web Speech API cho bóc tách thời gian thực độ trễ 0s
        this.speechRecognition = null;
        this.speechRecognitionActive = false;
        this.restartTimer = null;
        this.onTranscriptCallback = null;
        this.onStatusChange = null;
        this.onAudioLevelChange = null;
        this.visualizerAnimationId = null;
        this.currentSpeaker = null;
    }

    setCurrentSpeaker(speaker) {
        this.currentSpeaker = speaker;
    }

    _createSpeechRecognitionInstance() {
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRec) {
            console.warn('[MeetingAudioRecorder] Trình duyệt không hỗ trợ Web Speech API.');
            if (this.onStatusChange) this.onStatusChange('unsupported');
            return null;
        }

        // Dọn dẹp phiên cũ nếu còn tồn tại
        if (this.speechRecognition) {
            try {
                this.speechRecognition.onresult = null;
                this.speechRecognition.onerror = null;
                this.speechRecognition.onend = null;
                this.speechRecognition.abort();
            } catch (e) {}
            this.speechRecognition = null;
        }

        const sr = new SpeechRec();
        sr.continuous = true;
        sr.interimResults = true;
        sr.lang = 'vi-VN';
        sr.maxAlternatives = 1;

        sr.onstart = () => {
            this.speechRecognitionActive = true;
            console.log('[STT] Web Speech API đang lắng nghe và nhận diện tiếng Việt.');
            if (this.onStatusChange) this.onStatusChange('active');
        };

        sr.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                const res = event.results[i];
                if (res.isFinal) {
                    finalTranscript += res[0].transcript;
                } else {
                    interimTranscript += res[0].transcript;
                }
            }

            if (this.onTranscriptCallback) {
                if (finalTranscript.trim()) {
                    console.log('[STT Final Text]:', finalTranscript.trim());
                    this.onTranscriptCallback(finalTranscript.trim(), true);
                } else if (interimTranscript.trim()) {
                    this.onTranscriptCallback(interimTranscript.trim(), false);
                }
            }
        };

        sr.onerror = (e) => {
            console.warn('[STT] SpeechRecognition error:', e.error);
            if (e.error === 'not-allowed' || e.error === 'service-not-allowed') {
                this.permissionDenied = true;
                if (this.onStatusChange) this.onStatusChange('permission_denied');
            } else if (e.error === 'network') {
                if (this.onStatusChange) this.onStatusChange('network_error');
            }
        };

        sr.onend = () => {
            this.speechRecognitionActive = false;
            // Tự động khởi động lại ngay lập tức (50ms) để không bị ngắt quãng khi người nói tạm nghỉ
            if (this.isRecording && !this.isPaused && !this.permissionDenied) {
                if (this.restartTimer) clearTimeout(this.restartTimer);
                this.restartTimer = setTimeout(() => {
                    if (this.isRecording && !this.isPaused && !this.permissionDenied) {
                        this._startSpeechRecognition();
                    }
                }, 50);
            }
        };

        this.speechRecognition = sr;
        return sr;
    }

    _startSpeechRecognition() {
        if (!this.isRecording || this.isPaused || this.permissionDenied) return;
        try {
            const sr = this._createSpeechRecognitionInstance();
            if (sr) {
                sr.start();
            }
        } catch (err) {
            console.warn('[STT] Thử khởi động lại SpeechRecognition:', err);
            if (this.isRecording && !this.isPaused && !this.permissionDenied) {
                if (this.restartTimer) clearTimeout(this.restartTimer);
                this.restartTimer = setTimeout(() => {
                    this._startSpeechRecognition();
                }, 300);
            }
        }
    }

    async startRecording(sourceType = 'mic_only', canvasElement = null) {
        try {
            this.permissionDenied = false;
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            this.audioContext = new AudioCtx();
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }

            const destination = this.audioContext.createMediaStreamDestination();

            // 1. Thu âm Micro vật lý
            this.micStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });

            const micSource = this.audioContext.createMediaStreamSource(this.micStream);
            micSource.connect(destination);

            // 2. Nếu chọn Micro + Âm thanh hệ thống
            if (sourceType === 'mic_system' && navigator.mediaDevices.getDisplayMedia) {
                try {
                    this.systemStream = await navigator.mediaDevices.getDisplayMedia({
                        video: true,
                        audio: true
                    });
                    
                    const audioTracks = this.systemStream.getAudioTracks();
                    if (audioTracks.length > 0) {
                        const sysAudioStream = new MediaStream([audioTracks[0]]);
                        const sysSource = this.audioContext.createMediaStreamSource(sysAudioStream);
                        sysSource.connect(destination);
                    }
                } catch (e) {
                    console.warn('Người dùng không chọn chia sẻ âm thanh hệ thống:', e);
                }
            }

            this.mixedStream = destination.stream;

            // 3. Thiết lập Visualizer & Audio Activity Meter
            if (canvasElement) {
                this.setupVisualizer(canvasElement, micSource);
            }

            this.recordedBlobs = [];

            // 4. MediaRecorder để lưu trữ trọn vẹn tệp âm thanh buổi họp (.webm)
            const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
                ? 'audio/webm;codecs=opus'
                : (MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4');

            this.mediaRecorder = new MediaRecorder(this.mixedStream, { mimeType });
            this.mediaRecorder.ondataavailable = (e) => {
                if (e.data && e.data.size > 0) {
                    this.recordedBlobs.push(e.data);
                }
            };
            this.mediaRecorder.start(2000);

            this.isRecording = true;
            this.isPaused = false;

            // 5. Khởi động Web Speech API nhả chữ trực tiếp tức thì
            this._startSpeechRecognition();

            return true;
        } catch (err) {
            console.error('Lỗi khởi tạo thu âm micro:', err);
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                this.permissionDenied = true;
                if (this.onStatusChange) this.onStatusChange('permission_denied');
            }
            throw err;
        }
    }

    pauseRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.isPaused = true;
            try { this.mediaRecorder.pause(); } catch (e) {}
            if (this.speechRecognition) {
                try { this.speechRecognition.abort(); } catch (e) {}
            }
            if (this.restartTimer) clearTimeout(this.restartTimer);
            if (this.onStatusChange) this.onStatusChange('paused');
        }
    }

    resumeRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.isPaused = false;
            try { this.mediaRecorder.resume(); } catch (e) {}
            this._startSpeechRecognition();
            if (this.onStatusChange) this.onStatusChange('active');
        }
    }

    stopRecording() {
        this.isRecording = false;
        this.isPaused = false;
        if (this.restartTimer) {
            clearTimeout(this.restartTimer);
            this.restartTimer = null;
        }

        let finalBlob = null;
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            try { this.mediaRecorder.stop(); } catch (e) {}
        }

        if (this.recordedBlobs.length > 0) {
            const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : 'audio/webm';
            finalBlob = new Blob(this.recordedBlobs, { type: mimeType });
        }

        if (this.micStream) {
            this.micStream.getTracks().forEach(t => t.stop());
            this.micStream = null;
        }
        if (this.systemStream) {
            this.systemStream.getTracks().forEach(t => t.stop());
            this.systemStream = null;
        }
        if (this.audioContext && this.audioContext.state !== 'closed') {
            try { this.audioContext.close(); } catch (e) {}
            this.audioContext = null;
        }
        if (this.speechRecognition) {
            try {
                this.speechRecognition.onresult = null;
                this.speechRecognition.onerror = null;
                this.speechRecognition.onend = null;
                this.speechRecognition.abort();
            } catch (e) {}
            this.speechRecognition = null;
        }

        if (this.onStatusChange) this.onStatusChange('stopped');

        if (finalBlob && this.onRecordingComplete) {
            this.onRecordingComplete(finalBlob);
        }
        return finalBlob;
    }

    setupVisualizer(canvas, sourceNode) {
        if (!this.audioContext || !sourceNode || !canvas) return;
        canvas.width = 76;
        canvas.height = 20;

        const analyser = this.audioContext.createAnalyser();
        analyser.fftSize = 128;
        analyser.smoothingTimeConstant = 0.75;
        sourceNode.connect(analyser);

        const canvasCtx = canvas.getContext('2d');
        const numBars = 15;
        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        const draw = () => {
            if (!this.isRecording) {
                // Trạng thái nghỉ: các vạch phẳng êm dịu ở giữa
                canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
                const barW = 2.5;
                const gap = 2.5;
                const totalW = numBars * (barW + gap) - gap;
                const startX = Math.max(0, (canvas.width - totalW) / 2);
                canvasCtx.fillStyle = '#cbd5e1';
                for (let i = 0; i < numBars; i++) {
                    const x = startX + i * (barW + gap);
                    canvasCtx.fillRect(x, (canvas.height - 3) / 2, barW, 3);
                }
                return;
            }
            this.visualizerAnimationId = requestAnimationFrame(draw);

            analyser.getByteFrequencyData(dataArray);

            // Tính năng lượng dải tần số giọng nói
            let sum = 0;
            const voiceBins = Math.min(32, dataArray.length);
            for (let i = 0; i < voiceBins; i++) {
                sum += dataArray[i];
            }
            const avgVolume = sum / voiceBins;

            if (this.onAudioLevelChange) {
                this.onAudioLevelChange(avgVolume);
            }

            canvasCtx.clearRect(0, 0, canvas.width, canvas.height);

            const barW = 2.5;
            const gap = 2.5;
            const totalW = numBars * (barW + gap) - gap;
            const startX = Math.max(0, (canvas.width - totalW) / 2);
            const isSpeakingNow = avgVolume > 5;

            for (let i = 0; i < numBars; i++) {
                const sampleIdx = Math.floor((i / numBars) * voiceBins);
                const rawVal = dataArray[sampleIdx] || 0;

                let barH = 3;
                if (isSpeakingNow) {
                    const norm = rawVal / 255;
                    const waveFactor = 0.45 + 0.55 * Math.sin((i / (numBars - 1)) * Math.PI);
                    barH = Math.max(4, norm * (canvas.height - 2) * waveFactor * 1.5);
                    barH = Math.min(canvas.height - 2, barH);
                }

                const x = startX + i * (barW + gap);
                const y = (canvas.height - barH) / 2;

                canvasCtx.fillStyle = isSpeakingNow ? '#10b981' : '#cbd5e1';

                if (canvasCtx.roundRect) {
                    canvasCtx.beginPath();
                    canvasCtx.roundRect(x, y, barW, barH, 1.2);
                    canvasCtx.fill();
                } else {
                    canvasCtx.fillRect(x, y, barW, barH);
                }
            }
        };

        draw();
    }

    // Mô phỏng sóng âm sinh động cho chế độ Demo khi đại biểu đang nói
    startSimulation(canvas) {
        if (!canvas) return;
        canvas.width = 76;
        canvas.height = 20;
        const canvasCtx = canvas.getContext('2d');
        const numBars = 15;
        this.simulating = true;

        if (this.simAnimationId) {
            cancelAnimationFrame(this.simAnimationId);
        }

        let tick = 0;
        const renderSim = () => {
            if (!this.simulating) {
                canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
                canvasCtx.fillStyle = '#cbd5e1';
                const barW = 2.5;
                const gap = 2.5;
                const totalW = numBars * (barW + gap) - gap;
                const startX = Math.max(0, (canvas.width - totalW) / 2);
                for (let i = 0; i < numBars; i++) {
                    const x = startX + i * (barW + gap);
                    canvasCtx.fillRect(x, (canvas.height - 3) / 2, barW, 3);
                }
                return;
            }

            this.simAnimationId = requestAnimationFrame(renderSim);
            tick += 0.18;

            canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
            const barW = 2.5;
            const gap = 2.5;
            const totalW = numBars * (barW + gap) - gap;
            const startX = Math.max(0, (canvas.width - totalW) / 2);

            for (let i = 0; i < numBars; i++) {
                const waveFactor = 0.4 + 0.6 * Math.sin((i / (numBars - 1)) * Math.PI);
                const waveMotion = Math.abs(Math.sin(tick + i * 0.5) * Math.cos(tick * 0.8 + i * 0.3));
                const barH = Math.max(4, Math.min(canvas.height - 2, 4 + waveMotion * (canvas.height - 4) * waveFactor));
                const x = startX + i * (barW + gap);
                const y = (canvas.height - barH) / 2;

                canvasCtx.fillStyle = '#10b981';
                if (canvasCtx.roundRect) {
                    canvasCtx.beginPath();
                    canvasCtx.roundRect(x, y, barW, barH, 1.2);
                    canvasCtx.fill();
                } else {
                    canvasCtx.fillRect(x, y, barW, barH);
                }
            }
        };

        renderSim();
    }

    stopSimulation(canvas) {
        this.simulating = false;
        if (this.simAnimationId) {
            cancelAnimationFrame(this.simAnimationId);
            this.simAnimationId = null;
        }
        if (canvas) {
            const canvasCtx = canvas.getContext('2d');
            canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
            canvasCtx.fillStyle = '#cbd5e1';
            const numBars = 15;
            const barW = 2.5;
            const gap = 2.5;
            const totalW = numBars * (barW + gap) - gap;
            const startX = Math.max(0, (canvas.width - totalW) / 2);
            for (let i = 0; i < numBars; i++) {
                const x = startX + i * (barW + gap);
                canvasCtx.fillRect(x, (canvas.height - 3) / 2, barW, 3);
            }
        }
    }
}

// Global instance
window.meetingRecorder = new MeetingAudioRecorder();
