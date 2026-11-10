import os
import json
import base64
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Body, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.config import settings
from app.services.vocabulary import LEADERSHIP_MEMBERS, DEPARTMENTS, PRODUCTS_AND_PROJECTS
from app.services.meeting_service import meeting_manager, MeetingSession
from app.services.stt_service import stt_service
from app.services.demo_scenarios import DEMO_MEETING_OPTION_1, DEMO_MEETING_OPTION_2

app = FastAPI(
    title="Kim Long Phat AI Meeting Assistant Bot",
    description="Bot AI Trợ lý Thư ký Ghi âm & Phân tích Cuộc họp - CÔNG TY CỔ PHẦN TẬP ĐOÀN KIM LONG PHÁT",
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Request Models
class StartMeetingRequest(BaseModel):
    mode: str = "option_1"  # "option_1" hoặc "option_2"
    title: Optional[str] = None
    chairperson: Optional[str] = None
    secretary: Optional[str] = "Bà Lê Thu Thảo (Thư ký Ban TGĐ)"
    participants: Optional[List[str]] = None
    partner_name: Optional[str] = None
    partner_reps: Optional[List[str]] = None
    audio_source: Optional[str] = "mic_only"  # "mic_only" hoặc "mic_system"
    storage_dir: Optional[str] = None

class AddTranscriptRequest(BaseModel):
    speaker: str
    text: str
    timestamp: Optional[str] = None
    is_bookmark: bool = False
    note: str = ""
    auto_analyze: bool = False

class AddNoteRequest(BaseModel):
    note: str

class BookmarkRequest(BaseModel):
    transcript_id: Optional[int] = None
    custom_text: Optional[str] = ""

class ExportWordRequest(BaseModel):
    include_internal: bool = True
    edited_analysis: Optional[Dict[str, Any]] = None

class STTExportRequest(BaseModel):
    title: Optional[str] = "VĂN BẢN CHUYỂN ĐỔI TỪ BẢN GHI ÂM"
    text: str
    segments: Optional[List[Dict[str, Any]]] = None

# REST Endpoints
@app.post("/api/stt/transcribe")
async def transcribe_audio_api(file: UploadFile = File(...)):
    """Chuyển đổi file âm thanh hoặc bản thu âm trực tiếp thành văn bản tiếng Việt"""
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="File âm thanh rỗng")
    
    result = await stt_service.transcribe_general_audio(contents, filename=file.filename)
    return result

@app.post("/api/stt/export-docx")
def export_stt_docx(req: STTExportRequest):
    """Xuất văn bản đã phiên âm ra file Word (.docx)"""
    import docx
    from docx.shared import Pt, Inches, RGBColor
    
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(0.8)
        
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(13)
    style.font.color.rgb = RGBColor(30, 30, 30)

    # Tiêu đề
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_after = Pt(14)
    run_title = p_title.add_run(req.title or "VĂN BẢN CHUYỂN ĐỔI TỪ BẢN GHI ÂM")
    run_title.bold = True
    run_title.font.size = Pt(16)
    run_title.font.color.rgb = RGBColor(21, 62, 117)

    # Thời gian tạo
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_after = Pt(14)
    r_meta = p_meta.add_run(f"Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Số từ: {len(req.text.split())} từ")
    r_meta.italic = True
    r_meta.font.size = Pt(11)
    r_meta.font.color.rgb = RGBColor(100, 100, 100)

    # Nội dung toàn văn
    p_h = doc.add_paragraph()
    r_h = p_h.add_run("NỘI DUNG VĂN BẢN:")
    r_h.bold = True
    r_h.font.size = Pt(13)

    for para_text in req.text.split('\n'):
        if para_text.strip():
            p = doc.add_paragraph(para_text.strip())
            p.paragraph_format.line_spacing = 1.25
            p.paragraph_format.space_after = Pt(6)

    # Nếu có segments mốc thời gian
    if req.segments and len(req.segments) > 0:
        p_seg_h = doc.add_paragraph()
        p_seg_h.paragraph_format.space_before = Pt(16)
        r_seg_h = p_seg_h.add_run("CHI TIẾT THEO MỐC THỜI GIAN:")
        r_seg_h.bold = True
        r_seg_h.font.size = Pt(13)

        table = doc.add_table(rows=1, cols=3)
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "Thời gian"
        hdr_cells[1].text = "Người nói"
        hdr_cells[2].text = "Nội dung"
        for c in hdr_cells:
            for p in c.paragraphs:
                for r in p.runs:
                    r.bold = True

        for s in req.segments:
            row_cells = table.add_row().cells
            row_cells[0].text = s.get("timestamp", "")
            row_cells[1].text = s.get("speaker", "Người nói")
            row_cells[2].text = s.get("text", "")

    filename = f"VanBanGhiAm_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    file_path = os.path.join(settings.OUTPUT_DIR, filename)
    doc.save(file_path)

    return {
        "filename": filename,
        "download_url": f"/api/download/{filename}"
    }

