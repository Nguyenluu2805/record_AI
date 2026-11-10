"""
Kịch bản Cuộc họp Mẫu Thực tế của CÔNG TY CỔ PHẦN TẬP ĐOÀN KIM LONG PHÁT
Dùng cho tính năng 'Chạy Thử Cuộc Họp Mẫu (Demo)' giúp Thư ký và Ban Giám Đốc
nghiệm thu toàn bộ luồng hoạt động 2 cột thời gian thực và xuất file Word ngay lập tức.
"""

from typing import List, Dict, Any

# Kịch bản Option 1: Họp Giao Ban Nội Bộ Tập Đoàn Kim Long Phát
DEMO_MEETING_OPTION_1: List[Dict[str, Any]] = [
    {
        "speaker": "Bà Phan Thị Phát (Tổng Giám Đốc)",
        "role": "Chủ trì cuộc họp",
        "timestamp": "09:00:15",
        "text": "Chào các anh chị lãnh đạo các phòng ban. Hôm nay chúng ta họp giao ban trọng tâm về kế hoạch nước rút Quý 4/2026. Mục tiêu số một là rà soát doanh số dòng máy tạo nước ion kiềm iONPIA, và thứ hai là tháo gỡ dứt điểm tiến độ bàn giao cho dự án Tổ hợp Nam Sài Gòn. Đề nghị anh Trí báo cáo trước về tình hình kinh doanh.",
        "is_bookmark": False,
        "note": ""
    },
    {
        "speaker": "Ông Đặng Minh Trí (Trưởng Phòng Kinh Doanh)",
        "role": "Báo cáo phòng ban",
        "timestamp": "09:01:02",
        "text": "Dạ thưa Tổng Giám Đốc và các anh chị, tính đến hết tháng 10, Khối Kinh Doanh đã đạt 88% chỉ tiêu quý. Hiện tại chúng tôi đang đàm phán cung cấp 50 máy lọc ion kiềm chuyên dụng cho chuỗi phòng khám quốc tế. Khách hàng muốn nâng mức chiết khấu từ 8% lên 12%. Tôi xin ý kiến Ban Giám Đốc cho phép áp dụng mức chiết khấu 12% này để chốt đơn ngay trong tuần.",
        "is_bookmark": False,
        "note": "Kinh doanh đề xuất chiết khấu 12% cho lô 50 máy"
    },
    {
        "speaker": "Bà Phan Thị Phát (Tổng Giám Đốc)",
        "role": "Chủ trì cuộc họp",
        "timestamp": "09:02:18",
        "text": "Về đề xuất này, tôi đồng ý duyệt mức chiết khấu 12%, NHƯNG với điều kiện đối tác phải thanh toán tạm ứng 30% và phần còn lại không được để công nợ quá 15 ngày. Anh Trí phụ trách chốt hợp đồng này trước 17h00 ngày 12 tháng 11. Tuyệt đối không để phát sinh công nợ xấu cuối năm.",
        "is_bookmark": True,
        "note": "⭐ Sếp duyệt chiết khấu 12% kèm điều kiện tạm ứng 30%, deadline 12/11"
    },
    {
        "speaker": "Ông Phạm Đức Huy (Trưởng Phòng Kỹ Thuật)",
        "role": "Báo cáo phòng ban",
        "timestamp": "09:03:45",
        "text": "Báo cáo Sếp, về tiến độ dự án Nam Sài Gòn, toàn bộ 120 bộ linh kiện lọc nước công nghệ SPE/PEM đã về tới kho KLP. Tuy nhiên do mặt bằng bên đối tác bàn giao chậm 2 ngày nên tiến độ lắp đặt bị trễ một chút. Phòng Kỹ thuật xin được điều động thêm 4 nhân sự tăng ca cuối tuần để kịp nghiệm thu đúng hẹn.",
        "is_bookmark": False,
        "note": "Kỹ thuật xin tăng ca 4 người dự án Nam Sài Gòn"
    },
    {
        "speaker": "Bà Phan Thị Phát (Tổng Giám Đốc)",
        "role": "Chủ trì cuộc họp",
        "timestamp": "09:04:50",
        "text": "Tôi đồng ý duyệt phương án tăng ca. Anh Huy chủ động phân công anh em kỹ thuật viên, phải đảm bảo hoàn thành nghiệm thu kỹ thuật chậm nhất ngày 14 tháng 11, không làm ảnh hưởng đến uy tín thương hiệu Kim Long Phát với chủ đầu tư.",
        "is_bookmark": True,
        "note": "⭐ Sếp duyệt tăng ca, chốt nghiệm thu kỹ thuật ngày 14/11"
    },
    {
        "speaker": "Bà Nguyễn Mai Phương (Kế toán Trưởng)",
        "role": "Báo cáo phòng ban",
        "timestamp": "09:05:40",
        "text": "Về mặt tài chính, dòng tiền hiện tại rất lành mạnh, sẵn sàng giải ngân chi phí tăng ca và thanh toán cho nhà cung cấp thiết bị nhập khẩu. Tôi lưu ý anh Trí và anh Huy nộp đủ hóa đơn chứng từ trước ngày 15 tháng 11 để kế toán kịp khóa sổ tài chính tháng.",
        "is_bookmark": False,
        "note": "Kế toán lưu ý nộp chứng từ trước 15/11"
    },
    {
        "speaker": "Bà Phan Thị Phát (Tổng Giám Đốc)",
        "role": "Chủ trì cuộc họp",
        "timestamp": "09:06:30",
        "text": "Tốt. Riêng vấn đề quy chế thưởng hoa hồng cho đại lý miền Trung thì để sáng thứ Hai tuần sau Ban Giám Đốc sẽ họp phiên chuyên đề riêng. Thư ký ghi rõ các đầu việc, phân công người phụ trách và thời hạn để xuất biên bản gửi cho tôi ký duyệt ngay sau cuộc họp này.",
        "is_bookmark": False,
        "note": "Chốt kết thúc họp, xuất biên bản"
    }
]

