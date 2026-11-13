/**
 * App.js - Luồng Điều Khiển 3 Bước Bot AI Trợ Lý Thư Ký
 * CÔNG TY CỔ PHẦN TẬP ĐOÀN KIM LONG PHÁT
 */

document.addEventListener('DOMContentLoaded', () => {
    // State management
    const state = {
        currentStep: 1,
        mode: 'option_1', // 'option_1' or 'option_2'
        audioSource: 'mic_only',
        sessionId: null,
        meetingTitle: '',
        chairperson: '',
        secretary: '',
        partnerName: '',
        partnerReps: '',
        participants: [],
        currentActiveSpeaker: '',
        availableLeaders: [],
        transcripts: [],
        analysisState: {},
        timerInterval: null,
        meetingSeconds: 0,
        isPaused: false,
        isDemoRunning: false,
        socket: null,
        meetingAudioBlob: null,
        audioDownloadUrl: null,
        audioFilename: null,
        transcriptDownloadUrl: null,
        transcriptFilename: null,
        transcriptTextContent: null
    };

    // DOM Elements
    const screenStep1 = document.getElementById('screenStep1');
    const screenStep2 = document.getElementById('screenStep2');
    const screenStep3 = document.getElementById('screenStep3');
    const stepIndicator1 = document.getElementById('stepIndicator1');
    const stepIndicator2 = document.getElementById('stepIndicator2');
    const stepIndicator3 = document.getElementById('stepIndicator3');

    // Step 1 Elements
    const modeOption1 = document.getElementById('modeOption1');
    const modeOption2 = document.getElementById('modeOption2');
    const sourceMicOnly = document.getElementById('sourceMicOnly');
    const sourceMicSystem = document.getElementById('sourceMicSystem');
    const meetingTitleInput = document.getElementById('meetingTitleInput');
    const chairpersonInput = document.getElementById('chairpersonInput');
    const partnerNameInput = document.getElementById('partnerNameInput');
    const partnerRepsInput = document.getElementById('partnerRepsInput');
    const secretaryInput = document.getElementById('secretaryInput');
    const groupPartnerName = document.getElementById('groupPartnerName');
    const groupPartnerReps = document.getElementById('groupPartnerReps');
    const participantsTags = document.getElementById('participantsTags');
    const btnStartRealMeeting = document.getElementById('btnStartRealMeeting');
    const btnStartDemo = document.getElementById('btnStartDemo');
    const btnUploadAudioTrigger = document.getElementById('btnUploadAudioTrigger');
    const btnUploadAudioDuringMeeting = document.getElementById('btnUploadAudioDuringMeeting');
    const audioFileInput = document.getElementById('audioFileInput');

    // Step 2 Elements
    const liveModeBadge = document.getElementById('liveModeBadge');
    const liveMeetingTitle = document.getElementById('liveMeetingTitle');
    const meetingTimer = document.getElementById('meetingTimer');
    const waveformCanvas = document.getElementById('waveformCanvas');
    const recDot = document.getElementById('recDot');
    const audioSourceText = document.getElementById('audioSourceText');
    const btnHotBookmark = document.getElementById('btnHotBookmark');
    const btnPauseMeeting = document.getElementById('btnPauseMeeting');
    const btnTriggerAnalyze = document.getElementById('btnTriggerAnalyze');
    const btnEndMeeting = document.getElementById('btnEndMeeting');
    const transcriptScrollArea = document.getElementById('transcriptScrollArea');
    const transcriptEmptyState = document.getElementById('transcriptEmptyState');
    const turnCountBadge = document.getElementById('turnCountBadge');
    const activeSpeakerBar = document.getElementById('activeSpeakerBar');
    const activeSpeakerChips = document.getElementById('activeSpeakerChips');
    const currentActiveSpeakerName = document.getElementById('currentActiveSpeakerName');
    const quickSpeakerSelect = document.getElementById('quickSpeakerSelect');
    const quickSpeakerTagText = document.getElementById('quickSpeakerTagText');
    const btnScrollBottom = document.getElementById('btnScrollBottom');
    const quickTextInput = document.getElementById('quickTextInput');
    const btnSendQuickText = document.getElementById('btnSendQuickText');
    const secretaryNoteInput = document.getElementById('secretaryNoteInput');
    const btnSendSecretaryNote = document.getElementById('btnSendSecretaryNote');

    // Analysis Containers
    const analysisOption1Container = document.getElementById('analysisOption1Container');
    const analysisOption2Container = document.getElementById('analysisOption2Container');
    const aiSummaryGoals = document.getElementById('aiSummaryGoals');
    const aiLeaderDirections = document.getElementById('aiLeaderDirections');
    const aiDeptReports = document.getElementById('aiDeptReports');
    const tableSpeechAnalytics = document.getElementById('tableSpeechAnalytics').querySelector('tbody');
    const aiAgreedIssues = document.getElementById('aiAgreedIssues');
    const aiPendingIssues = document.getElementById('aiPendingIssues');
    const aiHotBookmarksList = document.getElementById('aiHotBookmarksList');
    const tableActionItems = document.getElementById('tableActionItems').querySelector('tbody');

    // Option 2 Specific Containers
    const dealScoreValue = document.getElementById('dealScoreValue');
    const dealScoreDesc = document.getElementById('dealScoreDesc');
    const aiCustomerPains = document.getElementById('aiCustomerPains');
    const aiKlpProposals = document.getElementById('aiKlpProposals');
    const tableCommercialTerms = document.getElementById('tableCommercialTerms').querySelector('tbody');
    const aiBuyingSignals = document.getElementById('aiBuyingSignals');
    const aiObjections = document.getElementById('aiObjections');
    const aiPartnerSpeakers = document.getElementById('aiPartnerSpeakers');
    const tableFollowUp = document.getElementById('tableFollowUp').querySelector('tbody');

    // Step 3 Elements
    const option1ExportBtns = document.getElementById('option1ExportBtns');
    const option2ExportBtns = document.getElementById('option2ExportBtns');
    const btnExportWordOption1 = document.getElementById('btnExportWordOption1');
    const btnExportWordOption2Full = document.getElementById('btnExportWordOption2Full');
    const btnExportWordOption2Partner = document.getElementById('btnExportWordOption2Partner');
    const btnBackToMeeting = document.getElementById('btnBackToMeeting');
    const btnNewMeeting = document.getElementById('btnNewMeeting');
    const btnGoHome = document.getElementById('btnGoHome');
    const documentPreviewContainer = document.getElementById('documentPreviewContainer');

    // Storage Picker Elements (Step 1 & Step 3)
    const storagePathInput = document.getElementById('storagePathInput');
    const btnBrowseStorageFolder = document.getElementById('btnBrowseStorageFolder');
    const btnOpenCurrentFolder = document.getElementById('btnOpenCurrentFolder');
    const displayStoragePath = document.getElementById('displayStoragePath');
    const btnOpenMeetingFolder = document.getElementById('btnOpenMeetingFolder');
    const btnCopyStoragePath = document.getElementById('btnCopyStoragePath');
    const btnQuickExportWord = document.getElementById('btnQuickExportWord');
    const audioFileName = document.getElementById('audioFileName');
    const audioFileSizeBadge = document.getElementById('audioFileSizeBadge');
    const transcriptFileName = document.getElementById('transcriptFileName');
    const textFileSizeBadge = document.getElementById('textFileSizeBadge');
    const wordFileName = document.getElementById('wordFileName');

    // Executive Popup Modal Elements
    const appPopupOverlay = document.getElementById('appPopupOverlay');
    const popupTitle = document.getElementById('popupTitle');
    const popupMessage = document.getElementById('popupMessage');
    const popupHeaderIcon = document.getElementById('popupHeaderIcon');
    const btnPopupClose = document.getElementById('btnPopupClose');
    const btnPopupConfirm = document.getElementById('btnPopupConfirm');
    const btnPopupCancel = document.getElementById('btnPopupCancel');

    let popupConfirmCallback = null;
    let popupCancelCallback = null;
    let popupAutoCloseTimer = null;

    // Show Modern Popup Modal
    function showPopup({
        title = 'Thông báo hệ thống',
        message = '',
        type = 'info', // 'success', 'warning', 'danger', 'info'
        confirmText = 'Đã hiểu',
        cancelText = null,
        onConfirm = null,
        onCancel = null,
        autoCloseMs = 0
    }) {
        if (!appPopupOverlay) return;

        if (popupAutoCloseTimer) {
            clearTimeout(popupAutoCloseTimer);
            popupAutoCloseTimer = null;
        }

        popupTitle.textContent = title;
        popupMessage.innerHTML = message;
        btnPopupConfirm.textContent = confirmText || 'Đã hiểu';

        // Styling type
        popupHeaderIcon.className = `popup-icon-wrap popup-type-${type}`;
        let iconHtml = '<i class="fa-solid fa-circle-info"></i>';
        if (type === 'success') {
            iconHtml = '<i class="fa-solid fa-circle-check"></i>';
        } else if (type === 'warning') {
            iconHtml = '<i class="fa-solid fa-triangle-exclamation"></i>';
        } else if (type === 'danger' || type === 'error') {
            iconHtml = '<i class="fa-solid fa-circle-exclamation"></i>';
        }
        popupHeaderIcon.innerHTML = iconHtml;

        if (cancelText) {
            btnPopupCancel.textContent = cancelText;
            btnPopupCancel.style.display = 'inline-flex';
            btnPopupCancel.classList.remove('hidden');
        } else {
            btnPopupCancel.textContent = '';
            btnPopupCancel.style.display = 'none';
            btnPopupCancel.classList.add('hidden');
        }

        popupConfirmCallback = onConfirm;
        popupCancelCallback = onCancel;

        appPopupOverlay.style.display = 'flex';
        appPopupOverlay.classList.remove('hidden');
        requestAnimationFrame(() => {
            appPopupOverlay.classList.add('active');
        });

        if (autoCloseMs > 0 && !cancelText) {
            popupAutoCloseTimer = setTimeout(() => {
                closePopup();
            }, autoCloseMs);
        }
    }

    function closePopup() {
        if (!appPopupOverlay) return;
        if (popupAutoCloseTimer) {
            clearTimeout(popupAutoCloseTimer);
            popupAutoCloseTimer = null;
        }
        appPopupOverlay.classList.remove('active');
        setTimeout(() => {
            appPopupOverlay.style.display = 'none';
            appPopupOverlay.classList.add('hidden');
        }, 150);
    }
    window.showPopup = showPopup;
    window.showPopupModal = showPopup;
    window.closePopup = closePopup;

    if (btnPopupClose) {
        btnPopupClose.addEventListener('click', () => {
            if (popupCancelCallback) popupCancelCallback();
            closePopup();
        });
    }

    if (btnPopupCancel) {
        btnPopupCancel.addEventListener('click', () => {
            if (popupCancelCallback) popupCancelCallback();
            closePopup();
        });
    }

    if (btnPopupConfirm) {
        btnPopupConfirm.addEventListener('click', () => {
            const cb = popupConfirmCallback;
            closePopup();
            if (cb) cb();
        });
    }

    if (appPopupOverlay) {
        appPopupOverlay.addEventListener('click', (e) => {
            if (e.target === appPopupOverlay) {
                if (popupCancelCallback) popupCancelCallback();
                closePopup();
            }
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && appPopupOverlay && appPopupOverlay.classList.contains('active')) {
            if (popupCancelCallback) popupCancelCallback();
            closePopup();
        }
    });

    // Helper: Show Toast - Re-routed to Executive Popup Dialog
    function showToast(message, type = 'info') {
        let title = 'Thông báo hệ thống';
        let autoClose = 3500;
        if (type === 'success') {
            title = 'Thành công';
            autoClose = 3000;
        } else if (type === 'warning') {
            title = 'Lưu ý';
            autoClose = 0; // Cần người dùng bấm Đã hiểu
        } else if (type === 'danger' || type === 'error') {
            title = 'Cảnh báo';
            autoClose = 0;
        }
        showPopup({
            title: title,
            message: message,
            type: type,
            confirmText: 'Đã hiểu',
            autoCloseMs: autoClose
        });
    }

    // Helper: Navigate Steps
    function setStep(step) {
        state.currentStep = step;
        [screenStep1, screenStep2, screenStep3].forEach((s, idx) => {
            if (s) {
                s.classList.toggle('active', idx + 1 === step);
                // Đảm bảo ẩn/hiện dứt khoát tránh lỗi đè bước
                if (idx + 1 === step) {
                    s.style.display = (step === 2) ? 'flex' : 'block';
                } else {
                    s.style.display = 'none';
                }
            }
        });
        [stepIndicator1, stepIndicator2, stepIndicator3].forEach((ind, idx) => {
            if (!ind) return;
            ind.classList.toggle('active', idx + 1 === step);
            ind.classList.toggle('done', idx + 1 < step);
            const circle = ind.querySelector('.step-circle');
            if (circle) {
                if (idx + 1 < step) circle.textContent = '✓';
                else circle.textContent = String(idx + 1);
            }
        });
        if (step === 3) {
            try {
                prepareStep3Review();
            } catch (err) {
                console.warn('Lỗi chuẩn bị bước 3:', err);
            }
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    window.setStep = setStep;
    window.showStep = setStep;

    [stepIndicator1, stepIndicator2, stepIndicator3].forEach((ind, idx) => {
        if (ind) {
            ind.addEventListener('click', () => {
                if (containerMeetingAssistant && containerMeetingAssistant.style.display !== 'none') {
                    setStep(idx + 1);
                }
            });
        }
    });

    // Initialize System Config from Backend
    async function loadConfig() {
        try {
            const res = await fetch('/api/config');
            const data = await res.json();
            state.availableLeaders = data.leadership_members || [];
            renderParticipantsTags();
        } catch (e) {
            console.warn('Không tải được config từ server:', e);
            // Default leaders
            state.availableLeaders = [
                { name: "Bà Phan Thị Phát", role: "Tổng Giám Đốc" },
                { name: "Ông Trần Văn Hùng", role: "Phó Tổng Giám Đốc" },
                { name: "Ông Đặng Minh Trí", role: "Trưởng Phòng Kinh Doanh" },
                { name: "Ông Phạm Đức Huy", role: "Trưởng Phòng Kỹ Thuật" },
                { name: "Bà Nguyễn Mai Phương", role: "Kế toán Trưởng" }
            ];
            renderParticipantsTags();
        }
    }

    function renderParticipantsTags() {
        if (!participantsTags) return;
        participantsTags.innerHTML = '';
        state.availableLeaders.forEach((leader, idx) => {
            const isSelected = leader.selected !== undefined ? leader.selected : (idx < 4);
            leader.selected = isSelected;

            const pill = document.createElement('div');
            pill.className = 'participant-pill' + (isSelected ? ' selected' : '');
            
            let pillContent = `<span class="pill-check-indicator"></span><span class="pill-name">${leader.name}</span> <span class="pill-role">(${leader.role})</span>`;
            if (leader.isCustom) {
                pillContent += `<span class="pill-del-btn" title="Xóa nhân sự này">&times;</span>`;
            }
            pill.innerHTML = pillContent;

            pill.addEventListener('click', (e) => {
                if (e.target.classList.contains('pill-del-btn')) {
                    e.stopPropagation();
                    const index = state.availableLeaders.indexOf(leader);
                    if (index > -1) {
                        state.availableLeaders.splice(index, 1);
                        renderParticipantsTags();
                        if (typeof toast === 'function') toast(`Đã xóa ${leader.name}`);
                    }
                    return;
                }
                leader.selected = !leader.selected;
                pill.classList.toggle('selected', leader.selected);
                updateSelectedParticipants();
            });

            participantsTags.appendChild(pill);
        });
        updateSelectedParticipants();
    }

    function updateSelectedParticipants() {
        if (!participantsTags) return;
        const allPills = participantsTags.querySelectorAll('.participant-pill');
        const selectedPills = participantsTags.querySelectorAll('.participant-pill.selected');
        
        state.participants = Array.from(selectedPills).map(p => {
            const name = p.querySelector('.pill-name')?.textContent || '';
            const role = p.querySelector('.pill-role')?.textContent || '';
            return `${name} ${role}`.trim();
        });

        const countBadge = document.getElementById('participantsCountBadge');
        if (countBadge) {
            countBadge.textContent = `Đã chọn: ${selectedPills.length}/${allPills.length} nhân sự`;
        }

        renderActiveSpeakerSelector();
    }

    // Controls for Participants: Select All / Deselect All / Toggle Collapse / Add Person
    function initParticipantsControls() {
        const btnSelectAll = document.getElementById('btnSelectAllParticipants');
        const btnDeselectAll = document.getElementById('btnDeselectAllParticipants');
        const btnToggle = document.getElementById('btnToggleParticipants');
        const collapseWrapper = document.getElementById('participantsCollapseWrapper');
        const toggleText = document.getElementById('toggleParticipantsText');
        const toggleIcon = document.getElementById('toggleParticipantsIcon');
        const btnAddPart = document.getElementById('btnAddParticipant');
        const nameInp = document.getElementById('newParticipantName');
        const roleInp = document.getElementById('newParticipantRole');

        if (btnSelectAll) {
            btnSelectAll.addEventListener('click', () => {
                state.availableLeaders.forEach(l => l.selected = true);
                if (participantsTags) {
                    participantsTags.querySelectorAll('.participant-pill').forEach(p => p.classList.add('selected'));
                }
                updateSelectedParticipants();
            });
        }

        if (btnDeselectAll) {
            btnDeselectAll.addEventListener('click', () => {
                state.availableLeaders.forEach(l => l.selected = false);
                if (participantsTags) {
                    participantsTags.querySelectorAll('.participant-pill').forEach(p => p.classList.remove('selected'));
                }
                updateSelectedParticipants();
            });
        }

        if (btnToggle && collapseWrapper) {
            btnToggle.addEventListener('click', () => {
                const isCollapsed = collapseWrapper.classList.toggle('collapsed');
                if (toggleText) toggleText.textContent = isCollapsed ? 'Mở rộng danh bạ' : 'Thu gọn';
                if (toggleIcon) {
                    toggleIcon.className = isCollapsed ? 'fa-solid fa-chevron-down' : 'fa-solid fa-chevron-up';
                }
            });
        }

        function doAddParticipant() {
            if (!nameInp) return;
            const name = nameInp.value.trim();
            const role = (roleInp && roleInp.value.trim()) || 'Thành viên tham dự';
            if (!name) {
                nameInp.focus();
                if (typeof showPopup === 'function') {
                    showPopup({
                        title: 'Chưa nhập họ tên',
                        message: 'Vui lòng nhập họ và tên của thành viên cần thêm vào cuộc họp.',
                        type: 'warning'
                    });
                }
                return;
            }

            // Check duplicate
            const exists = state.availableLeaders.some(l => l.name.toLowerCase() === name.toLowerCase());
            if (exists) {
                if (typeof showPopup === 'function') {
                    showPopup({
                        title: 'Thành viên đã có',
                        message: `Nhân sự "${name}" đã có trong danh sách thành viên.`,
                        type: 'info'
                    });
                }
                return;
            }

            const newMember = { name, role, isCustom: true, selected: true };
            state.availableLeaders.push(newMember);
            renderParticipantsTags();

            // Auto-expand if collapsed
            if (collapseWrapper && collapseWrapper.classList.contains('collapsed')) {
                collapseWrapper.classList.remove('collapsed');
                if (toggleText) toggleText.textContent = 'Thu gọn';
                if (toggleIcon) toggleIcon.className = 'fa-solid fa-chevron-up';
            }

            nameInp.value = '';
            if (roleInp) roleInp.value = '';
            nameInp.focus();

            if (typeof toast === 'function') {
                toast(`Đã thêm thành viên: ${name} (${role})`);
            }
        }

        if (btnAddPart) {
            btnAddPart.addEventListener('click', doAddParticipant);
        }

        [nameInp, roleInp].forEach(inp => {
            if (inp) {
                inp.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        doAddParticipant();
                    }
                });
            }
        });
    }
    initParticipantsControls();

    // Thanh Chọn Người Đang Phát Biểu (Trợ lý chủ động chọn)
    function renderActiveSpeakerSelector() {
        if (!activeSpeakerChips || !quickSpeakerSelect) return;

        const list = [];
        const chair = (chairpersonInput && chairpersonInput.value.trim()) || state.chairperson || "Bà Phan Thị Phát (Tổng Giám Đốc)";
        if (state.mode === 'option_1') {
            if (chair && !list.includes(chair)) list.push(chair);
        }

        if (state.participants && state.participants.length > 0) {
            state.participants.forEach(p => {
                if (p && !list.includes(p)) list.push(p);
            });
        }

        if (state.mode === 'option_2') {
            const klpLead = "Ông Trần Văn Hùng (Phó TGĐ KLP)";
            if (!list.includes(klpLead)) list.push(klpLead);

            const ptnVal = (partnerRepsInput && partnerRepsInput.value.trim()) || state.partnerReps || "Ông Vũ Đình Toàn (GĐ Dự Án), Bà Hoàng Thị Nga (Trưởng BP Mua Sắm)";
            ptnVal.split(',').forEach(rep => {
                const trimmed = rep.trim();
                if (trimmed && !list.includes(trimmed)) list.push(trimmed);
            });
        }

        const sec = (secretaryInput && secretaryInput.value.trim()) || state.secretary || "Bà Lê Thu Thảo (Thư ký Ban TGĐ)";
        if (sec && !list.includes(sec)) {
            list.push(sec);
        }

        if (list.length === 0) {
            list.push("Người phát biểu");
        }

        if (!state.currentActiveSpeaker || !list.includes(state.currentActiveSpeaker)) {
            state.currentActiveSpeaker = list[0];
        }

        // Dropdown
        quickSpeakerSelect.innerHTML = '';
        list.forEach(spk => {
            const opt = document.createElement('option');
            opt.value = spk;
            opt.textContent = spk;
            if (spk === state.currentActiveSpeaker) opt.selected = true;
            quickSpeakerSelect.appendChild(opt);
        });

        // Chips for 1-click active speaker switching
        activeSpeakerChips.innerHTML = '';
        list.forEach(spk => {
            const chip = document.createElement('div');
            chip.className = 'speaker-chip' + (spk === state.currentActiveSpeaker ? ' active' : '');
            chip.innerHTML = `<i class="fa-solid fa-user"></i> <span>${spk}</span>`;
            chip.addEventListener('click', () => {
                setActiveSpeaker(spk, true);
            });
            activeSpeakerChips.appendChild(chip);
        });

        if (currentActiveSpeakerName) {
            currentActiveSpeakerName.textContent = state.currentActiveSpeaker;
        }
    }

    function setActiveSpeaker(spkName, showNotice = false) {
        if (!spkName) return;
        state.currentActiveSpeaker = spkName;
        if (window.meetingRecorder && window.meetingRecorder.setCurrentSpeaker) {
            window.meetingRecorder.setCurrentSpeaker(spkName);
        }

        if (currentActiveSpeakerName) {
            currentActiveSpeakerName.textContent = spkName;
        }
        if (quickSpeakerTagText) {
            quickSpeakerTagText.textContent = spkName;
        }
        if (quickSpeakerSelect) {
            quickSpeakerSelect.value = spkName;
        }
        if (activeSpeakerChips) {
            activeSpeakerChips.querySelectorAll('.speaker-chip').forEach(c => {
                const span = c.querySelector('span');
                if (span && span.textContent === spkName) {
                    c.classList.add('active');
                    try {
                        const chipLeft = c.offsetLeft;
                        const chipWidth = c.offsetWidth;
                        const containerWidth = activeSpeakerChips.clientWidth;
                        activeSpeakerChips.scrollTo({
                            left: chipLeft - (containerWidth / 2) + (chipWidth / 2),
                            behavior: 'smooth'
                        });
                    } catch (_) {}
                } else {
                    c.classList.remove('active');
                }
            });
        }
        // Đã bỏ thông báo chuyển người phát biểu theo yêu cầu
        /*
        if (showNotice) {
            showToast(`Đã chuyển người phát biểu: ${spkName}`, 'info');
        }
        */
    }

    if (quickSpeakerSelect) {
        quickSpeakerSelect.addEventListener('change', () => {
            setActiveSpeaker(quickSpeakerSelect.value, true);
        });
    }

    // Step 1: Mode Switching
    modeOption1.addEventListener('click', () => {
        modeOption1.classList.add('active');
        modeOption2.classList.remove('active');
        state.mode = 'option_1';
        groupPartnerName.style.display = 'none';
        groupPartnerReps.style.display = 'none';
        meetingTitleInput.value = 'Cuộc họp Giao ban Triển khai Kế hoạch Trọng tâm Quý 4/2026';
        chairpersonInput.parentElement.style.display = 'flex';
        updateSelectedParticipants();
    });

    modeOption2.addEventListener('click', () => {
        modeOption2.classList.add('active');
        modeOption1.classList.remove('active');
        state.mode = 'option_2';
        groupPartnerName.style.display = 'flex';
        groupPartnerReps.style.display = 'flex';
        meetingTitleInput.value = 'Đàm phán Hợp đồng Cung cấp 60 Thiết bị Lọc nước Ion Kiềm iONPIA';
        chairpersonInput.parentElement.style.display = 'none';
        updateSelectedParticipants();
    });

    // Audio Source Switching
    sourceMicOnly.addEventListener('click', () => {
        sourceMicOnly.classList.add('active');
        sourceMicSystem.classList.remove('active');
        state.audioSource = 'mic_only';
    });

    sourceMicSystem.addEventListener('click', () => {
        sourceMicSystem.classList.add('active');
        sourceMicOnly.classList.remove('active');
        state.audioSource = 'mic_system';
    });

    // Start Real Meeting
    btnStartRealMeeting.addEventListener('click', async () => {
        await initializeMeetingSession(false);
    });

    // Start Demo Simulation
    btnStartDemo.addEventListener('click', async () => {
        await initializeMeetingSession(true);
    });

    if (btnBrowseStorageFolder) {
        btnBrowseStorageFolder.addEventListener('click', async () => {
            if ('showDirectoryPicker' in window) {
                try {
                    const dirHandle = await window.showDirectoryPicker();
                    if (dirHandle && dirHandle.name) {
                        storagePathInput.value = `D:\\review_agent\\output\\${dirHandle.name}`;
                        state.storagePath = storagePathInput.value;
                        showPopup({
                            title: 'Đã chọn thư mục lưu trữ',
                            message: `Hệ thống sẽ lưu trữ toàn bộ bản ghi âm (.webm), bản text (.txt) và file Word (.docx) vào thư mục: <strong>${dirHandle.name}</strong>`,
                            type: 'success',
                            autoCloseMs: 3500
                        });
                    }
                } catch (err) {
                    if (err.name !== 'AbortError') {
                        console.warn(err);
                    }
                }
            } else {
                showPopup({
                    title: 'Chọn thư mục lưu trữ',
                    message: 'Trình duyệt không hỗ trợ mở hộp thoại thư mục tự động. Bạn có thể nhập hoặc dán trực tiếp đường dẫn thư mục mong muốn vào ô nhập liệu bên cạnh (VD: <code>D:\\HopKLP_2026</code>).',
                    type: 'info'
                });
            }
        });
    }

    if (btnOpenCurrentFolder) {
        btnOpenCurrentFolder.addEventListener('click', async () => {
            const path = (storagePathInput && storagePathInput.value.trim()) || "D:\\review_agent\\output\\meetings";
            try {
                const res = await fetch('/api/open-local-path', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: path })
                });
                const data = await res.json();
                if (data.success) {
                    showPopup({
                        title: 'Đã mở thư mục',
                        message: `Đã mở thư mục lưu trữ trên máy tính: <code>${data.folder}</code>`,
                        type: 'success',
                        autoCloseMs: 3000
                    });
                } else {
                    showPopup({
                        title: 'Thư mục lưu trữ',
                        message: `Đường dẫn thư mục: <code>${data.folder}</code>`,
                        type: 'info'
                    });
                }
            } catch (e) {
                console.error(e);
            }
        });
    }

    if (btnUploadAudioTrigger) {
        btnUploadAudioTrigger.addEventListener('click', () => {
            if (audioFileInput) audioFileInput.click();
        });
    }

    if (btnUploadAudioDuringMeeting) {
        btnUploadAudioDuringMeeting.addEventListener('click', () => {
            if (audioFileInput) audioFileInput.click();
        });
    }

    if (audioFileInput) {
        audioFileInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            showToast(`Đang nạp file "${file.name}"... Đang tải lên máy chủ và khởi tạo AI phân tích`, 'info');

            // Nếu chưa có phiên họp, khởi tạo ngay
            if (!state.sessionId) {
                await initializeMeetingSession(false);
            }

            const formData = new FormData();
            formData.append('file', file);

            try {
                showToast(`Gemini AI đang nghe và bóc tách chữ thoại từng người từ file...`, 'info');
                const res = await fetch(`/api/meetings/${state.sessionId}/upload-audio`, {
                    method: 'POST',
                    body: formData
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || 'Lỗi khi nhận diện file âm thanh');
                }

                const data = await res.json();
                if (data.transcripts && data.transcripts.length > 0) {
                    transcriptScrollArea.innerHTML = '';
                    state.transcripts = data.transcripts;
                    state.transcripts.forEach(seg => appendTranscriptSegment(seg, false));
                    turnCountBadge.textContent = `${state.transcripts.length} lượt phát biểu`;
                }

                if (data.analysis_state) {
                    state.analysisState = data.analysis_state;
                    renderLiveAnalysis();
                }

                showToast(data.message || 'Phiên âm & bóc tách file ghi âm thành công!', 'success');
            } catch (err) {
                console.error('Lỗi khi tải file âm thanh:', err);
                showToast(err.message || 'Không thể xử lý file ghi âm này', 'warning');
            } finally {
                audioFileInput.value = '';
            }
        });
    }

    async function initializeMeetingSession(isDemo = false) {
        state.meetingTitle = meetingTitleInput.value.trim();
        state.chairperson = chairpersonInput.value.trim();
        state.secretary = secretaryInput.value.trim();
        state.partnerName = partnerNameInput.value.trim();
        state.partnerReps = partnerRepsInput.value.trim();
        state.storagePath = (storagePathInput && storagePathInput.value.trim()) || "D:\\review_agent\\output\\meetings";
        state.isDemoRunning = isDemo;
        state.transcripts = [];

        try {
            const payload = {
                mode: state.mode,
                title: state.meetingTitle,
                chairperson: state.chairperson,
                secretary: state.secretary,
                participants: state.participants,
                partner_name: state.partnerName,
                audio_source: state.audioSource,
                storage_dir: state.storagePath
            };

            const res = await fetch('/api/meetings/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            state.sessionId = data.session_id;
            state.analysisState = data.analysis_state || {};

            // Update UI Step 2
            liveMeetingTitle.textContent = state.meetingTitle;
            liveModeBadge.textContent = state.mode === 'option_1' ? 'Option 1: Họp Nội Bộ KLP' : 'Option 2: Họp Đối Tác & Khách Hàng';
            liveModeBadge.className = 'mode-pill' + (state.mode === 'option_2' ? ' partner' : '');

            analysisOption1Container.style.display = state.mode === 'option_1' ? 'block' : 'none';
            analysisOption2Container.style.display = state.mode === 'option_2' ? 'block' : 'none';

            transcriptScrollArea.innerHTML = '';
            transcriptScrollArea.appendChild(transcriptEmptyState);
            transcriptEmptyState.style.display = 'block';

            renderLiveAnalysis();
                        renderLiveAnalysis();
            renderActiveSpeakerSelector();
            startTimer();
            setStep(2);

            // Vẽ trạng thái chờ trên canvas sóng âm
            if (window.meetingRecorder && waveformCanvas) {
                window.meetingRecorder.stopSimulation(waveformCanvas);
            }

            if (isDemo) {
                audioSourceText.textContent = 'Demo Mode (Simulated Stream)';
                showToast('Đang chạy mô phỏng cuộc họp mẫu Kim Long Phát theo thời gian thực...', 'success');
                runDemoSimulation();
            } else {
                audioSourceText.textContent = state.audioSource === 'mic_only' ? 'Micro ON' : 'Micro + Hệ Thống ON';
                initRealAudioRecording();
                showToast('Hệ thống đã bắt đầu thu âm và nhận diện giọng nói trực tiếp!', 'success');
            }

        } catch (e) {
            console.error('Lỗi khởi tạo phiên họp:', e);
            showToast('Lỗi kết nối máy chủ khi tạo phiên họp', 'warning');
        }
    }

    // Audio Recording Handler - Chuyển giọng nói thành văn bản thuần (Web Speech API nhả chữ trực tiếp đầy đủ 100%)
    async function initRealAudioRecording() {
        if (!window.meetingRecorder) return;

        window.meetingRecorder.setCurrentSpeaker(state.currentActiveSpeaker || quickSpeakerSelect.value || state.chairperson);

        // Nhận diện giọng nói tiếng Việt trực tiếp (nhả đầy đủ toàn bộ chữ, không nuốt chữ, không độ trễ)
        window.meetingRecorder.onTranscriptCallback = async (text, isFinal) => {
            const speaker = state.currentActiveSpeaker || quickSpeakerSelect.value || state.chairperson || "Người phát biểu";
            if (!isFinal) {
                // Đang nói -> hiển thị trực tiếp chữ chạy theo con trỏ nhấp nháy
                renderInterimLiveBubble(speaker, text);
            } else {
                // Dứt câu -> chốt trọn vẹn toàn bộ câu thoại vào danh sách và gửi lên máy chủ
                removeInterimLiveBubble();
                if (text && text.trim()) {
                    await sendTranscriptToServer(speaker, text.trim());
                }
            }
        };

                window.meetingRecorder.onStatusChange = (status) => {
            if (status === 'active') {
                audioSourceText.textContent = state.audioSource === 'mic_only' ? 'Micro ON (Đang nghe)' : 'Micro + Hệ Thống ON';
                audioSourceText.style.color = '#059669';
                if (recDot) recDot.style.background = '#10b981';
            } else if (status === 'permission_denied') {
                audioSourceText.textContent = 'Micro bị chặn quyền';
                audioSourceText.style.color = '#dc2626';
                if (recDot) recDot.style.background = '#ef4444';
                showPopup({
                    title: 'Chưa Cấp Quyền Microphone',
                    message: 'Trình duyệt đang chặn quyền sử dụng Micro.\n\nQuý Thư ký vui lòng bấm vào biểu tượng Micro/Ổ khóa trên thanh địa chỉ trình duyệt, chọn "Cho phép" (Allow) rồi làm mới lại trang.',
                    type: 'warning',
                    confirmText: 'Đã hiểu'
                });
            } else if (status === 'network_error') {
                audioSourceText.textContent = 'Micro: Đang kết nối lại...';
                audioSourceText.style.color = '#d97706';
            } else if (status === 'paused') {
                audioSourceText.textContent = 'Micro: Tạm dừng';
                audioSourceText.style.color = '#64748b';
            }
        };

        window.meetingRecorder.onAudioLevelChange = (volume) => {
            if (volume > 6) {
                if (recDot) recDot.style.boxShadow = '0 0 8px #10b981';
                audioSourceText.textContent = 'Micro ON (Đang nghe)';
                audioSourceText.style.color = '#059669';
            } else {
                if (recDot) recDot.style.boxShadow = 'none';
                audioSourceText.textContent = 'Micro ON (Chờ nói)';
                audioSourceText.style.color = '#475569';
            }
        };

        // Audio chunk streaming is handled locally via Web Speech API with auto-recovering engine
        window.meetingRecorder.onAudioChunkCallback = null;

        window.meetingRecorder.onRecordingComplete = async (audioBlob) => {
            if (audioBlob && audioBlob.size > 0) {
                state.meetingAudioBlob = audioBlob;
                await uploadFullMeetingAudio(audioBlob);
            }
        };

        try {
            await window.meetingRecorder.startRecording(state.audioSource, waveformCanvas);
            initWebSocket();
        } catch (err) {
            console.warn('Không mở được micro:', err);
            audioSourceText.textContent = 'Micro lỗi / bị chặn';
            audioSourceText.style.color = '#dc2626';
            showPopup({
                title: 'Không Thể Mở Microphone',
                message: 'Không tìm thấy thiết bị Microphone hoặc quyền truy cập bị chặn trên trình duyệt.\n\nQuý Thư ký vui lòng bấm "Cho phép" (Allow) Micro trên thanh địa chỉ, hoặc có thể nhập phát biểu trực tiếp bằng khung nhập nhanh bên dưới.',
                type: 'warning',
                confirmText: 'Đã hiểu'
            });
        }
    }

    async function uploadFullMeetingAudio(blob) {
        if (!blob || !state.sessionId) return;
        const formData = new FormData();
        formData.append('file', blob, `Recording_${state.sessionId}.webm`);
        try {
            const res = await fetch(`/api/meetings/${state.sessionId}/save-audio`, {
                method: 'POST',
                body: formData
            });
            if (res.ok) {
                const data = await res.json();
                state.audioDownloadUrl = data.download_url;
                state.audioFilename = data.filename;
                const meetingAudioStatusText = document.getElementById('meetingAudioStatusText');
                if (meetingAudioStatusText) {
                    const sizeMb = (data.file_size / 1024 / 1024).toFixed(2);
                    meetingAudioStatusText.textContent = `Bản ghi âm (${sizeMb} MB) đã lưu tự động vào máy: output/recordings/${data.filename}`;
                }
                showToast(`✅ Đã lưu file ghi âm toàn bộ cuộc họp (${(data.file_size / 1024 / 1024).toFixed(2)} MB) vào máy!`, 'success');
            }
        } catch (e) {
            console.warn('Lỗi lưu audio lên máy chủ:', e);
        }
    }

    function initWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        state.socket = new WebSocket(`${protocol}//${window.location.host}/ws/meeting`);

        state.socket.onopen = () => {
            state.socket.send(JSON.stringify({
                type: 'join_session',
                session_id: state.sessionId
            }));
        };

        state.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'new_transcript') {
                if (data.segment && data.segment.text && data.segment.text.trim()) {
                    appendTranscriptSegment(data.segment);
                }
            } else if (data.type === 'analysis_updated') {
                state.analysisState = data.analysis_state;
                renderLiveAnalysis();
            }
        };
    }

    // Send Transcript to Backend
    async function sendTranscriptToServer(speaker, text, isBookmark = false, note = "") {
        if (!text || !text.trim()) return;
        const cleanText = text.trim();
        const noiseMarkers = ["[tiếng ồn]", "tiếng ồn", "[im lặng]", "im lặng", "[tiếng thở]", "noise", "silence", "[âm thanh]"];
        if (noiseMarkers.includes(cleanText.toLowerCase()) || cleanText.length < 2) return;

        try {
            const res = await fetch(`/api/meetings/${state.sessionId}/transcript`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    speaker,
                    text: cleanText,
                    is_bookmark: isBookmark,
                    note: note,
                    auto_analyze: false
                })
            });
            const data = await res.json();
            if (data.segment) {
                appendTranscriptSegment(data.segment);
            }
            if (data.analysis_state) {
                state.analysisState = data.analysis_state;
                renderLiveAnalysis();
            }
        } catch (e) {
            console.error('Lỗi gửi transcript:', e);
        }
    }

    // ==================== YOUTUBE LIVE CHAT ENGINE & HELPERS ====================
    function escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(text).replace(/[&<>"']/g, m => map[m]);
    }

    function getSpeakerInitials(speaker) {
        if (!speaker) return 'KLP';
        const words = speaker.trim().split(/\s+/);
        if (words.length === 1) return words[0].substring(0, 2).toUpperCase();
        return (words[words.length - 2][0] + words[words.length - 1][0]).toUpperCase();
    }

    function getSpeakerColorClass(speaker) {
        if (!speaker) return 'avatar-slate';
        const s = speaker.toLowerCase();
        if (s.includes('tổng giám đốc') || s.includes('tgđ') || s.includes('chủ tọa') || s.includes('chủ tịch')) {
            return 'avatar-gold';
        }
        const colors = ['avatar-blue', 'avatar-indigo', 'avatar-teal', 'avatar-emerald', 'avatar-rose', 'avatar-purple'];
        let hash = 0;
        for (let i = 0; i < speaker.length; i++) {
            hash = speaker.charCodeAt(i) + ((hash << 5) - hash);
        }
        return colors[Math.abs(hash) % colors.length];
    }

    function getSpeakerBadge(speaker) {
        if (!speaker) return '';
        const s = speaker.toLowerCase();
        if (s.includes('tổng giám đốc') || s.includes('tgđ')) {
            return '<span class="chat-badge badge-chair">TGĐ</span>';
        }
        if (s.includes('chủ tịch') || s.includes('chủ tọa')) {
            return '<span class="chat-badge badge-chair">Chủ tọa</span>';
        }
        if (s.includes('thư ký')) {
            return '<span class="chat-badge badge-secretary">Thư ký</span>';
        }
        return '';
    }

    // Smart Auto-Scroll Behavior (YouTube Live Chat)
    let userIsScrolledUp = false;

    function checkTranscriptScroll() {
        if (!transcriptScrollArea) return;
        const threshold = 70;
        const distanceFromBottom = transcriptScrollArea.scrollHeight - transcriptScrollArea.scrollTop - transcriptScrollArea.clientHeight;
        userIsScrolledUp = distanceFromBottom > threshold;

        if (btnScrollBottom) {
            if (userIsScrolledUp) {
                btnScrollBottom.classList.remove('hidden');
            } else {
                btnScrollBottom.classList.add('hidden');
            }
        }
    }

    function scrollTranscriptToBottom(force = false) {
        if (!transcriptScrollArea) return;
        if (force || !userIsScrolledUp) {
            requestAnimationFrame(() => {
                transcriptScrollArea.scrollTop = transcriptScrollArea.scrollHeight;
            });
        }
    }

    if (transcriptScrollArea) {
        transcriptScrollArea.addEventListener('scroll', checkTranscriptScroll);
    }

    if (btnScrollBottom) {
        btnScrollBottom.addEventListener('click', () => {
            userIsScrolledUp = false;
            btnScrollBottom.classList.add('hidden');
            scrollTranscriptToBottom(true);
        });
    }

    // Render Real-time Interim Live Streaming Bubble (YouTube Live Chat row)
    function renderInterimLiveBubble(speaker, text) {
        if (!text || !text.trim()) {
            removeInterimLiveBubble();
            return;
        }
        const cleanText = text.trim();
        const noiseMarkers = ["[tiếng ồn]", "tiếng ồn", "[im lặng]", "im lặng", "[tiếng thở]", "noise", "silence", "[âm thanh]"];
        if (noiseMarkers.includes(cleanText.toLowerCase()) || cleanText.length < 2) {
            removeInterimLiveBubble();
            return;
        }

        if (transcriptEmptyState) transcriptEmptyState.style.display = 'none';

        let interimEl = document.getElementById('interimTranscriptBubble');
        const initials = getSpeakerInitials(speaker);
        const colorClass = getSpeakerColorClass(speaker);
        const roleBadge = getSpeakerBadge(speaker);

        if (!interimEl) {
            interimEl = document.createElement('div');
            interimEl.id = 'interimTranscriptBubble';
            interimEl.className = 'chat-row interim-live-row transcript-bubble interim-live-bubble';
            transcriptScrollArea.appendChild(interimEl);
        }

        interimEl.innerHTML = `
            <div class="chat-avatar speaker-avatar ${colorClass}">${initials}</div>
            <div class="chat-body">
                <div class="chat-meta bubble-meta">
                    <span class="chat-author speaker-name">${escapeHtml(speaker)}</span>
                    ${roleBadge}
                    <span class="interim-live-tag interim-pulse-tag"><i class="fa-solid fa-microphone"></i> Đang nói...</span>
                </div>
                <div class="chat-text bubble-text">
                    <em>${escapeHtml(cleanText)}</em><span class="chat-typing-cursor interim-cursor"></span>
                </div>
            </div>
        `;

        scrollTranscriptToBottom();
    }

    function removeInterimLiveBubble() {
        const interimEl = document.getElementById('interimTranscriptBubble');
        if (interimEl) {
            interimEl.remove();
        }
    }

    // Append Transcript to Left Column UI (YouTube Live Chat Row)
    function appendTranscriptSegment(seg) {
        if (!seg || !seg.text || !seg.text.trim()) return;
        const cleanText = seg.text.trim();
        const noiseMarkers = ["[tiếng ồn]", "tiếng ồn", "[im lặng]", "im lặng", "[tiếng thở]", "noise", "silence", "[âm thanh]"];
        if (noiseMarkers.includes(cleanText.toLowerCase()) || cleanText.length < 2) return;

        if (transcriptEmptyState) transcriptEmptyState.style.display = 'none';

        let row = document.getElementById(`transcript-seg-${seg.id}`);
        const isNew = !row;
        if (isNew) {
            row = document.createElement('div');
            row.id = `transcript-seg-${seg.id}`;
        }
        row.className = 'chat-row transcript-bubble' + (seg.is_bookmark ? ' bookmark-hot' : '');

        const initials = getSpeakerInitials(seg.speaker);
        const colorClass = getSpeakerColorClass(seg.speaker);
        const roleBadge = getSpeakerBadge(seg.speaker);
        const isChair = seg.speaker && (seg.speaker.toLowerCase().includes('tổng giám đốc') || seg.speaker.toLowerCase().includes('chủ tịch'));

        row.innerHTML = `
            <div class="chat-avatar speaker-avatar ${colorClass}" title="${escapeHtml(seg.speaker)}">${initials}</div>
            <div class="chat-body">
                <div class="chat-meta bubble-meta">
                    <span class="chat-author speaker-name ${isChair ? 'chairperson' : ''}">${escapeHtml(seg.speaker)}</span>
                    ${roleBadge}
                    <span class="chat-time bubble-time">${seg.timestamp || ''}</span>
                </div>
                <div class="chat-text bubble-text" data-id="${seg.id}">${escapeHtml(cleanText)}</div>
                ${seg.is_bookmark && seg.note ? `
                    <span class="chat-bookmark-quote"><i class="fa-solid fa-bookmark"></i> "${escapeHtml(seg.note)}"</span>
                ` : ''}
            </div>
            <div class="chat-actions bubble-actions">
                <button class="btn-chat-bookmark btn-bubble-bookmark ${seg.is_bookmark ? 'bookmarked' : ''}" 
                        data-id="${seg.id}" 
                        title="${seg.is_bookmark ? 'Bỏ đánh dấu trọng tâm' : 'Đánh dấu trọng tâm đoạn này'}">
                    <i class="${seg.is_bookmark ? 'fa-solid' : 'fa-regular'} fa-bookmark"></i>
                </button>
                <button class="btn-chat-delete btn-bubble-delete" 
                        data-id="${seg.id}" 
                        title="Xóa câu thoại dư/sai này để AI tính toán lại">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
            </div>
        `;

        // Click on individual bookmark button of this bubble
        const btnBookmark = row.querySelector('.btn-chat-bookmark, .btn-bubble-bookmark');
        if (btnBookmark) {
            btnBookmark.addEventListener('click', (e) => {
                e.stopPropagation();
                // Check if user selected any text inside this bubble
                let selectedSnippet = "";
                const selection = window.getSelection();
                if (selection && selection.rangeCount > 0) {
                    const selText = selection.toString().trim();
                    const textEl = row.querySelector('.chat-text, .bubble-text');
                    if (selText && textEl && textEl.contains(selection.anchorNode)) {
                        selectedSnippet = selText;
                    }
                }
                toggleSegmentBookmark(seg.id, selectedSnippet);
            });
        }

        // Xóa câu thoại dư/sai bằng 1-Click (AI tự động tính toán lại)
        const btnDelete = row.querySelector('.btn-chat-delete, .btn-bubble-delete');
        if (btnDelete) {
            btnDelete.addEventListener('click', async (e) => {
                e.stopPropagation();
                const segId = btnDelete.getAttribute('data-id') || seg.id;
                if (!segId) return;

                // Hiệu ứng xóa trượt êm ái
                row.style.transition = 'all 0.25s ease';
                row.style.opacity = '0';
                row.style.transform = 'translateX(-24px)';
                setTimeout(() => {
                    row.remove();
                    if (state.transcripts.length === 0 && transcriptEmptyState) {
                        transcriptEmptyState.style.display = 'block';
                    }
                }, 250);

                // Loại khỏi bộ nhớ transcripts
                state.transcripts = state.transcripts.filter(t => String(t.id) !== String(segId));
                if (turnCountBadge) {
                    turnCountBadge.textContent = `${state.transcripts.length} lượt phát biểu`;
                }

                showToast('Đã xóa câu thoại dư thừa. AI đang tự động tính toán lại...', 'info');

                // Gọi backend xóa và kích hoạt AI phân tích lại
                try {
                    const res = await fetch(`/api/meetings/${state.sessionId}/transcript/${segId}`, {
                        method: 'DELETE'
                    });
                    const data = await res.json();
                    if (data && data.analysis_state) {
                        state.analysisState = data.analysis_state;
                        renderLiveAnalysis();
                    }
                } catch (err) {
                    console.warn('Lỗi khi xóa transcript trên server:', err);
                }
            });
        }

        if (isNew) {
            // Keep interim row at the very bottom if currently speaking
            const interimEl = document.getElementById('interimTranscriptBubble');
            if (interimEl && interimEl.parentNode === transcriptScrollArea) {
                transcriptScrollArea.insertBefore(row, interimEl);
            } else {
                transcriptScrollArea.appendChild(row);
            }
        }

        scrollTranscriptToBottom();

        const exists = state.transcripts.some(t => t.id === seg.id);
        if (!exists) {
            state.transcripts.push(seg);
        }
        turnCountBadge.textContent = `${state.transcripts.length} lượt phát biểu`;
    }

    // Toggle bookmark for a specific segment
    async function toggleSegmentBookmark(transcriptId, customText = "") {
        if (!state.sessionId) return;
        try {
            const res = await fetch(`/api/meetings/${state.sessionId}/bookmark`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    transcript_id: transcriptId,
                    custom_text: customText
                })
            });
            const data = await res.json();
            const isBookmarked = data.is_bookmark !== undefined ? data.is_bookmark : true;
            const tId = data.transcript_id || transcriptId;

            // Update transcript in local state
            const targetSeg = state.transcripts.find(t => t.id === tId);
            if (targetSeg) {
                targetSeg.is_bookmark = isBookmarked;
                if (customText) targetSeg.note = customText;
            }

            // Update DOM element for this segment
            const bubbleEl = document.getElementById(`transcript-seg-${tId}`);
            if (bubbleEl) {
                bubbleEl.classList.toggle('bookmark-hot', isBookmarked);
                const btn = bubbleEl.querySelector('.btn-bubble-bookmark, .btn-chat-bookmark');
                if (btn) {
                    btn.classList.toggle('bookmarked', isBookmarked);
                    btn.title = isBookmarked ? 'Bỏ đánh dấu trọng tâm' : 'Đánh dấu trọng tâm đoạn này';
                    btn.innerHTML = `<i class="${isBookmarked ? 'fa-solid' : 'fa-regular'} fa-bookmark"></i>`;
                }
                let tag = bubbleEl.querySelector('.bubble-bookmark-tag, .chat-bookmark-tag');
                let quoteEl = bubbleEl.querySelector('.chat-bookmark-quote');
                if (isBookmarked) {
                    const chatBody = bubbleEl.querySelector('.chat-body') || bubbleEl;
                    if (!tag) {
                        tag = document.createElement('div');
                        tag.className = 'chat-bookmark-tag bubble-bookmark-tag';
                        tag.innerHTML = `<i class="fa-solid fa-bookmark"></i> Trọng tâm chỉ đạo`;
                        chatBody.appendChild(tag);
                    }
                    if (customText) {
                        if (!quoteEl) {
                            quoteEl = document.createElement('span');
                            quoteEl.className = 'chat-bookmark-quote';
                            chatBody.appendChild(quoteEl);
                        }
                        quoteEl.textContent = `"${customText}"`;
                    }
                } else {
                    if (tag) tag.remove();
                    if (quoteEl) quoteEl.remove();
                }
            }

            if (data.analysis_state) {
                state.analysisState = data.analysis_state;
                renderLiveAnalysis();
            }
        } catch (e) {
            console.error('Lỗi đánh dấu trọng tâm:', e);
            showToast('Lỗi khi đánh dấu trọng tâm', 'warning');
        }
    }

    // Render Live AI Analysis (Right Column)
    function renderLiveAnalysis() {
        const a = state.analysisState || {};

        if (state.mode === 'option_1') {
            // Goals
            if (a.summary_goals && a.summary_goals.length > 0) {
                aiSummaryGoals.innerHTML = a.summary_goals.map(g => `<li>${g}</li>`).join('');
            } else {
                aiSummaryGoals.innerHTML = '<li style="color:#94a3b8; font-style:italic;">Đang lắng nghe và tổng hợp mục tiêu cuộc họp...</li>';
            }

            // Directions
            if (a.leader_directions && a.leader_directions.length > 0) {
                aiLeaderDirections.innerHTML = a.leader_directions.map(d => `<li>${d}</li>`).join('');
            } else {
                aiLeaderDirections.innerHTML = '<li style="color:#94a3b8; font-style:italic;">Chờ ý kiến chỉ đạo từ Lãnh đạo chủ trì...</li>';
            }

            // Dept Reports
            if (a.department_reports && a.department_reports.length > 0) {
                aiDeptReports.innerHTML = a.department_reports.map(r => `
                    <p style="margin-bottom: 8px;"><strong>• ${r.speaker}:</strong> ${r.content}</p>
                `).join('');
            } else {
                aiDeptReports.innerHTML = '<p class="placeholder-text" style="color:#94a3b8; font-style:italic;">Chưa có phát biểu báo cáo.</p>';
            }

            // Speech Analytics Table
            if (a.speech_analytics && a.speech_analytics.length > 0) {
                tableSpeechAnalytics.innerHTML = a.speech_analytics.map(item => `
                    <tr>
                        <td><strong>${item.speaker}</strong></td>
                        <td style="text-align: center;"><span class="badge" style="background:#eff6ff; color:#2563eb; border:1px solid #bfdbfe; padding:3px 10px; border-radius:999px; font-weight:700; font-size:12px;">${item.ratio_percent}%</span></td>
                        <td>${item.key_points || ''}</td>
                        <td><span style="background:#ecfdf5; color:#059669; border:1px solid #a7f3d0; padding:3px 9px; border-radius:6px; font-weight:600; font-size:12px;">${item.attitude || 'Tích cực'}</span></td>
                        <td><span style="background:#f1f5f9; color:#334155; border:1px solid #e2e8f0; padding:3px 9px; border-radius:6px; font-weight:600; font-size:12px;">${item.contribution_eval || ''}</span></td>
                    </tr>
                `).join('');
            } else {
                tableSpeechAnalytics.innerHTML = '<tr><td colspan="5" class="text-center" style="color:#94a3b8; font-style:italic; padding:14px;">Chưa có dữ liệu thống kê phát biểu.</td></tr>';
            }

            // Agreed & Pending
            if (a.agreed_issues && a.agreed_issues.length > 0) {
                aiAgreedIssues.innerHTML = a.agreed_issues.map(ag => `<li>${ag}</li>`).join('');
            } else {
                aiAgreedIssues.innerHTML = '<li style="color:#94a3b8; font-style:italic;">Chưa có quyết định được chốt.</li>';
            }

            if (a.pending_issues && a.pending_issues.length > 0) {
                aiPendingIssues.innerHTML = a.pending_issues.map(pe => `<li>${pe}</li>`).join('');
            } else {
                aiPendingIssues.innerHTML = '<li style="color:#94a3b8; font-style:italic;">Không có vấn đề vướng mắc.</li>';
            }

            // Hot Bookmarks
            if (a.hot_bookmarks && a.hot_bookmarks.length > 0) {
                aiHotBookmarksList.innerHTML = a.hot_bookmarks.map(bm => `
                    <li class="bookmark-item">
                        <strong>[${bm.timestamp}] ${bm.speaker}:</strong> "${bm.content}"
                    </li>
                `).join('');
            } else {
                aiHotBookmarksList.innerHTML = '<li class="placeholder-text" style="color:#94a3b8; font-style:italic;">Chưa có mốc đánh dấu nào. Thư ký bấm nút "Đánh dấu trọng tâm" để lưu mốc quan trọng.</li>';
            }

            // Action Items
            if (a.action_items && a.action_items.length > 0) {
                tableActionItems.innerHTML = a.action_items.map(act => `
                    <tr>
                        <td style="text-align: center;"><span style="display:inline-flex; align-items:center; justify-content:center; width:26px; height:26px; border-radius:6px; background:#f1f5f9; font-weight:700; font-family:var(--font-mono); font-size:12px; color:#475569;">${act.stt}</span></td>
                        <td><strong style="color:#0f172a;">${act.task}</strong></td>
                        <td><strong style="color:#1e40af;">${act.pic}</strong></td>
                        <td><span style="color:#475569;">${act.coordinating_dept}</span></td>
                        <td><span style="background:#fffbeb; color:#b45309; border:1px solid #fde68a; padding:3px 8px; border-radius:6px; font-weight:600; font-size:12px;">${act.deadline}</span></td>
                        <td><span style="color:#0f766e; font-weight:600;">${act.kpi}</span></td>
                    </tr>
                `).join('');
            } else {
                tableActionItems.innerHTML = '<tr><td colspan="6" class="text-center" style="color:#94a3b8; font-style:italic; padding:18px;">Chưa có đầu việc phân công. Hệ thống sẽ tự động bóc tách khi các đại biểu giao việc.</td></tr>';
            }

        } else {
            // Option 2 Rendering
            const conf = a.confidential_internal || {};
            const score = conf.deal_score || '--';
            dealScoreValue.textContent = score;
            dealScoreDesc.textContent = conf.deal_score_explanation || 'Đang theo dõi tiến trình thương thảo...';

            if (a.customer_pain_points && a.customer_pain_points.length > 0) {
                aiCustomerPains.innerHTML = a.customer_pain_points.map(p => `<li>${p}</li>`).join('');
            } else {
                aiCustomerPains.innerHTML = '<li style="color:#94a3b8; font-style:italic;">Chưa ghi nhận nhu cầu cụ thể...</li>';
            }

            if (a.klp_proposals && a.klp_proposals.length > 0) {
                aiKlpProposals.innerHTML = a.klp_proposals.map(k => `<li>${k}</li>`).join('');
            } else {
                aiKlpProposals.innerHTML = '<li style="color:#94a3b8; font-style:italic;">Chưa ghi nhận đề xuất cụ thể...</li>';
            }

            if (a.commercial_terms && a.commercial_terms.length > 0) {
                tableCommercialTerms.innerHTML = a.commercial_terms.map(c => `
                    <tr>
                        <td><strong>${c.term_name}</strong></td>
                        <td>${c.klp_offer}</td>
                        <td>${c.partner_demand}</td>
                        <td class="text-center"><span class="badge" style="background:#e0e7ff; color:#3730a3; padding:3px 8px; border-radius:4px; font-weight:bold;">${c.status}</span></td>
                    </tr>
                `).join('');
            } else {
                tableCommercialTerms.innerHTML = '<tr><td colspan="4" class="text-center" style="color:#94a3b8; font-style:italic; padding:14px;">Chưa có điều khoản thương mại phát sinh.</td></tr>';
            }

            if (conf.buying_signals && conf.buying_signals.length > 0) {
                aiBuyingSignals.innerHTML = conf.buying_signals.map(b => `<li>${b}</li>`).join('');
            } else {
                aiBuyingSignals.innerHTML = '<li style="color:#94a3b8; font-style:italic;">Chưa có tín hiệu ghi nhận.</li>';
            }

            if (conf.objections_and_red_flags && conf.objections_and_red_flags.length > 0) {
                aiObjections.innerHTML = conf.objections_and_red_flags.map(o => `<li>${o}</li>`).join('');
            } else {
                aiObjections.innerHTML = '<li style="color:#94a3b8; font-style:italic;">Không phát hiện rủi ro hay phản đối.</li>';
            }

            if (conf.partner_speakers_analysis && conf.partner_speakers_analysis.length > 0) {
                aiPartnerSpeakers.innerHTML = conf.partner_speakers_analysis.map(s => `
                    <li><strong>${s.speaker} [${s.role_category}]:</strong> ${s.assessment}</li>
                `).join('');
            } else {
                aiPartnerSpeakers.innerHTML = '<li style="color:#94a3b8; font-style:italic;">Đang lắng nghe đối tác trao đổi...</li>';
            }

            if (a.follow_up_plan && a.follow_up_plan.length > 0) {
                tableFollowUp.innerHTML = a.follow_up_plan.map(f => `
                    <tr>
                        <td><strong>${f.party}</strong></td>
                        <td>${f.task}</td>
                        <td>${f.pic}</td>
                        <td>${f.deadline}</td>
                        <td class="text-center"><span style="color:#b91c1c; font-weight:bold;">${f.priority}</span></td>
                    </tr>
                `).join('');
            } else {
                tableFollowUp.innerHTML = '<tr><td colspan="5" class="text-center" style="color:#94a3b8; font-style:italic; padding:14px;">Chưa có kế hoạch hành động tiếp theo.</td></tr>';
            }
        }
    }

    // Hot Bookmark Button (F2 or Ctrl+B or Click)
    btnHotBookmark.addEventListener('click', () => {
        triggerHotBookmark();
    });

    document.addEventListener('keydown', (e) => {
        if (state.currentStep === 2) {
            if (e.key === 'F2' || (e.ctrlKey && e.key === 'b')) {
                e.preventDefault();
                triggerHotBookmark();
            }
        }
    });

    async function triggerHotBookmark() {
        if (!state.sessionId) return;
        const latestSeg = state.transcripts.length > 0 ? state.transcripts[state.transcripts.length - 1] : null;
        const targetId = latestSeg ? latestSeg.id : null;
        await toggleSegmentBookmark(targetId, "");
    }

    // Secretary Note Dock
    btnSendSecretaryNote.addEventListener('click', async () => {
        const text = secretaryNoteInput.value.trim();
        if (!text || !state.sessionId) return;

        try {
            await fetch(`/api/meetings/${state.sessionId}/note`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ note: text })
            });
            showToast(`Ghi chú đã được chuyển vào AI phân tích!`, 'info');
            secretaryNoteInput.value = '';
            // Kích hoạt phân tích ngay
            triggerAIAnalysis();
        } catch (e) {
            console.error('Lỗi gửi note:', e);
        }
    });

    secretaryNoteInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            btnSendSecretaryNote.click();
        }
    });

    // Quick Manual Text Input
    btnSendQuickText.addEventListener('click', async () => {
        const text = quickTextInput.value.trim();
        const speaker = state.currentActiveSpeaker || quickSpeakerSelect.value || "Người phát biểu";
        if (!text || !state.sessionId) return;

        await sendTranscriptToServer(speaker, text);
        quickTextInput.value = '';
    });

    quickTextInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            btnSendQuickText.click();
        }
    });

    // Pause / Resume Meeting
    btnPauseMeeting.addEventListener('click', () => {
        state.isPaused = !state.isPaused;
        if (state.isPaused) {
            btnPauseMeeting.innerHTML = '<i class="fa-solid fa-play"></i> Tiếp tục';
            btnPauseMeeting.className = 'btn btn-primary';
            recDot.style.animationPlayState = 'paused';
            if (window.meetingRecorder) window.meetingRecorder.pauseRecording();
            showToast('Đã tạm dừng cuộc họp.', 'warning');
        } else {
            btnPauseMeeting.innerHTML = '<i class="fa-solid fa-pause"></i> Tạm dừng';
            btnPauseMeeting.className = 'btn btn-warning';
            recDot.style.animationPlayState = 'running';
            if (window.meetingRecorder) window.meetingRecorder.resumeRecording();
            showToast('Tiếp tục ghi âm và phân tích.', 'info');
        }
    });

    // Trigger AI Analysis Manually
    btnTriggerAnalyze.addEventListener('click', () => {
        triggerAIAnalysis();
    });

    async function triggerAIAnalysis() {
        if (!state.sessionId) return;
        btnTriggerAnalyze.disabled = true;
        btnTriggerAnalyze.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> AI đang phân tích...';

        try {
            const res = await fetch(`/api/meetings/${state.sessionId}/analyze`, { method: 'POST' });
            const data = await res.json();
            if (data.analysis_state) {
                state.analysisState = data.analysis_state;
                renderLiveAnalysis();
                showToast('Bản phân tích trực tiếp đã được cập nhật!', 'success');
            }
        } catch (e) {
            console.error('Lỗi phân tích:', e);
        } finally {
            btnTriggerAnalyze.disabled = false;
            btnTriggerAnalyze.innerHTML = '<i class="fa-solid fa-brain"></i> AI Cập nhật ngay';
        }
    }

    // End Meeting & Proceed to Step 3
    btnEndMeeting.addEventListener('click', () => {
        if (!state.sessionId) return;
        showPopup({
            title: 'Kết thúc cuộc họp?',
            message: 'Bạn có chắc chắn muốn kết thúc phiên họp trực tiếp để chuyển sang <strong>Bước 3: Rà soát & Xuất File Word</strong> không?<br><br>Toàn bộ âm thanh, băng chữ thoại và phân tích sẽ được tổng hợp và lưu trữ an toàn vào máy tính.',
            type: 'warning',
            confirmText: 'Kết thúc & Rà soát',
            cancelText: 'Hủy bỏ',
            onConfirm: async () => {
                stopTimer();
                if (window.meetingRecorder) {
                    const finalBlob = window.meetingRecorder.stopRecording();
                    if (finalBlob && finalBlob.size > 0) {
                        state.meetingAudioBlob = finalBlob;
                        await uploadFullMeetingAudio(finalBlob);
                    }
                }

                setStep(3);
                showToast('Đang chốt bản phân tích cuộc họp...', 'info');
                try {
                    const res = await fetch(`/api/meetings/${state.sessionId}/end`, { method: 'POST' });
                    const data = await res.json();
                    if (data.analysis_state) {
                        state.analysisState = data.analysis_state;
                    }
                    if (data.transcript_info) {
                        state.transcriptDownloadUrl = data.transcript_info.download_url;
                        state.transcriptFilename = data.transcript_info.filename;
                        state.transcriptTextContent = data.transcript_info.text_content;
                    }
                } catch (e) {
                    console.warn('Lỗi chốt phân tích:', e);
                }
                prepareStep3Review();
            }
        });
    });

    // Step 3: Prepare Review
    async function prepareStep3Review() {
        option1ExportBtns.style.display = state.mode === 'option_1' ? 'flex' : 'none';
        option2ExportBtns.style.display = state.mode === 'option_2' ? 'flex' : 'none';

        // Nếu là Option 2 (Họp Khách hàng & Đối tác): Ẩn hoàn toàn Card Ghi âm âm thanh
        const audioArchiveCard = document.querySelector('.archive-file-card.file-audio');
        if (audioArchiveCard) {
            audioArchiveCard.style.display = state.mode === 'option_2' ? 'none' : 'block';
        }
        const btnUploadDuringMeeting = document.getElementById('btnUploadAudioDuringMeeting');
        if (btnUploadDuringMeeting) {
            btnUploadDuringMeeting.style.display = state.mode === 'option_2' ? 'none' : 'inline-flex';
        }

        const displayStoragePath = document.getElementById('displayStoragePath');
        if (displayStoragePath) {
            displayStoragePath.textContent = state.storagePath || "D:\\review_agent\\output\\meetings";
        }

        const meetingAudioPlayer = document.getElementById('meetingAudioPlayer');
        const btnDownloadMeetingAudio = document.getElementById('btnDownloadMeetingAudio');
        const btnDownloadMeetingTranscript = document.getElementById('btnDownloadMeetingTranscript');
        const meetingAudioStatusText = document.getElementById('meetingAudioStatusText');
        const audioFileName = document.getElementById('audioFileName');
        const audioFileSizeBadge = document.getElementById('audioFileSizeBadge');
        const transcriptFileName = document.getElementById('transcriptFileName');
        const textFileSizeBadge = document.getElementById('textFileSizeBadge');
        const wordFileName = document.getElementById('wordFileName');

        if (audioFileName) {
            audioFileName.textContent = state.audioFilename || `GhiAm_${state.sessionId || 'KLP'}.webm`;
        }
        if (transcriptFileName) {
            transcriptFileName.textContent = state.transcriptFilename || `ChuThoai_${state.sessionId || 'KLP'}.txt`;
        }
        if (wordFileName) {
            wordFileName.textContent = state.mode === 'option_1' ? `BienBan_GiaoBan_${state.sessionId || 'KLP'}.docx` : `BienBan_DamPhan_${state.sessionId || 'KLP'}.docx`;
        }

        if (state.meetingAudioBlob && meetingAudioPlayer) {
            const audioUrl = URL.createObjectURL(state.meetingAudioBlob);
            meetingAudioPlayer.src = audioUrl;

            const sizeMb = (state.meetingAudioBlob.size / 1024 / 1024).toFixed(2);
            if (audioFileSizeBadge) audioFileSizeBadge.textContent = `${sizeMb} MB`;
            if (meetingAudioStatusText) {
                meetingAudioStatusText.textContent = `Bản ghi âm (${sizeMb} MB) và đoạn text chữ thoại nguyên văn đã được lưu tự động vào máy tính.`;
            }

            if (btnDownloadMeetingAudio) {
                btnDownloadMeetingAudio.onclick = () => {
                    const a = document.createElement('a');
                    a.href = state.audioDownloadUrl || audioUrl;
                    a.download = state.audioFilename || `GhiAm_${state.sessionId}.webm`;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    showPopup({
                        title: 'Đang tải tệp',
                        message: `Đang tải file ghi âm đầy đủ (${sizeMb} MB) về máy...`,
                        type: 'info'
                    });
                };
            }
        } else if (meetingAudioStatusText) {
            meetingAudioStatusText.textContent = 'Hồ sơ cuộc họp (bản text chữ thoại nguyên văn và biên bản Word) đã được lưu vào thư mục trên máy tính.';
            if (btnDownloadMeetingAudio) {
                btnDownloadMeetingAudio.onclick = () => {
                    if (state.audioDownloadUrl) {
                        const a = document.createElement('a');
                        a.href = state.audioDownloadUrl;
                        a.download = state.audioFilename || `GhiAm_${state.sessionId}.webm`;
                        document.body.appendChild(a);
                        a.click();
                        a.remove();
                    } else {
                        showPopup({
                            title: 'Thông báo ghi âm',
                            message: 'Không tìm thấy file ghi âm trực tiếp cho phiên demo.',
                            type: 'info'
                        });
                    }
                };
            }
        }

        if (textFileSizeBadge) {
            textFileSizeBadge.textContent = `${(state.transcripts || []).length} lượt thoại`;
        }

        // Hook nút tải file text chữ thoại nguyên văn
        if (btnDownloadMeetingTranscript) {
            btnDownloadMeetingTranscript.onclick = () => {
                if (state.transcriptDownloadUrl) {
                    const a = document.createElement('a');
                    a.href = state.transcriptDownloadUrl;
                    a.download = state.transcriptFilename || `ChuThoai_${state.sessionId}.txt`;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    showPopup({
                        title: 'Tải văn bản nguyên văn',
                        message: 'Đang tải file text chữ thoại nguyên văn về máy...',
                        type: 'success'
                    });
                } else {
                    let content = `CÔNG TY CỔ PHẦN TẬP ĐOÀN KIM LONG PHÁT\nBĂNG GHI CHỮ THOẠI NGUYÊN VĂN BÓC TÁCH TỪ FILE GHI ÂM\n\n`;
                    (state.transcripts || []).forEach(t => {
                        content += `[${t.timestamp}] ${t.speaker}:\n  ${t.text}\n\n`;
                    });
                    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(blob);
                    a.download = `ChuThoai_${state.sessionId || 'CuocHop'}.txt`;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    showPopup({
                        title: 'Đã xuất file text',
                        message: 'Đã tạo và tải file text chữ thoại nguyên văn thành công!',
                        type: 'success'
                    });
                }
            };
        }

        // Lấy thông tin các file đã lưu từ backend
        if (state.sessionId) {
            try {
                const res = await fetch(`/api/meetings/${state.sessionId}/files`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.storage_dir && displayStoragePath) {
                        displayStoragePath.textContent = data.storage_dir;
                        state.storagePath = data.storage_dir;
                    }
                    if (data.files) {
                        const fileMap = {};
                        if (Array.isArray(data.files)) {
                            data.files.forEach(f => { if (f && f.type) fileMap[f.type] = f; });
                        } else {
                            Object.assign(fileMap, data.files);
                        }

                        if (fileMap.audio) {
                            if (audioFileName && fileMap.audio.filename) audioFileName.textContent = fileMap.audio.filename;
                            if (audioFileSizeBadge) {
                                audioFileSizeBadge.textContent = fileMap.audio.size_mb ? `${fileMap.audio.size_mb} MB` : (fileMap.audio.size_kb > 0 ? `${(fileMap.audio.size_kb / 1024).toFixed(2)} MB` : 'Đã lưu trữ');
                            }
                            if (fileMap.audio.download_url) state.audioDownloadUrl = fileMap.audio.download_url;
                        }
                        if (fileMap.transcript_txt) {
                            if (transcriptFileName && fileMap.transcript_txt.filename) transcriptFileName.textContent = fileMap.transcript_txt.filename;
                            if (textFileSizeBadge) {
                                textFileSizeBadge.textContent = fileMap.transcript_txt.size_kb > 0 ? `${fileMap.transcript_txt.size_kb} KB` : `${(state.transcripts || []).length} lượt thoại`;
                            }
                            if (fileMap.transcript_txt.download_url) state.transcriptDownloadUrl = fileMap.transcript_txt.download_url;
                        }
                        if (fileMap.word_docx) {
                            if (wordFileName && fileMap.word_docx.filename) wordFileName.textContent = fileMap.word_docx.filename;
                        }
                    }
                }
            } catch (err) {
                console.warn('Lỗi tải danh sách file lưu trữ:', err);
            }
        }

        renderDocumentPreview();
    }

    // Thu thập toàn bộ nội dung mà người dùng vừa chỉnh sửa trực tiếp trên màn hình xem trước
    function collectEditedAnalysisFromDOM() {
        if (!state.analysisState) state.analysisState = {};
        const paper = document.querySelector('.word-paper');
        if (!paper) return state.analysisState;

        if (state.mode === 'option_1') {
            // 1. Tiêu đề cuộc họp
            const titleEl = paper.querySelector('.doc-editable-title');
            if (titleEl) {
                const rawTitle = titleEl.textContent.replace(/^Về việc:\s*/i, '').trim();
                if (rawTitle) state.analysisState.meeting_title = rawTitle;
            }

            // 2. Tóm tắt mục tiêu
            const goalEls = paper.querySelectorAll('.doc-editable-goals li');
            if (goalEls.length > 0) {
                state.analysisState.summary_goals = Array.from(goalEls).map(el => el.textContent.trim()).filter(Boolean);
            }

            // 3. Ý kiến chỉ đạo
            const dirEls = paper.querySelectorAll('.doc-editable-directions li');
            if (dirEls.length > 0) {
                state.analysisState.leader_directions = Array.from(dirEls).map(el => el.textContent.trim()).filter(Boolean);
            }

            // 4. Các vấn đề ĐÃ THỐNG NHẤT
            const agreedEls = paper.querySelectorAll('.doc-editable-agreed li');
            if (agreedEls.length > 0) {
                state.analysisState.agreed_issues = Array.from(agreedEls).map(el => el.textContent.trim()).filter(Boolean);
            }

            // 5. Các vấn đề CÒN TỒN ĐỌNG
            const pendingEls = paper.querySelectorAll('.doc-editable-pending li');
            if (pendingEls.length > 0) {
                state.analysisState.pending_issues = Array.from(pendingEls).map(el => el.textContent.trim()).filter(Boolean);
            }

            // 6. Bảng phân công Action items
            const actionRows = paper.querySelectorAll('.doc-action-row');
            if (actionRows.length > 0) {
                const items = [];
                actionRows.forEach((row, idx) => {
                    const stt = row.querySelector('[data-field="stt"]')?.textContent.trim() || String(idx + 1);
                    const task = row.querySelector('[data-field="task"]')?.textContent.trim() || '';
                    const pic = row.querySelector('[data-field="pic"]')?.textContent.trim() || '';
                    const coordinating = row.querySelector('[data-field="coordinating_dept"]')?.textContent.trim() || '';
                    const deadline = row.querySelector('[data-field="deadline"]')?.textContent.trim() || '';
                    const kpi = row.querySelector('[data-field="kpi"]')?.textContent.trim() || '';
                    if (task) {
                        items.push({ stt, task, pic, coordinating_dept: coordinating, deadline, kpi });
                    }
                });
                if (items.length > 0) state.analysisState.action_items = items;
            }
        } else {
            // Option 2 (Đàm phán Khách hàng & Đối tác)
            const titleEl = paper.querySelector('.doc-editable-title');
            if (titleEl) {
                const rawTitle = titleEl.textContent.replace(/^Dự án:\s*/i, '').trim();
                if (rawTitle) state.analysisState.project_title = rawTitle;
            }

            const painEls = paper.querySelectorAll('.doc-editable-pain-points li');
            if (painEls.length > 0) {
                state.analysisState.customer_pain_points = Array.from(painEls).map(el => el.textContent.trim()).filter(Boolean);
            }

            const propEls = paper.querySelectorAll('.doc-editable-proposals li');
            if (propEls.length > 0) {
                state.analysisState.klp_proposals = Array.from(propEls).map(el => el.textContent.trim()).filter(Boolean);
            }

            const termRows = paper.querySelectorAll('.doc-commercial-row');
            if (termRows.length > 0) {
                const terms = [];
                termRows.forEach(row => {
                    const term_name = row.querySelector('[data-field="term_name"]')?.textContent.trim() || '';
                    const klp_offer = row.querySelector('[data-field="klp_offer"]')?.textContent.trim() || '';
                    const partner_demand = row.querySelector('[data-field="partner_demand"]')?.textContent.trim() || '';
                    const status = row.querySelector('[data-field="status"]')?.textContent.trim() || 'Thống nhất';
                    if (term_name) {
                        terms.push({ term_name, klp_offer, partner_demand, status });
                    }
                });
                if (terms.length > 0) state.analysisState.commercial_terms = terms;
            }

            if (!state.analysisState.confidential_internal) state.analysisState.confidential_internal = {};
            const sigEls = paper.querySelectorAll('.doc-editable-signals li');
            if (sigEls.length > 0) {
                state.analysisState.confidential_internal.buying_signals = Array.from(sigEls).map(el => el.textContent.trim()).filter(Boolean);
            }
            const redEls = paper.querySelectorAll('.doc-editable-red-flags li');
            if (redEls.length > 0) {
                state.analysisState.confidential_internal.objections_and_red_flags = Array.from(redEls).map(el => el.textContent.trim()).filter(Boolean);
            }

            const followRows = paper.querySelectorAll('.doc-followup-row');
            if (followRows.length > 0) {
                const followups = [];
                followRows.forEach(row => {
                    const party = row.querySelector('[data-field="party"]')?.textContent.trim() || '';
                    const task = row.querySelector('[data-field="task"]')?.textContent.trim() || '';
                    const pic = row.querySelector('[data-field="pic"]')?.textContent.trim() || '';
                    const deadline = row.querySelector('[data-field="deadline"]')?.textContent.trim() || '';
                    const priority = row.querySelector('[data-field="priority"]')?.textContent.trim() || 'Cao';
                    if (task) {
                        followups.push({ party, task, pic, deadline, priority });
                    }
                });
                if (followups.length > 0) state.analysisState.follow_up_plan = followups;
            }
        }
        return state.analysisState;
    }

    function renderDocumentPreview() {
        const a = state.analysisState || {};
        const today = new Date().toLocaleDateString('vi-VN');

        const editorToolbarHtml = `
            <div class="doc-editor-toolbar">
                <div class="editor-hint">
                    <i class="fa-solid fa-pen-to-square"></i>
                    <span><strong>Chế độ Soạn thảo Trực tiếp:</strong> Quý Thư ký có thể bấm trực tiếp vào bất kỳ dòng văn bản, mục tiêu, chỉ đạo hoặc bảng phân công để chỉnh sửa trực tiếp trên màn hình. Bản tải về sẽ áp dụng 100% nội dung đã sửa.</span>
                </div>
            </div>
        `;

        let html = editorToolbarHtml;
        if (state.mode === 'option_1') {
            html += `
                <div class="word-paper">
                    <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
                        <div style="text-align:center; font-size:11pt; line-height:1.3;">
                            <strong>CÔNG TY CỔ PHẦN TẬP ĐOÀN<br>KIM LONG PHÁT</strong><br>
                            <em>Số: .../2026/BBH-KLP</em>
                        </div>
                        <div style="text-align:center; font-size:11pt; line-height:1.3;">
                            <strong>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM<br>Độc lập - Tự do - Hạnh phúc</strong><br>
                            <em>TP. Hồ Chí Minh, ngày ${new Date().getDate()} tháng ${new Date().getMonth()+1} năm ${new Date().getFullYear()}</em>
                        </div>
                    </div>

                    <h2>BIÊN BẢN CUỘC HỌP NỘI BỘ</h2>
                    <h3 class="doc-editable-title" contenteditable="true" title="Bấm để sửa tiêu đề">Về việc: ${a.meeting_title || state.meetingTitle}</h3>

                    <div class="section-heading">I. THÔNG TIN CHUNG & THÀNH PHẦN THAM DỰ</div>
                    <table>
                        <tr><td style="width:30%; background:#f4f4f5;"><strong>1. Thời gian & Hình thức:</strong></td><td contenteditable="true">${new Date().toLocaleDateString('vi-VN')} | ${state.audioSource === 'mic_only' ? 'Trực tiếp tại phòng họp' : 'Trực tiếp kết hợp Online Zoom'}</td></tr>
                        <tr><td style="background:#f4f4f5;"><strong>2. Chủ trì cuộc họp:</strong></td><td contenteditable="true">${state.chairperson}</td></tr>
                        <tr><td style="background:#f4f4f5;"><strong>3. Thư ký cuộc họp:</strong></td><td contenteditable="true">${state.secretary}</td></tr>
                        <tr><td style="background:#f4f4f5;"><strong>4. Thành phần tham dự:</strong></td><td contenteditable="true">${(Array.isArray(state.participants) && state.participants.length > 0 ? state.participants : ['Bà Phan Thị Phát (Tổng Giám Đốc)', 'Ông Nguyễn Kim Long (Chủ tịch HĐQT)', 'Ông Trần Văn Hùng (Phó TGĐ)', 'Bà Lê Thu Thảo (Thư ký)']).join('<br>')}</td></tr>
                    </table>

                    <div class="section-heading">II. NỘI DUNG CHỈ ĐẠO & PHÂN TÍCH PHÁT BIỂU</div>
                    <p><strong>1. Tóm tắt mục tiêu trọng tâm:</strong></p>
                    <ul class="doc-editable-goals">${(a.summary_goals || ['Đang tổng hợp mục tiêu...']).map(g => `<li contenteditable="true" title="Bấm để sửa mục tiêu">${g}</li>`).join('')}</ul>

                    <p><strong>2. Ý kiến chỉ đạo của Chủ trì (Ban Lãnh Đạo):</strong></p>
                    <ul class="doc-editable-directions">${(a.leader_directions || ['Đang tổng hợp ý kiến chỉ đạo...']).map(d => `<li contenteditable="true" title="Bấm để sửa ý kiến chỉ đạo">${d}</li>`).join('')}</ul>

                    <p><strong>Bảng Phân tích Thoại & Đánh giá Đóng góp:</strong></p>
                    <table>
                        <tr><th>Người tham gia</th><th>Tỷ lệ (%)</th><th>Luận điểm chính</th><th>Thái độ</th><th>Đánh giá</th></tr>
                        ${(a.speech_analytics || []).map(s => `
                            <tr>
                                <td><strong>${s.speaker}</strong></td>
                                <td style="text-align:center;" contenteditable="true">${s.ratio_percent}%</td>
                                <td contenteditable="true">${s.key_points || ''}</td>
                                <td contenteditable="true">${s.attitude || ''}</td>
                                <td contenteditable="true">${s.contribution_eval || ''}</td>
                            </tr>
                        `).join('')}
                    </table>

                    <div class="section-heading">III. ĐÁNH GIÁ KẾT QUẢ CUỘC HỌP</div>
                    <p><strong>✅ Các vấn đề ĐÃ THỐNG NHẤT:</strong></p>
                    <ul class="doc-editable-agreed">${(a.agreed_issues || ['Đang cập nhật...']).map(ai => `<li contenteditable="true" title="Bấm để sửa">${ai}</li>`).join('')}</ul>

                    <p><strong>⏳ Các vấn đề CÒN TỒN ĐỌNG:</strong></p>
                    <ul class="doc-editable-pending">${(a.pending_issues || ['Không có tồn đọng phát sinh.']).map(pi => `<li contenteditable="true" title="Bấm để sửa">${pi}</li>`).join('')}</ul>

                    <div class="section-heading">IV. BẢNG PHÂN CÔNG CÔNG VIỆC (ACTION ITEMS)</div>
                    <table>
                        <tr><th>STT</th><th>Đầu việc cụ thể</th><th>Phụ trách (PIC)</th><th>Phối hợp</th><th>Thời hạn</th><th>KPI đầu ra</th></tr>
                        ${(a.action_items || [
                            { stt: '1', task: 'Triển khai công việc theo đúng chỉ đạo ban TGĐ', pic: 'Các bộ phận liên quan', coordinating_dept: 'Ban TGĐ', deadline: 'Trong tuần', kpi: 'Hoàn thành 100%' }
                        ]).map(act => `
                            <tr class="doc-action-row">
                                <td style="text-align:center;" contenteditable="true" data-field="stt">${act.stt}</td>
                                <td><strong contenteditable="true" data-field="task">${act.task}</strong></td>
                                <td contenteditable="true" data-field="pic">${act.pic}</td>
                                <td contenteditable="true" data-field="coordinating_dept">${act.coordinating_dept}</td>
                                <td contenteditable="true" data-field="deadline">${act.deadline}</td>
                                <td contenteditable="true" data-field="kpi">${act.kpi}</td>
                            </tr>
                        `).join('')}
                    </table>

                    <div class="section-heading" style="margin-top:24px;">V. PHỤ LỤC: BĂNG GHI CHỮ THOẠI NGUYÊN VĂN TỪ BẢN GHI ÂM</div>
                    <table>
                        <tr>
                            <th style="width:40px; text-align:center;">STT</th>
                            <th style="width:75px; text-align:center;">Thời gian</th>
                            <th style="width:170px;">Người phát biểu</th>
                            <th>Lời phát biểu nguyên văn</th>
                        </tr>
                        ${(state.transcripts || []).map((t, idx) => `
                            <tr>
                                <td style="text-align:center;">${idx + 1 < 10 ? '0' + (idx + 1) : idx + 1}</td>
                                <td style="text-align:center;">${t.timestamp}</td>
                                <td><strong>${t.speaker}</strong> ${t.is_bookmark ? '<span class="doc-bookmark-badge"><i class="fa-solid fa-bookmark"></i> [Trọng tâm]</span>' : ''}</td>
                                <td contenteditable="true">${t.text} ${t.note ? `<br><small style="color:#64748b; font-style:italic;">-> Ghi chú: ${t.note}</small>` : ''}</td>
                            </tr>
                        `).join('')}
                    </table>

                    <div style="display:flex; justify-content:space-between; margin-top:40px; text-align:center;">
                        <div style="width:45%;">
                            <strong>THƯ KÝ CUỘC HỌP</strong><br><em>(Ký và ghi rõ họ tên)</em><br><br><br><br>
                            <strong>${state.secretary}</strong>
                        </div>
                        <div style="width:45%;">
                            <strong>CHỦ TRÌ CUỘC HỌP</strong><br><em>(Ký và ghi rõ họ tên)</em><br><br><br><br>
                            <strong>${state.chairperson}</strong>
                        </div>
                    </div>
                </div>
            `;
        } else {
            // Option 2 Preview
            const conf = a.confidential_internal || {};
            html += `
                <div class="word-paper">
                    <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
                        <div style="text-align:center; font-size:11pt; line-height:1.3;">
                            <strong>CÔNG TY CỔ PHẦN TẬP ĐOÀN<br>KIM LONG PHÁT</strong><br>
                            <em>Văn phòng Ban Tổng Giám Đốc</em>
                        </div>
                        <div style="text-align:center; font-size:11pt; line-height:1.3;">
                            <strong>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM<br>Độc lập - Tự do - Hạnh phúc</strong><br>
                            <em>TP. Hồ Chí Minh, ngày ${new Date().getDate()} tháng ${new Date().getMonth()+1} năm ${new Date().getFullYear()}</em>
                        </div>
                    </div>

                    <h2>BIÊN BẢN LÀM VIỆC & PHÂN TÍCH ĐÀM PHÁN ĐỐI TÁC</h2>
                    <h3 class="doc-editable-title" contenteditable="true" title="Bấm để sửa tiêu đề dự án">Dự án: ${state.meetingTitle}</h3>
                    <p style="text-align:right; color:#991b1b; font-weight:700; font-size:10pt;">[TÀI LIỆU LƯU HÀNH NỘI BỘ - MẬT]</p>

                    <div class="section-heading">PHẦN A. NỘI DUNG LÀM VIỆC CHUNG</div>
                    <table>
                        <tr>
                            <th style="width:50%;">ĐẠI DIỆN KIM LONG PHÁT (BÊN A)</th>
                            <th style="width:50%;">ĐẠI DIỆN ĐỐI TÁC (BÊN B)</th>
                        </tr>
                        <tr>
                            <td contenteditable="true">• Ông Trần Văn Hùng - Phó TGĐ<br>• Ông Đặng Minh Trí - Trưởng BP Kinh Doanh<br>• Thư ký: ${state.secretary}</td>
                            <td contenteditable="true">• Đơn vị: ${state.partnerName}<br>• Đại diện: ${state.partnerReps}</td>
                        </tr>
                    </table>

                    <p><strong>1. Nhu cầu & Pain Points của Đối tác:</strong></p>
                    <ul class="doc-editable-pain-points">${(a.customer_pain_points || ['Đang tổng hợp...']).map(cp => `<li contenteditable="true">${cp}</li>`).join('')}</ul>

                    <p><strong>2. Đề xuất & Giải pháp của Kim Long Phát:</strong></p>
                    <ul class="doc-editable-proposals">${(a.klp_proposals || ['Đang tổng hợp...']).map(kp => `<li contenteditable="true">${kp}</li>`).join('')}</ul>

                    <p><strong>3. Bảng Bóc tách Thông số Thương mại:</strong></p>
                    <table>
                        <tr><th>Hạng mục thương thảo</th><th>Đề xuất của Kim Long Phát</th><th>Phản hồi của Đối tác</th><th>Trạng thái chốt</th></tr>
                        ${(a.commercial_terms || [
                            { term_name: 'Báo giá thiết bị KLP', klp_offer: 'Giá ưu đãi đại lý', partner_demand: 'Chiết khấu bổ sung', status: 'Đang thảo luận' }
                        ]).map(c => `
                            <tr class="doc-commercial-row">
                                <td><strong contenteditable="true" data-field="term_name">${c.term_name}</strong></td>
                                <td contenteditable="true" data-field="klp_offer">${c.klp_offer}</td>
                                <td contenteditable="true" data-field="partner_demand">${c.partner_demand}</td>
                                <td style="text-align:center;"><strong contenteditable="true" data-field="status">${c.status}</strong></td>
                            </tr>
                        `).join('')}
                    </table>

                    <div class="section-heading" style="color:#991b1b;">PHẦN B. PHÂN TÍCH TÂM LÝ ĐÀM PHÁN & LƯU Ý MẬT (CHỈ NỘI BỘ KLP)</div>
                    <p><strong>1. Đánh giá Mức độ Đồng thuận (Deal Score): <span style="font-size:13pt; color:#059669;">${conf.deal_score || '--'}/10</span></strong></p>
                    <p><em contenteditable="true">${conf.deal_score_explanation || ''}</em></p>

                    <p><strong>2. Các tín hiệu đồng thuận & Động lực hợp tác (Buying Signals):</strong></p>
                    <ul class="doc-editable-signals">${(conf.buying_signals || ['Đang ghi nhận...']).map(b => `<li contenteditable="true">${b}</li>`).join('')}</ul>

                    <p><strong>3. Các điểm nghẽn & Vấn đề cần lưu ý (Red Flags):</strong></p>
                    <ul class="doc-editable-red-flags">${(conf.objections_and_red_flags || ['Không có rào cản lớn.']).map(o => `<li contenteditable="true">${o}</li>`).join('')}</ul>

                    <div class="section-heading">PHẦN C. KẾ HOẠCH HÀNH ĐỘNG TIẾP THEO (FOLLOW-UP PLAN)</div>
                    <table>
                        <tr><th>Bên thực hiện</th><th>Nội dung cam kết</th><th>Người phụ trách</th><th>Thời hạn</th><th>Ưu tiên</th></tr>
                        ${(a.follow_up_plan || [
                            { party: 'Kim Long Phát', task: 'Gửi bản chào giá chính thức', pic: 'Phòng Kinh Doanh', deadline: '24 giờ tới', priority: 'Cao' }
                        ]).map(f => `
                            <tr class="doc-followup-row">
                                <td><strong contenteditable="true" data-field="party">${f.party}</strong></td>
                                <td contenteditable="true" data-field="task">${f.task}</td>
                                <td contenteditable="true" data-field="pic">${f.pic}</td>
                                <td contenteditable="true" data-field="deadline">${f.deadline}</td>
                                <td style="text-align:center;" contenteditable="true" data-field="priority">${f.priority}</td>
                            </tr>
                        `).join('')}
                    </table>

                    <div class="section-heading" style="margin-top:24px;">V. PHỤ LỤC: BĂNG GHI CHỮ THOẠI NGUYÊN VĂN TỪ BẢN GHI ÂM</div>
                    <table>
                        <tr>
                            <th style="width:40px; text-align:center;">STT</th>
                            <th style="width:75px; text-align:center;">Thời gian</th>
                            <th style="width:170px;">Người phát biểu</th>
                            <th>Lời phát biểu nguyên văn</th>
                        </tr>
                        ${(state.transcripts || []).map((t, idx) => `
                            <tr>
                                <td style="text-align:center;">${idx + 1 < 10 ? '0' + (idx + 1) : idx + 1}</td>
                                <td style="text-align:center;">${t.timestamp}</td>
                                <td><strong>${t.speaker}</strong> ${t.is_bookmark ? '<span class="doc-bookmark-badge"><i class="fa-solid fa-bookmark"></i> [Trọng tâm]</span>' : ''}</td>
                                <td contenteditable="true">${t.text} ${t.note ? `<br><small style="color:#64748b; font-style:italic;">-> Ghi chú: ${t.note}</small>` : ''}</td>
                            </tr>
                        `).join('')}
                    </table>

                    <div style="display:flex; justify-content:space-between; margin-top:40px; text-align:center;">
                        <div style="width:45%;">
                            <strong>ĐẠI DIỆN TẬP ĐOÀN KIM LONG PHÁT</strong><br><em>(Ký và ghi rõ họ tên)</em><br><br><br><br>
                            <strong>Ông Trần Văn Hùng - Phó TGĐ</strong>
                        </div>
                        <div style="width:45%;">
                            <strong>ĐẠI DIỆN ĐỐI TÁC / KHÁCH HÀNG</strong><br><em>(Ký và ghi rõ họ tên)</em><br><br><br><br>
                            <strong>Ông Vũ Đình Toàn - Giám Đốc Dự Án</strong>
                        </div>
                    </div>
                </div>
            `;
        }

        documentPreviewContainer.innerHTML = html;
    }

    // Export Word Doc Handlers
    btnExportWordOption1.addEventListener('click', () => exportWordDocument(true));
    btnExportWordOption2Full.addEventListener('click', () => exportWordDocument(true));
    btnExportWordOption2Partner.addEventListener('click', () => exportWordDocument(false));

    async function exportWordDocument(includeInternal = true) {
        if (!state.sessionId) return;
        
        // Gom dữ liệu người dùng đã chỉnh sửa trực tiếp trên màn hình xem trước
        collectEditedAnalysisFromDOM();

        showToast('Đang tạo file Word (.docx) chuẩn hành chính KLP...', 'info');

        try {
            const res = await fetch(`/api/meetings/${state.sessionId}/export-word`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    include_internal: includeInternal,
                    edited_analysis: state.analysisState
                })
            });
            const data = await res.json();
            if (data.download_url) {
                showToast('Tạo file Word thành công! Đang tải về...', 'success');
                // Trigger auto download
                const link = document.createElement('a');
                link.href = data.download_url;
                link.download = data.filename;
                document.body.appendChild(link);
                link.click();
                link.remove();

                const wordFileName = document.getElementById('wordFileName');
                if (wordFileName && data.filename) {
                    wordFileName.textContent = data.filename;
                }
            }
        } catch (e) {
            console.error('Lỗi xuất Word:', e);
            showToast('Lỗi xuất file Word', 'warning');
        }
    }

    function goToHome() {
        stopTimer();
        state.meetingSeconds = 0;
        updateTimerDisplay();

        if (state.audioRecorder && state.isRecording) {
            try { state.audioRecorder.stopRecording(); } catch (e) {}
            state.isRecording = false;
        }

        state.sessionId = null;
        state.currentSpeaker = null;
        state.transcripts = [];
        state.meetingAudioBlob = null;
        state.audioDownloadUrl = null;
        state.transcriptDownloadUrl = null;
        state.isDemoRunning = false;

        if (transcriptScrollArea) {
            transcriptScrollArea.innerHTML = '';
            if (transcriptEmptyState) {
                transcriptScrollArea.appendChild(transcriptEmptyState);
                transcriptEmptyState.style.display = 'block';
            }
        }
        if (turnCountBadge) {
            turnCountBadge.textContent = '0 lượt phát biểu';
        }

        setStep(1);

        showPopup({
            title: 'Trang Chủ',
            message: 'Đã sẵn sàng cho cuộc họp tiếp theo. Quý Thư ký có thể thiết lập thông tin và bắt đầu.',
            type: 'info'
        });
    }

    if (btnGoHome) {
        btnGoHome.addEventListener('click', () => {
            showPopup({
                title: 'Quay về Trang Chủ',
                message: 'Toàn bộ dữ liệu phiên họp (tệp ghi âm, bản text nguyên văn và dữ liệu biên bản) đã được lưu trữ an toàn trong máy tính.\n\nBạn có chắc chắn muốn quay về Trang Chủ để thiết lập phiên họp mới?',
                type: 'confirm',
                confirmText: 'Về Trang Chủ',
                cancelText: 'Ở lại rà soát',
                onConfirm: () => {
                    goToHome();
                }
            });
        });
    }

    if (btnOpenMeetingFolder) {
        btnOpenMeetingFolder.addEventListener('click', async () => {
            if (!state.sessionId) {
                showPopup({
                    title: 'Chưa có phiên họp',
                    message: 'Chưa có phiên họp nào được chọn.',
                    type: 'warning'
                });
                return;
            }
            try {
                const res = await fetch(`/api/meetings/${state.sessionId}/open-folder`, { method: 'POST' });
                const data = await res.json();
                if (data.success) {
                    showPopup({
                        title: 'Đã mở thư mục',
                        message: `Thư mục lưu trữ hồ sơ cuộc họp đã được mở trên máy tính:\n\n📁 ${data.folder}`,
                        type: 'success'
                    });
                } else {
                    showPopup({
                        title: 'Đường dẫn thư mục',
                        message: `Bạn có thể truy cập thư mục theo đường dẫn:\n\n📁 ${data.folder}`,
                        type: 'info'
                    });
                }
            } catch (err) {
                showPopup({
                    title: 'Lỗi mở thư mục',
                    message: `Không thể kết nối đến máy chủ: ${err.message}`,
                    type: 'danger'
                });
            }
        });
    }

    if (btnCopyStoragePath) {
        btnCopyStoragePath.addEventListener('click', async () => {
            const p = state.storagePath || "D:\\review_agent\\output\\meetings";
            try {
                await navigator.clipboard.writeText(p);
                showPopup({
                    title: 'Đã sao chép đường dẫn',
                    message: `Đường dẫn thư mục lưu trữ đã được sao chép vào bộ nhớ tạm:\n\n📁 ${p}`,
                    type: 'success'
                });
            } catch (e) {
                showPopup({
                    title: 'Đường dẫn lưu trữ',
                    message: `Đường dẫn thư mục hồ sơ:\n\n📁 ${p}`,
                    type: 'info'
                });
            }
        });
    }

    if (btnQuickExportWord) {
        btnQuickExportWord.addEventListener('click', () => {
            exportWordDocument(true);
        });
    }

    btnBackToMeeting.addEventListener('click', () => setStep(2));
    btnNewMeeting.addEventListener('click', () => {
        showPopup({
            title: 'Tạo Cuộc Họp Mới',
            message: 'Bạn có chắc chắn muốn làm mới toàn bộ để tạo cuộc họp mới?',
            type: 'confirm',
            confirmText: 'Tạo Mới',
            cancelText: 'Hủy',
            onConfirm: () => {
                goToHome();
            }
        });
    });

    // Timer functions
    function startTimer() {
        state.meetingSeconds = 0;
        updateTimerDisplay();
        state.timerInterval = setInterval(() => {
            if (!state.isPaused) {
                state.meetingSeconds++;
                updateTimerDisplay();
            }
        }, 1000);
    }

    function stopTimer() {
        if (state.timerInterval) clearInterval(state.timerInterval);
    }

    function updateTimerDisplay() {
        const hrs = String(Math.floor(state.meetingSeconds / 3600)).padStart(2, '0');
        const mins = String(Math.floor((state.meetingSeconds % 3600) / 60)).padStart(2, '0');
        const secs = String(state.meetingSeconds % 60).padStart(2, '0');
        meetingTimer.textContent = `${hrs}:${mins}:${secs}`;
    }

    // Demo Simulation Flow
    async function runDemoSimulation() {
        try {
            const res = await fetch(`/api/meetings/demo-scenario/${state.mode}`);
            const data = await res.json();
            const dialogues = data.dialogues || [];

            for (let i = 0; i < dialogues.length; i++) {
                if (!state.isDemoRunning || state.currentStep !== 2) break;

                const item = dialogues[i];
                setActiveSpeaker(item.speaker, false);

                // Kích hoạt gợn sóng và trạng thái Đang nghe khi đại biểu phát biểu
                if (window.meetingRecorder && waveformCanvas) {
                    window.meetingRecorder.startSimulation(waveformCanvas);
                }
                if (recDot) recDot.style.boxShadow = '0 0 8px #10b981';
                audioSourceText.textContent = 'Micro ON (Đang nghe)';
                audioSourceText.style.color = '#059669';

                await sleep(2500); // Thời gian đại biểu đang phát biểu (sóng âm gợn liên tục)

                await sendTranscriptToServer(item.speaker, item.text, item.is_bookmark, item.note);

                // Dừng sóng âm trong khoảng nghỉ ngắn giữa 2 đại biểu
                if (window.meetingRecorder && waveformCanvas) {
                    window.meetingRecorder.stopSimulation(waveformCanvas);
                }
                if (recDot) recDot.style.boxShadow = 'none';
                audioSourceText.textContent = 'Micro ON (Chờ nói)';
                audioSourceText.style.color = '#475569';

                await sleep(400);

                if ((i + 1) % 2 === 0 || i === dialogues.length - 1) {
                    await fetch(`/api/meetings/${state.sessionId}/analyze`, { method: 'POST' });
                    const stRes = await fetch(`/api/meetings/${state.sessionId}/state`);
                    const stData = await stRes.json();
                    state.analysisState = stData.analysis_state;
                    renderLiveAnalysis();
                }
            }

            showToast('Đã hoàn thành phát kịch bản họp mẫu. Quý Thư ký có thể bấm "Kết thúc & Rà soát" để xem file Word.', 'success');
        } catch (e) {
            console.error('Lỗi chạy demo:', e);
        }
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // =========================================================================
    // CHẾ ĐỘ 1: GHI ÂM & CHUYỂN THÀNH VĂN BẢN (STT STUDIO CONTROLLER)
    // =========================================================================
    function initSTTStudio() {
        const btnModeRecorder = document.getElementById('btnModeRecorder');
        const btnModeMeeting = document.getElementById('btnModeMeeting');
        const meetingStepsNav = document.getElementById('meetingStepsNav');
        const screenRecorderSTT = document.getElementById('screenRecorderSTT');
        const containerMeetingAssistant = document.getElementById('containerMeetingAssistant');

        // Mode Navigation Switching
        if (btnModeRecorder && btnModeMeeting) {
            btnModeRecorder.addEventListener('click', () => {
                btnModeRecorder.classList.add('active');
                btnModeMeeting.classList.remove('active');
                if (screenRecorderSTT) screenRecorderSTT.style.display = 'block';
                if (containerMeetingAssistant) containerMeetingAssistant.style.display = 'none';
                if (meetingStepsNav) meetingStepsNav.style.display = 'none';
            });

            btnModeMeeting.addEventListener('click', () => {
                btnModeMeeting.classList.add('active');
                btnModeRecorder.classList.remove('active');
                if (screenRecorderSTT) screenRecorderSTT.style.display = 'none';
                if (containerMeetingAssistant) containerMeetingAssistant.style.display = 'flex';
                if (meetingStepsNav) meetingStepsNav.style.display = 'flex';
            });
        }

        // STT DOM Elements
        const btnSttRecord = document.getElementById('btnSttRecord');
        const recordIcon = document.getElementById('recordIcon');
        const sttRecordTimer = document.getElementById('sttRecordTimer');
        const sttStatusPill = document.getElementById('sttStatusPill');
        const sttStatusText = document.getElementById('sttStatusText');
        const sttWaveformCanvas = document.getElementById('sttWaveformCanvas');
        const btnSttPause = document.getElementById('btnSttPause');
        const btnSttStop = document.getElementById('btnSttStop');
        const optSttMicOnly = document.getElementById('optSttMicOnly');
        const optSttMicSystem = document.getElementById('optSttMicSystem');
        const sttDropzone = document.getElementById('sttDropzone');
        const sttFileInput = document.getElementById('sttFileInput');
        const btnViewParagraphs = document.getElementById('btnViewParagraphs');
        const btnViewTimeline = document.getElementById('btnViewTimeline');
        const wrapperParagraphs = document.getElementById('wrapperParagraphs');
        const wrapperTimeline = document.getElementById('wrapperTimeline');
        const sttWordCount = document.getElementById('sttWordCount');
        const sttCharCount = document.getElementById('sttCharCount');
        const sttDurationText = document.getElementById('sttDurationText');
        const sttEditorTextarea = document.getElementById('sttEditorTextarea');
        const btnSttCopy = document.getElementById('btnSttCopy');
        const btnSttDownloadDocx = document.getElementById('btnSttDownloadDocx');
        const btnSttDownloadTxt = document.getElementById('btnSttDownloadTxt');
        const btnSttClear = document.getElementById('btnSttClear');
        const btnSttGoToMeeting = document.getElementById('btnSttGoToMeeting');

        let sttIsRecording = false;
        let sttIsPaused = false;
        let sttSeconds = 0;
        let sttTimerInterval = null;
        let sttSource = 'mic_only';
        let sttSegments = [];

        function formatSTTTime(totalSec) {
            const h = String(Math.floor(totalSec / 3600)).padStart(2, '0');
            const m = String(Math.floor((totalSec % 3600) / 60)).padStart(2, '0');
            const s = String(totalSec % 60).padStart(2, '0');
            return `${h}:${m}:${s}`;
        }

        function updateStats() {
            if (!sttEditorTextarea) return;
            const text = sttEditorTextarea.value.trim();
            const words = text ? text.split(/\s+/).length : 0;
            if (sttWordCount) sttWordCount.textContent = words;
            if (sttCharCount) sttCharCount.textContent = text.length;
            if (sttDurationText) sttDurationText.textContent = `Thời lượng: ${formatSTTTime(sttSeconds)}`;
        }

        if (sttEditorTextarea) {
            sttEditorTextarea.addEventListener('input', updateStats);
        }

        function renderSTTTimeline() {
            if (!wrapperTimeline) return;
            if (!sttSegments || sttSegments.length === 0) {
                wrapperTimeline.innerHTML = '<p class="placeholder-text text-center" style="padding: 40px 0;">Chưa có mốc thoại nào. Bắt đầu thu âm hoặc tải file để xem mốc thời gian.</p>';
                return;
            }

            wrapperTimeline.innerHTML = '';
            sttSegments.forEach(item => {
                const entry = document.createElement('div');
                entry.className = 'timeline-entry';
                entry.innerHTML = `
                    <div class="timeline-entry-header">
                        <span><i class="fa-solid fa-clock"></i> [${item.timestamp || '00:00:00'}]</span>
                        <span><i class="fa-solid fa-user"></i> ${item.speaker || 'Người nói'}</span>
                    </div>
                    <div class="timeline-entry-text">${item.text || ''}</div>
                `;
                wrapperTimeline.appendChild(entry);
            });
        }

        // Audio Source Selection
        if (optSttMicOnly && optSttMicSystem) {
            optSttMicOnly.addEventListener('click', () => {
                optSttMicOnly.classList.add('selected');
                optSttMicSystem.classList.remove('selected');
                sttSource = 'mic_only';
            });
            optSttMicSystem.addEventListener('click', () => {
                optSttMicSystem.classList.add('selected');
                optSttMicOnly.classList.remove('selected');
                sttSource = 'mic_system';
            });
        }

        // View Mode Switch (Paragraphs vs Timeline)
        if (btnViewParagraphs && btnViewTimeline) {
            btnViewParagraphs.addEventListener('click', () => {
                btnViewParagraphs.classList.add('active');
                btnViewTimeline.classList.remove('active');
                if (wrapperParagraphs) wrapperParagraphs.style.display = 'flex';
                if (wrapperTimeline) wrapperTimeline.style.display = 'none';
            });
            btnViewTimeline.addEventListener('click', () => {
                btnViewTimeline.classList.add('active');
                btnViewParagraphs.classList.remove('active');
                if (wrapperParagraphs) wrapperParagraphs.style.display = 'none';
                if (wrapperTimeline) wrapperTimeline.style.display = 'flex';
                renderSTTTimeline();
            });
        }

        // Start/Stop Record Button
        if (btnSttRecord) {
            btnSttRecord.addEventListener('click', async () => {
                if (!sttIsRecording) {
                    await startSTT();
                } else {
                    stopSTT();
                }
            });
        }

        if (btnSttPause) {
            btnSttPause.addEventListener('click', () => {
                if (!sttIsRecording) return;
                if (!sttIsPaused) {
                    sttIsPaused = true;
                    window.meetingRecorder.pauseRecording();
                    btnSttPause.innerHTML = '<i class="fa-solid fa-play"></i> Tiếp tục';
                    btnSttPause.className = 'btn btn-small btn-success';
                    sttStatusText.textContent = 'Đang tạm dừng thu âm';
                    showToast('Đã tạm dừng thu âm', 'info');
                } else {
                    sttIsPaused = false;
                    window.meetingRecorder.resumeRecording();
                    btnSttPause.innerHTML = '<i class="fa-solid fa-pause"></i> Tạm dừng';
                    btnSttPause.className = 'btn btn-small btn-warning';
                    sttStatusText.textContent = 'Đang lắng nghe giọng nói...';
                    showToast('Đang tiếp tục thu âm', 'success');
                }
            });
        }

        if (btnSttStop) {
            btnSttStop.addEventListener('click', () => {
                stopSTT();
            });
        }

        async function startSTT() {
            try {
                sttIsRecording = true;
                sttIsPaused = false;
                sttSeconds = 0;
                sttRecordTimer.textContent = '00:00:00';
                btnSttRecord.classList.add('recording');
                recordIcon.className = 'fa-solid fa-stop';
                if (btnSttPause) {
                    btnSttPause.style.display = 'inline-flex';
                    btnSttPause.innerHTML = '<i class="fa-solid fa-pause"></i> Tạm dừng';
                    btnSttPause.className = 'btn btn-small btn-warning';
                }
                if (btnSttStop) btnSttStop.style.display = 'inline-flex';
                sttStatusPill.className = 'record-status-pill recording';
                sttStatusText.textContent = 'Đang lắng nghe giọng nói...';

                clearInterval(sttTimerInterval);
                sttTimerInterval = setInterval(() => {
                    if (!sttIsPaused) {
                        sttSeconds++;
                        sttRecordTimer.textContent = formatSTTTime(sttSeconds);
                        updateStats();
                    }
                }, 1000);

                // Web Speech API realtime text display
                window.meetingRecorder.onTranscriptCallback = (text, isFinal) => {
                    if (sttIsRecording && text.trim()) {
                        const current = sttEditorTextarea.value.trim();
                        if (isFinal) {
                            const ts = formatSTTTime(sttSeconds);
                            sttSegments.push({ timestamp: ts, speaker: 'Người nói', text: text.trim() });
                            sttEditorTextarea.value = current ? `${current}\n${text.trim()}` : text.trim();
                            updateStats();
                            renderSTTTimeline();
                        }
                    }
                };

                // On full recording complete callback
                window.meetingRecorder.onRecordingComplete = async (audioBlob) => {
                    await sendAudioBlobForRefinement(audioBlob);
                };

                await window.meetingRecorder.startRecording(sttSource, sttWaveformCanvas);
                showToast('Hệ thống đang thu âm trực tiếp...', 'success');
            } catch (err) {
                console.error('Lỗi khởi tạo thu âm:', err);
                sttIsRecording = false;
                btnSttRecord.classList.remove('recording');
                recordIcon.className = 'fa-solid fa-microphone';
                if (btnSttPause) btnSttPause.style.display = 'none';
                if (btnSttStop) btnSttStop.style.display = 'none';
                sttStatusPill.className = 'record-status-pill';
                sttStatusText.textContent = 'Không mở được Micro';
                showToast('Không thể truy cập Microphone trên trình duyệt', 'warning');
            }
        }

        function stopSTT() {
            if (!sttIsRecording) return;
            sttIsRecording = false;
            sttIsPaused = false;
            clearInterval(sttTimerInterval);

            btnSttRecord.classList.remove('recording');
            recordIcon.className = 'fa-solid fa-microphone';
            if (btnSttPause) btnSttPause.style.display = 'none';
            if (btnSttStop) btnSttStop.style.display = 'none';
            sttStatusPill.className = 'record-status-pill';
            sttStatusText.textContent = 'AI đang hiệu đính văn bản tiếng Việt...';

            window.meetingRecorder.stopRecording();
        }

        async function sendAudioBlobForRefinement(audioBlob) {
            if (!audioBlob || audioBlob.size < 2000) {
                sttStatusText.textContent = 'Hoàn tất thu âm';
                return;
            }

            showToast('Gemini AI đang hiệu đính ngữ pháp, dấu câu và chính tả...', 'info');
            const formData = new FormData();
            formData.append('file', audioBlob, 'recording.webm');

            try {
                const res = await fetch('/api/stt/transcribe', {
                    method: 'POST',
                    body: formData
                });
                if (res.ok) {
                    const data = await res.json();
                    if (data.full_text) {
                        sttEditorTextarea.value = data.full_text;
                        if (data.segments && data.segments.length > 0) {
                            sttSegments = data.segments;
                            renderSTTTimeline();
                        }
                        updateStats();
                        sttStatusText.textContent = 'Đã hoàn tất chuyển văn bản!';
                        showToast('Chuyển đổi văn bản thành công!', 'success');
                    }
                }
            } catch (e) {
                console.warn('Lỗi xử lý AI STT:', e);
                sttStatusText.textContent = 'Hoàn tất ghi âm';
            }
        }

        // File Drag & Drop / Upload
        if (sttDropzone && sttFileInput) {
            sttDropzone.addEventListener('click', () => sttFileInput.click());

            ['dragenter', 'dragover'].forEach(eventName => {
                sttDropzone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    sttDropzone.style.borderColor = 'var(--primary)';
                    sttDropzone.style.background = '#f0f7ff';
                });
            });

            ['dragleave', 'drop'].forEach(eventName => {
                sttDropzone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    sttDropzone.style.borderColor = '#cbd5e1';
                    sttDropzone.style.background = '#fafafa';
                });
            });

            sttDropzone.addEventListener('drop', (e) => {
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    processAudioFile(files[0]);
                }
            });

            sttFileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    processAudioFile(e.target.files[0]);
                }
            });
        }

        async function processAudioFile(file) {
            if (!file) return;
            showToast(`Đang tải lên và bóc tách file: ${file.name}...`, 'info');
            sttStatusPill.className = 'record-status-pill recording';
            sttStatusText.textContent = `Đang phiên âm file ${file.name}...`;

            const formData = new FormData();
            formData.append('file', file);

            try {
                const res = await fetch('/api/stt/transcribe', {
                    method: 'POST',
                    body: formData
                });
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || 'Không thể chuyển đổi file này');
                }

                const data = await res.json();
                if (data.full_text) {
                    sttEditorTextarea.value = data.full_text;
                    sttSegments = data.segments || [];
                    renderSTTTimeline();
                    updateStats();
                    sttStatusPill.className = 'record-status-pill';
                    sttStatusText.textContent = 'Chuyển đổi thành công!';
                    showToast('Phiên âm file ghi âm thành văn bản hoàn tất!', 'success');
                } else {
                    showToast('Không nhận diện được lời thoại trong file này', 'warning');
                }
            } catch (err) {
                console.error(err);
                sttStatusPill.className = 'record-status-pill';
                sttStatusText.textContent = 'Lỗi xử lý file';
                showToast(err.message || 'Lỗi khi phiên âm file âm thanh', 'warning');
            } finally {
                sttFileInput.value = '';
            }
        }

        // Toolbar Button Actions
        if (btnSttCopy) {
            btnSttCopy.addEventListener('click', () => {
                const text = sttEditorTextarea.value.trim();
                if (!text) {
                    showToast('Chưa có nội dung văn bản để sao chép', 'warning');
                    return;
                }
                navigator.clipboard.writeText(text).then(() => {
                    showToast('Đã sao chép toàn bộ văn bản vào bộ nhớ tạm!', 'success');
                }).catch(() => {
                    sttEditorTextarea.select();
                    document.execCommand('copy');
                    showToast('Đã sao chép văn bản!', 'success');
                });
            });
        }

        if (btnSttDownloadDocx) {
            btnSttDownloadDocx.addEventListener('click', async () => {
                const text = sttEditorTextarea.value.trim();
                if (!text) {
                    showToast('Chưa có nội dung để xuất file Word', 'warning');
                    return;
                }
                showToast('Đang tạo file Word (.docx)...', 'info');
                try {
                    const res = await fetch('/api/stt/export-docx', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            title: 'VĂN BẢN CHUYỂN ĐỔI TỪ BẢN GHI ÂM',
                            text: text,
                            segments: sttSegments
                        })
                    });
                    const data = await res.json();
                    if (data.download_url) {
                        const link = document.createElement('a');
                        link.href = data.download_url;
                        link.download = data.filename;
                        document.body.appendChild(link);
                        link.click();
                        link.remove();
                        showToast('Đã tải xuống file Word thành công!', 'success');
                    }
                } catch (e) {
                    console.error(e);
                    showToast('Lỗi khi xuất file Word', 'warning');
                }
            });
        }

        if (btnSttDownloadTxt) {
            btnSttDownloadTxt.addEventListener('click', async () => {
                const text = sttEditorTextarea.value.trim();
                if (!text) {
                    showToast('Chưa có nội dung để xuất file Text', 'warning');
                    return;
                }
                try {
                    const res = await fetch('/api/stt/export-txt', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            title: 'VĂN BẢN GHI ÂM',
                            text: text,
                            segments: sttSegments
                        })
                    });
                    const data = await res.json();
                    if (data.download_url) {
                        const link = document.createElement('a');
                        link.href = data.download_url;
                        link.download = data.filename;
                        document.body.appendChild(link);
                        link.click();
                        link.remove();
                        showToast('Đã tải file Text (.txt) thành công!', 'success');
                    }
                } catch (e) {
                    console.error(e);
                    showToast('Lỗi khi tải file Text', 'warning');
                }
            });
        }

        if (btnSttClear) {
            btnSttClear.addEventListener('click', () => {
                if (confirm('Bạn có chắc chắn muốn xóa toàn bộ văn bản và làm mới?')) {
                    sttEditorTextarea.value = '';
                    sttSegments = [];
                    sttSeconds = 0;
                    sttRecordTimer.textContent = '00:00:00';
                    updateStats();
                    renderSTTTimeline();
                    sttStatusText.textContent = 'Sẵn sàng thu âm';
                    showToast('Đã làm mới khung văn bản', 'info');
                }
            });
        }

        if (btnSttGoToMeeting) {
            btnSttGoToMeeting.addEventListener('click', () => {
                const text = sttEditorTextarea.value.trim();
                if (!text) {
                    showToast('Chưa có nội dung văn bản để tóm tắt', 'warning');
                    return;
                }
                // Switch to meeting mode
                btnModeMeeting.click();
                showToast('Đã chuyển sang Chế độ Biên bản & Tóm tắt cuộc họp!', 'info');
            });
        }
    }

    // Initial setup
    loadConfig();
    initSTTStudio();

    // Visual Preview Support for Automated Testing
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('test_view') === 'step3') {
        state.sessionId = 'klp_demo_review_2026';
        state.mode = 'option_1';
        state.storagePath = 'D:\\review_agent\\output\\meetings';
        state.meetingTitle = 'Cuộc họp Giao ban Triển khai Kế hoạch Trọng tâm Quý 4/2026';
        state.chairperson = 'Bà Phan Thị Phát (Tổng Giám Đốc)';
        state.secretary = 'Bà Lê Thu Thảo (Thư ký Ban TGĐ)';
        state.participants = [
            '1. Bà Phan Thị Phát - Tổng Giám Đốc (Chủ trì)',
            '2. Ông Trần Văn Hùng - Phó Tổng Giám Đốc Phụ trách Vận hành & Dự án',
            '3. Ông Phạm Đức Huy - Trưởng Phòng Kỹ Thuật',
            '4. Bà Nguyễn Mai Phương - Kế toán Trưởng'
        ];
        state.audioFilename = 'GhiAm_GiaoBan_Q4_2026.webm';
        state.transcriptFilename = 'ChuThoai_GiaoBan_Q4_2026.txt';
        state.transcripts = [
            { id: 1, speaker: 'Bà Phan Thị Phát (Tổng Giám Đốc)', text: 'Tôi đề nghị toàn bộ các phòng ban tập trung vào mục tiêu doanh số quý 4.', timestamp: '08:35:10', is_bookmark: true, note: 'Chỉ đạo tập trung mục tiêu' },
            { id: 2, speaker: 'Ông Trần Văn Hùng (Phó TGĐ)', text: 'Khối dự án đã chốt xong 3 hợp đồng lớn với các đối tác chiến lược.', timestamp: '08:36:20', is_bookmark: false, note: '' }
        ];
        prepareStep3Review();
        setStep(3);
    } else if (urlParams.get('test_view') === 'step2') {
        state.sessionId = 'klp_live_demo_2026';
        state.mode = 'option_1';
        state.storagePath = 'D:\\review_agent\\output\\meetings';
        state.meetingTitle = 'Cuộc họp Giao ban Triển khai Kế hoạch Trọng tâm Quý 4/2026';
        state.chairperson = 'Bà Phan Thị Phát (Tổng Giám Đốc)';
        state.analysisState = {
            meeting_title: 'Cuộc họp Giao ban Triển khai Kế hoạch Trọng tâm Quý 4/2026',
            summary_goals: ['Đang lắng nghe và tổng hợp mục tiêu cuộc họp...'],
            leader_directions: ['Chờ ý kiến chỉ đạo từ Lãnh đạo chủ trì...'],
            department_reports: [],
            speech_analytics: [
                {
                    speaker: 'Bà Phan Thị Phát (Tổng Giám Đốc)',
                    ratio_percent: 100,
                    key_points: 'Đã đóng góp 4 từ thảo luận.',
                    attitude: 'Tích cực',
                    contribution_eval: 'Đạt yêu cầu'
                }
            ],
            agreed_issues: [],
            pending_issues: [],
            hot_bookmarks: [],
            action_items: []
        };
        state.transcripts = [
            { id: 1, speaker: 'Bà Phan Thị Phát (Tổng Giám Đốc)', text: 'Cuộc họp giao ban quý 4 xin phép được bắt đầu.', timestamp: '08:30:15', is_bookmark: false, note: '' },
            { id: 2, speaker: 'Bà Phan Thị Phát (Tổng Giám Đốc)', text: 'Đề nghị khối kinh doanh và kỹ thuật báo cáo tiến độ chi tiết.', timestamp: '08:30:45', is_bookmark: true, note: 'Yêu cầu báo cáo tiến độ' }
        ];
        const meetingLiveTitle = document.getElementById('meetingLiveTitle');
        if (meetingLiveTitle) meetingLiveTitle.textContent = state.meetingTitle;
        state.participants = [
            'Bà Phan Thị Phát (Tổng Giám Đốc)',
            'Ông Trần Văn Hùng (Phó TGĐ)',
            'Ông Đặng Minh Trí (Trưởng Phòng Kinh Doanh)',
            'Ông Phạm Đức Huy (Trưởng Phòng Kỹ Thuật)'
        ];
        renderActiveSpeakerSelector();
        renderLiveAnalysis();
        if (transcriptScrollArea && transcriptEmptyState) {
            transcriptEmptyState.style.display = 'none';
            state.transcripts.forEach(seg => appendTranscriptSegment(seg));
        }
        setStep(2);
    } else if (urlParams.get('test_view') === 'popup') {
        showToast('Hệ thống đã bắt đầu thu âm và nhận diện giọng nói trực tiếp!', 'success');
    } else if (urlParams.get('test_view') === 'popup_confirm') {
        showPopup({
            title: 'Quay Về Trang Chủ',
            message: 'Toàn bộ dữ liệu phiên họp (tệp ghi âm, bản text nguyên văn và dữ liệu biên bản) đã được lưu trữ an toàn trong máy tính.\n\nBạn có chắc chắn muốn quay về Trang Chủ để thiết lập phiên họp mới?',
            type: 'warning',
            confirmText: 'Về Trang Chủ',
            cancelText: 'Ở lại rà soát'
        });
    }
});