@app.post("/api/stt/export-txt")
def export_stt_txt(req: STTExportRequest):
    """Xuất văn bản đã phiên âm ra file text (.txt)"""
    filename = f"VanBanGhiAm_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    file_path = os.path.join(settings.OUTPUT_DIR, filename)
    
    content = f"{req.title or 'VĂN BẢN GHI ÂM'}\n"
    content += f"Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
    content += f"Số từ: {len(req.text.split())} từ\n"
    content += "="*50 + "\n\n"
    content += req.text + "\n\n"
    
    if req.segments and len(req.segments) > 0:
        content += "="*50 + "\n"
        content += "CHI TIẾT THEO MỐC THỜI GIAN:\n"
        content += "="*50 + "\n"
        for s in req.segments:
            content += f"[{s.get('timestamp', '00:00:00')}] {s.get('speaker', 'Người nói')}: {s.get('text', '')}\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "filename": filename,
        "download_url": f"/api/download/{filename}"
    }

# REST Endpoints
@app.get("/api/config")
def get_system_config():
    """Lấy thông tin cấu hình ban đầu, danh bạ Lãnh đạo, phòng ban và sản phẩm KLP"""
    return {
        "company_name": settings.COMPANY_NAME,
        "company_short": settings.COMPANY_SHORT,
        "leadership_members": LEADERSHIP_MEMBERS,
        "departments": DEPARTMENTS,
        "products": PRODUCTS_AND_PROJECTS,
        "has_gemini_key": bool(settings.GEMINI_API_KEY)
    }

@app.post("/api/meetings/start")
def start_meeting(req: StartMeetingRequest):
    """Khởi tạo phiên họp mới (Bước 1)"""
    metadata = req.model_dump()
    if req.mode == "option_1" and not metadata.get("title"):
        metadata["title"] = "Cuộc họp Giao ban Nội bộ"
    elif req.mode == "option_2":
        if not metadata.get("project_title"):
            metadata["project_title"] = "Cuộc họp Đàm phán Đối tác"
        if not metadata.get("partner_name"):
            metadata["partner_name"] = req.partner_name or "Đối tác / Khách hàng"

    session = meeting_manager.create_session(mode=req.mode, metadata=metadata)
    return {
        "session_id": session.session_id,
        "mode": session.mode,
        "metadata": session.metadata,
        "analysis_state": session.analysis_state
    }

@app.get("/api/meetings/{session_id}/state")
def get_meeting_state(session_id: str):
    """Lấy trạng thái và toàn bộ dữ liệu cuộc họp hiện tại"""
    session = meeting_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên họp")
    return {
        "session_id": session.session_id,
        "mode": session.mode,
        "status": session.status,
        "metadata": session.metadata,
        "transcripts": session.transcripts,
        "secretary_notes": session.secretary_notes,
        "hot_bookmarks": session.hot_bookmarks,
        "analysis_state": session.analysis_state
    }

