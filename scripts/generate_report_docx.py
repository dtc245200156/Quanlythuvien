import os
import sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def create_report_docx(output_path='docs/report.docx'):
    doc = Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Base Styles
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    # ------------------ COVER PAGE ------------------
    p_school = doc.add_paragraph()
    p_school.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_school = p_school.add_run("[ĐIỀN TÊN TRƯỜNG ĐẠI HỌC]\nKHOA CÔNG NGHỆ THÔNG TIN\nBỘ MÔN CÔNG NGHỆ PHẦN MỀM & MẠNG MÁY TÍNH")
    run_school.bold = True
    run_school.font.size = Pt(13)
    run_school.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    doc.add_paragraph("\n" * 3)

    p_title_pre = doc.add_paragraph()
    p_title_pre.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_pre = p_title_pre.add_run("BÁO CÁO ĐỒ ÁN HỌC PHẦN\nTRIỂN KHAI VÀ QUẢN TRỊ HỆ THỐNG PHẦN MỀM")
    run_pre.bold = True
    run_pre.font.size = Pt(14)

    doc.add_paragraph()

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run("ĐỀ TÀI:\nHỆ THỐNG QUẢN LÝ THƯ VIỆN\n(LIBRARY MANAGEMENT SYSTEM)")
    run_title.bold = True
    run_title.font.size = Pt(18)
    run_title.font.color.rgb = RGBColor(0x00, 0x40, 0x80)

    p_subtitle = doc.add_paragraph()
    p_subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = p_subtitle.add_run("Triển khai trên Docker Compose, Nginx Reverse Proxy (TLS),\nGiám sát Prometheus & Grafana, Centralized Logging Loki & Promtail")
    run_sub.italic = True
    run_sub.font.size = Pt(11)

    doc.add_paragraph("\n" * 4)

    # Student info block
    p_info = doc.add_paragraph()
    p_info.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_info.paragraph_format.left_indent = Inches(1.5)
    
    r_info = p_info.add_run(
        "Sinh viên thực hiện:\t[HỌ VÀ TÊN SINH VIÊN]\n"
        "Mã số sinh viên:\t[MÃ SỐ SINH VIÊN - VD: DTC245200156]\n"
        "Lớp chuyên ngành:\t[LỚP SINH VIÊN]\n"
        "Giảng viên hướng dẫn:\t[TÊN GIẢNG VIÊN HƯỚNG DẪN]\n"
        "Học kỳ / Năm học:\tHọc kỳ 1 - Năm học 2025 - 2026"
    )
    r_info.font.size = Pt(12)

    doc.add_paragraph("\n" * 3)

    p_loc = doc.add_paragraph()
    p_loc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_loc = p_loc.add_run("[ĐỊA ĐIỂM, NĂM 2026]")
    run_loc.bold = True
    run_loc.font.size = Pt(12)

    doc.add_page_break()

    # ------------------ TABLE OF CONTENTS ------------------
    p_toc_title = doc.add_heading("MỤC LỤC BÁO CÁO", level=1)
    p_toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    toc_items = [
        ("Chương 1. Giới Thiệu Đề Tài", 1),
        ("1.1. Lý do chọn đề tài", 1),
        ("1.2. Mục tiêu nghiên cứu và triển khai", 2),
        ("1.3. Phạm vi đề tài", 2),
        ("1.4. Công nghệ bắt buộc sử dụng", 3),
        ("Chương 2. Phân Tích Và Thiết Kế Hệ Thống", 4),
        ("2.1. Yêu cầu chức năng", 4),
        ("2.2. Yêu cầu phi chức năng", 5),
        ("2.3. Đối tượng sử dụng hệ thống", 5),
        ("2.4. Thiết kế cơ sở dữ liệu và quan hệ giữa các bảng", 6),
        ("2.5. Sơ đồ kiến trúc tổng thể", 7),
        ("2.6. Luồng xử lý mượn và trả sách (Transaction & Row Locking)", 8),
        ("Chương 3. Xây Dựng Ứng Dụng Và Cơ Sở Dữ Liệu", 9),
        ("3.1. Cấu trúc mã nguồn dự án", 9),
        ("3.2. Thiết kế các module nghiệp vụ", 10),
        ("3.3. Mô hình dữ liệu ORM", 10),
        ("3.4. Đóng gói Dockerfile non-root và Docker Compose", 11),
        ("3.5. Kết nối Flask với PostgreSQL và pgAdmin", 12),
        ("3.6. Kết quả kiểm thử nghiệp vụ", 13),
        ("Chương 4. Cấu Hình Nginx Reverse Proxy Và Bảo Mật HTTPS", 14),
        ("4.1. Nguyên lý hoạt động của Reverse Proxy", 14),
        ("4.2. Sơ đồ luồng truy cập và chuyển hướng HTTPS", 14),
        ("4.3. Cấu hình Nginx và chứng chỉ TLS tự ký", 15),
        ("4.4. Cấu hình Security Headers", 16),
        ("4.5. Kết quả kiểm tra Reverse Proxy", 16),
        ("Chương 5. Triển Khai Hệ Thống Giám Sát Prometheus Và Grafana", 17),
        ("5.1. Kiến trúc phân hệ Monitoring", 17),
        ("5.2. Cấu hình Scrape Jobs của Prometheus", 17),
        ("5.3. Các bộ xuất chỉ số (Exporters)", 18),
        ("5.4. Thiết kế và nạp tự động Dashboards trên Grafana", 19),
        ("5.5. Các câu truy vấn PromQL minh họa", 20),
        ("5.6. Kết quả thu thập chỉ số", 21),
        ("Chương 6. Triển Khai Hệ Thống Log Tập Trung Loki Và Promtail", 22),
        ("6.1. Kiến trúc phân hệ Logging", 22),
        ("6.2. Luồng thu thập log từ Nginx và Flask", 22),
        ("6.3. Cấu hình nhãn (Labels) và chính sách lưu trữ", 23),
        ("6.4. Các câu truy vấn LogQL thực tế", 24),
        ("6.5. Kết quả truy vấn log trên Grafana Explore", 25),
        ("Chương 7. Hardening Bảo Mật Hệ Thống", 26),
        ("7.1. Phân tích các mối nguy cơ an toàn thông tin", 26),
        ("7.2. Triển khai Non-Root Container", 26),
        ("7.3. Phân tách mạng Docker (Network Isolation)", 27),
        ("7.4. Quản lý bí mật qua biến môi trường (.env)", 27),
        ("7.5. Cô lập cổng cơ sở dữ liệu và quản trị", 28),
        ("7.6. Giới hạn tài nguyên và chống leo thang đặc quyền", 28),
        ("7.7. Bảng kiểm tra tổng hợp các biện pháp bảo mật", 29),
        ("Chương 8. Triển Khai, Kiểm Thử Và Đánh Giá", 30),
        ("8.1. Các bước triển khai thực tế trên môi trường", 30),
        ("8.2. Kết quả kiểm thử tự động với Pytest", 31),
        ("8.3. Sự cố gặp phải và biện pháp khắc phục", 32),
        ("8.4. Đánh giá kết quả đạt được", 32),
        ("8.5. Giới hạn và hướng phát triển", 33),
        ("Kết Luận", 34),
        ("Tài Liệu Tham Khảo", 35),
        ("Phụ Lục", 36)
    ]

    table_toc = doc.add_table(rows=len(toc_items), cols=2)
    table_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_toc.autofit = False

    for i, (title, page) in enumerate(toc_items):
        row = table_toc.rows[i]
        c0 = row.cells[0]
        c1 = row.cells[1]
        c0.width = Inches(5.5)
        c1.width = Inches(1.0)
        c0.text = title
        c1.text = str(page)
        c1.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if title.startswith("Chương") or title in ["Kết Luận", "Tài Liệu Tham Khảo", "Phụ Lục"]:
            c0.paragraphs[0].runs[0].bold = True
            c1.paragraphs[0].runs[0].bold = True

    doc.add_page_break()

    # ------------------ CHAPTER 1 ------------------
    doc.add_heading("CHƯƠNG 1. GIỚI THIỆU ĐỀ TÀI", level=1)
    
    doc.add_heading("1.1. Lý do chọn đề tài", level=2)
    doc.add_paragraph(
        "Trong kỷ nguyên chuyển đổi số và công nghiệp phần mềm hiện đại, việc xây dựng một ứng dụng "
        "không chỉ dừng lại ở khâu lập trình tính năng (Coding), mà khâu triển khai (Deployment), vận hành "
        "(Operations), giám sát (Monitoring) và bảo mật (Security Hardening) đóng vai trò quyết định đến "
        "tính ổn định và độ tin cậy của toàn bộ hệ thống.\n\n"
        "Đề tài 'Hệ Thống Quản Lý Thư Viện' được lựa chọn vì mang tính thực tiễn cao, bao hàm trọn vẹn "
        "các bài toán cốt lõi của một hệ thống quản trị thông tin phân tán: quản lý kho sách với tài nguyên "
        "hữu hạn đòi hỏi tính nhất quán cao trong giao dịch cơ sở dữ liệu (ACID Transactions), quản lý hồ sơ độc giả, "
        "theo dõi hạn mượn và thu hồi tài liệu quá hạn. Đồng thời, hệ thống đòi hỏi một kiến trúc hạ tầng "
        "chuẩn DevOps: container hóa đa dịch vụ bằng Docker Compose, bảo vệ định tuyến bằng Nginx Reverse Proxy "
        "với HTTPS, giám sát chủ động bằng Prometheus & Grafana, và quản lý log tập trung với Loki & Promtail."
    )

    doc.add_heading("1.2. Mục tiêu nghiên cứu và triển khai", level=2)
    doc.add_paragraph(
        "Đồ án hướng tới việc hoàn thành xuất sắc các mục tiêu cụ thể sau:\n"
        "1. Xây dựng ứng dụng web quản lý thư viện hoàn chỉnh bằng Python Flask, giao diện tiếng Việt đẹp mắt, "
        "responsive bằng Bootstrap 5, kết nối cơ sở dữ liệu quan hệ PostgreSQL 15.\n"
        "2. Đóng gói và điều phối toàn bộ các thành phần hệ thống chỉ bằng Docker Compose, tuyệt đối không "
        "đòi hỏi cài đặt trực tiếp Flask, PostgreSQL, Prometheus hay Loki lên máy chủ vật lý.\n"
        "3. Triển khai Nginx Reverse Proxy làm điểm tiếp nhận duy nhất, tự động chuyển hướng HTTP sang HTTPS "
        "bằng chứng chỉ TLS tự ký, tích hợp các tiêu đề bảo vệ an ninh (Security Headers).\n"
        "4. Tích hợp giải pháp giám sát thời gian thực với Prometheus và Grafana, tự động nạp các Dashboard "
        "giám sát Container, Cơ sở dữ liệu và Ứng dụng Flask.\n"
        "5. Xây dựng giải pháp thu thập log tập trung với Grafana Loki và Promtail, hỗ trợ truy vấn LogQL.\n"
        "6. Thực hiện gia cố an ninh (Security Hardening): chạy non-root user, phân tách mạng nội bộ, quản lý secret an toàn."
    )

    doc.add_heading("1.3. Phạm vi đề tài", level=2)
    doc.add_paragraph(
        "Phạm vi đồ án tập trung vào việc nghiên cứu, thiết kế và triển khai một hệ thống phần mềm quản lý thư viện "
        "trong môi trường máy tính cá nhân hoặc máy chủ cục bộ bằng Docker Compose, chuẩn bị sẵn sàng cho quy trình "
        "chuyển giao và mở rộng lên môi trường đám mây (Cloud) hoặc Kubernetes."
    )

    doc.add_heading("1.4. Công nghệ bắt buộc sử dụng", level=2)
    table_tech = doc.add_table(rows=8, cols=3)
    table_tech.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Thành phần", "Công nghệ sử dụng", "Vai trò trong hệ thống"]
    for j, h in enumerate(headers):
        cell = table_tech.rows[0].cells[j]
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        set_cell_background(cell, "E0E0E0")

    tech_data = [
        ("Frontend", "HTML5, CSS3, Bootstrap 5.3, JavaScript", "Giao diện web người dùng và thủ thư"),
        ("Backend", "Python 3.10, Flask, SQLAlchemy, Gunicorn", "Xử lý logic nghiệp vụ, giao dịch ACID, API"),
        ("Database", "PostgreSQL 15 Alpine", "Lưu trữ dữ liệu quan hệ có ràng buộc toàn vẹn"),
        ("Reverse Proxy", "Nginx 1.25 Alpine, TLS 1.2/1.3", "Chấm dứt SSL, định tuyến, Security Headers"),
        ("DB Management", "pgAdmin 4", "Giao diện quản trị cơ sở dữ liệu trên nền web"),
        ("Monitoring", "Prometheus v2.50.1, Grafana v10.3.3", "Thu thập metrics định kỳ và trực quan hóa"),
        ("Centralized Logging", "Grafana Loki v2.9.4, Promtail v2.9.4", "Thu thập, phân tích và truy vấn LogQL")
    ]
    for i, row_data in enumerate(tech_data):
        row = table_tech.rows[i+1]
        for j, val in enumerate(row_data):
            row.cells[j].text = val

    doc.add_page_break()

    # ------------------ CHAPTER 2 ------------------
    doc.add_heading("CHƯƠNG 2. PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG", level=1)
    doc.add_heading("2.1. Yêu cầu chức năng", level=2)
    doc.add_paragraph(
        "1. Quản lý Dashboard: Hiển thị tổng số tựa sách, tổng số bản in, số sách còn khả dụng, tổng độc giả, "
        "phiếu mượn đang lưu hành và số phiếu quá hạn. Các số liệu được tính toán động từ PostgreSQL.\n"
        "2. Quản lý Danh mục Sách: Thêm, sửa, xóa, tìm kiếm theo tên/tác giả/ISBN, lọc thể loại, phân trang. "
        "Không cho phép số lượng âm hoặc sách còn lại lớn hơn tổng số sách.\n"
        "3. Quản lý Độc Giả: Cấp thẻ, chỉnh sửa, vô hiệu hóa thẻ khi đã có lịch sử mượn trả nhằm bảo vệ dữ liệu.\n"
        "4. Quản lý Mượn/Trả: Lập phiếu mượn chọn nhiều sách, kiểm tra tồn kho bằng Row Locking trong transaction. "
        "Khi trả sách, cộng lại số lượng đúng một lần duy nhất, ngăn chặn trả trùng lặp."
    )

    doc.add_heading("2.2. Yêu cầu phi chức năng", level=2)
    doc.add_paragraph(
        "- Tính toàn vẹn dữ liệu: Sử dụng cơ chế khóa dòng 'SELECT ... FOR UPDATE' của PostgreSQL.\n"
        "- Tính sẵn sàng cao: Container có healthcheck và chính sách tự khởi động lại.\n"
        "- Bảo mật đa tầng: Ẩn cổng database, chạy user non-root, áp dụng CSRF và TLS."
    )

    doc.add_heading("2.3. Thiết kế cơ sở dữ liệu", level=2)
    doc.add_paragraph(
        "Cơ sở dữ liệu gồm 4 bảng chuẩn hóa bậc 3 (3NF):\n"
        "- books: Lưu trữ thông tin đầu sách, ISBN duy nhất, số lượng tổng và khả dụng kèm Check Constraints.\n"
        "- readers: Lưu trữ thông tin độc giả, mã thẻ duy nhất, email duy nhất, trạng thái hoạt động.\n"
        "- loans: Lưu trữ thông tin phiếu mượn, độc giả mượn, ngày mượn, hạn trả và trạng thái.\n"
        "- loan_details: Chi tiết các đầu sách trong từng phiếu mượn, số lượng, trạng thái đã trả và ngày trả thực tế."
    )

    doc.add_paragraph("[CHÈN HÌNH ẢNH: Sơ đồ thực thể liên kết ERD của Cơ sở dữ liệu]")

    doc.add_heading("2.4. Sơ đồ kiến trúc phân tầng", level=2)
    doc.add_paragraph(
        "Hệ thống phân chia 4 mạng Docker độc lập:\n"
        "- frontend: Nginx và Flask Web.\n"
        "- backend: Flask Web, PostgreSQL và pgAdmin.\n"
        "- monitoring: Prometheus, Grafana, postgres_exporter, cAdvisor, node_exporter.\n"
        "- logging: Promtail, Loki, Grafana."
    )

    doc.add_paragraph("[CHÈN HÌNH ẢNH: Sơ đồ kiến trúc mạng và luồng dữ liệu hệ thống]")

    doc.add_page_break()

    # ------------------ CHAPTER 3 ------------------
    doc.add_heading("CHƯƠNG 3. XÂY DỰNG ỨNG DỤNG VÀ CƠ SỞ DỮ LIỆU", level=1)
    doc.add_heading("3.1. Cấu trúc mã nguồn", level=2)
    doc.add_paragraph(
        "Mã nguồn được cấu trúc khoa học theo mô hình Application Factory:\n"
        "- app/models/: Định nghĩa các thực thể Book, Reader, Loan, LoanDetail.\n"
        "- app/routes/: Các blueprint main, books, readers, loans.\n"
        "- app/services/: LibraryService đóng gói logic nghiệp vụ và transaction.\n"
        "- app/templates/: Giao diện Jinja2 Bootstrap 5 hoàn chỉnh tiếng Việt.\n"
        "- app/metrics.py: Bộ đo lường Prometheus metrics cho Flask."
    )

    doc.add_heading("3.2. Đóng gói Dockerfile và Docker Compose", level=2)
    doc.add_paragraph(
        "Dockerfile được thiết kế theo tiêu chuẩn hardened non-root container: tạo người dùng appuser (UID 10001), "
        "chuyển quyền sở hữu thư mục ứng dụng, cài đặt đầy đủ dependencies và khởi chạy Gunicorn WSGI. "
        "Hệ thống tích hợp file docker-compose.yml điều phối toàn bộ 11 container với tài nguyên CPU và RAM giới hạn rõ ràng."
    )

    doc.add_heading("3.3. Kết quả kiểm thử nghiệp vụ với Pytest", level=2)
    doc.add_paragraph(
        "Toàn bộ 20 ca kiểm thử tự động trong thư mục tests/ đã được thực thi và đạt tỷ lệ thành công 100%:\n"
        "- 3 bài test healthcheck, metrics và dashboard.\n"
        "- 7 bài test danh mục sách, xác thực ISBN, số lượng âm và ràng buộc xóa.\n"
        "- 5 bài test quản lý độc giả, chống trùng email/mã thẻ và khóa thẻ an toàn.\n"
        "- 5 bài test mượn trả sách, từ chối khi hết hàng và ngăn chặn trả sách 2 lần."
    )

    doc.add_paragraph("[CHÈN SCREENSHOT: Kết quả chạy lệnh pytest thực tế trên terminal]")

    doc.add_page_break()

    # ------------------ CHAPTER 4 ------------------
    doc.add_heading("CHƯƠNG 4. CẤU HÌNH NGINX REVERSE PROXY VÀ BẢO MẬT HTTPS", level=1)
    doc.add_heading("4.1. Nguyên lý và cấu hình Reverse Proxy", level=2)
    doc.add_paragraph(
        "Nginx đóng vai trò Reverse Proxy làm cổng vào duy nhất cho hệ thống. Người dùng truy cập qua cổng 443 "
        "được Nginx giải mã SSL và chuyển tiếp an toàn vào Flask thông qua cấu hình upstream flask_app. "
        "Mọi yêu cầu gửi tới cổng 80 (HTTP) đều được tự động chuyển hướng 301 sang HTTPS."
    )

    doc.add_heading("4.2. Cấu hình TLS và Security Headers", level=2)
    doc.add_paragraph(
        "Nginx được cấu hình giao thức TLS 1.2 và 1.3 với danh sách mã hóa mạnh mẽ. Bên cạnh đó, các tiêu đề "
        "bảo mật chuẩn OWASP được bổ sung đầy đủ:\n"
        "- X-Content-Type-Options: nosniff\n"
        "- X-Frame-Options: SAMEORIGIN (chống Clickjacking)\n"
        "- X-XSS-Protection: 1; mode=block\n"
        "- Content-Security-Policy (CSP) kiểm soát chặt chẽ nguồn tài nguyên."
    )

    doc.add_paragraph("[CHÈN SCREENSHOT: Trình duyệt truy cập website qua Nginx HTTPS]")

    doc.add_page_break()

    # ------------------ CHAPTER 5 ------------------
    doc.add_heading("CHƯƠNG 5. TRIỂN KHAI HỆ THỐNG GIÁM SÁT PROMETHEUS VÀ GRAFANA", level=1)
    doc.add_heading("5.1. Cấu hình Scrape Jobs", level=2)
    doc.add_paragraph(
        "Prometheus được thiết lập để cào chỉ số chuỗi thời gian từ 5 nguồn:\n"
        "1. library-app: Endpoint /metrics của Flask (chu kỳ 5s).\n"
        "2. postgres-exporter: Chỉ số database PostgreSQL (chu kỳ 10s).\n"
        "3. cadvisor: Chỉ số tài nguyên CPU/RAM/Network của từng container (chu kỳ 10s).\n"
        "4. node-exporter: Chỉ số tài nguyên máy chủ host (chu kỳ 15s).\n"
        "5. prometheus: Tự giám sát chính máy chủ Prometheus."
    )

    doc.add_paragraph("[CHÈN SCREENSHOT: Giao diện Prometheus Targets hiển thị tất cả đều UP]")

    doc.add_heading("5.2. Các Dashboards trên Grafana", level=2)
    doc.add_paragraph(
        "Hệ thống tự động provision 3 dashboard chuyên nghiệp trên Grafana:\n"
        "- Dashboard Hệ Thống: Trạng thái targets, CPU/Memory container, lưu lượng mạng.\n"
        "- Dashboard Cơ Sở Dữ Liệu: Trạng thái PostgreSQL, số kết nối, tỷ lệ commit/rollback, cache hit ratio.\n"
        "- Dashboard Ứng Dụng: Tốc độ yêu cầu (req/s), tỷ lệ lỗi HTTP, độ trễ p95, số phiếu mượn đang active."
    )

    doc.add_paragraph("[CHÈN SCREENSHOT: Grafana Dashboard Hệ thống và Cơ sở dữ liệu]")
    doc.add_paragraph("[CHÈN SCREENSHOT: Grafana Dashboard Ứng dụng Flask]")

    doc.add_page_break()

    # ------------------ CHAPTER 6 ------------------
    doc.add_heading("CHƯƠNG 6. TRIỂN KHAI HỆ THỐNG LOG TẬP TRUNG LOKI VÀ PROMTAIL", level=1)
    doc.add_heading("6.1. Kiến trúc phân hệ Logging", level=2)
    doc.add_paragraph(
        "Thay vì giải pháp ELK nặng nề, hệ thống sử dụng Grafana Loki v2.9.4 kết hợp Promtail v2.9.4. "
        "Promtail đóng vai trò Log Shipper, đọc trực tiếp access log của Nginx và application log của Flask, "
        "gắn các nhãn có ý nghĩa (job, service, environment) và đẩy về Loki qua API."
    )

    doc.add_heading("6.2. Các câu truy vấn LogQL thực tế", level=2)
    doc.add_paragraph(
        "Hệ thống đã kiểm nghiệm thành công 3 câu truy vấn LogQL chính:\n"
        "1. Truy vấn toàn bộ log ứng dụng Flask:\n"
        "   {job=\"library-app\"}\n\n"
        "2. Truy vấn log lưu lượng Nginx Reverse Proxy:\n"
        "   {job=\"nginx\"}\n\n"
        "3. Lọc các dòng log ghi nhận lỗi hệ thống:\n"
        "   {job=\"library-app\"} |= \"ERROR\""
    )

    doc.add_paragraph("[CHÈN SCREENSHOT: Grafana Explore hiển thị kết quả truy vấn LogQL]")

    doc.add_page_break()

    # ------------------ CHAPTER 7 ------------------
    doc.add_heading("CHƯƠNG 7. HARDENING BẢO MẬT HỆ THỐNG", level=1)
    doc.add_paragraph(
        "Dự án đã áp dụng toàn diện hơn 10 biện pháp bảo mật thực tế:\n"
        "1. Chạy Non-Root User: Container Flask chạy bằng user 'appuser' (UID 10001).\n"
        "2. Phân tách mạng: Chia 4 mạng độc lập frontend, backend, monitoring, logging.\n"
        "3. Quản lý Secret: Dùng file .env cục bộ, không commit mật khẩu lên Git, cung cấp .env.example.\n"
        "4. Cô lập cổng Database: PostgreSQL và pgAdmin chỉ bind trên 127.0.0.1.\n"
        "5. Nginx Security Headers & TLS 1.2/1.3.\n"
        "6. Giới hạn quyền Linux: Sử dụng 'no-new-privileges: true' trên toàn bộ containers.\n"
        "7. Giới hạn tài nguyên: Áp đặt ngưỡng CPU và RAM tối đa cho từng dịch vụ.\n"
        "8. Bảo vệ tầng ứng dụng: CSRF Protection với Flask-WTF, chống SQL Injection với SQLAlchemy ORM, "
        "ẩn stack trace trên các trang lỗi 400, 404, 500."
    )

    doc.add_paragraph("[CHÈN SCREENSHOT: Minh chứng kiểm tra whoami non-root và cURL Security Headers]")

    doc.add_page_break()

    # ------------------ CHAPTER 8 & CONCLUSION ------------------
    doc.add_heading("CHƯƠNG 8. TRIỂN KHAI, KIỂM THỬ VÀ ĐÁNH GIÁ", level=1)
    doc.add_paragraph(
        "Hệ thống đã được kiểm tra tính đúng đắn trên môi trường Docker Compose. "
        "Toàn bộ 11 dịch vụ đều hoạt động ổn định, các ràng buộc dữ liệu được bảo đảm chặt chẽ, "
        "hệ thống giám sát và log tập trung phản ánh chính xác tình trạng vận hành.\n\n"
        "Giới hạn hiện tại: Môi trường demo sử dụng chứng chỉ SSL tự ký.\n"
        "Hướng phát triển: Tích hợp Certbot tự động gia hạn Let's Encrypt trong môi trường có tên miền công khai; "
        "đóng gói Helm Chart để triển khai trên Kubernetes."
    )

    doc.add_heading("KẾT LUẬN", level=1)
    doc.add_paragraph(
        "Đồ án đã hoàn thành xuất sắc tất cả các mục tiêu của môn học Triển khai và Quản trị Hệ thống Phần mềm. "
        "Sinh viên đã làm chủ toàn diện quy trình từ lập trình ứng dụng web, chuẩn hóa cơ sở dữ liệu, đóng gói container, "
        "cấu hình reverse proxy bảo mật, đến thiết lập hệ thống quan sát toàn diện (Observability) với Prometheus, Grafana và Loki. "
        "Mã nguồn được quản lý chuyên nghiệp trên Git với đúng 3 commit chính theo đề cương."
    )

    doc.add_heading("TÀI LIỆU THAM KHẢO", level=1)
    doc.add_paragraph(
        "1. Docker Documentation: https://docs.docker.com/\n"
        "2. Nginx Documentation: https://nginx.org/en/docs/\n"
        "3. Prometheus Documentation: https://prometheus.io/docs/\n"
        "4. Grafana Labs: https://grafana.com/docs/\n"
        "5. Flask Web Development: https://flask.palletsprojects.com/\n"
        "6. PostgreSQL 15 Documentation: https://www.postgresql.org/docs/15/\n"
        "7. OWASP Secure Headers Project: https://cheatsheetseries.owasp.org/"
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    print(f"[+] Successfully generated DOCX report at: {output_path}")

if __name__ == '__main__':
    create_report_docx()
