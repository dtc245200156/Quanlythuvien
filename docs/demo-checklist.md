# KỊCH BẢN VÀ CHECKLIST BÁO CÁO DEMO ĐỒ ÁN
### Triển khai và Quản trị Hệ thống Phần mềm - Đề tài: Hệ Thống Quản Lý Thư Viện

---

## 1. Trình Tự Các Bước Báo Cáo Trước Giảng Viên (Demo Flow)

Để bài báo cáo đạt điểm tối đa (10/10), hãy thực hiện bài thuyết trình và demo theo trình tự 8 bước tiêu chuẩn sau:

### Bước 1: Giới thiệu Repository & Lịch sử Git 3 Commit
- **Thao tác**: Mở Terminal tại thư mục dự án và chạy:
  ```bash
  git log --oneline -n 3
  ```
- **Nội dung giải thích**:
  - *"Thưa thầy/cô, dự án được quản lý mã nguồn chặt chẽ qua Git với đúng 3 commit nghiệp vụ tương ứng các giai đoạn triển khai:"*
    1. `feat: deploy library app with PostgreSQL and Nginx reverse proxy`: Khởi tạo ứng dụng Flask, database PostgreSQL, pgAdmin, Nginx reverse proxy và HTTPS.
    2. `feat: add Prometheus and Grafana monitoring`: Tích hợp hệ thống giám sát metrics phân tán với Prometheus, postgres_exporter, cAdvisor, node_exporter và 3 dashboard Grafana.
    3. `feat: add centralized logging with Loki and Promtail`: Tích hợp kho log tập trung Loki, bộ chuyển tiếp log Promtail, kiểm thử nghiệp vụ pytest và hoàn thiện tài liệu báo cáo.

### Bước 2: Khởi động & Kiểm tra Trạng thái Cụm Container
- **Thao tác**: Chạy lệnh:
  ```bash
  docker compose ps
  ```
- **Nội dung giải thích**:
  - Chỉ ra 11 container đang chạy đồng bộ (`Up / healthy`).
  - Giải thích sự phân tách của 4 mạng Docker (`frontend`, `backend`, `monitoring`, `logging`) theo nguyên tắc đặc quyền tối thiểu.

### Bước 3: Demo Nginx Reverse Proxy & Chuyển Hướng HTTPS
- **Thao tác**:
  1. Mở trình duyệt gõ `http://localhost`. Trình duyệt lập tức chuyển hướng (HTTP 301) sang `https://localhost`.
  2. Bấm vào biểu tượng ổ khóa SSL trên thanh địa chỉ, mở xem chứng chỉ tự ký (`localhost / DevOps University`).
  3. Mở tab Network trong F12 Developer Tools, chỉ ra các Security Headers: `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Content-Security-Policy`.
- **Nội dung giải thích**:
  - Nginx là điểm tiếp nhận duy nhất, ứng dụng Flask không mở cổng công khai trực tiếp ra Internet.

### Bước 4: Demo Các Chức Năng Ứng Dụng Quản Lý Thư Viện
1. **Trang Tổng Quan (Dashboard)**:
   - Các con số thống kê (Tổng sách, tổng độc giả, phiếu đang mượn, sách quá hạn) được truy vấn động từ cơ sở dữ liệu PostgreSQL.
2. **Quản lý Sách**:
   - Tìm kiếm sách theo từ khóa (tên sách, tác giả, ISBN).
   - Thêm một cuốn sách mới và cho thấy tồn kho khả dụng tự động tăng.
3. **Quản lý Độc Giả**:
   - Thêm độc giả mới.
   - Trình bày cơ chế bảo toàn dữ liệu: Độc giả đã có lịch sử mượn trả sẽ không bị xóa cứng (hard delete) mà chuyển sang trạng thái "Ngừng hoạt động" (soft delete).
4. **Quy trình Mượn & Trả Sách (Điểm nhấn kỹ thuật)**:
   - Lập phiếu mượn mới: Chọn độc giả và nhiều sách cùng lúc.
   - Thử mượn vượt số lượng còn lại trong kho -> Hệ thống báo lỗi và rollback an toàn.
   - Xác nhận mượn thành công -> Kiểm tra số lượng sách trong kho bị trừ ngay lập tức trong transaction với khóa dòng (`with_for_update()`).
   - Xử lý trả sách: Trả từng cuốn hoặc trả toàn bộ. Thử bấm trả lần hai -> Hệ thống từ chối ngăn chặn trả trùng lặp.
   - Chỉ ra phiếu mượn demo quá hạn (`overdue`) hiển thị nhãn cảnh báo đỏ trên giao diện.