@app.post("/api/meetings/{session_id}/transcript")
async def add_transcript(session_id: str, req: AddTranscriptRequest):
    """Thêm đoạn hội thoại từ người nói (kèm tự động phân tích nếu yêu cầu)"""
    session = meeting_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên họp")

    cleaned = (req.text or "").strip()
    noise_markers = ["[tiếng ồn]", "tiếng ồn", "[im lặng]", "im lặng", "[tiếng thở]", "noise", "silence", "[âm thanh]"]
    if not cleaned or cleaned.lower() in noise_markers or (cleaned.startswith("[") and cleaned.endswith("]")) or len(cleaned) < 2:
        return {
            "segment": None,
            "analysis_state": session.analysis_state,
            "message": "Bỏ qua tiếng ồn hoặc văn bản rỗng"
        }

    segment = session.add_transcript_segment(
        speaker=req.speaker,
        text=req.text,
        timestamp=req.timestamp,
        is_bookmark=req.is_bookmark,
        note=req.note
    )

    if req.auto_analyze or len(session.transcripts) % 2 == 0:
        await session.run_ai_analysis()

    return {
        "segment": segment,
        "analysis_state": session.analysis_state
    }

@app.post("/api/meetings/{session_id}/bookmark")
def mark_bookmark(session_id: str, req: BookmarkRequest):
    """Thư ký bấm nút Đánh dấu trọng tâm (hỗ trợ theo từng đoạn text và toggle)"""
    session = meeting_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên họp")

    bm = session.mark_bookmark(transcript_id=req.transcript_id, custom_text=req.custom_text or "")
    return {
        "bookmark": bm,
        "is_bookmark": bm.get("is_bookmark", True),
        "transcript_id": bm.get("transcript_id"),
        "analysis_state": session.analysis_state
    }

@app.post("/api/meetings/{session_id}/note")
def add_note(session_id: str, req: AddNoteRequest):
    """Thư ký gửi ghi chú nhanh"""
    session = meeting_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên họp")

    note_obj = session.add_secretary_note(req.note)
    return {"note": note_obj}

@app.post("/api/meetings/{session_id}/analyze")
async def trigger_analysis(session_id: str):
    """Kích hoạt AI phân tích trực tiếp toàn bộ dữ liệu họp"""
    session = meeting_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên họp")

    updated_analysis = await session.run_ai_analysis()
    return {"analysis_state": updated_analysis}

@app.post("/api/meetings/{session_id}/end")
async def end_meeting(session_id: str):
    """Kết thúc cuộc họp, chốt kết quả phân tích và tự động lưu file text chữ thoại nguyên văn vào máy"""
    session = meeting_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên họp")

    session.status = "completed"
    final_analysis = await session.run_ai_analysis()
    
    # Tự động lưu toàn bộ đoạn text chữ thoại bóc tách từ file ghi âm vào máy tính
    transcript_info = session.save_transcript_text()
    
    return {
        "status": session.status,
        "analysis_state": final_analysis,
        "transcript_info": transcript_info
    }

@app.post("/api/meetings/{session_id}/upload-audio")
async def upload_audio_file(session_id: str, file: UploadFile = File(...)):
    """Tải lên file ghi âm cuộc họp (.mp3, .wav, .m4a, .webm, .ogg) để AI tự động chuyển thành văn bản & phân tích"""
    session = meeting_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên họp")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="File rỗng")

    participants = session.metadata.get("participants", [])
    dialogues = await stt_service.transcribe_audio_file(
        audio_bytes=contents,
        filename=file.filename or "recording.wav",
        participants=participants
    )

    if not dialogues:
        # Nếu model chưa trích xuất được do định dạng hoặc không có tiếng, thông báo
        raise HTTPException(status_code=422, detail="Không thể nhận diện văn bản từ file âm thanh này hoặc định dạng âm thanh chưa được hỗ trợ.")

    for d in dialogues:
        session.add_transcript_segment(
            speaker=d.get("speaker", "Người phát biểu"),
            text=d.get("text", ""),
            timestamp=d.get("timestamp"),
            is_bookmark=d.get("is_bookmark", False)
        )

    # Chạy AI phân tích tự động toàn diện
    analysis = await session.run_ai_analysis()

    return {
        "message": f"Đã nhận diện thành công {len(dialogues)} lượt phát biểu từ file ghi âm!",
        "transcripts": session.transcripts,
        "analysis_state": analysis
    }

