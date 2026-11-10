# BOT AI GHI ÂM & CHUYỂN GIỌNG NÓI THÀNH VĂN BẢN (STT)
### CÔNG TY CỔ PHẦN TẬP ĐOÀN KIM LONG PHÁT

Hệ thống AI Voice Recorder & Speech-to-Text chuyên dụng: **Thu âm 2 kênh (Microphone + Loa Zoom/Meet) hoặc Nạp file ghi âm có sẵn (.mp3/.wav/.m4a) $\rightarrow$ Chuyển giọng nói tiếng Việt thành văn bản tức thì với dấu câu chuẩn xác $\rightarrow$ Sao chép hoặc Xuất file Word (.docx) & Text (.txt).**

Hỗ trợ 2 chế độ linh hoạt:
1. **🎙️ Chế độ Ghi Âm & Chuyển Văn Bản (STT Studio)**: Tối giản, tập trung 100% vào việc thu âm, nghe nói và nhảy chữ tiếng Việt trực tiếp, bóc tách mốc thời gian, đếm từ, sao chép và tải file.
2. **📑 Chế độ Trợ Lý Thư Ký & Phân Tích Cuộc Họp**: Vừa chạy chữ thoại theo từng người phát biểu, vừa phân tích chỉ đạo, tính % phát biểu, lập bảng Action Items hoặc phân tích đàm phán đối tác (Deal Score 1-10) và xuất Biên bản cuộc họp chuẩn hành chính KLP.

---

## 🌟 Tính năng Cốt lõi

1. **Luồng thao tác 3 bước dành cho Thư ký**:
   - **Bước 1 - Thiết lập nhanh (10 giây)**:
     - Chọn chế độ: **Option 1 (Họp Nội Bộ KLP)** hoặc **Option 2 (Họp Đối Tác / Khách Hàng)**.
     - Chọn nguồn thu âm: *Chỉ Micro phòng họp* hoặc *Micro + Âm thanh hệ thống (2 kênh)*.
     - Chọn nhanh thành viên tham dự từ danh bạ Lãnh đạo Tập đoàn Kim Long Phát.
   - **Bước 2 - Trong cuộc họp (2 cột trực tiếp)**:
     - Cột trái: Chữ thoại tiếng Việt theo từng người nói, thời gian `[HH:MM:SS]`, avatar và badge người nói.
     - Cột phải: Bản phân tích cập nhật dần (Ý kiến chỉ đạo, báo cáo phòng ban, tỷ lệ nói %, việc đã chốt/tồn đọng, Action Items, Deal Score 1-10, Tín hiệu tích cực, Cảnh báo Red Flags).
     - Nút **[⭐ Đánh dấu nóng]** (Phím tắt `F2` hoặc `Ctrl + B`) để highlight mốc chỉ đạo nóng của Lãnh đạo.
     - Khung **Ghi chú nhanh của Thư ký**: Nhập ghi chú bullet point và đẩy trực tiếp vào AI phân tích.
   - **Bước 3 - Rà soát & Xuất File Word (.docx)**:
     - Xem trước bản biên bản hoàn chỉnh.
     - Tải về file `.docx` đúng chuẩn thể thức văn bản hành chính của Tập đoàn Kim Long Phát (Số hiệu, Tiêu ngữ, Bảng kẻ border, Chỗ ký tên 2 bên).
     - Với Option 2: Hỗ trợ xuất riêng **Bản Nội Bộ KLP (kèm Phân tích Mật)** hoặc **Bản Gửi Đối Tác (Chỉ gồm Phần A & C)**.

2. **Công nghệ AI & Nhận diện**:
   - Tích hợp **Google Gemini Audio & Multimodal Live API** phân tích trực tiếp với độ trễ thấp.
   - **Custom Vocabulary**: Nạp sẵn danh bạ Ban Lãnh đạo (Chủ tịch HĐQT, Tổng Giám Đốc, các Phó TGĐ, Trưởng phòng) và danh mục sản phẩm chủ lực (Máy tạo nước ion kiềm giàu hydro iONPIA/Kangen, thiết bị y tế SPE/PEM, các dự án học đường và khu đô thị Nam Sài Gòn).
   - Cơ chế **Fallback Rule-based Analysis**: Luôn đảm bảo hệ thống trích xuất dữ liệu mượt mà ngay cả khi ngoại tuyến hoặc gián đoạn mạng.

3. **Tính năng Demo 1-Click (Chạy thử Cuộc họp Mẫu)**:
   - Nút **[✨ Chạy Thử Cuộc Họp Mẫu (Demo KLP)]** giúp Thư ký và Ban Giám Đốc nghiệm thu ngay lập tức trải nghiệm 2 cột thời gian thực mà không cần chuẩn bị phòng họp thật.

---

## 🚀 Hướng dẫn Cài đặt & Khởi chạy

### 1. Môi trường yêu cầu
- Hệ điều hành: Windows / macOS / Linux
- Python: 3.10+ (Đã cấu hình trong thư mục `.venv`)

### 2. Cấu hình biến môi trường (`.env`)
File `.env` tại thư mục gốc:
```env
GEMINI_API_KEY=AIzaSy...your_gemini_api_key_here
GEMINI_MODEL=gemini-flash-lite-latest
SERVER_HOST=127.0.0.1
SERVER_PORT=8000
```

### 3. Khởi chạy ứng dụng
Chạy lệnh từ PowerShell hoặc Terminal:
```powershell
.venv\Scripts\python.exe run.py
```

Truy cập hệ thống trên trình duyệt:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 📁 Cấu trúc Thư mục Dự án

```
review_agent/
├── backend/
│   └── app/
│       ├── config.py              # Cấu hình hệ thống & Tập đoàn KLP
│       ├── main.py                # REST API & WebSocket streaming
│       └── services/
│           ├── vocabulary.py      # Danh bạ Lãnh đạo, Phòng ban & Sản phẩm KLP
│           ├── prompts.py         # System Prompts chuẩn Option 1 & Option 2
│           ├── meeting_service.py # Quản lý phiên họp, Live State & AI analysis
│           ├── docx_exporter.py   # Xuất file Word .docx chuẩn hành chính KLP
│           ├── stt_service.py     # Xử lý âm thanh & nhận diện giọng nói tiếng Việt
│           └── demo_scenarios.py  # Kịch bản họp mẫu Option 1 & Option 2
├── frontend/
│   ├── index.html                 # Giao diện Thư ký KLP 3 bước
│   ├── css/style.css              # Bộ giao diện thương hiệu Navy/Gold KLP
│   └── js/
│       ├── app.js                 # Điều khiển luồng họp, AI phân tích, xuất Word
│       └── audio_recorder.js      # Thu âm 2 kênh (Micro + Âm thanh hệ thống)
├── output/                        # Thư mục lưu trữ các file Word (.docx) đã xuất
├── run.py                         # File khởi chạy chính
└── requirements.txt               # Danh sách thư viện phụ thuộc
```