### Bước 5: Demo Quản Trị Cơ Sở Dữ Liệu Với pgAdmin 4
- **Thao tác**: Mở `http://localhost:5050`, đăng nhập và mở server `db`.
- **Nội dung giải thích**:
  - Mở bảng `books`, `readers`, `loans`, `loan_details`.
  - Chứng minh các ràng buộc khóa ngoại (Foreign Keys), Check Constraints (`available_quantity <= total_quantity`) và toàn vẹn dữ liệu được bảo đảm tại tầng DB.

### Bước 6: Demo Hệ Thống Giám Sát Prometheus
- **Thao tác**: Mở `http://localhost:9090` -> Vào mục **Status** -> **Targets**.
- **Nội dung giải thích**:
  - Chỉ ra tất cả các endpoints đang ở trạng thái **UP (1/1)**:
    - `library-app` (Flask `/metrics`)
    - `postgres-exporter` (PostgreSQL metrics)
    - `cadvisor` (Container metrics)
    - `node-exporter` (Host metrics)
    - `prometheus` (Self metrics)
  - Chạy thử một câu lệnh PromQL ví dụ: `rate(http_requests_total[1m])` hoặc `pg_up`.

### Bước 7: Demo Các Dashboard Trực Quan Trên Grafana
- **Thao tác**: Mở `http://localhost:3000`, vào thư mục **Library Infrastructure**:
  1. **Dashboard Hệ Thống (System Overview)**: CPU container, Memory làm việc, lưu lượng mạng Receive/Transmit.
  2. **Dashboard Cơ Sở Dữ Liệu (Postgres Metrics)**: Trạng thái DB, số lượng kết nối đang mở, tỷ lệ giao dịch commit/rollback, cache hit ratio.
  3. **Dashboard Ứng Dụng (Flask Metrics)**: Tốc độ xử lý yêu cầu (req/s), tỷ lệ lỗi 4xx/5xx, thời gian phản hồi theo phân vị (p95, p50), số phiếu mượn active thời gian thực.
  - *Thực hiện thao tác trên website thư viện (tải lại trang, thêm sách) và cho giảng viên thấy các biểu đồ trên Grafana nhảy số ngay lập tức!*

### Bước 8: Demo Thu Thập Log Tập Trung Với Loki & LogQL
- **Thao tác**: Trong Grafana, vào mục **Explore**, chọn datasource **Loki**:
  - **Query 1: Log ứng dụng Flask**:
    ```logql
    {job="library-app"}
    ```
    *(Hiển thị toàn bộ log nghiệp vụ phát sinh từ Flask và Gunicorn).*
  - **Query 2: Log truy cập Nginx**:
    ```logql
    {job="nginx"}
    ```
    *(Hiển thị log truy cập IP, URL, mã trạng thái HTTP từ Nginx).*
  - **Query 3: Lọc cảnh báo và lỗi**:
    ```logql
    {job="library-app"} |= "ERROR"
    ```
    *(Chứng minh khả năng lọc log lỗi nhanh chóng phục vụ điều tra sự cố).*

---

## 2. Bảng Tóm Tắt URL Trình Chiếu Nhanh

| Mục Demo | Địa chỉ URL | Cần chú ý khi trình bày |
| :--- | :--- | :--- |
| **Website Thư Viện** | `https://localhost` | Demo chuyển hướng 80 -> 443, bảo mật HTTPS |
| **Health API** | `https://localhost/health` | Trả về JSON trạng thái database |
| **Grafana Dashboards** | `http://localhost:3000` | Mở 3 dashboard đã chuẩn bị sẵn |
| **Grafana LogQL** | `http://localhost:3000/explore` | Chạy 3 câu truy vấn LogQL |
| **Prometheus Targets**| `http://localhost:9090/targets` | Chứng minh tất cả targets đều UP |
| **pgAdmin 4** | `http://localhost:5050` | Xem bảng dữ liệu và cấu trúc schema |