@app.post("/api/meetings/{session_id}/export-word")
def export_word_doc(session_id: str, req: ExportWordRequest):
    """Xuất biên bản thành file Microsoft Word (.docx) chuẩn hành chính KLP"""
    session = meeting_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên họp")

    if req.edited_analysis:
        session.analysis_state = req.edited_analysis

    file_path = session.export_word(include_internal=req.include_internal)
    filename = os.path.basename(file_path)

    return {
        "message": "Xuất file Word thành công!",
        "filename": filename,
        "download_url": f"/api/download/{filename}"
    }

@app.post("/api/meetings/{session_id}/save-audio")
async def save_meeting_audio(session_id: str, file: UploadFile = File(...)):
    """Lưu trữ toàn bộ file ghi âm nguyên vẹn của phiên họp vào ổ đĩa máy tính"""
    session = meeting_manager.get_session(session_id)
    recordings_dir = settings.RECORDINGS_DIR
    os.makedirs(recordings_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    orig_ext = os.path.splitext(file.filename or "")[1]
    ext = orig_ext if orig_ext in [".webm", ".wav", ".mp3", ".m4a", ".mp4", ".ogg"] else ".webm"
    mode_name = "NoiBo" if session and session.mode == "option_1" else "DoiTac"
    filename = f"GhiAm_{mode_name}_{session_id}_{timestamp}{ext}"
    file_path = os.path.join(recordings_dir, filename)

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    if session:
        session.metadata["audio_recording_file"] = filename
        session.metadata["audio_recording_path"] = file_path
        
        # Tự động sao chép file ghi âm vào thư mục do người dùng chọn nếu có
        storage_dir = session.metadata.get("storage_dir")
        if storage_dir:
            import shutil
            try:
                os.makedirs(storage_dir, exist_ok=True)
                shutil.copy2(file_path, os.path.join(storage_dir, filename))
            except Exception:
                pass

    return {
        "message": "Đã lưu bản ghi âm toàn bộ cuộc họp vào máy tính thành công!",
        "filename": filename,
        "file_size": len(contents),
        "download_url": f"/api/download/recordings/{filename}"
    }

@app.get("/api/download/recordings/{filename}")
def download_recording_file(filename: str):
    """Tải file ghi âm âm thanh từ thư mục recordings"""
    file_path = os.path.join(settings.RECORDINGS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File ghi âm không tồn tại")
    
    ext = os.path.splitext(filename.lower())[1]
    media_map = {
        ".webm": "audio/webm",
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".mp4": "audio/mp4",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg"
    }
    media_type = media_map.get(ext, "application/octet-stream")
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type
    )

@app.get("/api/meetings/{session_id}/files")
def get_meeting_files(session_id: str):
    """Lấy danh sách toàn bộ các file lưu trữ trong phiên họp (Audio, Text, Word)"""
    session = meeting_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên họp")
    files = session.get_all_files()
    storage_dir = session.metadata.get("storage_dir") or settings.OUTPUT_DIR
    return {
        "session_id": session_id,
        "storage_dir": storage_dir,
        "files": files
    }

@app.post("/api/meetings/{session_id}/open-folder")
def open_meeting_folder(session_id: str):
    """Mở trực tiếp thư mục lưu trữ hồ sơ cuộc họp trong File Explorer của Windows"""
    session = meeting_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên họp")
    folder = session.metadata.get("storage_dir") or settings.OUTPUT_DIR
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    try:
        if os.name == 'nt':
            os.startfile(folder)
        else:
            import subprocess
            subprocess.Popen(['xdg-open', folder])
        return {"success": True, "folder": folder, "message": f"Đã mở thư mục: {folder}"}
    except Exception as e:
        return {"success": False, "error": str(e), "folder": folder}

class OpenLocalPathRequest(BaseModel):
    path: str

@app.post("/api/open-local-path")
def open_local_path(req: OpenLocalPathRequest):
    """Mở thư mục bất kỳ trên máy tính người dùng"""
    folder = req.path or settings.OUTPUT_DIR
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    try:
        if os.name == 'nt':
            os.startfile(folder)
        else:
            import subprocess
            subprocess.Popen(['xdg-open', folder])
        return {"success": True, "folder": folder, "message": f"Đã mở thư mục: {folder}"}
    except Exception as e:
        return {"success": False, "error": str(e), "folder": folder}

@app.get("/api/download/transcripts/{filename}")
def download_transcript_file(filename: str):
    """Tải file text chữ thoại nguyên văn từ thư mục transcripts"""
    file_path = os.path.join(settings.TRANSCRIPTS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File chữ thoại không tồn tại")
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/plain; charset=utf-8"
    )

@app.get("/api/download/{filename}")
def download_file(filename: str):
    """Tải file .docx, .txt hoặc file ghi âm"""
    file_path = os.path.join(settings.OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        rec_path = os.path.join(settings.RECORDINGS_DIR, filename)
        tr_path = os.path.join(settings.TRANSCRIPTS_DIR, filename)
        if os.path.exists(rec_path):
            file_path = rec_path
        elif os.path.exists(tr_path):
            file_path = tr_path
        else:
            raise HTTPException(status_code=404, detail="File không tồn tại")
            
    ext = os.path.splitext(filename.lower())[1]
    media_map = {
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".txt": "text/plain; charset=utf-8",
        ".webm": "audio/webm",
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".mp4": "audio/mp4",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg"
    }
    media_type = media_map.get(ext, "application/octet-stream")
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type
    )

@app.get("/api/meetings/demo-scenario/{option}")
def get_demo_scenario(option: str):
    """Lấy kịch bản hội thoại mẫu phục vụ tính năng Demo 1-Click"""
    if option == "option_1":
        return {
            "mode": "option_1",
            "title": "Cuộc họp Giao ban Triển khai Kế hoạch Trọng tâm Quý 4/2026",
            "chairperson": "Bà Phan Thị Phát (Tổng Giám Đốc)",
            "secretary": "Bà Lê Thu Thảo (Thư ký Ban TGĐ)",
            "participants": [
                "1. Bà Phan Thị Phát - Tổng Giám Đốc (Chủ trì)",
                "2. Ông Đặng Minh Trí - Trưởng Phòng Kinh Doanh",
                "3. Ông Phạm Đức Huy - Trưởng Phòng Kỹ Thuật",
                "4. Bà Nguyễn Mai Phương - Kế toán Trưởng"
            ],
            "dialogues": DEMO_MEETING_OPTION_1
        }
    else:
        return {
            "mode": "option_2",
            "project_title": "Đàm phán Hợp đồng Cung cấp 60 Thiết bị Lọc nước Ion Kiềm iONPIA",
            "partner_name": "Công ty TNHH Đầu tư & Phát triển Tân Phát Đạt",
            "klp_signer": "Ông Trần Văn Hùng - Phó Tổng Giám Đốc",
            "partner_signer": "Ông Vũ Đình Toàn - Giám Đốc Dự Án",
            "klp_reps": [
                "• Ông Trần Văn Hùng - Phó Tổng Giám Đốc",
                "• Ông Đặng Minh Trí - Trưởng Phòng Kinh Doanh",
                "• Thư ký ghi nhận: Bà Lê Thu Thảo"
            ],
            "partner_reps": [
                "• Tên Đơn vị: Công ty TNHH Đầu tư & Phát triển Tân Phát Đạt",
                "• Ông Vũ Đình Toàn - Giám Đốc Dự Án",
                "• Bà Hoàng Thị Nga - Trưởng Phòng Mua Sắm & Đấu Thầu"
            ],
            "dialogues": DEMO_MEETING_OPTION_2
        }

# WebSocket Endpoint cho Live Audio/Text Streaming
@app.websocket("/ws/meeting")
async def websocket_meeting_endpoint(websocket: WebSocket):
    await websocket.accept()
    current_session: Optional[MeetingSession] = None

    try:
        while True:
            raw_text = await websocket.receive_text()
            data = json.loads(raw_text)
            event_type = data.get("type")

            if event_type == "join_session":
                session_id = data.get("session_id")
                current_session = meeting_manager.get_session(session_id)
                await websocket.send_text(json.dumps({
                    "type": "joined",
                    "session_id": session_id,
                    "state": current_session.analysis_state if current_session else None
                }))

            elif event_type == "audio_chunk":
                # Nhận mẩu âm thanh PCM/WAV (Base64) - chỉ xử lý khi client chỉ định speaker cụ thể
                audio_base64 = data.get("audio_data", "")
                chosen_speaker = data.get("speaker")
                if audio_base64 and current_session and chosen_speaker:
                    audio_bytes = base64.b64decode(audio_base64)
                    stt_result = await stt_service.transcribe_audio_chunk(audio_bytes)
                    text_content = (stt_result.get("text") or "").strip()
                    noise_markers = ["[tiếng ồn]", "tiếng ồn", "[im lặng]", "im lặng", "[tiếng thở]", "noise", "silence", "[âm thanh]"]
                    if text_content and text_content.lower() not in noise_markers and not (text_content.startswith("[") and text_content.endswith("]")) and len(text_content) >= 3:
                        seg = current_session.add_transcript_segment(
                            speaker=chosen_speaker,
                            text=text_content
                        )
                        if seg:
                            await websocket.send_text(json.dumps({
                                "type": "new_transcript",
                                "segment": seg
                            }))

            elif event_type == "transcript_chunk":
                if current_session:
                    raw_txt = (data.get("text") or "").strip()
                    noise_markers = ["[tiếng ồn]", "tiếng ồn", "[im lặng]", "im lặng", "[tiếng thở]", "noise", "silence", "[âm thanh]"]
                    if raw_txt and raw_txt.lower() not in noise_markers and len(raw_txt) >= 2:
                        seg = current_session.add_transcript_segment(
                            speaker=data.get("speaker", "Người phát biểu"),
                            text=raw_txt,
                            timestamp=data.get("timestamp"),
                            is_bookmark=data.get("is_bookmark", False),
                            note=data.get("note", "")
                        )
                        if seg:
                            await websocket.send_text(json.dumps({
                                "type": "new_transcript",
                                "segment": seg
                            }))

            elif event_type == "trigger_analysis":
                if current_session:
                    analysis = await current_session.run_ai_analysis()
                    await websocket.send_text(json.dumps({
                        "type": "analysis_updated",
                        "analysis_state": analysis
                    }))

            elif event_type == "bookmark":
                if current_session:
                    bm = current_session.mark_bookmark(
                        transcript_id=data.get("transcript_id"),
                        custom_text=data.get("custom_text", "")
                    )
                    await websocket.send_text(json.dumps({
                        "type": "bookmark_added",
                        "bookmark": bm
                    }))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")

# Phục vụ Frontend Static Files
frontend_dir = settings.FRONTEND_DIR

@app.get("/")
def serve_index():
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Giao diện index.html không tồn tại")

if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
