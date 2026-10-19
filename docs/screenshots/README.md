# DANH MỤC HÌNH ẢNH MINH CHỨNG (SCREENSHOTS CHECKLIST)
### Đồ án môn học: Triển khai và Quản trị Hệ thống Phần mềm

Thư mục này được sử dụng để lưu trữ các hình ảnh chụp màn hình thực tế từ hệ thống đang chạy để đính kèm vào báo cáo đồ án (`docs/report.md` và `docs/report.docx`).

> [!IMPORTANT]
> Theo quy định học phần, không sử dụng hình ảnh giả lập hoặc ảnh vẽ không có thật. Hãy chụp màn hình trực tiếp từ máy tính sau khi khởi động hệ thống với các bước hướng dẫn dưới đây.

---

## Danh Sách 12 Ảnh Cần Chụp Và Tên File Tương Ứng

| STT | Tên File Đề Xuất | Vị Trí / Màn Hình Cần Chụp | Hướng Dẫn Thao Tác Chụp |
| :---: | :--- | :--- | :--- |
| **1** | `01_dashboard_overview.png` | Trang Dashboard Quản lý Thư viện | Mở `https://localhost`, chụp toàn bộ màn hình hiển thị 4 thẻ thống kê (Tổng sách, Độc giả, Phiếu mượn, Quá hạn) và bảng lịch sử gần đây. |
| **2** | `02_books_management.png` | Trang Danh mục Sách | Vào menu "Quản lý Sách", thực hiện tìm kiếm một từ khóa và chụp danh sách sách hiển thị kèm số lượng tồn kho. |
| **3** | `03_readers_management.png` | Trang Danh sách Độc giả | Vào menu "Quản lý Độc giả", chụp bảng hiển thị danh sách các độc giả cùng trạng thái thẻ thư viện. |
| **4** | `04_borrow_return_action.png`| Chi tiết Phiếu Mượn & Trả Sách | Vào menu "Mượn & Trả sách", mở chi tiết một phiếu mượn có các đầu sách và nút thao tác "Trả sách này" hoặc nhãn "Quá hạn". |
| **5** | `05_pgadmin_database.png` | Giao diện pgAdmin 4 | Mở `http://localhost:5050`, mở cây thư mục `Servers` -> `db` -> `Databases` -> `library_db` -> `Tables` hiển thị 4 bảng (`books`, `readers`, `loans`, `loan_details`). |
| **6** | `06_nginx_https_security.png`| Nginx HTTPS & Security Headers | Mở tab mới truy cập `https://localhost`, bấm F12 mở tab **Network**, bấm vào request trang chủ để hiển thị các Response Headers: `X-Frame-Options`, `Content-Security-Policy`, `X-Content-Type-Options`. |
| **7** | `07_prometheus_targets.png` | Prometheus Targets Page | Mở `http://localhost:9090/targets`, chụp màn hình thể hiện tất cả các job (`library-app`, `postgres-exporter`, `cadvisor`, `node-exporter`) đều ở trạng thái **UP (1/1)** màu xanh lá. |
| **8** | `08_grafana_system_dashboard.png` | Grafana System Overview Dashboard | Mở `http://localhost:3000`, vào dashboard **Hệ Thống - Giám Sát Tài Nguyên & Containers**, chụp các biểu đồ CPU, Memory và Network của các container. |
| **9** | `09_grafana_app_dashboard.png` | Grafana Application Metrics Dashboard | Mở dashboard **Ứng Dụng - Flask Metrics & Hiệu Năng**, chụp biểu đồ Throughput (req/s), Latency phân vị và số lượng Active Loans thời gian thực. |
| **10**| `10_grafana_logql_loki.png` | Grafana Explore với LogQL | Vào mục Explore trên Grafana, chọn datasource Loki, nhập câu truy vấn `{job="library-app"}` hoặc `{job="nginx"}` và chụp các dòng log thực tế được trả về. |
| **11**| `11_docker_compose_ps.png` | Terminal hiển thị trạng thái Docker Compose | Chạy lệnh `docker compose ps` trong Terminal và chụp kết quả toàn bộ 11 containers đang ở trạng thái `running / healthy`. |
| **12**| `12_security_hardening_proof.png` | Minh chứng kiểm tra Hardening | Mở Terminal chạy lệnh `docker compose exec web whoami` (kết quả `appuser`) và lệnh `curl -kI https://localhost` để chứng minh quyền non-root và SSL. |