# Kịch bản Option 2: Đàm phán Hợp đồng Đối tác Khách hàng
DEMO_MEETING_OPTION_2: List[Dict[str, Any]] = [
    {
        "speaker": "Ông Trần Văn Hùng (Phó TGĐ Kim Long Phát)",
        "role": "Đại diện Bên A (KLP)",
        "timestamp": "14:00:10",
        "text": "Kính chào anh Toàn và chị Nga bên Tân Phát Đạt. Rất vui được tiếp đón quý công ty tại trụ sở Tập đoàn Kim Long Phát. Hôm nay chúng ta làm việc để thống nhất các điều khoản thương mại cho gói 60 máy tạo nước ion kiềm giàu hydro iONPIA cho dự án căn hộ dịch vụ cao cấp của bên anh.",
        "is_bookmark": False,
        "note": ""
    },
    {
        "speaker": "Ông Vũ Đình Toàn (Giám Đốc Dự Án Tân Phát Đạt)",
        "role": "Đại diện Bên B (Đối tác)",
        "timestamp": "14:01:05",
        "text": "Chào anh Hùng và đội ngũ Kim Long Phát. Về mặt kỹ thuật, Hội đồng chuyên môn của chúng tôi đánh giá rất cao dòng máy iONPIA của KLP, đặc biệt là nồng độ hydro hòa tan cao và chứng nhận thiết bị y tế. Dự án của chúng tôi cần bàn giao đợt 1 trước ngày 20 tháng 11 để kịp lễ khai trương.",
        "is_bookmark": False,
        "note": "Đối tác đánh giá rất cao chất lượng iONPIA (Buying Signal!)"
    },
    {
        "speaker": "Bà Hoàng Thị Nga (Trưởng Phòng Mua Sắm Tân Phát Đạt)",
        "role": "Đại diện Bên B (Đối tác)",
        "timestamp": "14:02:15",
        "text": "Tuy nhiên về mặt thương mại, báo giá tổng 1.85 tỷ VNĐ với mức chiết khấu 8% bên KLP đưa ra vẫn hơi cao so với ngân sách của chúng tôi. Chúng tôi đề nghị Kim Long Phát nâng mức chiết khấu lên 10%. Ngoài ra về thanh toán, bên tôi muốn tạm ứng 20%, còn 80% thanh toán sau khi nghiệm thu 30 ngày.",
        "is_bookmark": True,
        "note": "⭐ Đối tác đòi chiết khấu 10% và công nợ 30 ngày (Red Flag công nợ!)"
    },
    {
        "speaker": "Ông Đặng Minh Trí (Trưởng Phòng Kinh Doanh KLP)",
        "role": "Đại diện Bên A (KLP)",
        "timestamp": "14:03:30",
        "text": "Thưa chị Nga, mức giá 1.85 tỷ đã bao gồm toàn bộ chi phí phụ kiện nhập khẩu cao cấp và gói lắp đặt tận nơi. Nếu áp dụng công nợ 30 ngày cho 80% giá trị hợp đồng thì rủi ro dòng tiền cho bên em rất lớn. Kim Long Phát đề xuất phương án: Tạm ứng 25%, thanh toán 75% ngay khi bàn giao nghiệm thu đợt 1, đổi lại KLP tặng thêm gói bảo dưỡng định kỳ 24 tháng miễn phí trị giá 60 triệu VNĐ.",
        "is_bookmark": False,
        "note": "KLP phản hồi: Tạm ứng 25%, thanh toán 75% khi nghiệm thu + tặng bảo dưỡng 2 năm"
    },
    {
        "speaker": "Ông Vũ Đình Toàn (Giám Đốc Dự Án Tân Phát Đạt)",
        "role": "Đại diện Bên B (Đối tác)",
        "timestamp": "14:04:45",
        "text": "Gói bảo dưỡng 24 tháng hỗ trợ 24/7 của KLP rất thiết thực vì căn hộ dịch vụ cần đảm bảo nước uống liên tục cho cư dân. Về tiến độ, các anh cam kết giao đợt 1 30 máy trước ngày 20 tháng 11 chứ? Điều khoản phạt nếu chậm tiến độ là 0.05% mỗi ngày?",
        "is_bookmark": False,
        "note": "Đối tác ưng ý gói bảo dưỡng 24/7, hỏi chốt điều khoản phạt 0.05%/ngày"
    },
    {
        "speaker": "Ông Trần Văn Hùng (Phó TGĐ Kim Long Phát)",
        "role": "Đại diện Bên A (KLP)",
        "timestamp": "14:05:40",
        "text": "Chắc chắn rồi anh Toàn. Kim Long Phát cam kết bàn giao đợt 1 trước 20/11 và đồng thuận mức phạt vi phạm 0.05%/ngày đối xứng cho cả hai bên. Về chiết khấu, để thiện chí hợp tác lâu dài, KLP sẽ chốt ở mức 8.5% và giữ nguyên gói tặng bảo dưỡng 24 tháng. Anh Toàn thấy phương án này có thể chốt được chưa?",
        "is_bookmark": True,
        "note": "⭐ KLP chốt chiết khấu 8.5% + tặng bảo dưỡng + giao đợt 1 trước 20/11"
    },
    {
        "speaker": "Ông Vũ Đình Toàn (Giám Đốc Dự Án Tân Phát Đạt)",
        "role": "Đại diện Bên B (Đối tác)",
        "timestamp": "14:06:50",
        "text": "Tôi đồng ý với phương án này của anh Hùng. Chiều nay tôi sẽ báo cáo lại Ban Giám Đốc bên tôi để phê duyệt chính thức. Đề nghị bên KLP gửi lại dự thảo hợp đồng hoàn chỉnh kèm phụ lục trước 17h00 ngày mai để hai bên tiến hành ký kết.",
        "is_bookmark": False,
        "note": "Deal chốt! Đối tác đồng ý, yêu cầu gửi hợp đồng trước 17h ngày mai"
    }
]
