"""
Từ điển chuyên ngành và danh bạ nội bộ của CÔNG TY CỔ PHẦN TẬP ĐOÀN KIM LONG PHÁT
Hỗ trợ Custom Vocabulary cho Speech-to-Text và nhận diện thực thể (Entity Recognition)
"""

# Danh bạ Lãnh đạo & Nhân sự chủ chốt
LEADERSHIP_MEMBERS = [
    {"name": "Ông Nguyễn Kim Long", "role": "Chủ tịch Hội đồng Quản trị", "dept": "Ban Lãnh Đạo"},
    {"name": "Bà Phan Thị Phát", "role": "Tổng Giám Đốc", "dept": "Ban Tổng Giám Đốc"},
    {"name": "Ông Trần Văn Hùng", "role": "Phó Tổng Giám Đốc Phụ trách Vận hành & Dự án", "dept": "Ban TGĐ"},
    {"name": "Bà Lê Thu Thảo", "role": "Thư ký Ban Tổng Giám Đốc", "dept": "Ban Thư ký"},
    {"name": "Ông Vũ Hoàng Nam", "role": "Trưởng Ban Kế hoạch & Dự án", "dept": "Khối Dự Án"},
    {"name": "Ông Đặng Minh Trí", "role": "Trưởng Phòng Kinh Doanh Toàn quốc", "dept": "Khối Kinh Doanh"},
    {"name": "Bà Nguyễn Mai Phương", "role": "Kế toán Trưởng", "dept": "Phòng Tài chính - Kế toán"},
    {"name": "Ông Phạm Đức Huy", "role": "Trưởng Phòng Kỹ thuật & Công nghệ", "dept": "Khối Kỹ Thuật"},
    {"name": "Luật sư Hoàng Tuấn Anh", "role": "Trưởng Ban Pháp chế & Kiểm soát Tuân thủ", "dept": "Ban Pháp Chế"},
    {"name": "Bà Đỗ Thị Bích", "role": "Giám đốc Nhân sự & Đào tạo", "dept": "Khối Nhân Sự"}
]

# Các phòng ban và khối chức năng
DEPARTMENTS = [
    "Ban Tổng Giám Đốc",
    "Khối Kinh Doanh & Phân Phối",
    "Khối Dự Án & Đầu Tư",
    "Phòng Kỹ Thuật - Nghiên Cứu & Bảo Hành",
    "Phòng Tài Chính - Kế Toán",
    "Ban Pháp Chế & Đấu Thầu",
    "Khối Marketing & Truyền Thông",
    "Khối Nhân Sự & Hành Chính"
]

# Danh mục Sản phẩm & Dự án tiêu biểu của Tập đoàn Kim Long Phát
PRODUCTS_AND_PROJECTS = [
    {"code": "ION-9000", "name": "Máy tạo nước ion kiềm giàu hydro iONPIA / Kangen", "category": "Thiết bị y tế chăm sóc sức khỏe"},
    {"code": "H2-PORTABLE", "name": "Bình tạo nước giàu Hydro cầm tay công nghệ SPE/PEM", "category": "Sản phẩm cá nhân cao cấp"},
    {"code": "RO-PRO", "name": "Hệ thống lọc nước tổng tòa nhà công nghiệp KLP-Pure", "category": "Dự án cấp nước sạch đô thị"},
    {"code": "MED-CARE", "name": "Hệ thống nước vô trùng y tế dùng trong phòng mổ & bệnh viện", "category": "Thiết bị y tế chuyên dụng"},
    {"code": "AIR-CLEAN", "name": "Máy lọc không khí và khử khuẩn ion âm công suất lớn", "category": "Thiết bị xử lý môi trường"},
    {"code": "PROJ-HOCDUONG", "name": "Dự án Nước uống tinh khiết học đường 2026", "category": "Dự án hợp tác công - tư"},
    {"code": "PROJ-KDT-NAMSAIGON", "name": "Gói thầu cấp nước lọc ion kiềm Tổ hợp căn hộ cao cấp Nam Sài Gòn", "category": "Dự án Bất động sản"}
]

# Thuật ngữ Thương mại & Đàm phán
COMMERCIAL_TERMS = [
    "Chiết khấu đại lý (Discount Rate)",
    "Hạn mức công nợ & Thời hạn thanh toán (Credit Limit & Payment Term)",
    "Bảo lãnh thực hiện hợp đồng (Performance Bond)",
    "Biên bản nghiệm thu kỹ thuật (Acceptance Testing)",
    "Cam kết bảo hành 24/7 (SLA & Warranty)",
    "Phạt vi phạm tiến độ (Penalty Clause)",
    "Chỉ số ORP âm, nồng độ Hydro hòa tan (ppb), độ pH chuẩn y tế"
]

def get_vocabulary_prompt() -> str:
    """Tạo chuỗi context nạp sẵn cho AI để đảm bảo viết đúng chính tả tên người, đơn vị và sản phẩm"""
    leaders = ", ".join([f"{m['name']} ({m['role']})" for m in LEADERSHIP_MEMBERS])
    products = ", ".join([p["name"] for p in PRODUCTS_AND_PROJECTS])
    
    return f"""TỪ ĐIỂN CHUẨN NỘI BỘ TẬP ĐOÀN KIM LONG PHÁT:
- Tên công ty: CÔNG TY CỔ PHẦN TẬP ĐOÀN KIM LONG PHÁT (Viết tắt: Kim Long Phát, KLP).
- Ban Lãnh đạo & Cán bộ: {leaders}.
- Sản phẩm & Dự án chính: {products}.
- Yêu cầu chính tả: Khi người nói phát âm tên Lãnh đạo hoặc tên sản phẩm, luôn ưu tiên chuẩn hóa theo danh bạ trên.
"""
