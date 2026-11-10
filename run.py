import os
import sys

# Thêm thư mục backend vào sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

# Đảm bảo stdout luôn unbuffered và UTF-8 trên Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"============================================================")
    print(f"  CÔNG TY CỔ PHẦN TẬP ĐOÀN KIM LONG PHÁT")
    print(f"  BOT AI TRỢ LÝ THƯ KÝ GHI ÂM - PHÂN TÍCH CUỘC HỌP THỜI GIAN THỰC")
    print(f"  Hệ thống đang chạy tại: http://localhost:{settings.SERVER_PORT}")
    print(f"============================================================")
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=False
    )
